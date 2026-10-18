# Completed ten-question smoke evaluation

All three arms selected identical answers: English 2/3, Bangla 1/4, Hindi 1/3,
total 4/10. Per-item records, original text, and candidate likelihoods are in
the accompanying JSON files. Predictions use argmax of each candidate's first
`filtered_resps` value; the boolean is not a likelihood. No accuracy-changing
flips occurred. This sample cannot establish language rankings or quantization
equivalence. The extra fourth Bangla item has no English/Hindi counterpart here.

The frozen sample lock selected four Bangla and three each English/Hindi items.
No chat template, zero shots, context 8192, upstream Belebele task, raw `acc`.
Each runner checks prompt hashes, candidates, and targets against the lock.
The vLLM runner additionally checks all selected token sequences against the lock.

## Runtime and integration

GGUF arms use llama-cpp-python 0.3.36 with the local llama.cpp digit-split patch
and Python decoding-buffer patch recorded in tiny-aya-edge PRs #17 and #20.
The original artifact is served by vLLM 0.27.1 in BF16, eager mode, context 8192,
GPU memory utilization 0.5, legacy runner enabled for WSL, port 8099. All runs
used the pinned artifacts already audited in tiny-aya-edge.

GGUF uses unchanged upstream `GGUFLM`. vLLM uses unchanged upstream
`LocalCompletionsAPI`, Hugging Face tokenizer, tokenized requests and BOS enabled.
The GGUF integration was rejected for vLLM because its character-offset
interpretation failed validation. Remote tokenizer autodetection was unavailable
because this server lacks tokenizer_info. No custom adapter was introduced.

For vLLM the existing vLLM Python environment loads the installed lm-eval package
by appending the eval environment's site-packages to sys.path. This supplies its
existing Transformers dependency without installing packages; it is not a new
isolated lockfile environment. Record this mixed dependency environment when
reproducing, and consolidate it before scaling up. The eight synthetic token
sequences match; likelihoods differ from the earlier direct 512-context reference
by up to about 0.0613 natural-log units. This is reported, not claimed as exact
numerical parity. See vllm-local-api-check.json.

All 40 candidate requests completed per arm. A trailing Git metadata warning
(`Not a valid object name HEAD`) did not abort the runs: exit status was zero
and complete per-item results were saved. Record repository revisions separately.
The earlier interrupted attempts are not results. Temporary model servers were
stopped after completion.

## Limits and next decision

These are likelihood-selected choices, not generated explanations. The observed
English/Bangla/Hindi difference is based on very few questions. Negation is a
hypothesis from one matched item, not a demonstrated general weakness.
No controlled generation-speed, peak-memory, energy, or phone measurement was
performed. The different request durations are not model throughput benchmarks.
Do not expand the dataset until the next experiment scope is agreed.
