"""Flip rate as a function of the reference arm's top-two likelihood margin.

Joins two completed arms (reference and candidate) by language/source/question using the
raw five-question harness shards, bins each question by the reference arm's top-two margin
in nats, and reports how often the candidate arm selects a different option in each bin.
This asks whether answer churn under compression follows confidence (near-ties flip) or
language. It makes no claim about mechanism and never reads holdout data.

Usage:
  python scripts/margin_flip_analysis.py --reference results/stage2/bf16-three-hundred/bf16-gguf \
      --candidate results/stage1/local-q4-three-hundred/local-q4 --output /new/margin-flips.json
"""
import argparse
import glob
import json
import os

BINS = [(0.0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, float("inf"))]


def load_arm(directory):
    """Return {(task, source, question): (scores, target)} from raw harness shards."""
    records = {}
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if "samples" not in data:
            continue
        for task, rows in data["samples"].items():
            for sample in rows:
                doc = sample.get("doc", {})
                key = (task, doc.get("link"), str(doc.get("question_number")))
                if key[1] is None:
                    raise ValueError(f"missing source link in {path}")
                if key in records:
                    raise ValueError(f"duplicate identity {key} in {path}")
                scores = [float(r[0]) for r in sample["filtered_resps"]]
                if len(scores) != 4:
                    raise ValueError(f"expected four candidate scores for {key}")
                records[key] = (scores, int(sample["target"]))
    return records


def margin(scores):
    ordered = sorted(scores, reverse=True)
    return ordered[0] - ordered[1]


def argmax(scores):
    return max(range(len(scores)), key=scores.__getitem__)


def analyze(reference, candidate):
    """Per task: flip counts by reference-margin bin, plus the share of near-tie items."""
    keys = sorted(set(reference) & set(candidate))
    if not keys:
        raise ValueError("no joined identities")
    out = {}
    for task in sorted({k[0] for k in keys}):
        rows = [(reference[k], candidate[k], k) for k in keys if k[0] == task]
        bins = []
        for lo, hi in BINS:
            sel = [(r, c) for r, c, _ in rows if lo <= margin(r[0]) < hi]
            flips = sum(1 for r, c in sel if argmax(r[0]) != argmax(c[0]))
            bins.append({"margin_nats": [lo, hi if hi != float("inf") else None], "n": len(sel),
                         "flips": flips, "flip_rate": (flips / len(sel)) if sel else None})
        near = sum(1 for r, _, _ in rows if margin(r[0]) < 1.0)
        out[task] = {"n": len(rows), "bins": bins,
                     "share_margin_below_1_nat": near / len(rows),
                     "total_flips": sum(b["flips"] for b in bins)}
    return out


def render(result):
    lines = []
    for task, stats in result.items():
        lines.append(f"{task}: n={stats['n']}, flips={stats['total_flips']}, "
                     f"items with reference margin < 1 nat: {100*stats['share_margin_below_1_nat']:.0f}%")
        for b in stats["bins"]:
            lo, hi = b["margin_nats"]
            label = f"[{lo}, {hi})" if hi is not None else f"[{lo}, inf)"
            rate = "n/a" if b["flip_rate"] is None else f"{100*b['flip_rate']:.1f}%"
            lines.append(f"  margin {label:12s} n={b['n']:4d}  flips={b['flips']:3d}  rate={rate}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reference", required=True, help="directory of raw shards for the reference arm")
    parser.add_argument("--candidate", required=True, help="directory of raw shards for the candidate arm")
    parser.add_argument("--output", required=True, help="new JSON output path")
    args = parser.parse_args()
    if os.path.exists(args.output):
        raise FileExistsError(args.output)
    result = analyze(load_arm(args.reference), load_arm(args.candidate))
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump({"reference": args.reference, "candidate": args.candidate, "bins_nats": BINS[:-1] + [[2.0, None]],
                   "results": result}, handle, indent=1)
    print(render(result))


if __name__ == "__main__":
    main()
