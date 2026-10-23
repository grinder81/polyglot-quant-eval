# Exploratory margin and answer-flip analysis

`scripts/margin_flip_analysis.py` describes the association between a reference
arm's top-two **summed letter likelihood** margin and whether a matched candidate
arm selects a different option. The fixed bins are [0, .25), [.25, .5), [.5, 1),
[1, 2), and [2, infinity) nats. An exact tie selects the first displayed option.
It reports bin denominators, flip counts/rates, reference/candidate absolute
correct counts, accuracy deltas and their point gaps versus English.
Rates and accuracy deltas are stored as fractions; multiply a delta by 100 for
percentage points. Empty-bin rates are `null`, not zero.

These are descriptive development counts without source-clustered intervals or
a fitted language-adjusted effect. Shared passages and translated questions are
not independent observations. Binned associations cannot establish that margin
causes churn, explains language differences, or excludes a residual language
effect. A likelihood margin is not a calibrated probability of correctness.

## Supported input boundary

Only the existing **validated expanded original-order GGUF schema** is supported:

```text
REFERENCE_ROOT/
  sample-identities.json
  bf16-gguf-runtime.json
  bf16-gguf/identity.json
  bf16-gguf/{eng_Latn,ben_Beng,hin_Deva}-{000,005,...,295}.json
CANDIDATE_ROOT/
  sample-identities.json
  local-q4-runtime.json
  local-q4/identity.json
  local-q4/{eng_Latn,ben_Beng,hin_Deva}-{000,005,...,295}.json
```

The paths are evidence roots, **not** raw arm folders. Exactly 300 matched
questions per language, five per shard, and all three languages are required.
Membership includes official targets and prompt/ordered candidate hashes; raw
samples use `doc.link` and `doc.question_number`, original-order ` A`/` B`/` C`/
` D` arguments, and four finite `filtered_resps` scores. Raw `doc_id` is not a join
key. Missing questions, duplicated identities, partial overlap, additional tasks,
unexpected/missing shards or temporary files fail instead of being discarded.

The tool reuses `summarize_expanded_local.summarize` to validate frozen membership,
requests, targets, scores and accuracy, and `compare_expanded.validate_runtime_pair`
for matched scoring/lock/runner identity and runtime settings apart from the model.
The membership projections must also match exactly between arms. It records every
input shard hash plus membership, identity and runtime hashes in the new output.
Runtime/model source hashes are preserved manifest references; the tool does not
load weights or claim to revalidate the running server. Sources must be trusted
validated run artifacts, not user-created lookalikes of these JSON files.

The committed historical example can be analyzed with:

```text
python -m scripts.margin_flip_analysis \
  --reference results/stage2/bf16-three-hundred \
  --candidate results/stage1/local-q4-three-hundred \
  --output NEW_MARGIN_REPORT.json
```

This PR introduces validation and descriptive analysis, not a new measured result;
numerical margin/flip conclusions require a separately preserved output artifact.
Historical A1 inputs retain their original runtime identity and the A3 legacy
request-history caveat. They must not be labeled fresh cold-runtime baselines.

## Fresh-baseline compatibility

The accepted [A3 contract](scoring-contract-a3.md) requires fresh affected
comparators before downstream compression comparisons. This script does not
invent that runner's identity schema, strip rotations/variants from A3, or accept
an arbitrary compact-row export. A fresh original-order baseline can be accepted
only through an explicitly reviewed loader for its actual finalized identity,
membership and cold-runtime validation artifacts. The T1 readiness implementation
in `scripts/summarize_t1_baselines.py` integrates this module's pure `analyze`
function **after** the dedicated T1 runner's complete identity/shard validation;
it does not route T1 files through this historical loader. Review that integration
with the actual runner and complete-schema tests before launch. See
[T1 reporting readiness](t1-reporting-readiness.md). Do not weaken the historical
loader to make a new shape pass, or label old inputs as fresh results.
