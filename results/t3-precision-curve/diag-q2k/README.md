# Complete Q2_K task checkpoint

All 900 original-order questions, 180 shards and 3,600 candidate scores passed validation, followed by separate complete-arm validation. Full KL collection is running. The actual model is 1,481,973,248 bytes; actual tensor inventories, model/runtime identities and vocabulary receipts were committed before inference.

| Language | BF16 correct | Q2_K correct | Change pp and paired 95% interval |
| --- | ---: | ---: | --- |
| English | 230/300 | 180/300 | -16.67 [-22.11, -11.36] |
| Bangla | 187/300 | 149/300 | -12.67 [-18.86, -6.42] |
| Hindi | 184/300 | 142/300 | -14.00 [-19.46, -8.36] |

All three paired accuracy intervals are below zero. Bangla's change minus English is +4.00 pp [-3.70, +11.74]; Hindi's is +2.67 pp [-4.47, +9.84]. Those English-relative intervals include zero, so the result does not establish a causal language-specific vulnerability. Joint source-cluster bootstrap uncertainty uses 250 groups, 10,000 draws and seed 42. Canonical BF16 vLLM retains its separate identity.

English 180/300 fails the 221/300 selection floor and meets the frozen descent stop at 185 or fewer. No later stage with smaller builds may run. IQ3_S remains required: its previously measured native size prediction is 1,665,998,336 bytes, larger than both Q3_K_S and Q2_K. The frozen rule uses actual bytes rather than nominal bit names. No smaller optional point or imatrix-free IQ2 build is added.

The [complete task report](complete-accuracy.json.gz) contains normalized scores, identities, paired comparisons against BF16/local Q4, margin bins and prediction checks. The [197-member scoring archive](scoring-evidence/manifest.json) has SHA256 `c0aceddf57316ee163341cab896d4e3f40146513965e7a955d488d7cedad7cc2`. No operating point is selected before the complete required curve. No weights, raw vocabulary logits, A4-conditioned analyses, human judgments or holdout outcomes are published or newly collected here.
