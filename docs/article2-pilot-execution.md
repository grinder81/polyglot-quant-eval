# Tiny Aya language informed compression pilot

1 November 2026. Execution owner: Codex, following the user's authorization to complete the pilot after Astra's review. Master issue: [47](https://github.com/grinder81/polyglot-quant-eval/issues/47).

The goal is to decide whether language-informed precision allocation deserves a full Article 2 experiment. The pilot must establish an actionable deployment budget, reproducible differences between language-informed choices, feasible controls and an honest account of endpoint precision. It does not assume that Q4 damages Bangla: fresh BF16/Q4 correctness is 187/190 out of 300.

## Work and dependencies

| Order | Owner | Deliverable and completion evidence |
| --- | --- | --- |
| G0 | [eval 48](https://github.com/grinder81/polyglot-quant-eval/issues/48) | Versioned protocol and statistical amendments; source-pool audit; fixed construction budgets and decision rules before their outcomes are collected. |
| G1 | [edge 42](https://github.com/grinder81/tiny-aya-edge/issues/42) | Native export size feasibility, tied-weight accounting, immutable environment/artifact identities and a measured bounded KL/Fisher profile. CPU inventory and export dry runs can precede outcome collection. |
| G2 | Existing [edge 24](https://github.com/grinder81/tiny-aya-edge/issues/24) | Build Q6_K and Q3_K_M, validate exact tokens and cold/direct/client/reversed-order likelihoods, then score the fixed development requests. Reuse fresh BF16/Q4. Further precision stages follow the recorded descent rule; commit each stage report before the next. |
| G3 | Existing [edge 25](https://github.com/grinder81/tiny-aya-edge/issues/25) | A small, stratified native-quantizer intervention pilot. Compare measured output KL, a precisely specified per-example Fisher score and an activation proxy across BN/EN/pooled evidence with repeated construction/probe samples. Freeze exact membership, tensors, formats, estimator, resource cap and stability thresholds after G1 feasibility and before G3 collection. |
| G4 | [eval 49](https://github.com/grinder81/polyglot-quant-eval/issues/49) | Reproducible go, no-go or inconclusive report using actual bytes, endpoint precision, runtime cost and between-language versus within-language construction variation. |

Full map validation [edge 26](https://github.com/grinder81/tiny-aya-edge/issues/26), allocation [edge 27](https://github.com/grinder81/tiny-aya-edge/issues/27) and independent calibration and precision repair evaluation [edge 28](https://github.com/grinder81/tiny-aya-edge/issues/28) remain open. They are conditional follow-on work, not prerequisites for declaring this bounded pilot informative. The generation issue [eval 21](https://github.com/grinder81/polyglot-quant-eval/issues/21) remains open for its own frozen protocol and genuine human review.

## Protocol decisions

The 1 November authorization resumes implementation and pilot execution; it supersedes historical documentation statements that a planning update alone authorizes no execution. It does not remove technical readiness checks. PR [46](https://github.com/grinder81/polyglot-quant-eval/pull/46) supplies T3's model, quantizer, request lock, accepted scoring contract, stage order and numerical gate specifications. Amendments and their exact commit identities must precede the affected collection.

Use the proposed defaults of an English floor at 221/300, a descent stop at 185/300, no uncalibrated IQ2 point, IQ3_S as the third-stage point and no optional densification. These implement the accepted reviewed plan. The English floor selects a development operating point; it does not prove noninferiority. The 2.2 GB total shipped ceiling remains fixed. At this goal's end, any continued full study needs its own frozen protocol; neither pilot significance nor an attractive heatmap alone is sufficient.

The primary scientific contrast is BN-informed minus EN-informed allocation on Bangla correctness. The practical secondary comparison uses a comparator selected on development and frozen before the eventual holdout. Report English retention and English-relative deltas beside non-English changes. An estimate of at least 3 pp with a lower paired 95% interval above zero supports a positive effect with an observed magnitude of at least 3 pp; it does not establish a true effect of at least 3 pp. A smaller positive effect can be below the practical threshold. Cluster bootstrap task uncertainty and calibration-resample uncertainty answer different questions and must both remain visible.

The primary language arms must use the same construction procedure and total evidence budget. Pooled multilingual evidence divides that budget, rather than receiving extra data. Distinguish matched content from independently sampled content and expose domain/length differences. Actual source membership is frozen before probes. Calibration, fitting, development and final test pools remain source-disjoint.

Native default and uniform exports are not promised to match exactly. Enumerate feasible bytes first, then freeze a narrow tolerance for the primary language arms. If an untouched uniform/default export cannot meet it, label it as a separate lower-budget reference or implement a clearly defined comparator; padding is not a scientific matching method. Count the embedded tokenizer and unique stored embedding/output once. Runtime duplication is a separate memory quantity.

For future confirmation, retain both language-informed finalists and the frozen practical comparator, regardless of development ranking. The reserved 424 questions per language belong to 238 source clusters, not 424 independent sources. Their outcomes remain untouched during this pilot. The 300-question development set has 250 source clusters; fresh Bangla correctness discordance is 23, whereas all-answer churn is 33. Precision planning must use the former for paired accuracy scenarios.

## Resource and evidence rules

The user's latest instruction replaces the earlier 10% account-usage stop threshold with **below 2% remaining**: monitor weekly allowance and, if it drops below 2%, preserve a resumable checkpoint, launch no new operations and pause this goal. This is separate from the scientific/resource stop rules. Collection is divided into complete shard/question batches without changing the frozen scoring or KL implementations. The account meter is shared across chats; no allowance reset is authorized.

Use one GPU owner and inspect current processes before each launch. Preserve historical artifacts, failed evidence and immutable run identities. A competing process is not permission to terminate unrelated work. Build provenance includes the existing pinned native quantizer, exact command, binary/source hashes, output SHA256, measured bytes and tensor inventory. Weights and credentials never enter Git.

KL is KL(BF16 || candidate), descriptive beside task results. The profile must establish a bounded chunk/cache strategy and validate it against a full-array oracle. At vocabulary size 262144, float32 logits occupy 1 MiB per token; full-dataset caching needs an explicit disk budget. Distinguish raw logits, normalized log probabilities and numerical precision. Fisher means an average of squared per-example gradients under a specified objective and normalization, not the square of an averaged gradient. A resource failure is recorded rather than silently changing the estimator.

Every collection stage has a frozen specification and readiness receipt. Checks, profiles and result reports name their exact implementation commits. Code changes require relevant tests and passing CI. Keep article approval separate from research execution.

## Decision at the end

Proceed with full allocation only if language-informed choices are stable beyond within-language sample variation, change feasible precision decisions at the target budget, and can be evaluated with meaningful task and generation evidence. Report weak or mixed evidence as inconclusive. An absent statistically significant difference does not establish equivalence.

If allocation is unpromising or infeasible, nominate function-preserving MLP channel rebalancing as the next separate experiment. Verify unquantized equivalence before quantizing, use identity/BN/EN/pooled transformations with the same tensor types, and count actual shipped bytes. Do not combine rebalancing, learned repair, pruning and attention replacement into this allocation study. Their machinery has prior art; the cross-language controlled result is the prospective contribution.

## Issue audit

The 1 November audit inspected all issue and PR entries returned for both repositories, including every open issue. No open legacy issue had evidence that its entire remaining scope was completed. No issue is closed on the basis of Article 1, a documentation PR or the creation of this plan. Completed A1/A2/A3/B7 issues remain closed. A4 labels, B6 human generation review, C8-C11, phone measurement, broader Stage 1 checkpoint, Mac/kernel work, registry audit, literature follow-ups and upstream submissions remain open.

The new tracker links the existing execution owners instead of duplicating B5 or C8-C11. Date-stamped reconciliation notes identify the current pilot order on relevant issues. Historical measurements and original checklists remain available; no unrelated unfinished issue is edited or closed.
