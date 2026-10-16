# polyglot-quant-eval

One eval harness, many runtimes, per-language scoring.

**Question.** For a 3B multilingual model shipped for edge use (Cohere Labs' Tiny Aya), how
much language capability does each real deployment quantization format lose per language,
does judge-based evaluation reveal damage that multilingual MMLU hides, and can multilingual
calibration or QAT buy the capability back?

**How it works.** Every runtime is driven through an OpenAI-compatible HTTP endpoint
(vLLM, SGLang, llama-server, mlx_lm.server, an ExecuTorch shim). The harness wraps
`lm-evaluation-harness` for the built-in multilingual tasks and adds custom generation
tasks (FLORES-200, Language Confusion) and a pairwise judge module. All results are
normalized into one JSONL schema (`schema/results.schema.json`) keyed by
model x format x quantizer x calibration x runtime x device x task x language.

**Design decisions (fixed).**
- Languages (14): ar de en es fr it ja ko pt zh hi bn sw yo. See `configs/languages.yaml`.
- Tasks: Global-MMLU (lm-eval `global_mmlu_*`, 5-shot), Belebele (0-shot), MGSM (direct and
  native CoT where the language exists), FLORES-200 both directions (custom, chrF++ and
  spBLEU), Language Confusion (custom), XCOPA/XStoryCloze/XWinograd where available.
- Scoring modes: loglikelihood MCQ on runtimes that return logprobs (vLLM, SGLang,
  llama-server); generation-based MCQ with letter extraction on runtimes that do not
  (mlx_lm.server, ExecuTorch shim). Mode is recorded in every row. Never compare across
  modes without saying so.
- Judge: pairwise BF16 vs quantized, randomized order, 150 Aya Dolly-200 prompts per
  language, LLM judge plus multilingual reward model. Human eval for Bangla (native speaker)
  and community-annotated languages.
- Reference row: BF16 served by vLLM on the RTX 5090.

**Status.** Plumbing stage: reference runtime, smoke test and results schema are in place. See `LOG.md`.

**Quick start (smoke test).**
```bash
# terminal 1, on the 5090 box
bash scripts/serve_vllm.sh                 # serves CohereLabs/tiny-aya-global at :8000
# terminal 2
bash scripts/smoke_test.sh                 # Belebele, 3 languages, 50 items each
python scripts/normalize.py results/smoke --format bf16 --runtime vllm --device rtx5090 \
    --out results/rows.jsonl
python scripts/report.py results/rows.jsonl
```

License: Apache-2.0 for code. Results JSONL: CC-BY-4.0. Model weights are not in this repo.
