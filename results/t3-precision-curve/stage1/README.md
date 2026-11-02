# T3 Stage 1 complete report

1 November 2026. The [machine-readable report](complete-report.json.gz) combines complete Q6_K and Q3_K_M task arms with complete full-prompt KL for Q6, Q3 and existing local Q4. It validates all new task shards and each fidelity question's hash, source/prompt/token coverage, KL means, language aggregates and verified execution receipt. Existing BF16/Q4 task results retain their T1 identities. This completes the first precision stage, not the full curve or an allocation result.

| Artifact | Actual GGUF bytes | English correct | Bangla correct | Hindi correct |
| --- | ---: | ---: | ---: | ---: |
| BF16 GGUF control | 6,710,484,480 | 230/300 | 187/300 | 184/300 |
| Q6_K diagnostic | 2,759,532,032 | 233/300 | 188/300 | 185/300 |
| Existing local Q4_K_M | 2,143,976,960 | 229/300 | 190/300 | 180/300 |
| Q3_K_M | 1,799,740,928 | 221/300 | 186/300 | 173/300 |

Q3 English meets the frozen 221-correct development floor exactly. Neither new arm triggers the 185-correct descent stop. Therefore Stage 2 Q3_K_S/Q2_K and Stage 3 IQ3_S remain required before selecting the minimum-byte English-qualified operating point. Q6 exceeds the 2.2 GB shipped ceiling. The floor is a selection rule, not proven noninferiority; no operating point is selected here.

The [Q6](../diag-q6k/README.md) and [Q3](../diag-q3km/README.md) checkpoints report paired accuracy changes and English-relative changes with joint source-cluster intervals over 250 sources, 10,000 draws and seed 42. All their paired accuracy-difference and nontrivial English-relative intervals include zero. No equivalence or causal language effect follows. Answer churn, correctness changes and fidelity are separate endpoints. The original canonical BF16 vLLM reference remains separate from this BF16 GGUF control.

## Descriptive full-prompt fidelity

Each candidate covers all 900 questions and 176,756 content-token distributions. Entries are mean question-level KL(BF16 || candidate), in nats per content token.

| Candidate | English KL | Bangla KL | Hindi KL |
| --- | ---: | ---: | ---: |
| Q6_K | 0.004857 | 0.005127 | 0.003965 |
| Existing local Q4_K_M | 0.035018 | 0.038329 | 0.030844 |
| Q3_K_M | 0.102541 | 0.124599 | 0.095921 |

Teacher-distribution divergence increases as these formats become smaller, while task correctness is less monotonic and uncertain. These KL means are descriptive on different language prompts, not a causal comparison of language vulnerability or evidence that an allocation improves tasks. They do not authorize substituting a proxy for measured KL.

The preregistered P1 and P3 churn directions hold for all three languages at the completed points. P2's lower-margin flip-rate direction and P4's English-versus-non-English churn ordering hold for Q3. These are descriptive checks of the recorded predictions; the later points still complete the curve.

## Evidence, cost and limits

The point directories contain verified 197-member task archives and 903-member fidelity archives. [Q4 fidelity](../local-q4/README.md) is a new endpoint on the existing model, with no task recollection. The raw BF16 logit cache stays local; its [manifest](../reference-fidelity/manifest.json) is pinned. No model weights or raw vocabulary-logit arrays enter Git.

Q6 task collection intervals total about 17.5 minutes; Q3 totals 49.4 minutes. Recorded KL core intervals are 20.6 minutes for Q6, 28.9 for Q3 and 34.1 for Q4. Q3/Q4 used complete-question batches for the account-allowance guard; these sums exclude verification/import/process-startup intervals. Desktop load and I/O vary. These are evaluation costs, not controlled decoding or phone benchmarks.

The readable actual-file Q6 tensor inventory was attached after its task scoring, although actual model hash, bytes and native dry-run layout were pinned beforehand. The supplement matches the prediction in every tensor and discloses that timing deviation. Q3's actual inventory supplement preceded inference. Remaining builds include actual inventories in their original committed manifests before inference.

Stage 2 starts only after this report is committed. IQ3_S is slightly larger than Q3_K_S and Q2_K, so a Stage 2 descent failure does not automatically exclude it. C8 starts only after the complete required curve and English-only operating-point decision. No C8 comparative outcome, human generation judgment, A4-conditioned slice or final holdout outcome has been collected here.
