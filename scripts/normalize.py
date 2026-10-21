#!/usr/bin/env python3
"""Convert lm_eval output JSON into schema rows (JSONL).

Usage:
  python scripts/normalize.py results/smoke --format bf16 --runtime vllm --device rtx5090 --out results/rows.jsonl
Reads every results_*.json under the given directory.
"""
import argparse, datetime, glob, json, os, re, sys, uuid
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)

def build_reverse_index(langs, tasks):
    """Map upstream lm_eval task name -> (family, language, metric, mode, fewshot)."""
    idx = {}
    for fam, t in tasks["tasks"].items():
        pat = t.get("lm_eval_pattern")
        if not pat:
            continue
        field = re.search(r"\{(\w+)\}", pat).group(1)
        for code, info in langs["languages"].items():
            v = info.get(field)
            if v is None:
                continue
            idx[pat.format(**{field: v})] = (fam, code, t["metric"], t["mode"], t.get("fewshot"))
    return idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--format", required=True)
    ap.add_argument("--runtime", required=True)
    ap.add_argument("--device", required=True)
    ap.add_argument("--model-id", default="CohereLabs/tiny-aya-global")
    ap.add_argument("--model-revision")
    ap.add_argument("--sample-set-hash", help="Verified sample-membership manifest SHA256; never inferred from n")
    ap.add_argument("--scoring-contract-hash", help="Verified scoring/template settings manifest SHA256")
    ap.add_argument("--quantizer"); ap.add_argument("--quantizer-version")
    ap.add_argument("--calibration-set", default="none")
    ap.add_argument("--bits", type=float); ap.add_argument("--group-size", type=int)
    ap.add_argument("--backend"); ap.add_argument("--runtime-version"); ap.add_argument("--os-version")
    ap.add_argument("--mode-override", choices=["loglikelihood_mcq", "generation"])
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    langs = load_yaml(os.path.join(ROOT, "configs/languages.yaml"))
    tasks = load_yaml(os.path.join(ROOT, "configs/tasks.yaml"))
    rev = build_reverse_index(langs, tasks)
    run_id = a.run_id or f"{a.format}-{a.runtime}-{uuid.uuid4().hex[:8]}"
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    files = glob.glob(os.path.join(a.results_dir, "**", "results_*.json"), recursive=True)
    if not files:
        sys.exit(f"no results_*.json under {a.results_dir}")
    rows = []
    for fp in files:
        with open(fp) as f:
            data = json.load(f)
        nsamples = data.get("n-samples", {})
        cfgs = data.get("configs", {})
        for task, metrics in data.get("results", {}).items():
            if task not in rev:
                continue  # group aggregates and unknown tasks are skipped
            fam, code, metric, mode, fewshot = rev[task]
            key = next((k for k in metrics if k.split(",")[0] == metric), None)
            if key is None:
                continue
            se_key = key.replace(metric, metric + "_stderr")
            n = nsamples.get(task, {}).get("effective") or nsamples.get(task, {}).get("original") or 0
            rows.append({
                "run_id": run_id, "timestamp": ts, "model_id": a.model_id, "model_revision": a.model_revision,
                "sample_set_hash": a.sample_set_hash, "scoring_contract_hash": a.scoring_contract_hash,
                "format": a.format, "quantizer": a.quantizer, "quantizer_version": a.quantizer_version,
                "calibration_set": a.calibration_set, "bits": a.bits, "group_size": a.group_size,
                "runtime": a.runtime, "runtime_version": a.runtime_version, "backend": a.backend,
                "device": a.device, "os_version": a.os_version,
                "task": fam, "language": code, "metric": metric,
                "value": float(metrics[key]),
                "stderr": (float(metrics[se_key]) if se_key in metrics and metrics[se_key] not in ("N/A", None) else None),
                "n": int(n), "mode": a.mode_override or mode,
                "fewshot": cfgs.get(task, {}).get("num_fewshot", fewshot),
                "seed": None, "prompt_hash": None, "parity_rate": None,
                "source_file": os.path.relpath(fp, ROOT), "notes": None,
            })
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {a.out}")

if __name__ == "__main__":
    main()
