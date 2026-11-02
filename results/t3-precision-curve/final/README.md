# Complete T3 curve and operating-point decision

The [validated final report](complete-report.json.gz) covers every required precision stage: five new 900-question task arms, reused T1 BF16/Q4 task references and six full candidate KL endpoints. Each fidelity endpoint has 900 questions and 176,756 content-token distributions. Raw archives, hashes, runtime identities and uncertainty are linked from the point directories. Final selection ran only after the last complete-stage report was committed at `29206b0`.

| Candidate | Actual GGUF bytes | English correct | Bangla correct | Hindi correct | Meets English floor and byte ceiling |
| --- | ---: | ---: | ---: | ---: | --- |
| BF16 control | 6,710,484,480 | 230/300 | 187/300 | 184/300 | Reference only |
| Q6_K diagnostic | 2,759,532,032 | 233/300 | 188/300 | 185/300 | No: bytes |
| Existing local Q4_K_M | 2,143,976,960 | 229/300 | 190/300 | 180/300 | Yes |
| Q3_K_M | 1,799,740,928 | 221/300 | 186/300 | 173/300 | **Yes: minimum bytes** |
| IQ3_S, no imatrix | 1,665,998,336 | 188/300 | 160/300 | 138/300 | No: English |
| Q3_K_S | 1,660,984,832 | 210/300 | 179/300 | 178/300 | No: English |
| Q2_K | 1,481,973,248 | 180/300 | 149/300 | 142/300 | No: English |

The frozen English-only rule selects **Q3_K_M, 1,799,740,928 bytes, English 221/300**. This meets the observed development floor exactly and remains under the 2.2 GB shipped ceiling. It does not prove English noninferiority. Its paired English change is -3.00 pp [-6.73, +0.66]; Bangla is -0.33 pp [-4.48, +3.96] and Hindi -3.67 pp [-7.87, +0.66]. English-relative intervals are in the complete report and [Q3 checkpoint](../diag-q3km/README.md).

Q2 triggered the descent stop. IQ3 remained required because its actual bytes exceed both Stage 2 files; no later smaller format or IQ2 was added. All imatrix-free IQ3 claims are conditional on that export, not calibrated IQ3 methods generally. The original canonical BF16 vLLM reference is separate from BF16 GGUF.

## Fidelity and uncertainty

Mean question-level KL(BF16 || candidate), in nats per content token:

| Candidate | English | Bangla | Hindi |
| --- | ---: | ---: | ---: |
| Q6_K | 0.004857 | 0.005127 | 0.003965 |
| Existing local Q4_K_M | 0.035018 | 0.038329 | 0.030844 |
| Q3_K_M | 0.102541 | 0.124599 | 0.095921 |
| Q3_K_S | 0.185407 | 0.207971 | 0.168973 |
| IQ3_S | 0.276336 | 0.305826 | 0.255459 |
| Q2_K | 0.441425 | 0.580459 | 0.450495 |

These are descriptive fidelity values, not language-effect tests or task-benefit guarantees. All nontrivial English-relative task-difference intervals include zero across the new arms. This curve does not establish unusually large Bangla damage, and it does not establish language equivalence. Source-cluster uncertainty uses 250 groups, 10,000 draws and seed 42. Calibration-sample variation is a separate question for C8.

All recorded P1–P4 descriptive directions hold at their applicable completed points. This is not a multiplicity-adjusted confirmatory result. Per-point reports retain full paired intervals, churn decompositions and margin bins. C8 remains necessary to test whether language information changes a feasible precision choice reproducibly.

The readable actual Q6 tensor inventory was attached after task scoring, with the pinned model hash/bytes and earlier native prediction unchanged; that timing deviation remains disclosed. Later actual inventories preceded inference. All task and KL gates, question hashes, token/source coverage, numerical receipts and report aggregates passed validation. No raw weights or vocabulary-logit arrays are in Git. No A4-conditioned analysis, human generation judgment, final holdout outcome or phone-performance claim belongs to this development curve.
