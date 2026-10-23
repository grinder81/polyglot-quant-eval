# T1 offline readiness — 2026-10-23

No new model probabilities, generation, server calls or GPU inference were run.
The collection directory has not been created. Live expanded validation and
collection still require the agreed explicit go-ahead.

The original 300-question-per-language development membership passes exact
prompt/candidate byte and model-ID reproduction with the current pinned HF
tokenizer: 900 contexts and 3,600 candidates. Every letter continuation is exactly
one token. The first 100 original-order items per language match A3 plain-letter/r0
by index, source/question, target, bytes and model/wire token IDs.

The new 12,818,649-byte lock is retained locally rather than duplicated here.
Its SHA-256 is `27d4164a13c62c61ac43ceecbcb684f5a58c541320e9ce12bceddc2a395f9e04`.
The retained path and all compact artifact hashes are in `offline-evidence.json`.
`preparation-v2.json` binds the original lock, preparer/helper sources and tokenizer.
Both `*-token-check-v3.json` files pass 900 contexts and 3,600 candidates under the
exact model, native library and wrapper identities in the A3 v4 runtime manifests.

The longest full model inputs are English 325, Bangla 475 and Hindi 462 tokens,
all at original index 188. These are shorter than the A3 gate's observed maximum
717, but that is not a universal correctness guarantee. Compared with each
language's actual A3 48-context gate subset (all variants), the 900 T1 requests
contain 6,895 / 2,709 / 3,882 additional distinct model token IDs and 280 / 179 /
192 additional distinct four-token context suffixes, respectively. These are
coverage counts, not evidence of incorrect scoring or guarantees from a bounded
gate. `offline-evidence.json` retains these counts and the planned 12-row selection.
The live plan checks index 0, 100, 188 (longest), and 299 per language, all four
candidates, plus the complete reverse order. None of those live checks has run.

Actual `--validate-only` passes for both arms without HTTP or creating score
directories. It checks both complete A3 arms, cold/order evidence and current
model/runtime/client/source/tokenizer identities. Each proposed arm contains zero
of 180 T1 shards; no legacy scores are relabeled as fresh T1 results.
The unchanged upstream ConfigurableTask passes an offline exact-request and
acc/acc_norm smoke check in the pinned isolated client environment.

The first BF16 vocabulary attempt used `LD_LIBRARY_PATH`, which did not override
the wrapper's packaged native library. Its 75 token-ID failures are preserved in
`bf16-token-check.json` and are **not** a passed readiness artifact. The checker
now requires a runtime manifest and validates the actually loaded native library,
wrapper and model before tokenization. `LLAMA_CPP_LIB_PATH` selects the correct
pinned native library; both final v3 checks pass. The provisional v1 lock and
earlier pinned BF16 v2 token check remain in the local readiness directory.

Validation: 74 tests and 82 subtests pass, including a complete 360-shard synthetic
report integration, wrong request/target/metric/score/identity rejection, all
present shards checked despite earlier gaps, strict overlap intersection,
prediction inversion preservation, Python `-O` rejection, and raw expanded-gate
tampering rejection. Future A3 overlap uses a maximum absolute single-token error
of 0.0002 nats **and** a separate summed limit of 0.001 nats, with no tolerance
relaxation. Any prediction inversion stops for review.

The runtime validator/protocol lives in the separate reviewed runtime repository;
its source hash is pinned in future expanded-gate artifacts. Readiness does not
claim those gates pass, freeze a publication result, or authorize any launch.
