# Local Q4 expanded development baseline

All 900 questions completed on 20 October 2026 (Pacific time): 300 matched questions each in English, Bangla, and Hindi. Only the locally built Q4_K_M model ran. No other model has a 300-per-language comparison here.

| Language | Correct | Accuracy | Approximate 95% passage-cluster bootstrap interval |
|---|---:|---:|---:|
| English | 226/300 | 75.3% | 70.3–80.1% |
| Bangla | 189/300 | 63.0% | 57.5–68.4% |
| Hindi | 176/300 | 58.7% | 53.1–64.3% |

Total: 591/900, or 65.7%. Translations are paired, so this total does not represent 900 independent underlying questions. Each language covers the same 300 question groups from 250 source passages. Intervals resample entire source passages with replacement, retaining all selected questions per passage (10,000 draws, seed 42, percentile endpoints). They describe sampling variation conditional on this development sample; they do not include translation/key errors, benchmark contamination, or broad language/task representativeness. No pooled confidence interval is claimed.

English/Bangla paired outcomes: both correct 174, English only correct 52, Bangla only correct 15, both wrong 59. These are behavioral results, not evidence identifying a model layer or quantization cause. The official benchmark labels are preserved, including suspected ambiguous items.

## Provenance and validation

The join-control correction merged in [tiny-aya-edge's tokenizer fix](https://github.com/grinder81/tiny-aya-edge/pull/23) passed all 900 contexts and 3,600 candidate tokenization checks before execution. All 300 per language were rerun from zero under this runtime; earlier results were not reused or relabeled. Model weights, questions, zero-shot plain prompts, A/B/C/D likelihood scoring, and the upstream harness were unchanged.

`local-q4-runtime.json` records the model, shared-library and Python-wrapper hashes and package versions. `local-q4/identity.json` binds the runtime manifest, full frozen sample-lock hash and unchanged scoring runner hash. `sample-identities.json` is a compact projection of that exact lock, verified against its hash when copied. It retains original indices, source/question keys, prompt/continuation hashes and targets. The full original lock remains in WSL at `/home/shohag/tiny-aya-stage1/pilot/sample-lock.json`.

Validation checks exactly 180 five-item shards; 900 unique language/source/question identities; exact expected shard membership; prompt and continuation hashes; four finite candidate scores; target labels; per-item argmax correctness; shard accuracy reconciliation; and matching question keys across languages. Runtime-manifest bytes match the checkpoint identity. Raw evidence is retained without newline conversion.

The upstream raw `doc_id` field is inconsistent with the frozen document index in 707 records. Content, prompt hashes, targets and scores pass the identity checks. Therefore summaries join by `(language, passage source, question number)`, not raw `doc_id` or array position. Raw records remain unchanged. The exporter/index-label discrepancy needs separate investigation; no harness or scoring patch was introduced to produce this report. Earlier narrative item identifiers may be raw IDs, so locate those examples by passage and question text.

Reproduce from the repository root:

```sh
python scripts/summarize_expanded_local.py results/stage1/local-q4-three-hundred
python -m unittest discover -s tests -p test_expanded_local.py
```

`summary.json` contains computed counts, paired outcomes and uncertainty. `rows.jsonl` contains schema-style accuracy rows. The original runtime paths in the manifest are provenance, not portable executable paths.

## Interpretation and remaining work

The larger sample is a more informative local-Q4 baseline, not a model improvement. On the first 50 English and Bangla questions, the fresh run still scores 33/50 and 30/50, respectively; BF16 previously scored 35/50 and 31/50 on those same questions. That small matched comparison remains separate from the 300-question result. Do not compare 300-question Q4 accuracy with 50-question BF16 accuracy as a compression delta.

This run measures reading-comprehension choice accuracy. It does not measure free-form Bangla quality, calibrated confidence, generation throughput, peak memory or phone performance. Broader BF16 comparisons and hardware tests remain separate work. No larger or other-model run was launched.
