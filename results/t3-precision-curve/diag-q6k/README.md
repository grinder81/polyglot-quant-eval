# Complete Q6 accuracy checkpoint

Collected 1 November 2026 under the frozen T3 specification. Q6_K has all 180 validated five-question shards, 900 original-order questions and 3,600 candidate scores. A separate complete offline validation exited zero, and the owned scoring server was stopped. Q6's full-prompt KL endpoint is also complete. The remaining precision points are pending; this is a completed arm checkpoint, not a complete stage or allocation result.

| Language | BF16 correct | Q6_K correct | Q6 minus BF16 pp and paired 95% interval |
| --- | ---: | ---: | --- |
| English | 230/300 | 233/300 | +1.00 [-0.99, +2.99] |
| Bangla | 187/300 | 188/300 | +0.33 [-1.34, +2.03] |
| Hindi | 184/300 | 185/300 | +0.33 [-1.35, +2.03] |

The Bangla and Hindi changes minus the English change are both -0.67 pp, with intervals [-3.29, +1.97] and [-3.32, +1.96], respectively. All accuracy-difference and nontrivial English-relative intervals include zero. They establish neither equivalence nor a language-specific effect. The original canonical BF16 vLLM reference retains its separate identity.

The complete report includes comparisons against local Q4_K_M, source-paired uncertainty over 250 source clusters, answer-churn decompositions, predicted-letter histograms, fixed BF16 margin bins and descriptive score/margin changes. Ten thousand bootstrap draws use seed 42. Q6_K is 2,759,532,032 bytes, above the 2.2 GB final budget; it is a diagnostic.

The [complete accuracy report](complete-accuracy.json.gz) retains the model manifest, frozen identities and all normalized score rows. The [evidence manifest](scoring-evidence/manifest.json) indexes 197 losslessly archived members: all raw shards, identity, config and readiness/source evidence. It excludes weights and raw vocabulary-logit caches. Archive SHA256 is `0c3cacbcabe61450b521ab767d75c0e954d9f3dfc5bd52c76458d05eff540be4`.

```sh
python -m scripts.archive_t3_arm verify results/t3-precision-curve/diag-q6k/scoring-evidence
```

The first 20 shards took 110.22 seconds and the remaining 160 took 939.92 seconds, roughly 17.5 minutes of recorded collection intervals combined. These are workstation evaluation timings, not device decoding throughput. Staged operating-point selection, the C8 pilot, generation review and final holdout remain separate work.

## Complete fidelity endpoint

The fresh verified run covers all900questions and176,756content-token distributions. Mean question-level KL(BF16 || Q6_K), in nats per content token, is0.004857for English,0.005127for Bangla and0.003965for Hindi. These are descriptive fidelity values on different language prompts, not task-accuracy effects or a test of language differences. The execution interval was1,235.02seconds,20.6minutes, including inference, cache verification, float64 reduction and a separate CPU oracle on every question's first chunk.

The [accuracy and fidelity report](complete-accuracy-fidelity.json.gz) verifies every per-question hash, source/prompt/token identity, KL mean and language aggregate. The [903-member fidelity archive](fidelity-evidence/manifest.json) contains all900per-question summaries, identities and verified native-before-Torch execution receipt; SHA256 `0132dfef29354189d99fc7d552624d2a55b5341f80cd3ba1423da65af72cd125`. The [BF16 reference manifest](../reference-fidelity/manifest.json) is pinned at SHA256 `9964b004736d733b872e3a4f2e294631f7b4744894d4626b60a928d2f193aa6e`. Raw vocabulary-logit arrays remain local.

The earlier slower partial run is preserved outside this package and excluded from the endpoint. Native backend initialization precedes Torch import, and the verified host-thread setting is one; the immutable extraction and KL core remain the reference producer's implementation. The readable actual-file tensor inventory was attached after Q6 task scoring, as disclosed in runtime PR43, while actual model hash, bytes and native dry-run layout were pinned beforehand.
