# A3 upstream execution and reporting

Runtime [PR36](https://github.com/grinder81/tiny-aya-edge/pull/36) validates the
unchanged upstream LocalCompletionsAPI with explicit HF tokenization and string
requests. The original runtime's prefix reuse failed cold-logit comparisons.
The new isolated runtime cold-prefills echoed likelihood requests; an exactly
equivalent top-one echo ranking optimization changes no probabilities. Both arms
passed 192 independent candidate checks plus 36 reversed-order checks. Preserve
their manifests and complete raw gate identities when running this driver.

The legacy A2 numerical bridge does not pass its original bound universally:
42/60 selected BF16 and 55/60 Q4 candidate comparisons exceed 0.001 nats. No
selected winner changed, which is not proof of equivalence. This new plain-letter
arm is a separate cold diagnostic baseline. Existing A1/A2 outputs retain their
own runtime identities. Request-order dependence is an additional possible
confound in old rotation comparisons; its contribution is not yet estimated.

## Frozen upstream path

`scripts/run_scoring_variants.py` uses unchanged upstream ConfigurableTask,
LocalCompletionsAPI and simple_evaluate. Only the supported task dataset and
text/choice/target fields are supplied. No adapter or scorer is overridden.
The task still adds exactly one ASCII-space delimiter. Choices exclude that
delimiter, so upstream acc_norm divides by Unicode choice characters.

The immutable request lock contains exactly 3 languages × 3 variants × 100
questions × 4 rotations. Every five-question shard keeps exact source/question,
rotation, prompt, candidates, displayed choices, targets and character lengths.
Redundant token arrays stay in the hash-pinned lock rather than every raw sample.
No holdout, task-key correction, truncation or cherry-picked questions are used.

There are 720 shards, 3,600 contexts and 14,400 candidate scores per arm; both
arms share the same 300 unique questions. Rotations are repeated measurements,
not additional independent questions. Primary predictions use raw sums;
acc_norm remains a separately reported diagnostic.

## Run and resume

From this repository root, use the isolated client Python and fresh output paths:

```text
python scripts/run_scoring_variants.py --lock REQUEST_LOCK.json \
  --runtime ARM_RUNTIME.json --validation ARM_CLIENT_GATE.json \
  --order-validation ARM_ORDER_GATE.json --tokenizer ORIGINAL_TOKENIZER_DIR \
  --base-url http://127.0.0.1:8098/v1/completions --directory NEW_ARM_DIRECTORY
```

The endpoint must serve the manifest's exact model path. The driver verifies
runtime/model/native/client/tokenizer source hashes, complete successful primary
and order gates, exact membership and saved shard contents. Its identity pins
both gates, source modules, versions, model arguments and served model ID.
Existing shards are reused only under identical identity and exact validation.
New outputs are validated before atomic promotion. Cold prefills make skipping
validated shards independent of prior server request history.

`--max-new-shards 1` is a bounded live smoke test; `0` validates saved shards until
the first missing one and performs no new scored requests. Use a separate smoke
directory. Any identity mismatch, unexpected shard, failed gate or corrupt output
stops execution. Preserve artifacts rather than deleting them to force a resume.

The original A2 EOS discrepancy is explicit in runtime evidence: Python servers
used effective EOS 6 although an older conversion manifest required 3. These
candidate continuations append no EOS. The current diagnostic does not silently
ratify generation EOS settings.

After complete evidence, `scripts/summarize_scoring_variants.py` validates exact
both-arm membership, runtime/client compatibility and all 1,440 shards before
joint source-clustered bootstrap reporting. It reports all raw/normalized
variants, original and rotation-mean accuracy, content consistency, agreement,
letter histograms, flips and English-relative compression deltas. A partial run
cannot produce a final report. Use `--help` for its explicit input paths.

The user reviews the complete canonical-contract recommendation before B5.
Changed settings require fresh affected baseline identities; historical numbers
are never relabeled. Runtime validation and development uncertainty do not replace
the held-out finalist evaluation.
