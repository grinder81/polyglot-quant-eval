#!/usr/bin/env bash
# Serve Tiny Aya BF16 on the RTX 5090 as the reference runtime.
# Prereq: `hf auth login` with a token that has accepted the gated CohereLabs/tiny-aya-global terms.
set -euo pipefail
MODEL="${MODEL:-CohereLabs/tiny-aya-global}"
PORT="${PORT:-8000}"
exec vllm serve "$MODEL" \
  --served-model-name tiny-aya-global \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --port "$PORT"
