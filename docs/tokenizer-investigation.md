# Pilot gate: Tiny Aya digit pre-tokenization

No pilot accuracy run was performed. The prepared seed-42 selection contains 300
aligned items per language; the first 50 are the pilot. All fit below 8192 tokens.
Selection is development material, not the reserved final test pool.

## Verified mismatch

Both verified GGUF artifacts match the original tokenizer on 580/600 candidate
requests. Five of 150 contexts differ: Bangla item 184 and English items 28, 533,
846 and 36. Hindi contexts all match. Candidate sequences differ on all four
choices for each affected context. Audit JSON files preserve indices and slices.

Minimal input: two ASCII spaces followed by `46`.

| Tokenizer | IDs including BOS |
| --- | --- |
| Original Hugging Face | `[2, 271, 3621]` |
| Native pinned llama.cpp | `[2, 235, 235, 3621]` |
| Pinned llama-cpp-python | `[2, 235, 235, 3621]` |

Native revision: `797de63b2fa7396dcc8caca76834c699ac84e1c3`.
Python package revision: `1652066e0af45f2313b339670ef9555e8a54e545`, bundled
llama.cpp `0c1e57098bba43ac29e6e3b677cdceebdd22334f`.
The BF16 GGUF reproduces the mismatch, ruling out weight rounding as its cause.
The older native build reproduces it, so adding the Python package did not introduce it.

## First divergent operation

The original tokenizer first isolates digit matches. For this input its first
split separates the two spaces from `46`. llama.cpp routes Tiny Aya's digit regex
to `unicode_regex_split_custom_afmoe` in `src/unicode.cpp`. That function advances
past non-digits without emitting the pending prefix before emitting the first
digit group. It therefore returns one segment containing both spaces and `46`.
The later whitespace regex then splits the spaces differently.

`tests/tiny_aya_digit_split.cpp` calls that existing upstream splitter directly.
Compiled against the pinned bundled `unicode.cpp` and `unicode-data.cpp`, it
prints one segment, `"  46"`. This test requires no GGUF or model weights and
locates this reproduction in the runtime implementation, not artifact metadata.
It does not establish that all five mismatches have only this cause.

## Fixed-weight diagnostic

`probe_tokenization_impact.py` evaluates original and GGUF token sequences using
the same BF16 GGUF, runtime, candidate token IDs and context limit. This is direct
logit inspection, not an adapter or a replacement benchmark scoring path.

All five selected answers remained unchanged. Largest absolute candidate
log-probability shifts were 0.35690 for the Bangla item and 0.30523 across English
items. These are natural-log units, not accuracy percentage points. No general
quality claim follows from five examples. Raw valid results are committed.

An initial diagnostic attempted to read the public scores buffer with
`logits_all=False`, which did not populate that buffer and yielded uniform values.
That attempt is invalid and excluded. The corrected run enables logits storage
and asserts finite, nonconstant logits before using them.

## Upstream context and recommended next change

- [Tiny Aya support](https://github.com/ggml-org/llama.cpp/pull/19611) introduced
  its custom digit-grouping pre-tokenizer.
- [Older Command-R mismatch](https://github.com/ggml-org/llama.cpp/issues/6104)
  concerns different whitespace behavior and was closed as stale. It is related
  precedent, not confirmation that this Tiny Aya issue is already tracked.
- No exact matching issue was found in the searches performed. That is not proof
  that none exists.

Recommend a dedicated Tiny Aya digit splitter matching the original regex's
isolated-match semantics, decimal-digit class and word-boundary condition. Merely
changing the shared AFMoE routine risks other tokenizers and does not address all
regex semantics. A follow-up upstream patch needs regression cases for spaces,
punctuation, letter-adjacent numbers, Unicode digits and groups of varying length,
then full pilot token parity. No runtime patch, adapter, text normalization or
sample exclusion has been applied. Pilot scoring remains gated.

## Reproduction

Run `prepare_pilot.py` in the existing eval environment with `--tokenizer`,
`--tokenizer-python` pointing to the existing converter Python, and fresh `--output`.
This keeps the isolated dependency environments separate. The compact committed
selection manifest records indices, source IDs, prompt/candidate hashes and labels;
the full local lock additionally contains rendered prompts and token IDs.
Run `check_pilot_tokens.py` in the Python GGUF environment with that `--lock`, each
`--model`, and a fresh `--output`; expected result is a failing gate with five contexts.
Run `probe_tokenization_impact.py` with `--lock`, `--audit`, BF16 `--model`, and fresh
`--output` in the same environment. No new packages are required.

Compile the C++ reproduction using the upstream source directory as an include
path and compile its `unicode.cpp` and `unicode-data.cpp` alongside the test.
No changes to upstream source are necessary to reproduce the failure.
