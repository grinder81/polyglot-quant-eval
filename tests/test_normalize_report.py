"""normalize.py and report.py end to end on synthetic lm_eval output. Run: python -m pytest -q"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")

def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout

def test_end_to_end(tmp_path):
    rows = tmp_path / "rows.jsonl"
    run("scripts/normalize.py", f"{FIX}/bf16", "--format", "bf16", "--runtime", "vllm", "--device", "rtx5090", "--bits", "16", "--out", str(rows))
    run("scripts/normalize.py", f"{FIX}/q4", "--format", "gguf-q4_k_m", "--runtime", "llama_server_cuda", "--device", "rtx5090", "--bits", "4.5", "--out", str(rows))
    recs = [json.loads(l) for l in rows.read_text().splitlines() if l.strip()]
    assert len(recs) == 6
    by = {(r["format"], r["task"], r["language"]): r for r in recs}
    assert by[("bf16", "belebele", "bn")]["value"] == 0.62
    assert by[("gguf-q4_k_m", "mgsm_direct", "bn")]["metric"] == "exact_match"
    assert all(r["mode"] in ("loglikelihood_mcq", "generation") for r in recs)
    # schema required fields present
    schema = json.load(open(os.path.join(ROOT, "schema", "results.schema.json")))
    for r in recs:
        for k in schema["required"]:
            assert k in r, k
    out = run("scripts/report.py", str(rows))
    assert "delta vs bf16" in out and "bn" in out
