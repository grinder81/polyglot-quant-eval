# Tiny Aya research landscape and evidence review

Review date: 25 October 2026. Repository starting point: `88adfa3437f49ab2b40c851ba1d52401bae3057d`. This is a literature and community-resource review, not a new experiment, systematic-review completeness claim, or change to the approved [Stage 2 plan](stage2-plan.md).

Follow-up owner: [research evidence issue 44](https://github.com/grinder81/polyglot-quant-eval/issues/44). [Independent review record](research-review-record.md).

## Conclusion

Continue the research, with a narrower contribution claim. Multilingual quantization, language-dependent degradation, answer instability despite similar accuracy, language-aware calibration, and sensitivity-guided mixed precision already have substantial prior art. Tiny Aya's own report includes quantization and phone measurements. Our useful contribution can be a reproducible, carefully controlled Tiny Aya comparison followed by a **tested** language-aware allocation under equal measured shipped bytes. Whether allocation helps remains an open hypothesis.

This review does not certify novelty. It identifies the strongest overlaps found, their limitations, and what our experiments must control to add evidence rather than repeat a headline. No model weights were downloaded, inference launched, holdout accessed, human labels invented, or community messages sent in this review.

## Reading map

| Document | What it contains |
|---|---|
| [Primary evidence](research-primary-evidence.md) | Multilingual quantization, Bangla-specific work, calibration, TASA, Fair-GPTQ, tokenizer, Tiny Aya and mobile/rotation foundations; versioned sources and numerical caveats |
| [Overlap audit](research-overlap-audit.md) | Accuracy versus answer flips, fidelity, regional-language quantization and English-calibration counterevidence |
| [Community public resources](research-community-resources.md) | Evaluation infrastructure, local deployment, Indic resources and bounded safety research; public-artifact availability |
| [Additional sources and discovery coverage](research-search-coverage.md) | Search scope, community channel map, supporting sources, unresolved leads and exclusions |

Each ledger distinguishes the text inspected from author-reported findings and from our recommendations. None of the external experiments was replicated here. A paper's abstract, repository README, talk announcement and raw reproducible result are different evidence levels.

## What others have established, and what it changes for us

| Research question | Closest evidence | Implication for this project |
|---|---|---|
| Can aggregate scores hide multilingual damage? | [Marchisio et al.](https://arxiv.org/html/2407.03211v2), [compressed multilingual MT](https://aclanthology.org/2022.findings-emnlp.317/) | Already established in other models/tasks. Add bounded Tiny Aya evidence; do not claim first discovery or transfer the magnitude. |
| Is Bangla quantization already studied? | [Bangla systematic evaluation](https://arxiv.org/html/2608.24615v1) | Yes. Its checkpoint/format confounds and missing English interaction make controlled identity and paired English-relative effects especially useful. |
| Does similar accuracy imply similar behavior? | [Overlap audit](research-overlap-audit.md) | No. Report regressions, corrections and wrong-to-wrong transitions separately; correctness-flip metrics are not identical to all-choice churn. |
| Are language gaps, churn and margin diagnostics an unexplored combination? | [Lightweight but Linguistically Fair?](https://arxiv.org/html/2610.18343v1) | No. This close Bavarian/German/English study combines aligned language comparisons, instability, calibration and free-form evaluation. Our checkpoint/deployment case and later intervention must supply their own value. |
| Can calibration language matter? | [Calibrating Beyond English](https://arxiv.org/html/2601.18306v1), [MT calibration](https://arxiv.org/html/2508.20893v1), and counterevidence in [coverage notes](research-search-coverage.md) | Treat effects as model/task/quantizer dependent. Control token budgets and calibration membership; do not assume English calibration necessarily harms Bangla. |
| Is task-aware mixed precision new? | [TASA](https://arxiv.org/html/2607.00908v1), [MixQuant](https://arxiv.org/abs/2607.23047v1) | No. Distinguish calibration from allocation, account for interacting layers, and validate simulated ranks against real supported builds. |
| Is mobile Tiny Aya a new direction? | [Tiny Aya report, §6](https://arxiv.org/html/2603.11510v1), [deployment resources](research-community-resources.md) | Existing prior art. Our future contribution would be a specified device/workload and quality/bytes/latency tradeoff, not the fact that a small model runs locally. |
| Does lower benchmark loss establish safety? | [Beyond Perplexity](https://aclanthology.org/2024.findings-emnlp.901/), [Fair-GPTQ](https://arxiv.org/html/2509.15206v1) | No. Capability, demographic bias, language adherence and permission-respecting agent behavior require distinct endpoints. |

## What our evidence actually says

The [complete T1 report](../results/t1-cold-baselines/README.md) is the authority. These are original-order Belebele development results for Tiny Aya Global, 300 questions per language, BF16 **GGUF** versus local Q4_K_M under the accepted cold-runtime plain-letter summed-likelihood contract. They do not replace the original BF16 vLLM reference.

| Language | BF16 / Q4 correct out of 300 | Q4 minus BF16, pp [95% interval] | Delta minus English, pp [95% interval] | All-choice churn |
|---|---:|---:|---:|---:|
| English | 230 / 229 | -0.33 [-3.03, +2.36] | Reference | 21/300 (7.00%) |
| Bangla | 187 / 190 | +1.00 [-2.01, +4.15] | +1.33 [-2.63, +5.37] | 33/300 (11.00%) |
| Hindi | 184 / 180 | -1.33 [-4.70, +2.03] | -1.00 [-4.93, +2.97] | 34/300 (11.33%) |

Intervals use 10,000 paired, jointly resampled source-cluster draws over 250 source clusters, seed 42. All displayed difference intervals include zero. This establishes neither equivalence nor a language-specific compression penalty. Bangla churn is approximately 1.57 times English churn, not doubled. The exploratory low-margin association is not a causal account of language differences.

The historical-to-fresh comparison is a **combined recorded runtime/settings transition**, not an isolated cache-patch experiment. The full-900 Q4 maximum absolute candidate-score differences are 0.89890 nats English, 1.33790 Bangla and 0.79041 Hindi. Earlier selected-context bridge maxima were smaller; neither is a universal bound. Preserve both histories rather than repeating the early 0.01-nat description as if it characterized all changes. The report's raw archives and provenance remain unchanged.

## Contribution and decision matrix

| Candidate contribution | Current status | Evidence needed to claim it |
|---|---|---|
| Reproducible multilingual measurement checkpoint | Supported within recorded T1/A3 scope | Existing identity, scoring, direct-logit/reversed-order checks and raw evidence; preserve bounded-runtime caveats |
| Association between BF16 margin and answer churn | Exploratory association | Frozen prediction and prospectively evaluated approved precision points; distinguish previously inspected development membership from independent validation, and never relabel it as untouched holdout |
| Bangla benefits from language-aware precision allocation | Untested | Real builds at equal measured shipped bytes; uniform and three seeded random controls; identical calibration where isolating allocation; English retention and paired uncertainty |
| Sensitivity map identifies an internal mechanism | Not established | Intervention validation, interactions and repeatability; ranking alone is insufficient |
| Good MCQ results imply good Bangla generation | Unsupported | Separate generation protocol, blinded native-speaker judgments, absolute correctness and language confusion |
| Smaller files improve phone experience | Untested here | Actual device, peak memory, prefill/decode latency, thermal and energy measurements with fixed workloads |
| Compression preserves agent safety | Untested here | Separate, authorized, isolated behavior study with permissions, stopping and intervention endpoints |

## Next work, in the existing gate order

1. Complete the existing A4 human Bangla negation review. Do not substitute an LLM judge for the required human labels. Keep [issue 19](https://github.com/grinder81/polyglot-quant-eval/issues/19) as owner.
2. Before T3/B5, preregister the precision curve, margin prediction, practically meaningful effect threshold, English retention and matched-byte tolerance. Carry the literature comparison into that review; it does not itself authorize the sweep. Keep [runtime issue 24](https://github.com/grinder81/tiny-aya-edge/issues/24) as owner.
3. Prepare the blinded generation rubric and matched runtime/decoding settings under [B6](https://github.com/grinder81/polyglot-quant-eval/issues/21). Resolve the separate EOS/stopping identity and generation validation; likelihood cold-prefill validation does not establish generation parity. Human availability remains explicit.
4. Validate real quantizer fidelity and sensitivity predictions before allocation. C9 remains six extreme-group builds plus one random build; after two map-validation failures use the existing measured-build fallback. The Q4_K_M/uniform/three-random allocation controls belong to the later allocation comparison, not a redefinition of C9.
5. Freeze finalists before any protected holdout access, and measure devices only under the approved device protocol. Retain the 2.2 GB total shipped-byte cap, including tokenizer/adapters once. Adaptation and safety branches require their own scope decisions.

These are links to existing owners, not duplicate experiment tickets or changes to their acceptance criteria. The review's follow-up issue tracks literature ambiguities, comparator design and evidence gaps only.

## Questions worth taking back to the community

- Evaluation: Which generation rubric and judge-validation checks would make a small Bangla/English sample useful without overstating representativeness?
- Compression: Which calibration-versus-allocation ablation and serialized-byte accounting should precede a language-aware claim?
- Systems: Would the bounded request-history reproducer and identity checks be useful as an evaluation regression fixture?
- Indic NLP: Which publicly licensed, native-reviewed resources cover script, transliteration and code mixing without contaminating our protected pools?

These are proposed discussion questions. This task posts no messages or unsolicited author contacts. Public sources are cited in the ledgers; private chats, meeting links, contact details and unpublished project documents are not reproduced.
