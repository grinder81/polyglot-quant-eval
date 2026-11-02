# Complete IQ3_S task checkpoint

All 900 original-order questions, 180 shards and 3,600 candidate scores passed validation, followed by separate complete-arm validation. Full KL collection is running. The actual GGUF is 1,665,998,336 bytes; its complete inventory, model/runtime identities and vocabulary receipts were committed before inference.

| Language | BF16 correct | IQ3_S correct | Change pp and paired 95% interval |
| --- | ---: | ---: | --- |
| English | 230/300 | 188/300 | -14.00 [-18.92, -9.21] |
| Bangla | 187/300 | 160/300 | -9.00 [-14.38, -3.92] |
| Hindi | 184/300 | 138/300 | -15.33 [-20.20, -10.60] |

All three paired accuracy intervals are below zero. Bangla's change minus English is +5.00 pp [-1.73, +11.86]; Hindi's is -1.33 pp [-7.56, +4.97]. Those relative intervals include zero. These results do not establish a causal language-specific vulnerability. Joint source-cluster uncertainty uses 250 groups, 10,000 bootstrap draws and seed 42; canonical BF16 vLLM retains its separate identity.

English 188/300 fails the 221-correct selection floor. This point was required despite Q2's descent stop because its actual bytes exceed both Stage 2 files. It uses no importance matrix, as frozen to avoid confounding the precision curve with calibration. The result describes this imatrix-free export and runtime, not calibrated IQ3_S methods generally.

The [complete task report](complete-accuracy.json.gz) contains normalized scores, identities, paired comparisons against BF16/local Q4, fixed margin bins and prediction checks. The [197-member scoring archive](scoring-evidence/manifest.json) has SHA256 `740eb27d00b5cd9f07b4afc00d94098b3e8a39b58ad1cde5d2fb874746fef11b`. No operating point is selected before the complete required curve and its committed report. No weights or raw vocabulary logits are published; A4-conditioned slices, human generation judgments and holdout outcomes remain untouched.
