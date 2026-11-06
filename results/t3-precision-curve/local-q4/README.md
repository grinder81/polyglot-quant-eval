# Existing local Q4 full fidelity

The existing Q4_K_M model's full KL endpoint is complete: 900 questions, 176,756 content-token distributions, the frozen T1 runtime and the same BF16 reference cache as Q6/Q3. No Q4 task score was recollected. Model SHA256 remains `5823bd1e52be1027a7ba6f31b43edfd40ae1766020cddec967f0d76618948290`.

Mean question-level KL(BF16 || Q4), in nats per content token, is 0.035018 English, 0.038329 Bangla and 0.030844 Hindi. These are descriptive fidelity values, not accuracy effects or a test of language differences. See the [combined Stage 1 report](../stage1/README.md) for task results, interpretation and the remaining stages.

All question hashes, source/prompt/token identities, means, aggregates and the verified native-before-Torch execution receipt passed validation. The [903-member archive manifest](fidelity-evidence/manifest.json) indexes the per-question evidence and identities; archive SHA256 is `06780f172d5d717a79672aed3b65d2be27f1d987b512cc65f996352b4aaa3247`. Raw vocabulary logits stay local. Thirty complete-question batches total 2,048.05 seconds, 34.1 minutes, of core intervals excluding process/verification/import startup; this is an evaluation cost, not device throughput.
