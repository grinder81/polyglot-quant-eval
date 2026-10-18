# Fifty-question-per-language baseline

All three arms finished the same 50 questions in each of English, Bangla and
Hindi (450 scored question/model pairs, four candidate likelihoods per pair).
The two BF16 arms chose identical answers on all 150 questions. Q4 changed
15 answers: nine right-to-wrong, two wrong-to-right, and four wrong-to-different-wrong.

| Language | Original BF16 / vLLM | BF16 GGUF / Python | Q4_K_M GGUF / Python | Q4 minus BF16 (pp) | Delta gap vs English (pp) |
|---|---:|---:|---:|---:|---:|
| English | 35/50 (70%) | 35/50 (70%) | 33/50 (66%) | -4 | 0 |
| Bangla | 31/50 (62%) | 31/50 (62%) | 30/50 (60%) | -2 | +2 |
| Hindi | 27/50 (54%) | 27/50 (54%) | 23/50 (46%) | -8 | -4 |
| Overall | 93/150 (62%) | 93/150 (62%) | 86/150 (57.3%) | -4.7 | — |

Accuracy gaps relative to English are -8 pp for Bangla and -16 pp for Hindi in
both BF16 arms; Q4 gaps are -6 pp and -20 pp respectively. These are descriptive
sample results, not evidence of a general language ranking or a statistically
established language-specific compression effect. Each question changes a
language's score by two percentage points. The matched translations also mean
the 150 items should not be treated as 150 independent source questions for
uncertainty estimates. No significance claim is made.

| BF16 GGUF to Q4 | Changed choices | Right → wrong | Wrong → right | Wrong → different wrong |
|---|---:|---:|---:|---:|
| English | 2 | 2 | 0 | 0 |
| Bangla | 7 | 3 | 2 | 2 |
| Hindi | 6 | 4 | 0 | 2 |

Bangla's net loss of one correct answer hides seven changed choices. These are
useful cases for inspection, but do not by themselves identify an attention,
MLP, negation, or other mechanism failure. The original and converted BF16
likelihoods differ even though their selected answers match.

## Method and reproducibility

This is the authorized expansion of the ten-question development smoke run.
It uses the frozen first 50 aligned samples per language, seed 42, zero shots,
no chat template, context 8192, upstream Belebele prompts and raw `acc`.
Dataset revision: `7899cdfa4e1e0d733fd77c848e2c273cb1d32be2`.
The sample lock SHA is recorded in each `identity.json`. This pool overlaps
the inspected smoke questions and is not an untouched final test set.

GGUF uses upstream GGUFLM; vLLM uses upstream LocalCompletionsAPI with the
original HF tokenizer, tokenized requests and BOS. No custom adapter or scoring
change was introduced. The runners validate against the frozen lock. The
summary additionally checks 50 unique document hashes per language/arm,
identical full prompt/continuation strings and targets across arms, finite
four-choice likelihoods, recomputed argmax accuracy, and runtime manifest hashes.

Runs were sequential: Q4, BF16 GGUF, then original BF16/vLLM. Five-question
checkpoints contain complete upstream per-item evidence. Runtime manifests
record artifact and installed code hashes, commands and package inventories.
The GGUF runtime contains the local digit-tokenizer and Python decoding-buffer
fixes (tiny-aya-edge PRs 17 and 20), plus the exact-output echo-ranking
optimization (PR 21). The original artifacts were not modified.

The vLLM client uses the vLLM Python executable with eval site-packages on
PYTHONPATH; it is a mixed dependency environment, not a newly consolidated
lockfile environment. Preserve that distinction when reproducing. Server
package inventories describe the launch environments, while each shard records
the evaluator environment. Occasional Git metadata warnings did not prevent
complete output; implementation was merged as polyglot-quant-eval commit
`e68fd7d` before this run. Temporary servers stopped after completion.

The official Q4 artifact's exact original checkpoint and quantizer provenance
remain unknown. This is a controlled runtime comparison of audited artifacts,
not a claim that quantization alone is proved to cause every difference.

Run `python scripts/summarize_baseline.py results/stage1/fifty-per-language`
to regenerate `summary.json` and the nine schema-compatible `rows.jsonl` rows.
The timestamp in those rows marks result aggregation, not individual inference.
Raw files are retained unchanged. `summary.json` also reports mean change in
top-two log-likelihood margin, in natural-log units; that is a score separation,
not calibrated confidence or statistical confidence.

No controlled generation speed, peak memory, energy, or phone benchmark was
performed. Request durations include scoring integration overhead and must not
be reported as generation tokens per second.
