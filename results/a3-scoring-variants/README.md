# A3 scoring-format results

Completed 22 October 2026. All 1,440 shards passed the frozen complete-evidence loader. Each arm scored the same 100 development questions per language in four cyclic rotations under three variants: 3,600 contexts and 14,400 candidate likelihoods per arm. Both arms share 300 distinct questions; rotations and variants are repeated measurements, not additional independent questions. No holdout was evaluated.

The conservative recommendation is to retain plain-letter summed-likelihood scoring under the newly validated cold runtime, pending the user’s explicit canonical-contract decision. Chat-letter is a useful sensitivity diagnostic, with mixed accuracy/consistency consequences; option-text performs substantially worse here. This recommendation does not relabel historical A1/A2 evidence or authorize B5 before that decision.

## Scope, scoring and uncertainty

Primary predictions maximize the sum of continuation log probabilities. Separate `acc_norm` predictions divide that sum by the Unicode character count of the displayed choice text, excluding the added ASCII-space delimiter. This is neither token nor UTF-8-byte normalization. No EOS is appended. The frozen variants compare plain prompt + letter, original chat template + letter, and plain prompt + complete option text; they do not estimate a full chat-by-answer-format interaction.

Predictions are mapped back to original option indices for content comparisons. All-four consistency is the fraction of questions selecting identical content across rotations, regardless of correctness. Six-pair agreement is the fraction of the six within-question rotation pairs selecting identical content. Each cell has 100 questions, 400 scored contexts and 600 rotation pairs.

Intervals resample 96 source clusters jointly across languages, both arms and all variants, with 10,000 draws and seed 42. Percentages below are point estimates; delta intervals are in percentage points (pp). The full report retains intervals for every absolute metric and paired contrast, plus r0–r3 accuracy. These are exploratory development endpoints with no multiplicity adjustment. An interval containing zero does not establish equivalence; isolated exclusions do not support a confirmatory claim after selection.

## Primary raw summed-likelihood accuracy

| Variant | Language | BF16 mean | Q4 mean | Q4−BF16, pp [95% CI] | Compression delta−English, pp [95% CI] |
| --- | --- | --- | --- | --- | --- |
| plain-letter | English | 76.75% | 76.00% | -0.75 [-3.03, 1.53] | +0.00 [0.00, 0.00] |
| plain-letter | Bangla | 59.50% | 59.25% | -0.25 [-3.28, 2.81] | +0.50 [-3.54, 4.41] |
| plain-letter | Hindi | 58.00% | 55.75% | -2.25 [-5.73, 0.77] | -1.50 [-5.61, 2.27] |
| chat-letter | English | 80.00% | 76.50% | -3.50 [-5.95, -1.25] | +0.00 [0.00, 0.00] |
| chat-letter | Bangla | 62.25% | 59.25% | -3.00 [-5.93, -0.25] | +0.50 [-3.37, 4.34] |
| chat-letter | Hindi | 58.25% | 56.75% | -1.50 [-4.08, 1.00] | +2.00 [-1.02, 5.00] |
| plain-option-text | English | 54.00% | 52.25% | -1.75 [-4.61, 1.20] | +0.00 [0.00, 0.00] |
| plain-option-text | Bangla | 40.00% | 37.00% | -3.00 [-7.07, 0.99] | -1.25 [-6.19, 3.61] |
| plain-option-text | Hindi | 41.25% | 39.75% | -1.50 [-5.94, 2.75] | +0.25 [-4.50, 4.95] |

All raw rotation-mean English-relative compression interaction intervals include zero. The chat-letter Q4−BF16 intervals exclude zero in English (−3.50 pp [−5.95, −1.25]) and Bangla (−3.00 pp [−5.93, −0.25]); the remaining raw compression intervals include zero. Thus chat-letter exposes a larger observed compression penalty in both languages, while this sample does not establish a Bangla-specific penalty or its absence. These exploratory differences are part of the scoring-format sensitivity, not a reason to select an endpoint after observing it.

Original-order (r0) accuracy, all-four content consistency and six-pair agreement follow. Each BF16 / Q4 pair is a percentage; the report preserves exact predictions and all metric intervals.

| Variant | Language | r0 accuracy BF16 / Q4 | All-four consistency BF16 / Q4 | Six-pair agreement BF16 / Q4 |
| --- | --- | --- | --- | --- |
| plain-letter | English | 77.00% / 73.00% | 67.00% / 65.00% | 78.00% / 76.83% |
| plain-letter | Bangla | 59.00% / 59.00% | 43.00% / 44.00% | 58.33% / 61.00% |
| plain-letter | Hindi | 59.00% / 57.00% | 52.00% / 46.00% | 66.17% / 60.00% |
| chat-letter | English | 80.00% / 73.00% | 76.00% / 69.00% | 85.17% / 78.50% |
| chat-letter | Bangla | 60.00% / 58.00% | 48.00% / 39.00% | 64.83% / 58.83% |
| chat-letter | Hindi | 63.00% / 61.00% | 48.00% / 41.00% | 65.33% / 60.00% |
| plain-option-text | English | 50.00% / 49.00% | 30.00% / 29.00% | 54.00% / 52.00% |
| plain-option-text | Bangla | 34.00% / 34.00% | 29.00% / 22.00% | 50.67% / 45.17% |
| plain-option-text | Hindi | 33.00% / 36.00% | 29.00% / 24.00% | 50.50% / 45.33% |

## Separate character-normalized diagnostic

For plain-letter and chat-letter, raw and `acc_norm` predictions, metrics, intervals, histograms and flips are identical: every candidate choice has one Unicode character. Their normalized results are exactly the corresponding two variant blocks above. Option-text normalization changes predictions and is reported separately below; it is not substituted for the primary result.

| Language | BF16 mean | Q4 mean | Q4−BF16, pp [95% CI] | Compression delta−English, pp [95% CI] |
| --- | --- | --- | --- | --- |
| English | 41.50% | 40.75% | -0.75 [-4.13, 2.53] | +0.00 [0.00, 0.00] |
| Bangla | 31.25% | 30.00% | -1.25 [-3.71, 1.24] | -0.50 [-4.85, 3.83] |
| Hindi | 27.25% | 27.25% | +0.00 [-3.32, 2.81] | +0.75 [-3.71, 5.20] |

| Language | r0 accuracy BF16 / Q4 | All-four consistency BF16 / Q4 | Six-pair agreement BF16 / Q4 |
| --- | --- | --- | --- |
| English | 40.00% / 37.00% | 44.00% / 34.00% | 66.00% / 59.33% |
| Bangla | 29.00% / 28.00% | 43.00% / 45.00% | 64.67% / 65.50% |
| Hindi | 24.00% / 24.00% | 37.00% / 36.00% | 60.83% / 56.83% |

Normalized option-text agreement can rise while accuracy falls. Consistency alone is not evidence that the selected content is correct.

## Paired variant accuracy differences

Every prespecified variant pair is shown, right minus left. English-relative gaps in the last column are Bangla−English / Hindi−English **point estimates only**: the frozen report does not emit intervals for these variant interactions. The per-language difference intervals are paired; subtracting their CI endpoints would not produce a valid interaction interval. Letter-pair normalized results equal raw results.

### Raw sums

| Arm | Difference | English, pp [95% CI] | Bangla, pp [95% CI] | Hindi, pp [95% CI] | Gap vs English BN / HI, pp (point only) |
| --- | --- | --- | --- | --- | --- |
| bf16-gguf | chat-letter − plain-letter | +3.25 [0.26, 6.13] | +2.75 [-0.77, 6.37] | +0.25 [-3.54, 4.04] | -0.50 / -3.00 |
| bf16-gguf | plain-option-text − plain-letter | -22.75 [-29.34, -16.49] | -19.50 [-27.91, -11.30] | -16.75 [-24.01, -9.85] | +3.25 / +6.00 |
| bf16-gguf | plain-option-text − chat-letter | -26.00 [-32.83, -19.39] | -22.25 [-30.15, -14.65] | -17.00 [-24.50, -9.85] | +3.75 / +9.00 |
| local-q4 | chat-letter − plain-letter | +0.50 [-2.78, 4.04] | +0.00 [-3.88, 3.96] | +1.00 [-3.28, 5.25] | -0.50 / +0.50 |
| local-q4 | plain-option-text − plain-letter | -23.75 [-30.67, -17.25] | -22.25 [-30.67, -14.03] | -16.00 [-23.50, -8.66] | +1.50 / +7.75 |
| local-q4 | plain-option-text − chat-letter | -24.25 [-31.55, -17.33] | -22.25 [-30.20, -14.69] | -17.00 [-24.75, -9.60] | +2.00 / +7.25 |

### Normalized option-text differences

| Arm | Difference | English, pp [95% CI] | Bangla, pp [95% CI] | Hindi, pp [95% CI] | Gap vs English BN / HI, pp (point only) |
| --- | --- | --- | --- | --- | --- |
| bf16-gguf | plain-option-text − plain-letter | -35.25 [-43.94, -26.44] | -28.25 [-38.24, -17.93] | -30.75 [-38.86, -22.77] | +7.00 / +4.50 |
| bf16-gguf | plain-option-text − chat-letter | -38.50 [-47.06, -29.85] | -31.00 [-40.75, -21.17] | -31.00 [-39.29, -22.77] | +7.50 / +7.50 |
| local-q4 | plain-option-text − plain-letter | -35.25 [-42.89, -27.75] | -29.25 [-39.60, -18.88] | -28.50 [-36.78, -20.30] | +6.00 / +6.75 |
| local-q4 | plain-option-text − chat-letter | -35.75 [-44.06, -27.70] | -29.25 [-39.36, -19.19] | -29.50 [-37.87, -21.12] | +6.50 / +6.25 |

## Position counts and answer churn

Each histogram contains 400 displayed A/B/C/D selections per cell. Gold counts are exactly 100/100/100/100. Option-text labels below identify the displayed position of the chosen text. Full per-rotation histograms are in `statistics.cells`; zero counts are retained in the report.

| Variant | Language | BF16 raw A/B/C/D | Q4 raw A/B/C/D |
| --- | --- | --- | --- |
| plain-letter | English | 141/89/90/80 | 147/87/85/81 |
| plain-letter | Bangla | 194/70/72/64 | 180/77/71/72 |
| plain-letter | Hindi | 169/69/83/79 | 185/65/75/75 |
| chat-letter | English | 123/97/93/87 | 139/97/86/78 |
| chat-letter | Bangla | 138/69/93/100 | 131/71/90/108 |
| chat-letter | Hindi | 153/88/72/87 | 164/98/58/80 |
| plain-option-text | English | 190/83/69/58 | 202/75/70/53 |
| plain-option-text | Bangla | 201/68/72/59 | 216/63/63/58 |
| plain-option-text | Hindi | 207/71/67/55 | 218/65/68/49 |

| Normalized option-text language | BF16 A/B/C/D | Q4 A/B/C/D |
| --- | --- | --- |
| English | 162/90/78/70 | 179/84/84/53 |
| Bangla | 165/83/75/77 | 168/81/77/74 |
| Hindi | 178/78/76/68 | 189/73/78/60 |

BF16→Q4 flips below count changed rotation contexts. R/I/W denotes regressions, improvements and wrong-to-wrong changes. Net accuracy can conceal substantial churn. Normalized letter flips equal raw letter flips.

| Variant | Language | Raw changed /400 | Raw R/I/W | Raw changed r0 /100 | Normalized changed /400 | Normalized R/I/W |
| --- | --- | --- | --- | --- | --- | --- |
| plain-letter | English | 26 | 10/7/9 | 7 | 26 | 10/7/9 |
| plain-letter | Bangla | 44 | 16/15/13 | 11 | 44 | 16/15/13 |
| plain-letter | Hindi | 42 | 20/11/11 | 12 | 42 | 20/11/11 |
| chat-letter | English | 30 | 18/4/8 | 13 | 30 | 18/4/8 |
| chat-letter | Bangla | 47 | 20/8/19 | 10 | 47 | 20/8/19 |
| chat-letter | Hindi | 45 | 16/10/19 | 11 | 45 | 16/10/19 |
| plain-option-text | English | 45 | 21/14/10 | 12 | 44 | 19/16/9 |
| plain-option-text | Bangla | 59 | 26/14/19 | 14 | 43 | 15/10/18 |
| plain-option-text | Hindi | 56 | 23/17/16 | 11 | 49 | 15/15/19 |

There are no exact duplicate-choice flags among the 300 language-specific questions. This exact-string check does not rule out synonymous choices or translation ambiguity; official keys and scores remain unchanged. `statistics.variant_flips` preserves all three paired variant comparisons for both arms, languages and scoring modes, including regression/improvement/wrong-to-wrong and per-rotation counts.

## Deterministic changed examples

For each language, arm and variant pair, the first changed raw prediction in lexicographic `(source, question-as-string, rotation)` order is selected. This fixed selection rule illustrates churn without selecting examples by correctness. Indices below are **one-based original content indices**, followed by the winning raw continuation log probability in nats; gold is the official original index. Absolute continuation sums across different formats are not calibrated measures of answer quality. Full four-candidate scores and prompt/choice text remain in the corresponding archived shard. These examples are not an error taxonomy.

| Arm | Language | Right − left | Source / question / rotation | Left content (score) | Right content (score) | Gold |
| --- | --- | --- | --- | --- | --- | --- |
| bf16-gguf | English | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r1 | 2 (-0.394827) | 3 (-6.179731) | 3 |
| bf16-gguf | English | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.243881) | 1 (-10.919769) | 3 |
| bf16-gguf | English | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-4.884947) | 1 (-10.919769) | 3 |
| bf16-gguf | Bangla | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles](https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles) / q2 / r0 | 1 (-0.627433) | 4 (-13.342005) | 2 |
| bf16-gguf | Bangla | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Coaching_Youth_Middle_Distance_Runners/Training](https://en.wikibooks.org/wiki/Coaching_Youth_Middle_Distance_Runners/Training) / q1 / r0 | 3 (-0.316773) | 1 (-11.130193) | 1 |
| bf16-gguf | Bangla | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles](https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles) / q2 / r0 | 4 (-13.342005) | 1 (-8.990781) | 2 |
| bf16-gguf | Hindi | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.426474) | 1 (-9.389676) | 3 |
| bf16-gguf | Hindi | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.426474) | 1 (-8.146729) | 3 |
| bf16-gguf | Hindi | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r1 | 3 (-9.907346) | 2 (-4.869803) | 3 |
| local-q4 | English | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r1 | 2 (-0.154685) | 3 (-8.024472) | 3 |
| local-q4 | English | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.336796) | 1 (-9.274685) | 3 |
| local-q4 | English | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-6.396721) | 1 (-9.274685) | 3 |
| local-q4 | Bangla | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 1 (-0.294111) | 4 (-12.080777) | 3 |
| local-q4 | Bangla | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles](https://en.wikibooks.org/wiki/Castles_of_England/Tudor_Castles) / q2 / r1 | 2 (-0.792761) | 4 (-7.619915) | 2 |
| local-q4 | Bangla | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 4 (-12.080777) | 1 (-6.323573) | 3 |
| local-q4 | Hindi | chat-letter − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.701611) | 1 (-8.971146) | 3 |
| local-q4 | Hindi | plain-option-text − plain-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r0 | 3 (-0.701611) | 1 (-7.502918) | 3 |
| local-q4 | Hindi | plain-option-text − chat-letter | [https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods](https://en.wikibooks.org/wiki/Blended_Learning_in_K-12/Synchronous_and_asynchronous_communication_methods) / q2 / r1 | 3 (-8.928752) | 2 (-4.412109) | 3 |

## Interpretation and canonical-contract gate

Chat-letter raises BF16 rotation-mean accuracy by 3.25 pp in English, 2.75 pp in Bangla and 0.25 pp in Hindi; local-Q4 changes are +0.50, 0.00 and +1.00 pp. The paired intervals above expose the uncertainty rather than treating these point gains as general improvements. Q4 Bangla all-four consistency falls from 44% to 39%, and Hindi from 46% to 41%; BF16 Hindi consistency also falls from 52% to 48%. Chat’s lower A frequency therefore does not establish a uniformly better contract.

Raw option-text accuracy is markedly below both letter formats in English, Bangla and Hindi in both precisions. Character normalization lowers its accuracy further, despite some higher consistency. These observations support retaining summed letter scoring rather than adopting either option-text endpoint for this benchmark.

**Recommendation pending user decision:** retain the plain-letter summed-likelihood contract and use fresh cold-runtime baseline identities for subsequent compression work; retain chat-letter and normalized option-text as named diagnostics. English’s raw plain-letter Q4−BF16 estimate is −0.75 pp, Bangla’s −0.25 pp and Hindi’s −2.25 pp, with the paired uncertainty shown above. This recommendation balances accuracy, stability and continuity; it is not a claim that plain-letter removes position sensitivity. The user must explicitly freeze the canonical contract before B5. If settings change, rerun affected baselines with new identities; do not relabel old scores.

The 100-question-per-language A3 diagnostic does not replace the 300-question A1 reference. Decide which affected baseline comparisons need fresh collection under the ratified runtime/scoring identity before the sweep; the old runtime's scores cannot be presented as new cold-runtime baselines.

## Runtime limits, evidence and reproduction

The unchanged upstream ConfigurableTask / LocalCompletionsAPI path passed both-arm direct-logit probability checks (192 candidates per arm) and reversed-order checks (36 per arm) in isolated v4 cold-prefill runtimes. The former prefix-reuse runtime failed cold comparisons. Its legacy A2 bridge exceeded the original 0.001-nat bound for 42/60 BF16 and 55/60 Q4 selected candidates, although no selected winner changed. This is not universal parity; possible request-history effects on old A2 results remain unquantified. Historical A1/A2 outputs and runtime identities are preserved.

The Python servers used effective EOS 6 whereas an older conversion manifest required 3. These likelihood candidates append no EOS; this report does not ratify generation EOS settings or claim generation quality, speed, memory or phone performance. See [execution protocol](../../docs/scoring-variant-execution.md) and [frozen variant specification](../../docs/scoring-variant-control.md).

The lossless [archive manifest](evidence/archive-manifest.json) indexes two arm archives with 720 original shards plus identity per arm, and the [compressed validated report](evidence/validated-report.json.gz). Every source-file hash matched the complete report before packaging. The manifest records compressed archive hashes and original member hashes/byte lengths, lock location/hash and evaluation/runtime reproduction commits; the immutable token lock and model weights are referenced rather than duplicated. Original WSL evidence remains under `/home/shohag/tiny-aya-stage1/pilot/scoring-control/full-v4`. Validation source/protocol/runtime references are retained in the report and linked runtime evidence; raw predecessors remain separate.

An independent review recomputed all 18 cells and flip decompositions from the raw shards, then independently reproduced 36 raw/normalized compression and English-relative 95% intervals, agreeing with the report within 1e−12. This checks the raw evidence and bootstrap arithmetic separately from merely rerunning the reporting helper. The full isolated test suite passed 52 tests plus 21 subtests; archive verification checked 1,443 original byte identities.

Original report SHA-256: `4b97bf7394fba8a5af4aac74be0667d43c4e24f7e304d47c97f2429b82311495` (1,865,298 bytes). Request lock SHA-256: `75486c22c0c25f7c6c9d3da6abfaaa0165babf4a5de24970147ab9d1488d9844`.

Verify committed evidence without extracting members: `python -m scripts.archive_scoring_variants verify results/a3-scoring-variants/evidence`. Recompute the scientific report in the byte-pinned environment with `python -m scripts.summarize_scoring_variants` and its explicit original arm, lock, runtime, client/direct/order gate, validator-script and protocol paths. Its loader refuses incomplete or mismatched runs and writes only a new output. Compressed JSON preserves original bytes; it is not a reserialized replacement.

The [execution record](execution-record.json) preserves the exact `report_command` and `report_working_directory`, frozen hashes, process history and successful final verification. Its machine paths and operational state are historical records; both scoring servers were stopped at completion. Use those recorded inputs to reproduce the report in the preserved environment.

In the decompressed JSON, tuple-keyed maps are lists of `{key, value}` records: `statistics.cells` keys are `[arm, variant, language]`; `statistics.contrasts` keys identify compression, compression−English or ordered variant differences. `statistics.arm_flips`, `statistics.variant_flips`, predictions, exact duplicate flags, cell intervals and all per-rotation outputs remain inspectable. The tables here are deterministic rounded projections of that report.
