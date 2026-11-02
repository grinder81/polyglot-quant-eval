# Complete Q3_K_M accuracy checkpoint

Collected 1 November 2026 under the frozen T3 specification. Q3_K_M completed all 180 validated five-question shards, 900 original-order questions and 3,600 candidate scores. Direct, API-client, reversed-order and vocabulary gates passed before collection; separate complete-arm validation also passed. The owned scoring server stopped before full KL collection began. This is a completed task checkpoint, not the complete precision curve or an allocation result.

| Language | BF16 correct | Q3_K_M correct | Q3 minus BF16 pp and paired 95% interval |
| --- | ---: | ---: | --- |
| English | 230/300 | 221/300 | -3.00 [-6.73, +0.66] |
| Bangla | 187/300 | 186/300 | -0.33 [-4.48, +3.96] |
| Hindi | 184/300 | 173/300 | -3.67 [-7.87, +0.66] |

The Bangla change minus the English change is +2.67 pp [-2.61, +8.03]; the Hindi change minus English is -0.67 pp [-6.15, +4.90]. All paired accuracy-difference and nontrivial English-relative intervals include zero. They establish neither equivalence nor a causal language mechanism. Ten thousand joint source-cluster bootstrap draws use seed 42 and the same 250 source groups as T1. BF16 GGUF and the original canonical BF16 vLLM reference retain separate identities.

English's 221 correct answers meet the frozen development floor exactly. That floor is an operating-point selection rule, not proven noninferiority. The 185-correct descent stop is not triggered, so the later precision stages remain required. No operating point is selected from this partial curve.

The actual GGUF is 1,799,740,928 bytes, below the 2.2 GB shipped ceiling. Its model hash, bytes, native layout prediction and actual-file inventory supplement were committed before inference. The late-inventory timing deviation disclosed for Q6 does not apply to this Q3 inference sequence. Answer churn versus BF16 is 35 English, 52 Bangla and 57 Hindi; the corresponding right-to-wrong / wrong-to-right counts are 20/11, 21/20 and 27/16. Churn is not accuracy damage.

The [complete task report](complete-accuracy.json.gz) includes normalized score rows, full identities, comparisons against both BF16 and local Q4, source-paired uncertainty and fixed margin-bin predictions. The [197-member scoring archive](scoring-evidence/manifest.json) retains all raw shards and readiness/source evidence, excluding weights and vocabulary-logit caches. Its SHA256 is `159138dc4ce32c9077ea5d2e2b7ddb21c62cbd278829151fd3cd81d46ee1517c`.

```sh
python -m scripts.archive_t3_arm verify results/t3-precision-curve/diag-q3km/scoring-evidence
```

The nine complete collection batches total 2,965.70 seconds, 49.4 minutes, excluding their initial identity-validation and process-startup intervals. Q6's combined collection interval was about 17.5 minutes on this workstation. These are evaluation costs under the recorded desktop load and scorer; they are not controlled decoding-throughput or phone-performance benchmarks. Full Q3 and Q4 KL, the remaining curve, C8, genuine generation review and final holdout confirmation remain separate work. A4-conditioned slices and holdout outcomes remain sealed.
