# Resumable fifty-per-language evaluation

`scripts/run_shards.py` runs the frozen first 50 examples in each language as
five-question groups using `run_pilot.py` and the unchanged upstream task and
scorer. Completed JSON files are atomically published. Restarting reuses completed
groups; an interrupted group is retried. This bounds lost work to five questions.

The checkpoint identity hashes the sample lock, runner, and a required runtime
manifest, and records backend, model arm and tokenizer. Use a manifest containing
the exact model hashes, source revisions, local patches, environment, and server
settings. Changing the identity rejects reuse. Keep each model in its own
directory. Do not edit a manifest to relabel existing scores.

The runner does not add an adapter or alter scoring. It avoids relying on
GGUFLM's cache, which does not checkpoint individual responses inside an
interrupted loglikelihood call. The resume test checks that completed groups are
not executed again and a changed runtime is rejected.

Aggregate per-item records, not unweighted averages of group summaries. Verify
150 unique document identities per arm and the same identities across arms
before reporting accuracy and paired flips. The smoke examples remain development
data; these results are not an untouched final test set.
