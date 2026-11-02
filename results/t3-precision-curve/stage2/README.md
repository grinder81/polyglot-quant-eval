# T3 Stage 2 complete report

The [complete report](complete-report.json.gz) validates all four new task arms, all five candidate full-KL endpoints and their original T1 references. Every new arm has 900 task questions and 900 KL questions. No holdout or A4-conditioned outcome is used.

| Candidate | Actual bytes | English correct | Bangla correct | Hindi correct |
| --- | ---: | ---: | ---: | ---: |
| BF16 control | 6,710,484,480 | 230/300 | 187/300 | 184/300 |
| Q6_K diagnostic | 2,759,532,032 | 233/300 | 188/300 | 185/300 |
| Existing local Q4_K_M | 2,143,976,960 | 229/300 | 190/300 | 180/300 |
| Q3_K_M | 1,799,740,928 | 221/300 | 186/300 | 173/300 |
| Q3_K_S | 1,660,984,832 | 210/300 | 179/300 | 178/300 |
| Q2_K | 1,481,973,248 | 180/300 | 149/300 | 142/300 |

Both new Stage 2 points fail the 221-correct English selection floor. Q2 triggers the descent stop at 185 or fewer; all three Q2 paired accuracy intervals are below zero. Non-English changes relative to English remain uncertain. Point directories contain complete paired intervals, source-cluster uncertainty, normalized scores, raw scoring archives and verified per-question KL evidence. The original canonical BF16 vLLM reference remains separate.

Mean question-level KL(BF16 || candidate), in nats per content token:

| Candidate | English | Bangla | Hindi |
| --- | ---: | ---: | ---: |
| Q6_K | 0.004857 | 0.005127 | 0.003965 |
| Existing Q4_K_M | 0.035018 | 0.038329 | 0.030844 |
| Q3_K_M | 0.102541 | 0.124599 | 0.095921 |
| Q3_K_S | 0.185407 | 0.207971 | 0.168973 |
| Q2_K | 0.441425 | 0.580459 | 0.450495 |

All endpoints cover the same 176,756 content-token distributions. KL is descriptive; it does not establish language-specific task vulnerability. Shared runtime, request lock, tokenizer, float64 reduction and verified native-before-Torch execution preserve comparability. The disclosed late readable Q6 inventory attachment remains the only inventory-timing deviation; later actual inventories were committed before inference.

No later smaller artifact is permitted after Q2's stop. Stage 3 IQ3_S remains required because its frozen native size prediction, 1,665,998,336 bytes, is larger than both Stage 2 points. No IQ2 or optional densification is added. This report is committed before IQ3_S is built. The full curve and English-only operating-point decision still precede all C8 comparative measurements. This is development evidence, not final allocation, generation or device success.
