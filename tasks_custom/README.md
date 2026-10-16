# Custom tasks

The upstream harness has no FLORES-200 and no Language Confusion task, so these live here.
Both are generation tasks driven through the same OpenAI-compatible endpoint.

- `flores.py`: FLORES-200 devtest, xx->en and en->xx, 0-shot chat prompt, chrF++ and
  spBLEU via sacrebleu. Dataset candidates: `openlanguagedata/flores_plus` (gated, CC-BY-SA)
  or `facebook/flores`. 14 languages from `configs/languages.yaml`.
- `language_confusion.py`: Cohere's Language Confusion Benchmark
  (github.com/for-ai/language-confusion). Monolingual and cross-lingual prompts; line-level
  pass rate via fastText language id, as in Marchisio et al.
- `executorch_shim.py`: a minimal OpenAI-compatible chat server over an ExecuTorch
  `.pte` so the same harness runs against the on-device format on desktop.
- `judge.py`: pairwise BF16 vs quantized, randomized order, 150 Aya Dolly-200 prompts
  per language; LLM judge served locally plus RM-as-judge.
