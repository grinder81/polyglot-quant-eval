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

## 2026-11-01 — Bounded pilot execution authorized

- The user instructed Codex to create the execution plan and issues, reconcile related work and complete the Astra-reviewed pilot. Tracker #47, protocol #48, resource task tiny-aya-edge#42 and decision report #49 reuse the existing B5/C8-C11 execution issues. The audit found no fully completed remaining scope among open legacy issues, so none was closed.
- Reconciled the T3 specification with that authorization: adopted the proposed operational defaults, retained all technical gates and protected analyses, separated the primary BN-versus-EN contrast from the practical comparator, clarified discrete byte matching and preserved both language-informed finalists for later holdout confirmation. An independent Astra review approved the umbrella plan subject to the concrete pre-outcome freezes.
- Existing-model G1 profiling is distinct from T3 collection: the verified T1 development lock has 176,756 non-BOS prompt tokens, projecting 185,342,099,456 raw float32 reference-logit bytes. Native byte dry runs and three-prompt KL profiling are reported under tiny-aya-edge#42. No new T3 artifact or task result is claimed by this entry. The T3 freeze blob identity follows exact-commit review and merge.

## 2026-11-01 — T3 specification frozen before new builds

- PR46 merged as `2bfea18c282cf2667fa24c8c05a888ce8e50a838` after both GitHub CI checks passed and Astra approved exact head `d3ce91ba0b9f34bb4356f22de88eaf2c9ad89f97` without blockers. Frozen `docs/t3-preregistration.md` Git blob: `700a0f601e6503d95b485ad5d048c20b4ef96910`. Git blob identity refers to repository content, not a platform-dependent checkout newline hash.
- The freeze precedes Q6_K/Q3_K_M quantization. It does not claim any new T3 build, numerical gate or task result. Per-build readiness review and the separate C8 pilot freeze remain required; holdout outcomes and A4 slices remain sealed.

## 2026-11-01 — First T3 arm readiness and throughput checkpoint

- Q6_K and Q3_K_M builds completed from the pinned BF16 source; manifests and actual bytes are committed in runtime PR43. Q6_K is2,759,532,032bytes; Q3_K_M is1,799,740,928bytes. Both vocabulary-only checks passed900contexts and3,600candidates. These are build/readiness facts, not precision-curve results.
- Q6_K passed the48candidate direct,48client and48reversed-order numerical gates. The new runner's offline identity/raw-gate verification exited0. Astra reviewed the collection code and found one arm-label provenance blocker; commit ef2582e fixes it with an arm/format map and rejection test. All3 runner tests and both GitHub CI checks passed before collection.
- The first20five-question shards completed and validated. The raw completion log records throughput and the remaining160shards continue under the same frozen identity. No partial accuracy or language claim is reported; the complete arm and stage report remain pending.

## 2026-11-01 — Q6 accuracy checkpoint and C8 design freeze

- Q6_K completed all 900 original-order development questions and passed separate complete validation. Correct counts are English 233, Bangla 188 and Hindi 185 out of 300; BF16 counts are 230,187,184. All paired accuracy-difference and nontrivial English-relative intervals include zero. [Complete checkpoint and 197-member verified archive](results/t3-precision-curve/diag-q6k/README.md). The owned server was stopped; the BF16 reference-logit cache is now collecting. Stage 1 and the full fidelity endpoint remain incomplete.
- Astra approved the bounded C8 design at exact content commit6e72eb3. Frozen design Git blob after its status-only update: `cd43458f25672a0522958a4d1de0e1a88c307dc7`. The mechanically derived format pair and exact-byte eligibility record still follow the full T3 curve, before C8 comparative outcomes. This is an investment screen, not an allocation-success claim. No C8 rankings, A4 slices or holdout outcomes were collected.

## 2026-11-01 — Fidelity validation and inventory timing

- Full KL reporting now verifies all 900 per-question hashes, source/prompt/token coverage, token means and language aggregates, and requires the verified native-before-Torch execution receipt. Rejection tests cover changed question evidence, aggregate manipulation and absent execution receipts. No scoring or fidelity collection implementation changed.
- The first two T3 build records lacked attached actual-file tensor inventories, although the actual model hashes, bytes and native dry-run layouts were pinned. Runtime PR43 now includes supplements that match every predicted type, shape and payload size. The Q6 supplement follows task scoring; the Q3 supplement precedes inference. Original manifests and Q6 run identities remain intact. Remaining builds attach actual inventories before inference.

## 2026-11-01 — Q6 full fidelity complete

- The fresh native-before-Torch run completed 900 questions and 176,756 content-token KL distributions in 1,235.02 seconds. English/Bangla/Hindi mean question KL is 0.004857/0.005127/0.003965 nats per content token. All question hashes, source/prompt/token identities, token means, aggregates and numerical execution receipts passed reporting validation. These are descriptive fidelity endpoints; no language-effect or allocation-success conclusion follows.
- Published the [combined Q6 checkpoint and 903-member KL archive](results/t3-precision-curve/diag-q6k/README.md), excluding raw logits and the preserved interrupted run. Q3 direct validation has started. T3 Stage 1 remains incomplete, and no operating point or C8 outcome is selected. The user's weekly-allowance stop threshold is recorded in the execution plan.

## 2026-11-01 — Readiness issues reconciled

- Closed the newly scoped protocol #48 and runtime resource task tiny-aya-edge#42 with completion receipts and evidence links. The master #47 and every unfinished legacy scope remain open. Clarified the master's goal as a bounded investment decision rather than a claim of established allocation task benefit.
- Q3 passed its direct, API-client, reversed-order and offline identity gates. Its first 100 task questions completed and validated in 242.34 seconds. Collection continues in complete batches under the unchanged identity. The [resume guide](docs/article2-pilot-resume.md) records artifact locations, protected analyses and the account-allowance stop procedure.

## 2026-11-01 — Q3_K_M task checkpoint complete

- All 900 Q3 task questions and separate complete validation passed. Correct counts are EN 221, BN 186 and HI 173, versus BF16 230/187/184. Paired changes are -3.00/-0.33/-3.67 pp; all paired accuracy and nontrivial English-relative intervals include zero. The [complete report and verified 197-member archive](results/t3-precision-curve/diag-q3km/README.md) preserve the raw evidence and identities.
- Q3 meets the English development floor exactly but does not trigger the descent stop. The later stages remain required; no operating point is selected. Collection batches total 2,965.70 seconds, 49.4 minutes, before process/identity startup overhead. These are evaluation costs, not a device throughput result. The owned server stopped and Q3 full KL collection began through the unchanged verified wrapper. Weekly allowance was 13% at the latest check; the user stop guard remains active.

## 2026-11-01 — Q3 full fidelity complete

- Q3 completed and validated all 900 KL questions and 176,756 content-token distributions. English/Bangla/Hindi mean question KL is 0.102541/0.124599/0.095921 nats per content token. The combined report verifies every question's hash, source/prompt/token identity, KL mean, language aggregate and verified execution receipt. These are descriptive fidelity endpoints, not task-benefit or causal language-effect evidence.
- Published the [combined Q3 checkpoint and 903-member fidelity archive](results/t3-precision-curve/diag-q3km/README.md). Thirty complete-question batches total 1,732.25 seconds, 28.9 minutes, of core intervals excluding process/verification/import startup. Existing Q4 full KL has begun; Stage 1 remains incomplete until that endpoint is validated and its report committed. Weekly allowance was 11% at the latest check; the below-10% stop guard remains active.

## 2026-11-01 — Account stop threshold revised by the user

- The user explicitly authorized continued execution and replaced the earlier 10% threshold with a stop **below 2% weekly allowance remaining**. The execution plan and resume record now carry that rule. No scientific endpoint, sample, runtime or decision rule changed. Q4 KL collection continues under its existing identity, with complete-question checkpoints and no allowance-reset action.

## 2026-11-01 — T3 Stage 1 complete

- Q4 full KL completed and validated all 900 questions and 176,756 content-token distributions. EN/BN/HI mean question KL is 0.035018/0.038329/0.030844 nats per content token. Published its verified 903-member archive and the [combined complete Stage 1 report](results/t3-precision-curve/stage1/README.md), including Q6/Q3 full task/fidelity and the reused T1 BF16/Q4 task identities.
- Q3's English 221/300 meets the development floor exactly; neither new arm triggers the 185/300 descent stop. Stages 2 and 3 remain required; no operating point or C8 result is selected. Q4 core intervals total 2,048.05 seconds, 34.1 minutes, excluding inter-process startup. Native collection ended and no owned GPU scoring/fidelity process remains. The report is committed before the next stage's builds; Q6's disclosed inventory-attachment timing deviation remains in its interpretation.

## 2026-11-01 — Stage 2 builds and first-arm readiness

- After Stage 1 report commit `2cf0371`, Q3_K_S and Q2_K were built and passed vocabulary checks. Both actual inventories match all 290 prior predicted tensor types/payloads and exact file bytes: 1,660,984,832 and 1,481,973,248. Runtime commit `d737c68` records actual inventories, model hashes, runtime bindings, vocabulary receipts and the preceding-report prerequisite before either model's inference.
- Q3_K_S subsequently passed direct, client, reversed-order and offline identity gates and began complete-shard task collection. Both repositories' CI checks pass. Q2_K task inference, the full Stage 2 report, Stage 3, operating-point selection and C8 remain pending. The user's revised account stop threshold remains below 2% weekly allowance remaining.

## 2026-11-01 — Q3_K_S task checkpoint complete

- All 900 questions and separate complete-arm validation passed. Correct counts are EN 210, BN 179 and HI 178, versus BF16 230/187/184. Paired changes are -6.67/-2.67/-2.00 pp. English's paired 95% interval [-10.74, -2.67] is below zero; non-English and English-relative intervals include zero. The [complete task report and verified 197-member archive](results/t3-precision-curve/diag-q3ks/README.md) retain the evidence.
- English fails the frozen 221/300 selection floor but remains above the 185/300 descent stop. The full required curve continues, with no operating point selected. Full Q3_K_S KL is running; Q2_K follows under its committed identity. No C8 comparative outcome, A4 slice or holdout outcome has been collected.

## 2026-11-01 — Q3_K_S fidelity complete

- Completed and validated all 900 KL questions and 176,756 content-token distributions. EN/BN/HI mean question KL is 0.185407/0.207971/0.168973 nats per content token. The [combined checkpoint and verified 903-member archive](results/t3-precision-curve/diag-q3ks/README.md) preserve all identities, question-level summaries and numerical receipts. These are descriptive fidelity values, not causal language or task-benefit findings.
- Q2_K direct validation began after the Q3_K_S worker finished. Stage 2 and the complete curve remain pending; no operating point is selected. The latest account meter reports 100% weekly allowance remaining; Codex performed no reset action, and the user's below-2% stop threshold remains active.

## 2026-11-01 — Q2_K task checkpoint and descent stop

- All 900 task questions and separate complete validation passed. Correct counts are EN 180, BN 149 and HI 142 versus BF16 230/187/184; paired changes are -16.67/-12.67/-14.00 pp, with all three paired intervals below zero. English-relative BN/HI intervals include zero. The [complete report and verified 197-member archive](results/t3-precision-curve/diag-q2k/README.md) retain raw evidence and identities.
- English triggers the 185-or-fewer descent stop, prohibiting later smaller artifacts. IQ3_S remains required because its frozen native size prediction is larger than both Stage 2 files; this is the preregistered size-aware rule, not a new exception. Full Q2_K KL is collecting before the complete Stage 2 report. No operating point, C8 comparison, A4 slice or holdout outcome is selected or collected.
