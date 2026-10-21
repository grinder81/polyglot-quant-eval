# A4 bilingual polarity review protocol

This prepares human review for issue 19. It does not run the interaction analysis
before A3 or assign verified labels automatically. The 300 matched development
pairs come from the existing sample lock and completed BF16 raw documents; no
reserved final-holdout items are read. Original benchmark scores and keys stay intact.

## Packet and screening

`results/stage2/negation-review/review.md` contains the paired passages, questions
and choices. `packet.json` holds the same material plus empty review fields; use a
separate annotated copy so the original packet and its recorded hash are preserved.
The packet deliberately excludes model predictions, probabilities, correctness and
answer keys. It includes all questions, so both model successes and failures enter
without the reviewer knowing which is which.

The generator uses exact source/question joins, not the raw harness `doc_id`.
It checks that both languages cover exactly the frozen 300 groups. Input hashes,
generator hash and packet hash are recorded. Reproduce with:

```text
python scripts/prepare_negation_review.py --lock SAMPLE_LOCK.json \
  --raw-directory BF16_RAW_SHARD_DIRECTORY --output-directory NEW_PACKET_DIRECTORY
```

The word lists are navigation hints only. They flag 42 pairs in both languages,
25 in English only and six in Bangla only; 227 have no hints. These are **not**
negation counts, translation-error counts, or model-error counts. For example,
"least expensive" may be an ordinary minimum comparison, and a Bangla expression
can convey an exception without matching this small word list. Every pair remains
in the review packet; no-hint items must not automatically become negative controls.

## Required bilingual judgments

A fluent English–Bangla reviewer reads the actual Bangla question and relevant
passage, not merely the English marker or an automatic translation. For each
language set `selection_polarity` to:

- `negated_selection`: the question asks for an unsupported/false proposition,
  an exception, or another genuine reversal of the ordinary selection criterion.
- `ordinary_selection`: it asks for a supported fact, ordinary comparison or
  attribute without that reversal. A negative statement in the passage alone
  does not make the question a negated selection.
- `unclear`: wording, scope or translation prevents a reliable decision.

Record a short subtype (for example explicit negation, exception, minimum
comparison or ordinary fact), an exact `scope_quote`, and explanatory notes.
Do not correct wording or choose the answer as part of this label. Negation in a
quoted claim, a double negative, "without", or "least" needs a semantic judgment.

For each pair record whether polarity is equivalent (`true`, `false`, or `null`
if unresolved), whether a translation issue is present (`true`, `false`, or `null`),
reviewer identifier, review date and adjudication notes. Flag previously inspected
examples in the notes if known. An uncertain or disagreeing pair requires explicit
adjudication; do not silently force agreement. A second bilingual review is useful
for these cases, but no machine-generated label counts as human verification.

The primary interaction includes reviewed, polarity-equivalent pairs with no
translation issue and the same non-unclear label in both languages. Keep the
remaining cases in an exclusion ledger, not out of the official benchmark.
Unreviewed items remain unreviewed, never ordinary by default. Before analysis,
reconcile reviewed/unreviewed, both selection groups, translation disagreements,
unclear labels and exclusions back to the full 300 pairs, with source counts.

## Analysis after the A3 contract decision

Use the canonical scoring contract the user selects after A3. If that contract
changes, use fresh matched BF16/Q4 results under it; do not relabel A1's outputs.
Freeze the adjudicated labels and their hash before joining outcomes.

For each model arm and reviewed selection group, report both English and Bangla
correct/total, accuracy and the paired Bangla-minus-English gap. The language
interaction is that gap on negated selection minus the gap on ordinary selection.
The compression interaction is the Q4 interaction minus the BF16 interaction.
Negative values indicate a larger relative Bangla deficit under this definition.
Do not substitute an unpaired comparison of unrelated question sets.

Use the same jointly resampled source-document clusters across languages and arms
(10,000 bootstrap draws, seed 42). Report point estimates, effect intervals and
valid-replicate counts. Empty groups are not estimable, not zero; report insufficient
support rather than inventing an effect. This is an observational subgroup contrast
within the development set, not a randomized manipulation of negation. It cannot
separate negation from topic, difficulty or translation differences by itself.

Conclude supported, unsupported or unresolved evidence for the proposed interaction
in these data, with uncertainty and exclusions visible. Statistical significance
alone neither identifies a defective layer nor selects a repair target. Human
review and the A3 decision remain prerequisites; no interaction result is claimed
by creating this packet.
