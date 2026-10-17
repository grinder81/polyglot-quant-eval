# CLAUDE.md — polyglot-quant-eval

Purpose: per-language evaluation of quantized multilingual LLMs across on-device and server
runtimes. Case study: Cohere Labs' Tiny Aya (cohere2, 3.35B, CC-BY-NC, gated). Companion repo:
github.com/grinder81/tiny-aya-edge (builds, device protocol, microbenchmarks). The design decisions in the
README are fixed; do not re-decide languages, tasks, metrics or scoring modes in code.

## Fixed decisions (see README)
- 14 languages in `configs/languages.yaml`. Task codes per family live there; `null` means the
  upstream task does not exist for that language.
- Scoring modes: `loglikelihood_mcq` on runtimes with logprobs (vLLM, SGLang, llama-server);
  `generation` on runtimes without (mlx_lm.server, ExecuTorch shim). Every row records `mode`.
  Never silently compare across modes.
- Reference row is BF16 on vLLM, RTX 5090. All deltas are against it.
- One results schema: `schema/results.schema.json`. Rows are JSONL, append-only, CC-BY-4.0.
- No UI. CLI, JSON, figures only.
- Every delta table also prints the gap vs English. Never report a non-English delta without it.
- Format names for diagnostics start with `diag-` (e.g. `diag-ffn_down-q8`, base `diag-flat-q4k`);
  they are compared against `diag-flat-q4k`, not against Q4_K_M.
- Repaired candidates are compared against Q4_K_M, a uniform allocation and random allocations
  (3 seeds) at the same total shipped bytes (budget 2.2 GB including tokenizer and adapters).
- Four disjoint data pools split by source document: calibration, train, development, test. All
  selection on development; test is touched once by frozen finalists.
- Report absolute task success beside pairwise preference; BF16's answer is not assumed correct.

## Layout
- `configs/` languages, runtimes (OpenAI-compatible endpoints), tasks.
- `scripts/serve_vllm.sh`, `scripts/smoke_test.sh` (plumbing check), `scripts/normalize.py`
  (lm_eval JSON -> schema rows), `scripts/report.py` (per-language tables, deltas vs BF16).
- `tasks_custom/` FLORES-200 and Language Confusion (generation tasks), judge module,
  ExecuTorch shim.
- `tests/` synthetic lm_eval output; CI runs normalize + report on it.
- `LOG.md` dated entries with numbers; keep them factual.

## Conventions
- Python 3.11+. Keep dependencies to what `pyproject.toml` lists; add only with a reason in the PR.
- Every script runs from the repo root and takes paths as arguments; nothing hardcodes a machine.
- New task families: add to `configs/tasks.yaml`, extend `build_reverse_index` in `normalize.py`
  if the naming pattern differs, add a synthetic case to `tests/`.
- Numbers in README or LOG must come from a results JSONL that is committed or linked.
- Commit messages: imperative, one line, body says what was measured if anything was.

## What is verified and what is not
- Verified on synthetic data: normalize.py, report.py.
- Not verified until the 5090 box runs it: smoke_test.sh task names, `--apply_chat_template` with
  `local-completions`, llama-server logprob support on /v1/completions.
