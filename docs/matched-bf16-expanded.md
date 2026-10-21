# Matched BF16 reference at 300 questions per language

This run closes Stage 2 A1 against the completed local-Q4 300-per-language run.
It uses the same current patched GGUF runtime, frozen sample lock and unchanged
upstream Belebele letter-likelihood scoring. It does not reuse the older 50-item
BF16 results as if they came from this runtime. Only BF16 GGUF runs in this task.

```sh
python scripts/run_three_arms.py --root /path/to/stage1 --output /new/bf16-three-hundred \
  --bf16-gguf-only --start 0 --count 300
```

Before scoring, all 900 contexts and 3600 candidate sequences passed token-ID and
roundtrip validation. Live manifests agree with the local-Q4 run on runtime files,
packages, server settings, scoring runner and sample lock, excluding the model
artifact and arm name. The original preflight and manifests accompany final results.
All 180 five-question shards now validate. Results and the paired comparison are
in `results/stage2/bf16-three-hundred/README.md`.

## Report contract

`summarize_expanded_local.py --arm bf16-gguf` validates all 900 source/question
identities, prompt and continuation hashes, finite likelihoods, answer keys and
recomputed accuracies. Raw harness document IDs are retained but not used to join
results (issue 16). A compact projection of the original lock must accompany the
evidence, with its original byte hash verified before copying.

`compare_expanded.py` rejects unequal runtime or scoring identities, then joins
BF16 and Q4 by language/source/question. Report absolute accuracy, Q4 minus BF16
accuracy, changed choices, right-to-wrong, wrong-to-right and wrong-to-wrong counts,
and predicted/gold letter histograms. Letter frequency is diagnostic, not evidence
of a causal position bias without the planned rotation control.

For uncertainty, jointly resample source passages 10,000 times with seed 42. Keep
all questions in each sampled source and the same source draws across languages
and arms. Report percentile 95% intervals on the paired accuracy delta and on
each language's delta minus English's delta. Also report each arm's accuracy gap
to English. These intervals describe development-sample uncertainty conditional
on this instrument; they do not establish equivalence, rule out contamination,
or identify a particular model component. No practical-equivalence threshold is
introduced retrospectively here.

```sh
python scripts/compare_expanded.py --reference /path/to/bf16-evidence \
  --candidate /path/to/local-q4-evidence --output /new/comparison.json
```

The output path must be new. Keep raw evidence and original model/runtime hashes.
Do not interpret results until full validation succeeds. Generation quality and
device speed/memory remain separate tasks.
