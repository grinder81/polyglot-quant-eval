# LOG

## Matched Stage 2 BF16 reference
- Completed and validated 900 BF16 GGUF questions on the same runtime and frozen selection as local Q4. English 230/300, Bangla 188/300, Hindi 184/300; local Q4 226, 189 and 176 respectively. Paired deltas, uncertainty, answer churn and letter counts: results/stage2/bf16-three-hundred/README.md. No rotation or generation result is claimed yet.

## Belebele task/data audit
- Downloaded pinned English, Bangla and Hindi subsets and recorded 900 rows each, label checks, content hashes and installed task definitions in results/stage1/belebele-task-audit.json.
- Confirmed upstream candidates are A/B/C/D; canonical Stage 1 uses zero-shot acc without a chat template. No model scoring or sample lock yet.

Dated entries: what changed, the numbers, open problems.

## 2026-10-16
- Repository created: research question, design decisions, 14-language config, results schema,
  reference-runtime serve script, smoke test, normalize and report scripts (tested on synthetic output).
- Open: first BF16 Belebele run on the reference runtime; confirm upstream task names for
  `global_mmlu_*` and `mgsm_*`.

## 2026-10-16 (later)
- Aligned to the loop baseline, inspect, intervene, measure, explain. report.py now prints the gap
  vs English under every delta table; diagnostic and repaired formats have naming rules.

## 2026-10-17
- Added a reviewable Stage 1 protocol and proposed data-pool intentions; aligned harness
  documentation with adaptation as the broader goal and explicit runtime controls.
- No model runs, downloads or measurements performed. Artifact revisions and sample locks
  remain gates for later tasks. Existing smoke and report scripts need separate fixes.

## 2026-10-20
- Completed local Q4 only on 300 Belebele questions per language: English 226/300, Bangla 189/300, Hindi 176/300. Evidence and caveats: results/stage1/local-q4-three-hundred/README.md. All questions rerun under the join-control-corrected runtime; no other models or performance tests run.

## 2026-10-22 — A3 execution preparation
- Added a resumable driver around unchanged upstream ConfigurableTask, LocalCompletionsAPI and evaluator, plus complete-evidence reporting for all three locked variants, both arms and all rotations. Primary summed likelihood and character-normalized acc_norm remain separate; this entry is not a full variant accuracy result.
- The isolated cold-prefill runtime passed 192 independent candidate checks and 36 reversed-order checks per arm. Raw evidence and the failed/incomplete predecessor diagnostics are preserved in [runtime PR36](https://github.com/grinder81/tiny-aya-edge/pull/36). Legacy A2 numerical differences are explicitly reported; historical A1/A2 identities remain unchanged.
- The full diagnostic, canonical-contract choice and affected-baseline decisions remain distinct gates before B5. No holdout or generation-quality result is claimed.

## 2026-10-22 — A3 complete development diagnostic
- Completed both cold-runtime arms: 720 validated five-question shards, 3,600 contexts and 14,400 candidate scores per arm, covering the same 100 development questions per language, four rotations and three frozen scoring variants. The complete report jointly bootstraps 96 source clusters, 10,000 draws, seed 42; rotations are repeated observations of 300 distinct questions across both arms.
- Raw rotation-mean BF16 / Q4 accuracy (English, Bangla, Hindi): plain-letter 76.75/76.00%, 59.50/59.25%, 58.00/55.75%; chat-letter 80.00/76.50%, 62.25/59.25%, 58.25/56.75%; plain-option-text 54.00/52.25%, 40.00/37.00%, 41.25/39.75%. Character-normalized option-text: 41.50/40.75%, 31.25/30.00%, 27.25/27.25%. Letter normalization changes no prediction. All raw rotation-mean English-relative compression interaction intervals include zero. Chat-letter compression intervals exclude zero in English (−3.50 pp [−5.95, −1.25]) and Bangla (−3.00 pp [−5.93, −0.25]); remaining raw compression intervals include zero. Multiple development endpoints remain exploratory; nonsignificance does not establish equivalence.
- Full paired intervals, original-order accuracy, content consistency, six-pair agreement, histograms, flips, duplicate checks and deterministic changed examples: [A3 results](results/a3-scoring-variants/README.md). Every raw shard and identity is retained in lossless archives with original/compressed hashes; validated report SHA-256 `4b97bf7394fba8a5af4aac74be0667d43c4e24f7e304d47c97f2429b82311495`.
- Recommend retaining summed plain-letter scoring under fresh validated cold-runtime identities, pending the user's explicit canonical-contract decision before B5. Chat's Q4 Bangla accuracy is unchanged and its Bangla/Hindi all-four consistency falls; lower A frequency alone does not select a contract. Historical A1/A2 identities and the legacy numerical bridge/EOS limitations remain explicit. No holdout, generation, device-performance or final optimized-model claim is made.
- Independent raw-shard recomputation matched all 18 cells and flip decompositions; an independent bootstrap reproduced 36 raw/normalized compression and English-relative intervals within 1e−12. The isolated suite passed 52 tests plus 21 subtests; archive verification checked 1,443 original file byte identities.
