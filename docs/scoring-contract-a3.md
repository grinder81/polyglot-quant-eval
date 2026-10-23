# A3 canonical scoring decision

On 22 October 2026, after reviewing the complete A3 results, the user selected:
**“Retain plain-letter summed likelihood on fresh cold-runtime baselines.”**
This closes A3's diagnostic and canonical-contract decision. It records the
selected contract; it does not claim new baseline collection or authorize a B5
run. Evidence: [results PR38](https://github.com/grinder81/polyglot-quant-eval/pull/38),
[A3 results](../results/a3-scoring-variants/README.md),
[frozen variant specification](scoring-variant-control.md), and
[runtime PR36](https://github.com/grinder81/tiny-aya-edge/pull/36).

## Selected task and prediction

- Use the unchanged upstream Belebele plain prompt, without a chat template,
  system preamble or assistant prefix. Its schematic form is `P: <passage>`,
  `Q: <question>`, four displayed `A: ...` through `D: ...` lines, and final
  `Answer:`, separated by the exact upstream newlines. The frozen source/task
  identities and request bytes are authoritative; preserve all Unicode,
  punctuation and existing whitespace rather than reconstructing or correcting
  text from this schematic.
- Continuations, in displayed order, are exactly ` A`, ` B`, ` C`, ` D`: one
  ASCII-space delimiter followed by one ASCII letter. Append no newline or EOS.
  Use the unchanged upstream `ConfigurableTask`, `LocalCompletionsAPI` and scorer.
- The supported client uses explicit HF tokenization and non-tokenized string
  requests: `tokenized_requests=False`, `add_bos_token=False`. The server supplies
  exactly one BOS; verify complete IDs and the context/continuation boundary
  against the pinned tokenizer. Do not add a literal BOS to the plain wire text
  or strip/add special tokens to force agreement. Score only continuation tokens,
  excluding the context, BOS and generated echo suffix.
- Select the highest **summed** continuation log probability. An exact tie selects
  the first displayed candidate in A/B/C/D order. Character-normalized `acc_norm`
  remains separately labeled; for these one-character letters its prediction is
  identical to raw scoring. It does not select option-text or chat scoring.
- Preserve official targets and source/question joins. For cyclic rotation `s`,
  displayed position `p` maps to original content `(p + s) % 4`; the displayed
  gold index is `(original_target - s) % 4`. A3 uses all four rotations as a
  diagnostic. Keep original-order accuracy and rotation-average accuracy separately
  named; do not silently replace the baseline's original-order endpoint with
  pooled rotations. Each downstream run must record its membership and rotation
  protocol in its fresh identity.

## Selected runtime identity

Use the isolated, validated v4 cold-prefill runtime for affected GGUF comparisons.
Echoed likelihood requests must bypass prefix reuse/saved-cache restoration as
validated; retain the equivalent top-one echo ranking optimization. Use matching
settings across BF16 GGUF and local Q4 except the model artifact: server context
8,192, all logits enabled, GPU layers −1; client maximum length 8,192 and batch
size 1. Pin model/native/wrapper/tokenizer/client sources and versions, served
model identity, and direct-probability plus reversed-order validation artifacts
in each run manifest. The complete authority is the archived arm identities and
[execution record](../results/a3-scoring-variants/execution-record.json).

| Identity | Pin |
|---|---|
| Evaluation execution source | `e1712e2aa5fbaf65012fcf7684bff20a3eb8bc3f` |
| Runtime source | `8d3a4a84f357f656bf3bd9bbddbca7706a6b065e` |
| BF16 v4 runtime manifest SHA-256 | `f405c7da19b898e943d0dfba89465d39c9f04b940fca54c1a2ecb211da38429f` |
| Local-Q4 v4 runtime manifest SHA-256 | `ba55c25a5d962a7cf1286c8d151265ebb4ae972c0e970f8c85dc491ab56f013f` |
| Cold-prefill patch SHA-256 | `4f2f0a7028e8c1965b62ce6ca00170d76625da9e10295835546ed9a79ebc5c88` |
| Additional echo-ranking patch SHA-256 | `e2a4b8405cdd20aa657a939ecb582ea5128619b94420c37aed7f222b2bfe3a70` |
| Native library SHA-256 | `82eb4435a7e680be716b44c2964fbf7da3649194dfe8563d2e8701717417535e` |
| A3 request-lock SHA-256 | `75486c22c0c25f7c6c9d3da6abfaaa0165babf4a5de24970147ab9d1488d9844` |

The isolated client pins lm-eval 0.4.13, Transformers 5.20.1, tokenizers 0.23.3
and datasets 5.1.0. Original offline rendering used Transformers 4.57.6; do not
silently relabel that rendering environment. Exact tokenizer hashes, model hashes,
client source hashes and gate identities remain in the archived arm identities.

Effective server EOS was 6 although an older conversion manifest required 3.
These candidate continuations append no EOS. This likelihood decision does not
settle generation EOS settings or establish generation/device performance.

## Consequences and remaining gates

Fresh affected downstream comparator arms, including BF16 GGUF and local Q4,
**are required under new cold-runtime identities before compression comparisons**.
Use the matched downstream development membership and intended rotation protocol;
when a full 300-question-per-language reference is used, collect those affected
full comparator runs afresh. The existing A3 cold arms cover only 100 development
questions per language and are diagnostics, not silently completed 300-question
baseline reruns. No fresh full baseline is claimed by this decision record.

Keep historical A1/A2 numbers, files and runtime identities unchanged. Their
legacy numerical bridge is not universal parity. This GGUF scoring decision
does not replace the canonical original BF16 **vLLM** reference or merge it with
llama.cpp BF16 evidence.

The canonical-contract gate is resolved. A4 still requires human Bangla negation
labels before confirmatory grouping; B5 retains its remaining prerequisites and
fresh comparator requirements under the approved [Stage 2 plan](stage2-plan.md).
Protect the reserved holdout and do not tune or score it during this baseline
work. Chat-letter and option-text remain named development diagnostics. No new
inference, sweep, holdout evaluation or generation result occurred as part of
recording this decision.

## Subsequent evidence: 23 October 2026

The affected full comparator collection is now recorded separately in [fresh T1 results](../results/t1-cold-baselines/README.md): 300 original-order development questions per language in each new BF16 GGUF/local-Q4 arm. This link does not rewrite the 22 October decision or historical runtime/result identities; A4 and later B5 gates remain.
