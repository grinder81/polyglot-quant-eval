# C8 bounded language-sensitivity pilot: G4 outcome

The [frozen design](../../../docs/c8-bounded-pilot.md) (Git blob `cd43458f…`) and the [mechanically derived execution plan](../c8-plan.json) (SHA-256 `e7ccdb50…`) were completed on 7 November 2026 after the [host-storage interruption](https://github.com/grinder81/tiny-aya-edge/tree/codex/article2-pilot/reports/article2-pilot/storage-incident) of 1 November was recovered under its gate. The [decision record](decision.json) rebuilt by `scripts/report_c8_pilot.py` from the original evidence reports the condition **inconclusive**: all four prespecified equal-byte pairs were byte-feasible, every budget and evidence gate passed, and the frozen nomination rule found **no pair** whose Bangla and English preference directions were opposite in both discovery repetitions. No complete-map confirmation was therefore exported or measured. Inconclusive is the design's word for this outcome; it does not establish language equivalence, and it is not a task or generation result.

## What was measured

Sixteen degrade-one diagnostics (eight fixed tensors × native Q2_K and Q3_K, every other tensor at BF16, no importance matrix; manifests committed in the [runtime repository](https://github.com/grinder81/tiny-aya-edge/tree/codex/article2-pilot/reports/article2-pilot/c8-diagnostics) before any probe) were scored against the BF16 control with mean per-token KL(BF16 ‖ diagnostic) over 64 content tokens, in the pinned native runtime, on three frozen TED2020 probe talks per repetition in English, Bangla and Hindi (nine examples per repetition per diagnostic; 27 in all). Sequence-Fisher and activation proxies were computed on the disjoint construction talks of each repetition. Repetitions 1–2 are discovery; the [nomination](discovery-nomination.json) was written and committed (`c713006`) before repetition 3, whose reports are bound to its hash.

| Evidence | Report | SHA-256 |
| --- | --- | --- |
| Native BF16 reference, repetitions 1–2 | [native-reference-discovery-report.json](native-reference-discovery-report.json) | `b101422073e4…` |
| Native diagnostics, repetitions 1–2 | [native-discovery-report.json](native-discovery-report.json) | `744eb2731086…` |
| Proxies, repetitions 1–2 | [proxy-discovery-report.json](proxy-discovery-report.json) | `224aea68b3c8…` |
| Frozen nomination (none) | [discovery-nomination.json](discovery-nomination.json) | `74797adb60f9…` |
| Native BF16 reference, repetition 3 | [native-reference-confirmation-report.json](native-reference-confirmation-report.json) | `2cf79e3b6d62…` |
| Native diagnostics, repetition 3 | [native-confirmation-diagnostics-report.json](native-confirmation-diagnostics-report.json) | `2c7fd88c93d2…` |
| Proxies, repetition 3 | [proxy-confirmation-report.json](proxy-confirmation-report.json) | `9aa61b0a2b4b…` |
| Budget ledger as closed | [resource-ledger.json](resource-ledger.json) | `8e2fcb8652ac…` |

Each committed report is the byte-identical file the measurement wrote in the workspace; the decision record carries the same hashes. Raw logits, quantization-error arrays and weights stay outside Git.

## Discovery margins and the nomination

For a pair, a language's margin is the KL saved by raising the first tensor from Q2_K to Q3_K minus the KL saved by raising the second; a positive margin prefers higher precision on the first tensor. A pair is nominatable only when Bangla and English have opposite signs in both repetitions, each language keeps its sign, and every absolute margin exceeds 1e-5 nats per token.

| Pair (first / second) | Rep | English | Bangla | Hindi | Pooled | Nominatable |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `blk.0.attn_v.weight` / `blk.3.attn_v.weight` | 1 | +0.001569 | +0.038339 | +0.001246 | +0.003262 | No: same BN/EN sign |
|  | 2 | +0.003757 | +0.004680 | +0.001990 | +0.007062 |  |
| `blk.0.ffn_down.weight` / `blk.17.ffn_down.weight` | 1 | +0.082594 | +0.103535 | +0.066984 | +0.077391 | No: same BN/EN sign |
|  | 2 | +0.092402 | +0.123616 | +0.122517 | +0.125247 |  |
| `blk.17.ffn_down.weight` / `blk.35.ffn_down.weight` | 1 | −0.033696 | −0.032708 | −0.023820 | −0.030487 | No: same BN/EN sign |
|  | 2 | −0.038939 | −0.036671 | −0.021561 | −0.029032 |  |
| `blk.17.ffn_gate.weight` / `blk.17.ffn_up.weight` | 1 | −0.001501 | −0.000981 | −0.000683 | −0.001028 | No: same BN/EN sign |
|  | 2 | −0.000581 | −0.001054 | −0.000969 | −0.000743 |  |

Every margin is stable in sign across the two repetitions and above the epsilon, so the screen did produce reproducible preferences; they are the same preferences in both languages. All three languages prefer the extra precision on block 0 over block 3 for attention V, on block 0 over block 17 and on block 35 over block 17 for MLP down, and on the up projection over the gate at block 17. Language differences appear in magnitude, not direction: Bangla's attention-V margin is 24× English's in repetition 1 and 1.2× in repetition 2, which is also the least stable margin in the table. An equal-byte swap between the two tensors of a pair cannot exploit a magnitude difference, which is why the rule records none.

## Measured degrade-one costs

Mean per-token KL(BF16 ‖ diagnostic) in nats per content token, mean of the three repetitions with the repetition range; 64 content tokens × 3 sources per repetition and language.

| Tensor :: format | English | Bangla | Hindi |
| --- | ---: | ---: | ---: |
| `token_embd.weight::Q2_K` | 0.3874 (0.3813–0.3951) | 0.2749 (0.2482–0.3192) | 0.2273 (0.2234–0.2299) |
| `token_embd.weight::Q3_K` | 0.1050 (0.1010–0.1129) | 0.0769 (0.0740–0.0817) | 0.0626 (0.0568–0.0722) |
| `blk.0.attn_v.weight::Q2_K` | 0.0056 (0.0045–0.0067) | 0.0323 (0.0129–0.0705) | 0.0073 (0.0062–0.0087) |
| `blk.0.attn_v.weight::Q3_K` | 0.0015 (0.0014–0.0016) | 0.0039 (0.0030–0.0056) | 0.0024 (0.0015–0.0035) |
| `blk.3.attn_v.weight::Q2_K` | 0.0019 (0.0018–0.0019) | 0.0130 (0.0038–0.0308) | 0.0037 (0.0032–0.0042) |
| `blk.3.attn_v.weight::Q3_K` | 0.0004 (0.0003–0.0005) | 0.0009 (0.0005–0.0017) | 0.0005 (0.0005–0.0006) |
| `blk.0.ffn_down.weight::Q2_K` | 0.0954 (0.0839–0.1056) | 0.1201 (0.1014–0.1388) | 0.1058 (0.0812–0.1377) |
| `blk.0.ffn_down.weight::Q3_K` | 0.0115 (0.0112–0.0119) | 0.0141 (0.0137–0.0147) | 0.0126 (0.0115–0.0138) |
| `blk.17.ffn_down.weight::Q2_K` | 0.0030 (0.0025–0.0034) | 0.0021 (0.0017–0.0026) | 0.0022 (0.0019–0.0025) |
| `blk.17.ffn_down.weight::Q3_K` | 0.0008 (0.0008–0.0008) | 0.0006 (0.0005–0.0007) | 0.0006 (0.0006–0.0006) |
| `blk.35.ffn_down.weight::Q2_K` | 0.0470 (0.0455–0.0493) | 0.0472 (0.0455–0.0493) | 0.0332 (0.0310–0.0349) |
| `blk.35.ffn_down.weight::Q3_K` | 0.0102 (0.0086–0.0115) | 0.0112 (0.0108–0.0114) | 0.0081 (0.0080–0.0081) |
| `blk.17.ffn_gate.weight::Q2_K` | 0.0020 (0.0019–0.0021) | 0.0013 (0.0010–0.0017) | 0.0014 (0.0012–0.0016) |
| `blk.17.ffn_gate.weight::Q3_K` | 0.0005 (0.0005–0.0005) | 0.0005 (0.0003–0.0009) | 0.0004 (0.0003–0.0005) |
| `blk.17.ffn_up.weight::Q2_K` | 0.0033 (0.0028–0.0036) | 0.0024 (0.0022–0.0026) | 0.0025 (0.0023–0.0026) |
| `blk.17.ffn_up.weight::Q3_K` | 0.0008 (0.0008–0.0008) | 0.0006 (0.0005–0.0007) | 0.0006 (0.0005–0.0007) |

Descriptively, the tied embedding dominates every language's cost by an order of magnitude, and it is the one tensor where English pays more than Bangla or Hindi. Bangla is the most sensitive language to degrading the attention-V tensors of blocks 0 and 3, with the widest repetition ranges in the table, and to the MLP down projections of blocks 0 and 35; for the three block-17 MLP matrices Bangla and Hindi cost less than English. These are three short source samples per repetition; they are not language-effect tests, and they say nothing about task accuracy.

## Proxy agreement

Spearman rank correlation between each proxy and the measured native KL across tensor-formats, for repetitions 1, 2 and 3:

| Language | Subset | Fisher proxy | Activation proxy |
| --- | --- | --- | --- |
| English | all 16 | +0.99, +0.99, +0.99 | +0.66, +0.69, +0.69 |
| English | Q2_K (8) | +1.00, +0.98, +0.98 | +0.60, +0.67, +0.64 |
| English | Q3_K (8) | +0.95, +0.98, +1.00 | +0.43, +0.48, +0.50 |
| Bangla | all 16 | +0.96, +0.99, +0.99 | +0.48, +0.55, +0.55 |
| Bangla | Q2_K (8) | +0.95, +1.00, +1.00 | +0.36, +0.52, +0.52 |
| Bangla | Q3_K (8) | +0.79, +0.98, +0.93 | +0.38, +0.33, +0.29 |
| Hindi | all 16 | +0.98, +0.97, +0.98 | +0.64, +0.56, +0.63 |
| Hindi | Q2_K (8) | +1.00, +1.00, +1.00 | +0.52, +0.52, +0.52 |
| Hindi | Q3_K (8) | +0.95, +0.93, +0.95 | +0.36, +0.33, +0.38 |
| Pooled | all 16 | +0.97, +0.97, +0.98 | +0.66, +0.54, +0.59 |
| Pooled | Q2_K (8) | +0.98, +1.00, +1.00 | +0.57, +0.52, +0.52 |
| Pooled | Q3_K (8) | +0.95, +0.95, +0.95 | +0.48, +0.38, +0.33 |

The sequence-Fisher proxy ranks the sixteen tensor-formats almost exactly as the measured KL does in every language; the activation proxy is markedly weaker, especially within the Q3_K subset. Repeat ranges are descriptive, the proxies are uncalibrated in magnitude ([raw score ranges](decision.json) are in the record), and this pilot cannot authorize replacing measured KL with a proxy.

## Resources and gates

- Native builds and probes: 1,996 s of the 5,400 s cap (37 %), 20 passed rows plus the one interrupted export row closed as failed through the recorded recovery receipt (31.38 s retained).
- Proxies: 767 s of the 1,800 s cap (43 %), two passed rows.
- Artifacts: largest recorded footprint 112.5 GB of the 400 GB cap. The host-storage guard observed at least 351 GB free on the backing Windows volume across its 13 guarded operations.
- Every report was accepted by `scripts/validate_c8_reports.py`: passed final budget checks, identity-to-case linkage, frozen source coverage, 64-token KL arrays consistent with their means, and reference lineage.

## Reading for G4

Of the three prespecified conditions, **inconclusive** occurred: the screen was affordable and valid, and the pairs were feasible, but no pair showed reproducible opposite Bangla/English preferences. On this fixed subset and these samples, language information would not have changed the direction of an equal-byte precision choice; it changes how much each choice costs, with Bangla more sensitive at early attention V. Whether that magnitude signal justifies a larger study, a different allocation design (for example byte-unequal or channel-level rebalancing, which the design names as the separate alternative), or stopping here is the owner's investment decision. Final allocation claims would still require C9/C10 task comparisons, independent review and the once-only frozen confirmation; the holdout and A4-conditioned slices remain sealed.
