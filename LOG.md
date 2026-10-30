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

## 2026-10-22 — A3 canonical-contract decision
- The user selected “Retain plain-letter summed likelihood on fresh cold-runtime baselines.” Recorded the exact selected format, token boundaries, prediction/tie rules, normalization/rotation interpretation and validated v4 runtime pins in [the contract decision](docs/scoring-contract-a3.md). A3's diagnostic and contract-decision gate are complete; observed results and historical A1/A2 identities are unchanged.
- Fresh affected BF16 GGUF and local-Q4 comparator arms with new cold-runtime identities are required before downstream compression comparisons. The existing A3 100-question-per-language diagnostics are not full 300-question baseline reruns. This does not replace the canonical BF16 vLLM reference. A4 human labels and B5's other prerequisites remain outstanding gates; no new inference, sweep or holdout scoring occurred in recording this decision.

## 2026-10-23 — Fresh T1 cold-runtime comparators complete
- Completed 180 validated five-question shards per arm: 900 original-order development questions and 3,600 candidate scores each, BF16 GGUF and local Q4_K_M. Frozen report exited 0; runners exited 0 and owned servers stopped. Historical A1/A2/A3 and the original BF16 vLLM reference retain their own identities.
- BF16/Q4 correct out of 300: English 230/229, Bangla 187/190, Hindi 184/180. Q4−BF16 deltas −0.33/+1.00/−1.33 pp; all paired-source accuracy-difference and English-relative interaction intervals include zero, without establishing equivalence or no harm. Churn is 21/33/34 questions: Bangla 11% versus English 7%, not doubled.
- Historical→fresh changes are BF16 0/1/0 and Q4 7/12/10 predictions (English/Bangla/Hindi). Combined runtime differences are descriptive, not isolated patch effects. Fresh margin-bin associations remain exploratory.
- [Complete T1 results](results/t1-cold-baselines/README.md) include absolute/paired intervals, transition decompositions, histograms, historical score/margin distributions, a static interval figure and source links. Report SHA-256 c1ffee6b6030b1d5beb6c6afe3d855c1e1703df3e2fd6329270b06d55a1941a1; archive verification checked 379 original evidence files. Independent review reconstructed all 1,800 rows and recomputed fresh source-bootstrap endpoints. A4 human labels, sweep prerequisites and publication review remain; no holdout or generation measurement.

## 2026-10-29 — Article 2 setup decisions recorded; T3 preregistration drafted
- The user ratified eight Article 2 setup decisions on 26 October 2026: T3 may run before A4 labels with negation slices sealed; the allocation operating point is chosen by an English-only retention rule after the curve; the 2.2 GB ceiling stands with the point allowed below it; Belebele is the primary allocation endpoint and B6 generation the secondary; a 3 pp meaningful margin with positive/null/inconclusive criteria; Tiny Aya Fire deferred; adaptation secondary with Language-Conditional Dequantization cited; T3 points Q6_K, Q3_K_M, Q3_K_S, Q2_K and IQ3_S in three stages. The sequencing change is recorded as a dated amendment in [the Stage 2 plan](docs/stage2-plan.md).
- [T3 preregistration](docs/t3-preregistration.md) committed as a **draft**: pins, builds and stages, per-build readiness gates, endpoints and statistics, four falsifiable predictions, the operating-point rule, sealed analyses and the items to confirm before freezing (English floor 3 pp, descent stop 15 pp, no imatrix-free IQ2 point at the pinned quantizer). It is not frozen; its freeze hash will be recorded here when the user approves it. No build, inference, generation or holdout access occurred.

## 2026-10-30 — Allocation design decisions adopted
- The user adopted: the narrowed Article 2 question and C10 arm set (Bangla-, English- and multilingual-informed allocations built by the same procedure, plus default, uniform and three seeded random, at equal measured bytes); a preregistered metric-comparison pilot before the C8 scan (measured degrade-one KL, per-weight diagonal Fisher, activation-weighted proxy, per language); C9 validation of equal-budget ranking separately from magnitude; and a descriptive per-language KL fidelity endpoint in T3. Prior art for the probe, cost-table, knapsack and GGUF-export machinery (including *Ranking Is Enough*, preprints.org 10.20944/preprints202610.1935.v1) is cited, not claimed. The T3 draft carries these in §6, §9 and §12; C8–C10 restate them in their own preregistrations. No build or inference occurred.
