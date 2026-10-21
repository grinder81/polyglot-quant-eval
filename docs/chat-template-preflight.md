# A3 chat-template prerequisites

This is an offline prerequisite investigation for issue 18, while A2 runs.
It is not an A3 accuracy result, a scoring adapter, or a canonical contract change.

The pinned lm-eval 0.4.13 `GGUFLM` inherits `LM.apply_chat_template`, which raises
`NotImplementedError`. Enabling that flag alone cannot implement the chat arm.
Upstream `ConfigurableTask` can consume pre-rendered context and choice fields;
that route still needs a reviewed diagnostic configuration and boundary validation.

The original tokenizer's named `default` template adds a literal BOS, its system
preamble, turn delimiters, and an assistant `START_RESPONSE` prefix. Replacing it
with a generic template would test a different prompt. Rendering with the original
tokenizer and then encoding with automatic special tokens duplicates BOS in the
three examples tested. The completion server also inserts BOS for string inputs.

`scripts/probe_chat_echo_boundaries.py` records an offline reproduction on the
first locked development question in each language. It loads only the vocabulary,
uses the original tokenizer in a subprocess, and never accesses the running server.
The saved evidence is `docs/chat-echo-boundary-probe.json`, with input, model,
native library, wrapper, tokenizer and probe hashes.

After removing just the leading literal BOS for the server's automatic insertion,
the reconstructed GGUF input IDs match the original tokenizer in all three cases.
However, the wrapper's default detokenization omits special-token strings. Its
echoed character-boundary calculation therefore differs from the supplied text:

| Language | Context characters, excluding literal BOS | Default echoed boundary | With special-token text retained |
|---|---:|---:|---:|
| English | 2528 | 2352 | 2528 |
| Bangla | 2505 | 2329 | 2505 |
| Hindi | 2559 | 2383 | 2559 |

These are three translations of one source question, not a broad sample. The
176-character difference is reproduced by the current wrapper's offset formula;
no live chat likelihood request was made. `detokenize(..., special=True)` restores
the exact text in these examples, but that alone does not establish a complete
endpoint fix. Token strings, BOS exclusion, UTF-8 boundaries, per-token offsets
and likelihood indexing must all remain consistent.

Reproduce using the pinned Python wrapper and `LLAMA_CPP_LIB_PATH` from the runtime
manifest:

```text
python scripts/probe_chat_echo_boundaries.py --lock SAMPLE_LOCK.json \
  --tokenizer ORIGINAL_TOKENIZER_DIRECTORY --tokenizer-python TOKENIZER_PYTHON \
  --model LOCAL_Q4.gguf --output NEW_REPORT.json
```

The probe never overwrites its output. The vocabulary-only context warning is not
an inference failure; no model inference is performed.

Before A3 scoring:

1. Finish A2 with its existing runtime and preserve its manifest.
2. Validate a supported upstream prompt/scorer path, or a separately tested runtime
   correctness fix, without changing the scorer. Any custom adapter still requires
   user approval. Do not patch the active A2 environment.
3. Freeze the exact chat template/hash, BOS treatment, continuation delimiter,
   option-text normalization, and all rotation membership in a small PR. Upstream
   `acc_norm` divides by choice character count, not token count; do not mislabel it.
4. Verify every diagnostic token sequence and boundary, then compare actual echoed
   continuation probabilities with direct logits before collecting accuracy.
5. Report all diagnostic variants. User review selects the canonical contract
   before the sweep; changed settings require new baseline run identities.

No claim here changes the completed plain-prompt baselines or active A2 run.
