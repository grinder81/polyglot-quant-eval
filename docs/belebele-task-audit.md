# Belebele preparation: pinned data and task definitions

Downloaded the English (`eng_Latn`), Bangla (`ben_Beng`) and Hindi (`hin_Deva`)
test subsets from dataset revision `7899cdfa4e1e0d733fd77c848e2c273cb1d32be2`.
Each contains 900 rows. All answer labels were checked to be 1 through 4.
No model scoring was performed. The datasets are cached outside the repository.

`results/stage1/belebele-task-audit.json` captures installed lm-eval task YAML,
file hashes, package versions, row counts and ordered content hashes. Content
hashes use sorted compact UTF-8 JSON plus a newline per row; dates are ISO strings.
Reproduce in the isolated eval environment:

```bash
python scripts/audit_belebele.py --output /absolute/path/to/new-audit.json
```

## Exact upstream scoring contract

The installed task presents the passage, question and all four answer texts,
then ends with `Answer:`. Its candidates are the letters A, B, C and D, not the
full answer texts. The correct label is mapped from 1–4 to a zero-based index.
Stage 1 selects upstream `acc`, not `acc_norm`, with zero demonstrations and no
chat template. Tokenization and candidate-prefix whitespace must be audited in
the actual request adapter before scores are compared.

The upstream YAML names the test split as its few-shot split. We use zero-shot;
do not change that count and inadvertently draw demonstrations from evaluated data.
Repeatedly inspected Stage 1 examples are development/baseline material, not the
reserved final test pool.

## Gates still open

The existing `scripts/smoke_test.sh` is a legacy unvalidated launcher. It applies
a chat template and does not pin this dataset revision or sample IDs. Do not use
it for canonical Stage 1 measurements. This audit deliberately does not turn it
into an executable benchmark before the request/scoring path is verified.

Next: lock aligned item/source-document IDs and rendered prompt/candidate hashes,
check HF versus GGUF token IDs and candidate boundaries, and validate continuation
loglikelihoods on each endpoint. The 300-item baseline/50-item smoke selection is
not yet made. Do not equate download success with tokenizer or scoring parity.

This is partial progress on issue #3. Global-MMLU and MGSM remain unaudited.
