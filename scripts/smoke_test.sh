#!/usr/bin/env bash
# Plumbing test: Belebele, 3 languages, 50 items each, against a vLLM endpoint.
# Validates: endpoint reachable, task names exist, loglikelihood works through completions, results land in results/smoke.
set -euo pipefail
BASE_URL="${BASE_URL:-http://127.0.0.1:8000/v1/completions}"
SERVED="${SERVED:-tiny-aya-global}"
TOKENIZER="${TOKENIZER:-CohereLabs/tiny-aya-global}"
OUT="${OUT:-results/smoke}"
LIMIT="${LIMIT:-50}"

echo "[1/3] checking task names exist in this lm_eval install"
lm_eval --tasks list 2>/dev/null | grep -E "^belebele_(eng_Latn|ben_Beng|hin_Deva)$" || {
  echo "Belebele task names not found. Run: lm_eval --tasks list | grep belebele_ | head"; exit 1; }
echo "    global_mmlu tasks available:"; lm_eval --tasks list 2>/dev/null | grep -E "^global_mmlu" | head -20 || true
echo "    mgsm tasks available:";        lm_eval --tasks list 2>/dev/null | grep -E "^mgsm_(direct|native_cot)_" | head -20 || true

echo "[2/3] endpoint check"
curl -sf "${BASE_URL%/completions}/models" | head -c 300; echo

echo "[3/3] running"
lm_eval --model local-completions \
  --model_args "model=${SERVED},base_url=${BASE_URL},num_concurrent=8,max_retries=3,tokenized_requests=False,tokenizer=${TOKENIZER},tokenizer_backend=huggingface,max_length=8192" \
  --tasks belebele_eng_Latn,belebele_ben_Beng,belebele_hin_Deva \
  --num_fewshot 0 \
  --limit "${LIMIT}" \
  --apply_chat_template \
  --output_path "${OUT}" \
  --log_samples
echo "done -> ${OUT}"
