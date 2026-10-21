# A2: option-position diagnostic

Freeze this specification before collecting rotation results. A1 must complete
before scoring this control. Use the first 100 matched development groups from
the existing sample lock in each of English, Bangla and Hindi, in BF16 GGUF and
local Q4. Membership is in `configs/option-rotation.json`. Do not use final holdout
questions. No selection by whether a model previously answered correctly.

For shifts 0, 1, 2 and 3, display original option `(position + shift) % 4` at each
position. Remap the gold letter accordingly. Keep passage, question and upstream
prompt template identical. The task remains four upstream letter log-likelihoods.
This is a diagnostic variant, not a replacement benchmark or endpoint adapter.
Validate zero-rotation prompt hashes against the lock and all remapped answer
contents. Before inference, validate every rotated context/candidate token sequence
and roundtrip against the original tokenizer. Record hashes and a new run identity.

Report each rotation's accuracy, gold/predicted letter counts, paired BF16/Q4 flips,
and original-content predictions. Define rotation consistency as the fraction of
questions with the same original option selected in all four rotations, with
pairwise agreement also reported. Report accuracy averaged over rotations and
original-order accuracy separately. Identical-text choices retain distinct original
indices and are flagged; do not infer a semantic change solely from their index.

## Prespecified correction diagnostic

Separately for each arm and language, center each four-letter score vector by its
mean. Average centered scores at each displayed position over all four rotations
of fitting questions. This estimates a zero-sum additive letter offset without
using labels. It relies on an additive content/position approximation; interactions
can violate it. Subtract the fitted offsets and take the usual first-index argmax.

Use five source-group folds: SHA256 of the source string as a big integer modulo
five. Every question and translation from a source shares its fold. For each held
fold, fit only on other folds; no held-source score or target enters its correction.
Report fold sizes and offsets, raw versus cross-fitted accuracy and consistency,
paired flips and passage-cluster uncertainty. Refit the estimator within each
bootstrap replicate rather than treating fitted offsets as known. Bootstrap whole
sources jointly across arms/languages, keeping their original folds, with seed 42
and 10,000 draws. Flag any replicate with an empty training fold rather than silently
using held data.

Do not select a correction because A becomes less common. Improvement in
cross-fitted accuracy and content consistency, with multilingual retention and
uncertainty reported, is the evidence to discuss. No automatic canonical switch
or retuning of this estimator is authorized by this diagnostic. Applying it beyond
the 100-question diagnostic requires review of that evidence and the A3 scoring
decision. If eventually approved, retain cross-fitted estimates for the first 100
and train only on those 100 for the other 200; keep all adjusted results labeled.

The utility tests check content/gold mapping across all rotations, recovery under
a known additive bias, and source exclusion. These do not prove a real model has
an additive letter prior. Runtime and full diagnostic-run validation remain required.

## Execution tooling

Prepare a fresh lock with `scripts/prepare_rotation_lock.py --lock SOURCE_LOCK
--spec configs/option-rotation.json --tokenizer ORIGINAL_MODEL_DIRECTORY
--tokenizer-python TOKENIZER_PYTHON --output NEW_ROTATION_LOCK`. This renders only
the selected development questions and stores original-tokenizer context/candidate IDs.

Run `scripts/check_rotation_tokens.py --lock ROTATION_LOCK --model GGUF
--output NEW_PREFLIGHT` for each GGUF arm using the pinned patched library. It checks
1,200 contexts and 4,800 candidate sequences plus decoded-text roundtrips, recording
model/library/Python-wrapper hashes. Vocabulary-only checks perform no scoring.

After A1 closes, start one pinned server at a time with the recorded baseline
command/settings and capture its runtime manifest. Run `scripts/run_rotation_shards.py
--lock ROTATION_LOCK --preflight PREFLIGHT --runtime-manifest MANIFEST --arm ARM
--base-url ENDPOINT --directory NEW_RESULTS_DIRECTORY`. It uses the unchanged upstream
GGUF scorer and evaluator on five transformed development documents per shard.
No held-out documents are transformed. All four rotations are run anew for both arms.

The runner requires matching lock, preflight and runtime identities, rechecks artifact
hashes, and validates existing shards before reuse. Changed code or runtime rejects
resume. Interrupted incomplete shards are not treated as completed results. Save
the full lock, preflights, identities, manifests and raw outputs with the final report.
This tooling does not itself establish endpoint likelihood parity; the same validated
upstream integration remains required. No custom scoring adapter is introduced.
