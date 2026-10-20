# Local Q4 control comparison

The locally quantized Q4_K_M completed the same 150 frozen questions. It matches
the official Q4 on all 150 selected choices and all 600 stored candidate
log-likelihood values exactly in this run. The local build is a controlled
baseline, not a quality improvement.

| Language | Original BF16 | BF16 GGUF | Official Q4 | Local Q4 | Local minus BF16 | Delta gap vs English |
|---|---:|---:|---:|---:|---:|---:|
| English | 35/50, 70% | 35/50, 70% | 33/50, 66% | 33/50, 66% | -4 pp | 0 pp |
| Bangla | 31/50, 62% | 31/50, 62% | 30/50, 60% | 30/50, 60% | -2 pp | +2 pp |
| Hindi | 27/50, 54% | 27/50, 54% | 23/50, 46% | 23/50, 46% | -8 pp | -4 pp |
| Overall | 93/150 | 93/150 | 86/150 | 86/150 | -4.7 pp | — |

Local Q4 versus either BF16 arm changes 15 choices: nine correct-to-wrong,
two wrong-to-correct, four wrong-to-other-wrong. Bangla has seven changed
choices (three regressions, two improvements, two wrong-to-wrong), identical
to the official Q4 comparison. Bangla's accuracy gap versus English is -6 pp
in both Q4 arms and -8 pp in both BF16 arms; Hindi's is -20 pp and -16 pp.

## What the fourth arm adds

The local file was made directly from our audited BF16 GGUF, using the pinned
native llama.cpp quantizer, default Q4_K_M allocation, eight threads and no
importance matrix or training. Its source, executable, command and output hash
are recorded in the [build evidence](https://github.com/grinder81/tiny-aya-edge/tree/main/reports/local-q4-control).
It is 2,143,976,960 bytes; the official file is 2,143,977,056 bytes. Both contain
216 Q4_K, 37 Q6_K and 37 F32 tensors with matching names/shapes and parameter count.

The local-versus-source-BF16 comparison now has known quantization provenance.
Agreement with the official artifact on this sample does not prove their files,
weights, recipes, or behavior on other inputs are identical. The official
artifact's historical provenance remains unknown.

## Validation and execution

All 150 prompt token sequences and 600 candidate sequences matched the frozen
original-tokenizer lock before evaluation. Candidate decoding round-tripped
exactly. Separate native generation smoke tests passed in English and Bangla
with the source BF16 EOS override. Evaluation uses the same patched Python
llama.cpp runtime, server settings, upstream GGUFLM scorer, zero-shot prompts,
no chat template and raw accuracy as the existing GGUF arms.

The launch-only `--local-q4-only` flag selects the new artifact without changing
the scorer or sample selection. Each five-question checkpoint is retained with
full upstream evidence. Runtime metadata and identity are adjacent to the raw
files. The comparison validator checks manifest hashes, shared runner/lock
hashes, unique samples, identical prompts/targets, finite likelihoods, and
recomputed per-item accuracy before comparing arms.

Reproduce the comparison with:

```sh
python scripts/compare_local_q4.py results/stage1/local-q4-fifty results/stage1/fifty-per-language
```

`comparison.json` contains the resulting metrics; `rows.jsonl` adds three
separate schema-compatible local-arm rows. Existing results are unchanged.
The result timestamp marks aggregation, not per-question inference time.

These remain 50-item-per-language development measurements, with matched
translations and overlap with earlier inspected examples. No statistical
significance, general Bangla quality, calibrated confidence, or architectural
cause is established. The earlier translation ambiguities remain in the
official scoring. No larger run, training, phone benchmark, controlled
generation-speed or peak-memory test was started.
