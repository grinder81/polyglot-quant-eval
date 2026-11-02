# Complete Q3_K_S task checkpoint

All 900 original-order questions, 180 shards and 3,600 candidate scores passed validation, followed by separate complete-arm validation. All 900 full-KL questions are also complete and validated. The actual model is 1,660,984,832 bytes; its complete tensor inventory, model/runtime identities and vocabulary receipts were committed before inference.

| Language | BF16 correct | Q3_K_S correct | Change pp and paired 95% interval |
| --- | ---: | ---: | --- |
| English | 230/300 | 210/300 | -6.67 [-10.74, -2.67] |
| Bangla | 187/300 | 179/300 | -2.67 [-7.05, +1.96] |
| Hindi | 184/300 | 178/300 | -2.00 [-6.33, +2.38] |

Bangla's change minus English is +4.00 pp [-1.94, +9.76]; Hindi's is +4.67 pp [-1.02, +10.56]. English's paired interval is below zero; the non-English and English-relative intervals include zero. These development estimates are not equivalence or a causal language-mechanism result. Joint bootstrap resampling uses 250 source clusters, 10,000 draws and seed 42. Canonical BF16 vLLM retains its separate identity.

English 210/300 fails the frozen 221/300 development floor, so this point cannot be selected by that operating-point rule. It remains above the 185/300 descent stop. Stage 2 and the complete curve remain unfinished; no operating point or C8 outcome is selected.

The [complete task report](complete-accuracy.json.gz) contains normalized scores, identities, paired comparisons against BF16 and local Q4, margin bins and prediction checks. The [197-member scoring archive](scoring-evidence/manifest.json) preserves raw shards and readiness/source evidence; SHA256 `120b5455a4005ca74479b3d21c3899899f2d356e223267ba84a257367e408f22`. No weights or raw vocabulary logits are published. A4-conditioned slices, human generation review and final holdout outcomes remain separate and untouched.

The [combined task and fidelity report](complete-accuracy-fidelity.json.gz) covers 176,756 content-token distributions. Mean question-level KL(BF16 || Q3_K_S), in nats per content token, is 0.185407 English, 0.207971 Bangla and 0.168973 Hindi. These descriptive values do not establish a causal language effect or a task benefit. All per-question hashes, source/prompt/token identities, token means, language aggregates and verified execution receipts passed validation. The [903-member fidelity archive](fidelity-evidence/manifest.json) has SHA256 `2aaa798f821881c24253c23eacf9d0bd81ba86e10d66524bf559092815fda4c6`. Q2_K validation has begun; Stage 2 remains incomplete.
