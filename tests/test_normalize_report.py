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
    assert "No deltas" in out and "bn" in out
    assert "no averaging" in out


def test_explicit_reference_cli_preserves_provenance(tmp_path):
    rows = tmp_path / 'explicit.jsonl'
    for source, run_id, fmt, runtime in [('bf16', 'canonical', 'bf16', 'vllm'),
            ('bf16', 'control', 'bf16', 'llama_cpp_python'),
            ('q4', 'candidate', 'gguf-q4_k_m', 'llama_cpp_python')]:
        run('scripts/normalize.py', f'{FIX}/{source}', '--format', fmt, '--runtime', runtime,
            '--device', 'rtx5090', '--run-id', run_id, '--runtime-version', 'pinned',
            '--model-revision', 'source-commit', '--backend', 'cuda', '--os-version', 'wsl',
            '--sample-set-hash', 'a' * 64, '--scoring-contract-hash', 'b' * 64,
            '--out', str(rows))
    records = [json.loads(line) for line in rows.read_text().splitlines()]
    assert all(r['sample_set_hash'] == 'a' * 64 for r in records)
    out = run('scripts/report.py', str(rows), '--task', 'belebele', '--canonical-run',
              'canonical', '--control-run', 'control', '--candidate-run', 'candidate')
    assert all(label in out for label in ['runtime/conversion', 'same-runtime compression',
                                        'total difference', 'gap vs English', 'unavailable'])
