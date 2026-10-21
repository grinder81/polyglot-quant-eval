# A2 option-rotation results

Completed 21 October 2026. Each arm scored the same 100 development questions per language in four cyclic option orders: 1,200 contexts and 4,800 candidate likelihoods per arm. These are 300 distinct questions, not 1,200 independent questions. All 480 shards, lock membership, targets, prompt hashes, finite candidate scores, runtime equivalence and evidence identities passed the unchanged summarizer validation.

## Raw results (canonical scoring unchanged)

| Language | BF16 average accuracy | Q4 average accuracy | Q4 minus BF16, pp (95% CI) | Difference in delta vs English, pp (95% CI) | BF16 / Q4 content consistency |
|---|---:|---:|---|---|---|
| eng_Latn | 76.75% | 76.25% | -0.50 [-2.78, 1.75] | 0.00 [0.00, 0.00] | 67.00% / 66.00% |
| ben_Beng | 60.00% | 60.50% | 0.50 [-2.23, 3.25] | 1.00 [-2.55, 4.57] | 43.00% / 47.00% |
| hin_Deva | 57.75% | 55.25% | -2.50 [-6.12, 0.75] | -2.00 [-6.12, 1.77] | 52.00% / 46.00% |

Accuracy averages the four rotations. Content consistency is the fraction selecting the same original answer content in all four positions; predictions are mapped back before comparison.

## Letter counts and cross-fitted diagnostic

| Arm | Language | Raw A/B/C/D (400 predictions) | Original-order accuracy | Cross-fitted average accuracy | Cross-fitted consistency |
|---|---|---|---:|---:|---:|
| bf16-gguf | eng_Latn | 141/89/90/80 | 77.00% | 79.25% | 73.00% |
| bf16-gguf | ben_Beng | 193/71/73/63 | 60.00% | 64.00% | 51.00% |
| bf16-gguf | hin_Deva | 168/69/83/80 | 59.00% | 62.25% | 51.00% |
| local-q4 | eng_Latn | 146/87/84/83 | 73.00% | 77.75% | 68.00% |
| local-q4 | ben_Beng | 173/78/75/74 | 61.00% | 59.00% | 50.00% |
| local-q4 | hin_Deva | 186/66/75/73 | 57.00% | 58.50% | 46.00% |

Gold letters total exactly 100 each per language across rotations. The excess A predictions and low content consistency establish option-position sensitivity under this plain-letter protocol in both precisions. This is not a quantization-only phenomenon.

The cross-fitted correction uses preregistered arm/language-specific centered letter offsets from other source folds, without labels. It remains a diagnostic, not a replacement benchmark. In Bangla it raises BF16 average accuracy from 60% to 64%, but lowers Q4 from 60.5% to 59%. Thus subtracting a letter prior is not a universally successful remedy, and these results do not support explaining all quantization churn as a simple shifted prior.

Raw mean accuracy deltas and their differences versus English include zero in their paired intervals. This does not establish equivalence. Hindi pairwise content agreement falls under Q4; full metrics and intervals are preserved in validated-report.json. These are development diagnostics with many endpoints; no multiplicity-adjusted confirmatory claim is made.

## Evidence and uncertainty

The JSON report includes per-rotation accuracy, original and cross-fitted predictions for all 300 items, paired flip tallies, letter counts, offsets, and metric intervals. The bootstrap resamples 96 source clusters jointly across languages and arms, with 10,000 replicates and seed 42; offsets are refitted within each replicate. Invalid empty-training-fold replicates: 0. Rotations and questions from a shared source are not treated as independent.

Raw arm folders, identity files, runtime manifests, preflights and rotation-lock.json are retained beside the report. Server logs remain in WSL at /home/shohag/tiny-aya-stage1/pilot/rotation-control. Model files are unchanged. The run used scoring checkout 5212caf; reporting code is identical at 157957f. Local-Q4 resumed after an interrupted session: 94 saved shards were revalidated, then remaining shards completed, without changing runtime or scoring.

Reproduce: `python -m scripts.summarize_rotations results/stage2/rotation-control --output NEW_REPORT.json`.

## Decision and pause

A2 is complete. Preserve canonical raw scoring. Option-position sensitivity must be considered before treating letter-scored misses as failures of fact binding. A3 remains the next instrument-control task, but no A3 run or subsequent work is authorized while the user-requested pause is active. No holdout was evaluated.
