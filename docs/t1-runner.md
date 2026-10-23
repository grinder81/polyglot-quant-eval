# Original-order T1 readiness and collection boundary

T1 prepares fresh BF16 GGUF and local-Q4 cold-runtime baselines for the same
300 development questions per language used in A1. Preparation does not collect
new probabilities, launch a server, inspect holdout content, or authorize collection.

The original sample-lock file contains 300 items despite its historical
`pilot_count: 50` default. Its byte hash is checked against the frozen A3
provenance. The preparer reads only these development items, reproduces every
prompt and candidate with the local HF tokenizer, checks the original full model
IDs, and joins the first 100 items per language to exact A3 plain-letter/r0
requests. No dataset download or whole-dataset render is needed.

Each candidate is exactly one continuation token. The client excludes BOS;
the server supplies one BOS. Candidate text remains ` A`, ` B`, ` C`, ` D`.
The primary score is unchanged upstream summed continuation log likelihood,
with first-index ties. The separate `acc_norm` divides by choice character
lengths, all one here. No generation or EOS is appended.

```sh
python -m scripts.prepare_t1_baselines --sample-lock ORIGINAL300.json \
  --a3-lock A3.json --tokenizer LOCAL_HF --output NEW_LOCK.json --summary NEW_PREP.json
LLAMA_CPP_LIB_PATH=PINNED_NATIVE_DIRECTORY python -m scripts.check_t1_tokens \
  --lock NEW_LOCK.json --model ARM.gguf --runtime A3_ARM_RUNTIME.json --output NEW_TOKENS.json
```

The vocabulary checker requires the exact native library, model and wrapper
hashes from the runtime manifest before loading the vocabulary. `vocab_only=True`
and `n_gpu_layers=0` perform no model inference. A failed initial library-selection
attempt is preserved separately from successful pinned-library checks.

Readiness validation is explicitly offline:

```sh
python -m scripts.run_t1_baselines --validate-only --lock NEW_LOCK.json \
  --readiness NEW_PREP.json --token-check ARM_TOKENS.json --a3-lock A3.json \
  --a3-execution-record results/a3-scoring-variants/execution-record.json \
  --arm bf16-gguf --tokenizer LOCAL_HF --directory NEW_FUTURE_ARM_DIRECTORY \
  --base-url http://127.0.0.1:8098/v1/completions
```

This validates original membership, current source/package/tokenizer/model
identities, both complete A3 arms and their cold/order gates, and every present
T1 shard. It creates no output directory and makes no HTTP request. Python `-O`
is rejected because the frozen upstream sample validator uses assertions.

After separate explicit approval, run the reviewed runtime repository's new
`setup/validate_t1_cold.py` against the exact lock SHA. The structural selection
contains indices 0, 100, 299 and the first longest full request per language.
All four candidates are checked, then the complete selected sequence is reversed.
The direct oracle uses raw full-vocabulary logits independently of the echo
parser. Expanded coverage being shorter than the old maximum does not establish
universal correctness. These live checks are planned, not passed at readiness.

Future collection adds `--collect --expanded-gate GATE_PATHS.json` instead of
`--validate-only`. The config contains absolute paths named `oracle`,
`validation`, `order_validation`, `validator_script`, and `protocol`. The runner
rehashes these files and recomputes the raw numerical checks, rather than trusting
empty failure lists. It requires the original A3 cold runtime and current scorer
module identities, exact client settings and one-token IDs. Changing any of these
requires a fresh reviewed identity; it cannot resume existing checkpoints.

The gate requires finite values, exact token boundaries and counts, parser versus
the same supplied array within 1e-8, independent per-token differences at most
0.0002 nats, and summed differences at most 0.001 nats. Both limits must pass.
The future A3 overlap checks 1,200 candidate scores per arm (2,400 across both)
with the stricter intersection of these limits. One-token continuations make
candidate differences genuine token differences; cancellation cannot hide drift.
Every candidate delta is retained. Any overlap prediction inversion stops for
review, even if it lies inside the numerical bounds.

The runner reuses the frozen `task_for` and sample validator from A3, with added
strict numeric checks. It never changes the model adapter, payload/parser or
scoring rule. It validates all saved shards before new requests, including shards
after a missing checkpoint. Each arm has 180 five-question shards in language and
original index order. Successful temporary files are validated before atomic
promotion. Failed temporary responses remain for inspection, and prevent resume.
Use a fresh directory; never delete or overwrite failed evidence to resume.

`--max-new-shards N` bounds new collection without skipping validation of later
saved shards. Cold-prefill runtime reset makes each scoring request independent
of previous requests and restart order; the expanded reverse gate tests that
property on the frozen coverage. Complete reporting requires all 180 shards for
each arm and all 900 exact original identities, never a silent intersection.

Historical A1 comparisons retain their original identities. They describe the
combined runtime change on identical requests and model artifacts; observed
bridge maxima are subset measurements, not uniform stopping bounds. Fresh margin
analysis remains exploratory association, not a mechanism or a claim about a
language. Generation/EOS validation and later T3/A4 decisions are separate gates.
