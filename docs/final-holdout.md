# Reserved final Belebele membership

`configs/belebele-final-holdout.json` reserves the same 424 question identities in English,
Bangla and Hindi at dataset revision `7899cdfa4e1e0d733fd77c848e2c273cb1d32be2`.
The reservation reads source links and question numbers only, without evaluating answers.
It records the development lock hash and a deterministic membership hash.

Each language has 900 questions. The 300 development questions occupy 250 source links.
Of the remaining 600, 176 share a development source and are excluded from the final test.
The reserved 424 questions occupy 238 other source links. Source links are a conservative
grouping unit; this is not proof that cross-source near-duplicates or pretraining contamination
are absent. Training and calibration pools remain unselected and must be audited against
these sources and their translations/near-duplicates before use.

Reproduce with the pinned dataset available in the evaluation environment:

```sh
python scripts/reserve_holdout.py --lock /path/to/sample-lock.json --output /new/path/holdout.json
```

The command refuses to overwrite an existing reservation. The committed reservation was
generated from the cached pinned revision in offline mode; no model or scoring request ran.

## Access and analysis gate

All rotations, scoring selection, sensitivity mapping, calibration, allocation and repair
selection use development or separately audited calibration/training data. Final test
membership must not be used to choose examples or targets for those activities.

Before opening final answers or scoring this set, freeze finalist model/runtime hashes,
scoring contract, byte budget/tolerance, baseline arms, primary paired comparisons, and
retention bounds in a PR. Evaluate the frozen finalists and controls once. Report every
result, including failures; do not retune after viewing results. Any later tuning makes
this set development and requires a newly reserved test set.

Report uncertainty by resampling whole source links and keeping translated questions and
model comparisons paired. Do not treat the 424 questions or their translations as independent
observations. This protocol does not choose the numerical retention/effect thresholds;
those must be preregistered before candidate selection.
