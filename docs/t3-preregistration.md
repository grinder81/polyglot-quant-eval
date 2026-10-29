# T3 preregistration: staged precision curve for Tiny Aya Global

Status: **draft for review, not yet frozen.** This document becomes binding when it is committed on `main` with its hash recorded in `LOG.md`, before any T3 build is quantized or scored. It carries the decisions the user ratified on 26 October 2026 and the governing [Stage 2 plan](stage2-plan.md), including its 26 October sequencing amendment. It authorizes no inference: collection starts only after the per-build readiness gates below pass review and the user confirms collection separately, as for T1. Items marked **confirm at review** are defaults the user may change before freezing; everything else is settled.

## 1. Purpose and what T3 is not

T3 measures how Belebele development accuracy, answer churn and candidate-score margins change across llama.cpp precision points for `CohereLabs/tiny-aya-global`, per language, against the fresh BF16 GGUF control and the local Q4_K_M point already collected in [T1](../results/t1-cold-baselines/README.md). Its outputs are development evidence: the per-language curve, the preregistered predictions in §7, and the operating point selected by the rule in §8 for the later allocation work (C8–C10).

T3 is not the allocation test. It makes no claim that language-aware allocation helps or fails, no equivalence or harmlessness claim, no generation, device or holdout claim. The reserved holdout is not scored. Historical A1/A2/A3 results and the canonical BF16 vLLM reference keep their identities.

## 2. Fixed inputs

| Item | Pin |
|---|---|
| Model | `CohereLabs/tiny-aya-global`, revision `af89d219b53ed9b13b8a4645f9c8028973510324` |
| BF16 GGUF control (source of every build) | SHA-256 `0e2f666ac8fb50a7f53d14164147beeca35905b76b93eb90e0e3a963eb203b4b`, 6,710,484,480 bytes |
| Local Q4_K_M (existing point, not rebuilt) | SHA-256 `5823bd1e52be1027a7ba6f31b43edfd40ae1766020cddec967f0d76618948290`, 2,143,976,960 bytes; 216 Q4_K, 37 Q6_K, 37 F32 tensors ([inventory](https://github.com/grinder81/tiny-aya-edge/blob/8a0d922ef40f86ba3ea11e0b4a2656d25d4bcea4/reports/control-tensor-inventory.md)) |
| Quantizer | llama.cpp `797de63b2fa7396dcc8caca76834c699ac84e1c3`, `llama-quantize` binary SHA-256 `6a2c2efac5f38ebe2c1994befd0dee745cb24ec5c33d6a2c5a50fb8b9fe1e5f0`, invoked as for the local Q4_K_M: `llama-quantize <control> <output> <TYPE> 8`, no importance matrix, no requantization ([Q4_K_M build manifest](https://github.com/grinder81/tiny-aya-edge/blob/8a0d922ef40f86ba3ea11e0b4a2656d25d4bcea4/reports/local-q4-control/manifest.json)) |
| Request lock | The T1 original-order lock, SHA-256 `6dfdd304dcba7bd772c37a7634e74c0c16d1e4b70728be6dcb0e218f3847aa19`: the same 900 requests, targets and ` A`/` B`/` C`/` D` candidates as T1, unchanged |
| Scoring contract | [Accepted A3 contract](scoring-contract-a3.md): plain upstream prompt, summed continuation likelihood, first displayed maximum on an exact tie, one automatic BOS, no appended EOS, original order only |
| Runtime | The validated v4 cold-prefill runtime and settings of T1 (server context 8,192, all logits, GPU layers −1; client lm-eval 0.4.13, Transformers 5.20.1, tokenizers 0.23.3, datasets 5.1.0, maximum length 8,192, batch size 1), with a new runtime manifest per build that differs from T1's only in the model artifact |
| Reference arms | T1 BF16 GGUF and T1 local Q4_K_M rows are reused as the curve's reference and Q4 points under their existing identities; they are not re-collected |

## 3. Builds and stages (decision D8)

All builds are `diag-*` diagnostics derived from the BF16 control at the pinned quantizer with its default per-tensor type assignment for each file type. Each build has a committed manifest before its inference: command, quantizer binary hash, output SHA-256, actual bytes, and the tensor-type inventory. Actual bytes, not nominal bits, are the budget quantity.

| Stage | Builds | Note |
|---|---|---|
| 1 | `diag-q6k` (Q6_K), `diag-q3km` (Q3_K_M) | Brackets the existing Q4_K_M point |
| 2 | `diag-q3ks` (Q3_K_S), `diag-q2k` (Q2_K) | Q2_K, unlike Q2_K_S, needs no importance matrix at the pinned commit |
| 3 | `diag-iq3s` (IQ3_S) | IQ3_S needs no importance matrix at the pinned commit. **No IQ2 point is built**: every IQ2 file type at this commit assigns tensors (IQ2_XXS, IQ2_XS, IQ2_S) that the quantizer refuses without an importance matrix, and calibration data would confound the curve with the question C11 asks. **Confirm at review**: whether to build a separately labelled, imatrix-bearing IQ2 point later under C11 instead. |

Stages run in order. A stage starts only after the previous stage's report is committed. Stop rules:

- A failed identity, token or probability gate (§5) halts that build until the failure is diagnosed and recorded; it is never worked around by changing the lock, the tolerance or the contract.
- Descent stop (**default 15 pp, confirm at review**): if any build's English original-order accuracy is at or below the BF16 control's English accuracy minus 15.00 pp (230/300 − 45 = 185 correct or fewer), no stage with smaller builds is run.
- Any question that would touch the contract, the pools, the holdout or a fixed decision stops the affected work and goes to the user.

## 4. Why the local Q4_K_M is a comparator, not only a reference

The local Q4_K_M is already a heuristic mixed-precision allocation chosen by llama.cpp (Q6_K on the embedding and on selected attention-V and MLP-down tensors, Q4_K elsewhere). Every T3 build has the same property for its own file type. The later uniform-allocation control in C10 therefore tests whether llama.cpp's heuristic matters for any language before a language-aware allocation is asked to improve on it; T3 records each build's inventory so that comparison is possible.

## 5. Readiness gates per build, on the T1 pattern

1. Build manifest committed (§3).
2. Runtime manifest for the build prepared with the same tooling as T1's v4 manifests and bound in the arm identity.
3. Token check on the pinned native library and tokenizer: 900 contexts and 3,600 candidates reproduce the lock's model token IDs; every letter continuation is one token (`vocab_only`, no inference).
4. Cold-likelihood gate with the T1 validator (`validate_t1_cold.py`): direct cold forwards with float64 full-vocabulary log-softmax on the T1 selection (rows 0, 100, 188 and 299 per language, all four candidates, 48 candidates), then the client path against that oracle, then the same 48 candidates in reversed request order. Bounds: 0.0002 nats per continuation token and per supplied echoed probability; `max(0.001, k × 0.0002)` for the summed continuation; parser agreement 1e-8; exact IDs, one BOS, echo strings and counts, one generated suffix; no winner inversion. Tolerances never excuse token misalignment.
5. Resumable original-order runner with a new arm identity binding the lock, readiness, token check, runtime and gate hashes; 180 five-question shards; resumption only from validated shards under the identical identity.
6. Scoring throughput recorded after the first 20 shards and the stage time box replanned from it in `LOG.md`.
7. Exactly one GPU owner at a time; servers stopped and recorded after each arm.

Collection of a stage begins only after its readiness package is reviewed and the user confirms collection for that stage.

## 6. Endpoints and statistics

For each build `b` and each language, on the 300 development questions:

- Accuracy `acc_b`; paired delta `acc_b − acc_BF16` and `acc_b − acc_Q4KM`, in percentage points; English delta beside every non-English delta, always.
- Delta minus English for each paired delta.
- All-answer churn versus BF16 and versus Q4_K_M, with the right→wrong, wrong→right and wrong→wrong decomposition; denominators shown.
- Predicted-letter histograms against gold 72/92/72/64.
- Margin association: the fresh BF16 top-two summed-score margin per question, with the fixed bins [0, 0.25), [0.25, 0.5), [0.5, 1), [1, 2), [2, ∞) nats from [the margin analysis](margin-flip-analysis.md); per bin, the count of questions and the count whose selected option differs from BF16 (and separately from Q4_K_M).
- Candidate-score and margin deltas versus BF16 as descriptive distributions.

Uncertainty: paired bootstrap over the 250 source clusters, jointly resampled across languages and arms, 10,000 draws, seed 42, percentile 95% intervals, exactly as in T1 (`scripts/compare_expanded.compare_rows` and `scripts/summarize_t1_baselines.paired_report`). Margin-bin counts are descriptive and carry no intervals. Multiple endpoints are reported together without a multiplicity-adjusted confirmatory claim; T3 is development evidence.

Reporting: a new `scripts/summarize_t3_curve.py` that reuses the T1 loader, validation and statistics functions for an N-arm curve, writes one frozen report with its hash, and a results README under `results/t3-precision-curve/` with the tables above per stage. Raw shards, identities, manifests and gate artifacts are archived losslessly with hashes, as T1's were.

## 7. Predictions, each with what falsifies it

These restate the Stage 3 predictions in testable form. They concern churn and margins on the development set; none is the allocation claim.

| # | Prediction | Falsified if |
|---|---|---|
| P1 | For every language, `diag-q3km` changes more selected answers versus BF16 than the local Q4_K_M does (T1: 21/33/34). | Any language where Q3_K_M churn versus BF16 is less than or equal to Q4_K_M's. |
| P2 | For every language and every build at or below Q4_K_M bytes, the flip rate versus BF16 in the sub-1-nat margin bins exceeds the flip rate in the bins at or above 1 nat. Exploratory companion: more than half of each such build's flips fall in the sub-1-nat bins (T1 Q4_K_M: 71%, 85%, 85%). | Any language and build where the sub-1-nat flip rate is not higher. |
| P3 | For every language, `diag-q6k` changes fewer selected answers versus BF16 than the local Q4_K_M does. | Any language where Q6_K churn versus BF16 is greater than or equal to Q4_K_M's. |
| P4 | English, whose BF16 sub-1-nat share is the smallest (38/300 against 82 and 83), shows the lowest churn versus BF16 of the three languages for every build at or below Q4_K_M bytes. No ordering is predicted between Bangla and Hindi: their shares differ by one question. | Any such build where English churn is not the lowest. |

Flat or mixed outcomes are reported as such. A confirmed prediction describes the development set; it localizes no tensor and establishes no mechanism.

## 8. Operating-point selection (decision D2) and the byte ceiling (D3)

The allocation operating point for C8–C10 is chosen by this rule, evaluated on English only, after the last stage's report is committed and before any sensitivity work begins:

1. Order all builds (the T3 builds and the local Q4_K_M) by measured shipped bytes, descending.
2. The English floor is the BF16 control's English original-order accuracy minus 3.00 pp: 76.67% − 3.00 = 73.67%, that is **221 or more correct out of 300** (**default, confirm at review**).
3. The operating point is the smallest build whose English accuracy point estimate meets the floor. Bangla and Hindi results play no part in this choice.
4. If no T3 build meets the floor, the operating point is the local Q4_K_M (229/300).
5. The choice, the builds considered and their English accuracies are recorded in a dated `LOG.md` entry and in the results README before C8 starts.

The 2.2 GB total shipped-byte ceiling (model file with embedded tokenizer counted once, any adapter counted) is unchanged; the operating point may sit below it without further ratification. C10's equal-byte comparisons are made at the operating point's measured bytes within the equal-byte tolerance frozen in C10's own preregistration.

## 9. Endpoint roles and the meaningful margin for the later allocation claim (D4, D5)

Recorded here so they are frozen before any curve result is seen; they bind C10, not T3.

- Primary endpoint: original-order Belebele development accuracy under the accepted contract, reported as per-language delta versus the control at equal bytes and as delta minus English, with paired source-clustered 95% intervals.
- Secondary endpoint: the B6 generation protocol (absolute task success, naturalness, wrong-language flag, pairwise preference) with blinded Bangla human judgment, frozen separately before any generation.
- Meaningful benefit: a per-language accuracy gain of at least 3.00 pp on the primary endpoint over the best equal-byte control. Positive: the paired 95% interval's lower bound exceeds 0 and the point estimate is at least 3.00 pp. Null: the interval's upper bound is below 3.00 pp. Inconclusive: neither; reported as inconclusive, never as "allocation does not work".
- Instrument limit, stated in advance: with 300 questions per language the paired half-width is about 3 pp, so the Belebele arm may be inconclusive. The development set is not expanded for Article 2.

## 10. Scope decisions carried (D6, D7)

Tiny Aya Fire is deferred; T3 and C8–C10 evaluate the Global checkpoint only. Adaptation remains secondary: no adapter, LoRA or weight change is planned before the allocation result exists; Language-Conditional Dequantization (arXiv 2608.11786) is cited as prior art for language-aware post-hoc repair, distinct from allocation, and any future adapter's bytes count against the ceiling.

## 11. Sealed analyses (plan amendment of 26 October)

Until the A4 adjudicated labels are merged with a recorded hash, none of the following is computed, read or reported for any arm, T1 or T3:

- The negation-slice language interaction and compression interaction defined in the [negation review protocol](negation-review-protocol.md), §"Analysis after the A3 contract decision".
- Any accuracy, churn, margin or candidate-score breakdown conditioned on a negation or scope label.

After the labels are merged, these run once on the frozen T1 and T3 rows, with the same 250-cluster joint bootstrap, and are reported with the English comparison and the exclusion ledger.

## 12. Items flagged for the review before freezing

1. The English floor of 3.00 pp (221/300) in §8.
2. The descent stop of 15.00 pp (185/300) in §3.
3. The IQ2 decision in §3: no IQ2 point without an importance matrix; an imatrix-bearing IQ2 build, if wanted, is a C11 calibration arm with its own labelling.
4. IQ3_S as the stage-3 point rather than IQ3_M or IQ3_XS.
5. Optional densification near the expected operating point (Q4_K_S, Q5_K_S) as a further stage; not required by the decisions and not planned unless the user adds it.
6. Whether `scripts/archive_t1_baselines.py` is generalized for N arms or a sibling script is written; either way the archive format and verification command are recorded in the results README.

## 13. What this document does not do

It does not authorize quantization or inference, change the scoring contract, the data pools, the holdout rule, the C9 seven-build design, the two-failure measured-only fallback or the C10 control set (Q4_K_M heuristic, uniform, three seeded random). It does not touch Article 1 or any historical identity. The user decides every item marked for confirmation; any other open question is brought to the user rather than resolved here.
