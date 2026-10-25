# Public primary-source evidence ledger

Checked 2026-10-25. This primary-paper pass involved no experiments, downloads of model weights, private-community access, or changes to experiment gates. Version notes identify what was inspected; HTML version links are pinned, while some publication and abstract links are mutable. **Fulltext inspected** means relevant HTML methods/results/limitations passages and tables were read, not an exhaustive replication or a claim that every appendix was audited. **Abstract only** claims remain provisional.

## Closest overlaps and quantitative caveats

### Calibrating Beyond English (2026)

[arXiv v1, 26 January 2026](https://arxiv.org/html/2601.18306v1); [EACL proceedings](https://aclanthology.org/2026.eacl-long.223/). Fulltext inspected: setup, Figure 1–3, results; abstract checked separately. Eight calibration conditions (five monolingual, three mixes), GPTQ/AWQ, ten evaluation languages, principally Llama3.1-8B and Qwen2.5-7B. Figure 1 gives 4-bit AWQ mean perplexity across ten languages: English calibration 14.88, multilingual 14.64 (0.24 perplexity points, not 0.24 accuracy points). Abstract reports reductions up to 3.52 perplexity points; do not treat that maximum as the typical gain. The inspected text links multilingual sets with larger vocabulary and longer examples, which requires token-budget control when interpreting causality. Direct prior art for language-aware calibration; no claim that multilingual calibration itself is novel is defensible. Perplexity improvements do not establish translated-choice accuracy, generation quality, or mobile latency gains.

### Uneven Impact of PTQ in Machine Translation (2025)

[arXiv v1, 28 August 2025](https://arxiv.org/html/2508.20893v1). Fulltext inspected: methods, Tables 3–8, calibration, limitations. Five models, approximately 1.7B–70B, four PTQ families; abstract says 55 languages while introduction says 55 language pairs, so preserve that scope ambiguity. Q4_K_M and Q2_K are named GGUF recipes with imatrix, not interchangeable mathematical 4-/2-bit uniform weights. Table 7: Llama3.1-8B English→Bengali Q2_K COMET increases 44.9→48.0 with Bengali rather than English calibration (+3.1 score points).

**Internal contradictions:** §6 says Q4 changes stay within 0.2, but Table 8 Bengali→English Q4 gives 63.9→65.8 (+1.9). Prose claims Q2 Bengali→English improves 71.5→72.3, while Table 8 assigns English calibration 72.3 and Bengali 71.5 (−0.8). Do not repeat the prose as settled evidence. Limitations explicitly acknowledge single-run COMET and implementation sensitivity. This is direct multilingual quantization/calibration prior art, with unresolved numerical reporting issues.

### TASA: Beyond Activation Alignment (2026)

[arXiv v1, 1 July 2026](https://arxiv.org/html/2607.00908v1). Fulltext inspected: §4–5, Table 2, Appendix C/D. Jointly selects general/task calibration mixture, combines perplexity/reasoning sensitivity, optimizes layer budgets, and refines group precision using GPTQ/OBS. This substantially overlaps generic “task-aware sensitivity plus mixed precision” contributions. Seven accuracy tasks form the unweighted Avg.; WikiText PPL is an eighth benchmark excluded from Avg. Llama3-8B b3.5 Avg. 68.9 versus FP16 70.9 is 97.2% retained aggregate accuracy; “12.5% fewer bits” compares nominal 3.5 with 4.0, not demonstrated equal serialized model bytes. Table 2 random allocation uses three seeds but Wiki calibration, while MOA 68.9 uses mixed calibration; MOA+Wiki is 66.8 versus random+Wiki 65.4. Thus 68.9−65.4 mixes allocation and calibration effects. Appendix D explicitly warns that TACQ comparisons use different evaluation protocols. No inspected result establishes Tiny Aya language fairness or equal shipped-byte runtime dominance.

### Bangla quantization systematic evaluation (2026)

[arXiv v1, 25 August 2026](https://arxiv.org/html/2608.24615v1). Fulltext inspected: §3–5, Tables 1–4. Six checkpoints: three families, each with one baseline and one quantized variant; five Bangla multiple-choice/Boolean tasks, zero-shot candidate log-likelihood scoring. The headline 57.35% is relative accuracy loss: GPT-OSS CommonsenseQA 0.440→0.188, approximately (0.440−0.188)/0.440; absolute loss is 25.2 percentage points. Architecture, checkpoint, format, and backend vary together, preventing causal ranking of GPTQ versus GGUF. Table 1 labels “GPTQ-Q8” and “GGUF-W8A16” without establishing equivalent serialized bytes or exact tensor layouts; do not infer a GGUF-wide failure.

**Further inconsistency:** text says LLaMA degradation stays below 1% on every benchmark, but raw MMLU 0.358→0.333 is 2.5 percentage points (about 7.0% relative). This motivates checkpoint/format/scoring validation, not accepting the reported generalization. No English comparison isolates a Bangla-specific interaction.

## Foundation and adjacent evidence

### How Does Quantization Affect Multilingual LLMs? (2024)

[arXiv v2, 12 October 2024](https://arxiv.org/html/2407.03211v2); [EMNLP publication](https://aclanthology.org/2024.findings-emnlp.935/). Fulltext inspected: results, relative-change definitions, human evaluation. Command 35B/103B and Aya23 8B/35B establish prior multilingual quantization analysis across tasks/scripts and model sizes. Automatic aggregate changes average relative deltas because metric scales differ. Human 103B W4-g Japanese Internal result is −16.0% relative to a 50% tie-baseline win rate, corresponding to 42% wins, not a 16-percentage-point accuracy loss. The abstract contrasts this with a 1.7% automatic-task average drop; these have different denominators and tasks. Group-wise and activation approaches can help aggregate metrics yet impair particular tasks. Important precedent for evaluating generation/language adherence beyond aggregate accuracy; no direct Tiny Aya result.

### Fair-GPTQ (2025)

[arXiv v1, 18 September 2025](https://arxiv.org/html/2509.15206v1). Fulltext inspected: objective, setup, Table 1. Adds protected-group bias constraints during GPTQ rounding; studies occupational stereotypes and gender/race/religion, principally English OPT/Mistral. This is fairness-aware quantization prior art, not multilingual language parity evidence. Abstract's “at least 90%” retained zero-shot accuracy is not a guarantee for every model/variant/task: Table 1 Mistral lower-layer HellaSwag is 47.11 versus FP16 60.93 (77.3% retained). Bias scores have task-specific interpretation; StereoSet/CrowS-Pairs neutrality is 50, rather than universally lower being better. Do not transfer its fairness objective or numerical guarantee to languages without new validation.

### Tokenizer unfairness (2023)

[arXiv v2, 20 October 2023](https://arxiv.org/abs/2305.15425). **Abstract only**; HTML fulltext endpoint unavailable in this pass. Reports translated-text token lengths differing up to 15×, and character/byte approaches exceeding 4× for some pairs. These are token-length ratios on matched content, not quality or latency measurements for Tiny Aya. Supports recording token fertility and content coverage, and separating tokens/s from matched-content latency; quantitative transfer requires tokenizer-specific measurements.

### SpinQuant (2024–2025)

[arXiv v4, 20 February 2025](https://arxiv.org/html/2405.16406v4). Fulltext inspected: result summaries, Table 3. Learned rotations preserve full-precision function while improving low-bit behavior. W4A4KV4 Llama2-7B reaches 64.0 average zero-shot accuracy, 2.9 percentage points below its full-precision baseline; this includes activation and cache quantization, so it is not an equivalent comparison to weight-only GGUF. Random rotation variation motivates seeded controls but does not prove language-aware allocation gains.

### MobileLLM (2024)

[arXiv v2, 27 June 2024](https://arxiv.org/html/2402.14905v2). Fulltext inspected: architecture and zero-shot table/discussion. Deep/thin models, embedding sharing, GQA, immediate block sharing. Reported 2.7/4.3 improvements concern zero-shot benchmark average accuracy points for roughly 125M/350M models against preceding models; not multilingual PTQ improvements. Architectural efficiency is adjacent context rather than direct language-aware quantization evidence.

### Tiny Aya's own quantization evaluation (2026)

[arXiv v1, 12 March 2026, §6](https://arxiv.org/html/2603.11510v1). Fulltext inspected: quantization section and Figure 13–15 descriptions. Already evaluates Q4_0/Q4_K_M/Q8_0, mobile throughput, and language web-presence relationships. Q4_K_M reports 2.14 GB, 32.4 decode tokens/s on newer hardware; standardized workload is 100 input and 100 output tokens. Older iPhone13 reaches approximately 10 decode tokens/s. mDolly mean judge-score degradation is 1.4 points Q4_K_M, 2.1 Q4_0, negligible Q8_0 relative to BF16. These are judge-score points, not accuracy percentages or all-language guarantees. Higher-web-presence languages tend to smaller penalties; the penalty tapers in the lowest bins. Thus neither first Tiny Aya quantization nor first per-language quantization assessment is available as a novelty claim.

### Further prior art discovered, not yet fulltext audited

[Multilingual Brain Surgeon, LREC-COLING May 2024](https://aclanthology.org/2024.lrec-main.1030/): **abstract only**; multilingual calibration sampling proportional to training-language distributions. [CoopQ, arXiv v2, 12 December 2025](https://arxiv.org/abs/2509.15455): metadata/abstract page inspected; earlier search index calls v1 “IMPQ,” current title is CoopQ. Treat as additional layerwise mixed-precision prior art; quantitative claims not imported here. These are leads for further review, not evidence of superiority or absence of overlap.

## Defensible contribution direction

The evidence supports a bounded evaluation/engineering contribution: validated multilingual candidate scoring and checkpoint/runtime identity, followed by a language-aware allocation test on a specified Tiny Aya checkpoint under **equal measured shipped bytes**, with uniform and seeded random allocation controls, matched calibration/token budgets, and real supported runtime measurements. Separate calibration effects from allocation effects and report per-language absolute/relative deltas and uncertainty. Generic multilingual quantization harms, multilingual calibration, task-aware sensitivity, mixed precision, random controls, and Tiny Aya mobile quantization all have direct prior art.

This is a proposed contribution boundary, not a novelty certification. None of the reviewed papers establishes that this specific pipeline will improve quality, fairness, latency, or energy. Literature review does not authorize new experiment runs or alter existing gates.
