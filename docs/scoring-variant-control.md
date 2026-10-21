# A3: scoring-variant diagnostic

Prerequisite preparation for issue 18. Actual scoring follows A2. No custom
adapter, canonical contract change, training, or final-holdout access is included.

## Frozen comparisons

Use exactly A2's first 100 matched development questions per language and all four
cyclic option rotations. Keep the same BF16 GGUF and local Q4 arms. Do not select
questions by previous correctness, margin, error label, or translation judgment.

| Variant | Context | Continuations |
|---|---|---|
| plain-letter | Unchanged upstream Belebele prompt | ` A`, ` B`, ` C`, ` D` |
| chat-letter | Original tokenizer's default template, one user message containing that same prompt, assistant generation prefix | Same letters |
| plain-option-text | Unchanged upstream Belebele prompt, including the displayed options | Space followed by the displayed choice text |

This three-way comparison does not estimate a full chat-by-answer-format
interaction. Option-text scoring keeps the question and displayed choices, so it
tests a different continuation representation without silently rewriting the task.

The delimiter is one ASCII space. Preserve all choice text, including Unicode and
any existing whitespace. No EOS is appended to the candidate. Chat rendering uses
the original template, including its system preamble and response prefix; the final
`Answer:` is still inside the user's message. Strip only the initial literal BOS
from the wire string when the server supplies that same token automatically.
Verify the resulting complete model IDs against original-tokenizer rendering.
Never strip or add other special tokens to make a check pass.

## Evidence prepared

`scripts/prepare_scoring_variants.py` takes the existing rotation lock and original
tokenizer, then writes a new request lock and compact summary. It does not load
model weights or call a server. It checks all 1,200 rotation identities, remapped
gold indices, unchanged plain-letter tokens, implicit BOS equivalence, every
continuation boundary, exact HF text roundtrips and the 8,192-token limit. Failure
stops preparation; no items are dropped or truncated.

`docs/scoring-variant-render-check.json` records 3,600 contexts and 14,400 candidate
continuations passing these offline checks with Transformers 4.57.6. Maximum full
candidate length is 717 model tokens. It pins the rotation/source locks, original
tokenizer files and preparer hash. The large request lock is retained at
`/home/shohag/tiny-aya-stage1/pilot/scoring-control/request-lock.json` on the run
machine, with its SHA-256 recorded in the summary; reproduce it using:

```text
python scripts/prepare_scoring_variants.py --rotation-lock ROTATION_LOCK.json \
  --tokenizer ORIGINAL_TOKENIZER_DIRECTORY --output NEW_REQUEST_LOCK.json \
  --summary NEW_SUMMARY.json
```

This does not yet prove that the endpoint consumes these IDs or that its output
probabilities are indexed correctly. The special-token echo problem documented in
`chat-template-preflight.md` remains an execution gate for the current GGUFLM path.

## Supported-path validation before inference

The pinned upstream `LocalCompletionsAPI` offers a possible alternative without a
custom adapter: it accepts an HF tokenizer, non-tokenized string requests and
parses echoed probabilities by context token count instead of character offsets.
Use explicit configuration, not auto-detection. Pre-rendered diagnostic fields can
be passed through upstream `ConfigurableTask`; do not override its scorer.

This is a candidate path, not a verified solution. Before selecting it:

- Verify exact `create_message` roundtrips with the pinned tokenizer, including
  special markers and whitespace; its default batch decoding must also be checked.
- Confirm the server inserts exactly one BOS, omits it from echoed arrays as
  expected, and returns all supplied token probabilities in order plus precisely
  the generated-token suffix the parser excludes.
- Check actual continuation probabilities against direct logits for all three
  languages, multiple-token option texts, every rotation, and chat special tokens.
  Include the longest input and non-ASCII examples; reject missing/extra tokens.
- Bridge the same plain-letter requests to the existing GGUFLM results before
  attributing any difference to a prompt variant. Record exact differences and
  justified numerical tolerances before collecting the full diagnostic.
- Pin the isolated environment and new run identity. Do not install into or modify
  A2's active environment. If neither supported path validates, report the evidence
  and seek approval before any custom adapter.

No inference is authorized merely by a passing offline lock. The approved A2/A3
order and these validation gates still apply.

## Analysis fixed before collecting variant scores

Keep raw summed continuation log-likelihood as the primary prediction for each
variant. Also report upstream `acc_norm`, which divides by the Unicode character
count of the choice text, excluding the added delimiter. This is neither token nor
UTF-8-byte normalization. For letters it changes nothing; for option texts it is
a separate diagnostic prediction. Retain the original scores and both predictions.

Report original-order and rotation-average accuracy, original-content consistency
across all four rotations, six-pair agreement, gold/predicted letter histograms,
paired model and variant flips, and exact duplicate-choice flags. Remap predictions
to original option indices before comparing content. Review synonymous choices
separately without changing official keys or scores.

Use the same source-clustered paired bootstrap across languages, models and
variants (10,000 draws, seed 42). Include Q4-minus-BF16 deltas and their differences
from English. Report all variants rather than selecting the best Bangla result
after seeing scores. Intervals are development-sample uncertainty, not independent
holdout validation or proof of equivalence.

Decision order: first require verified token/probability correctness; then examine
paired task accuracy and content consistency; then use position diagnostics to
explain trade-offs. Lower A frequency alone cannot win. Any recommended contract
must show its English and Hindi consequences and examples where its prediction
changes. No automatic winner is defined: bring the complete evidence to the user
for the explicit canonical-contract decision before B5. If the contract changes,
rerun affected baselines under fresh identities; never relabel previous results.
