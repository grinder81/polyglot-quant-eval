# Matched BF16 versus local Q4, 300 questions per language

All 900 BF16 GGUF items completed and passed validation against the frozen sample
identities. The comparison uses the completed local-Q4 run in
`../../stage1/local-q4-three-hundred`. Both arms use the same patched runtime,
server settings, scoring runner, sample lock and unchanged upstream letter
likelihood scoring. This is a GGUF BF16 reference, not the vLLM reference.

| Language | BF16 correct / 300 | Q4 correct / 300 | Q4 minus BF16 (points) | Paired 95% interval (points) | BF16 / Q4 gap to English (points) |
|---|---:|---:|---:|---:|---:|
| English | 230 (76.67%) | 226 (75.33%) | -1.33 | [-3.83, 1.02] | 0 / 0 |
| Bangla | 188 (62.67%) | 189 (63.00%) | +0.33 | [-2.77, 3.64] | -14.00 / -12.33 |
| Hindi | 184 (61.33%) | 176 (58.67%) | -2.67 | [-6.29, 0.99] | -15.33 / -16.67 |

Totals are 602/900 for BF16 and 591/900 for Q4. These totals weight the three
languages equally and do not replace the language-specific comparisons.

| Language | Changed choice | Correct to wrong | Wrong to correct | Wrong to different wrong |
|---|---:|---:|---:|---:|
| English | 17 | 9 | 5 | 3 |
| Bangla | 36 | 12 | 13 | 11 |
| Hindi | 37 | 19 | 11 | 7 |

Bangla's net accuracy is nearly unchanged despite 12% answer churn. The paired
intervals include zero for every language; this does not demonstrate equivalence
or exclude meaningful damage. Relative to English's compression delta, Bangla is
+1.67 points (95% interval [-2.33, 5.61]) and Hindi is -1.33 points
([-5.21, 2.61]). The data do not establish disproportionate Bangla damage at Q4.

## Letter counts and next control

| Language / arm | A | B | C | D |
|---|---:|---:|---:|---:|
| Gold, each language | 72 | 92 | 72 | 64 |
| English BF16 | 106 | 73 | 68 | 53 |
| English Q4 | 110 | 75 | 65 | 50 |
| Bangla BF16 | 137 | 66 | 54 | 43 |
| Bangla Q4 | 127 | 67 | 57 | 49 |
| Hindi BF16 | 134 | 58 | 59 | 49 |
| Hindi Q4 | 148 | 55 | 48 | 49 |

The Bangla A count decreases under Q4, while Hindi's increases. A single global
shift toward A cannot be inferred from the earlier small sample. Frequencies
alone do not establish position bias: the next experiment rotates answer choices
while preserving their content and remapping the key. No model component is
localized by these results.

## Evidence and validation

- `bf16-gguf/`: all 180 unmodified five-question harness outputs and run identity.
- `bf16-gguf-runtime.json` and `preflight.json`: runtime/model hashes and successful
  token checks for 900 contexts and 3,600 candidate sequences.
- `sample-identities.json`: projection of the byte-hash-verified original lock.
- `rows.jsonl` and `summary.json`: validated question records and absolute results.
- `comparison.json`: paired deltas, answer transitions, letter counts and intervals.

Validation checks the complete expected file set, 900 unique language/source/
question identities, shard membership, targets, prompt and continuation hashes,
four finite candidate scores, and recomputed predictions and accuracies. Raw
harness document IDs remain unchanged; joins use source/question identity.
Runtime settings and runner/lock identities match across arms, excluding the
model artifact and arm name. The completed process exited with status zero.

Intervals use 10,000 joint source-passage bootstrap draws, seed 42, retaining all
questions within each sampled passage and using the same draws across arms and
languages (250 source clusters). They describe development-sample uncertainty
conditional on this instrument. Translation concerns retain their official keys;
the reserved final holdout was not scored. Generation quality, speed and memory
are not measured here. The repeated harness Git provenance warning is retained
in the external run logs; explicit runtime manifests supply the pinned identities.

Reproduce from the repository root:

```sh
python scripts/summarize_expanded_local.py results/stage2/bf16-three-hundred --arm bf16-gguf
python scripts/compare_expanded.py --reference results/stage2/bf16-three-hundred \
  --candidate results/stage1/local-q4-three-hundred --output /new/comparison.json
```
