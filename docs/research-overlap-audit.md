# Research overlap audit

Audit date: 25 October 2026. This is a targeted overlap assessment, not an exhaustive literature review or a priority claim. Sources were read through their primary publication pages, arXiv HTML, and the author's repository README. No experiments were run and no external implementation was executed. Repository state was inspected through README, CLAUDE.md, `docs/stage2-plan.md`, and `docs/margin-flip-analysis.md`.

## Finding

The broad premise is established: near-preserved accuracy can hide substantial item-level changes under compression; multilingual effects depend on language, model, method, calibration, and evaluation. Per-language answer churn, BF16 margin analysis, and free-form judging are therefore useful measurements but cannot independently carry a novelty claim. The strongest prospective contribution is a carefully controlled Tiny Aya deployment case study with Bangla human evaluation and measured precision-allocation interventions at matched total shipped bytes. Those are plans until completed evidence supports them.

## Sources and exact read depth

### Accuracy is Not All You Need — Dutta et al., NeurIPS 2024

[Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/e0e956681b04ac126679e8c7dd706b2e-Abstract-Conference.html); [arXiv v1 HTML](https://arxiv.org/html/2407.09141v1).

Read depth: proceedings abstract; arXiv v1 abstract, introduction and Section 2 metric definitions. The proceedings PDF fetch failed; this audit does not claim to have read the final conference full text, experimental appendices, or verified numerical tables.

The paper explicitly defines flips as correct-to-incorrect plus incorrect-to-correct transitions, excluding incorrect-to-incorrect answer changes. Its KL metric averages full-vocabulary divergence over answer-option tokens, options and examples. It studies compression beyond quantization and relates flips to free-form MT-Bench degradation. This directly precedes an accuracy-versus-flips motivation and any suggestion that a BF16-relative distance measure is new. Its benchmark and model coverage does not by itself resolve this project's Tiny Aya/Bangla deployment question. Numerical effect sizes should be checked against the final version before quotation.

### FlipEval — author-maintained repository

[Repository](https://github.com/amoghsingh130/flipeval); [README inspected](https://raw.githubusercontent.com/amoghsingh130/flipeval/main/README.md).

Read depth: GitHub landing page and README introduction, API/metric fields, planning helpers and input-contract excerpt. No source functions, tests, paper, result artifacts, or installation were audited; `main` is mutable and no commit SHA was pinned in this pass.

The README distinguishes accuracy-state churn from wrong-to-different-wrong churn and total answer churn. It advertises paired McNemar testing, declared-margin equivalence testing, bootstrap intervals, sample-size planning, rank stability and seed/item resampling. It pairs records by item ID and describes duplicate rejection. Thus, paired churn reporting and an equivalence/power apparatus already have an identifiable software precedent. README claims of statistical soundness, corpus coverage and empirical ratios remain author claims here, not independently replicated findings. Reuse or comparison requires a commit-pinned code audit and verification that the resampling unit matches this project's shared-source questions.

### English K_Quantization … Multilingual Performance — Borgersen and Goodwin

[arXiv v4, 22 January 2026](https://arxiv.org/html/2503.03592v4); [version history](https://arxiv.org/abs/2503.03592).

Read depth: abstract, method Sections 3–3.2, and results discussion through the free-form-results introduction (HTML lines 79–95). Later limitations text and figure pixels were not inspected; counts inside figures were not transcribed.

The study quantizes Llama 3.3 70B using English, Norwegian and Malayalam importance texts and evaluates English/Norwegian MixEval. Its MCQ setup constrains a valid answer index in the first token; it also discusses free-form evaluation. It reports nonsignificant calibration-language results and flags translated text/cultural context and constrained decoding as limitations. This overlaps directly with testing English-centric calibration and unequal language loss in GGUF deployment. The model size, evaluated languages and task setting limit transfer to Tiny Aya and Bangla. Nonsignificance does not demonstrate general multilingual equivalence; Malayalam calibration is not Malayalam evaluation.

### Lightweight but Linguistically Fair? — John et al.

[arXiv v1, 13 October 2026](https://arxiv.org/html/2610.18343v1); [record](https://arxiv.org/abs/2610.18343).

Read depth: abstract; Sections 3.1–3.4, initial results table/discussion; conclusion and limitations. Appendix headings were inspected, but appendix analyses, underlying data/code and judge outputs were not audited.

This is especially close: 14 instruction models, BF16/GPTQ-8/GPTQ-4/AWQ-4, aligned Bavarian/German/English questions, option-text likelihood, cross-language delta differences, correctness transitions and correctness-preserving answer changes, calibration ablations and blinded free-form judging. It uses source-question bootstrap and practical-equivalence margins. Its abstract also links instability to BF16 uncertainty. A margin/churn plot or language-relative delta is consequently insufficient differentiation. Limits include one regional benchmark, a single LLM judge, focused calibration-language replication and hardware-specific deployment measurements. Its larger models and dialect comparison leave room for a small multilingual-model case study, but do not establish that such a study is unprecedented.

### Accuracy is Not Enough … Fidelity Loss — Qamar et al.

[arXiv v2, 9 September 2026](https://arxiv.org/html/2609.07664v2); [record](https://arxiv.org/abs/2609.07664).

Read depth: abstract, Section III-B/C, Sections IV-A–D, and the initial results table. No complete empirical appendix, implementation, or theorem verification was undertaken.

The paper compares full-vocabulary prompt-boundary distributions using TVD and JSD, separately from candidate-sequence accuracy. It examines five architectures, four benchmarks and multiple llama.cpp precisions. Its “total flips” means harmful plus beneficial correctness transitions, not every changed answer. It explicitly limits divergence to fidelity relative to BF16, without establishing correctness, safety or perceived quality. This precedes a distribution-sensitive GGUF evaluation contribution; adding TVD/JSD alone would be incremental. Its prompt-boundary diagnostic also differs from Dutta et al.'s option-token-averaged KL and from this repository's letter-score margins: these values must not be treated as interchangeable.

### Unsloth Dynamic GGUFs — maintainer documentation

[Dynamic 2.0 documentation](https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs); [Dynamic 3.0 documentation](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs.md). Added in the second pass of 25 October.

Read depth: both documentation pages. No code, imatrix file, selection algorithm or quantized artifact was audited; the pages are mutable and undated apart from an April 2026 update note, and no snapshot was pinned.

The documentation describes selecting the quantization type of every possible layer per model to reduce divergence from BF16 at small size cost, motivated explicitly by Dutta et al.'s flips argument against accuracy-only comparison. Quality is reported as mean KL divergence and top-1 agreement against BF16 on held-out text, a 300-prompt greedy-decoding divergence set that includes non-Latin prompts, and, for the 2.0 generation, a reproduced 5-shot MMLU harness. The 3.0 generation uses a refined imatrix calibration set described as multilingual, released publicly, with no QAT. No per-language results, no uniform or random-allocation ablation and no equal-measured-bytes comparison are published, so the benefit of the layer selection cannot be isolated from the pages. Per-tensor allocation in GGUF is therefore established practice; this project's differentiator is the language dimension, the uniform and seeded-random controls, equal measured shipped bytes and paired uncertainty, not the mechanism. Cite it as a precedent rather than as a validated method.

## Metric contract needed in this project

For matched single-answer MCQ items, let H count baseline-correct/candidate-wrong items, B baseline-wrong/candidate-correct items, and W items where both are wrong but choose different answers. With N matched items:

| Quantity | Definition | What it answers |
|---|---|---|
| Net accuracy change | (B − H) / N | Did measured task success change? |
| Correctness-state churn | (H + B) / N | How often did correctness change? |
| All-answer churn | (H + B + W) / N | How often did the selected answer change? |
| Harmful / beneficial rates | H / N; B / N | Which direction contributed to the change? |

These identities assume a unique correct answer and matched scoring. For multiple accepted answers, correctness-preserving correct-to-different-correct changes also belong in all-answer churn. Textual mismatch in free-form output is a separate construct and needs normalization or semantic assessment.

The existing margin-analysis document defines its flip as a **different selected option**. That corresponds to all-answer churn for the repository's single-gold MCQs; it is broader than Dutta's flips and FlipEval's accuracy-state churn. Keep the current historical contract intact, but spell out the definition whenever comparing papers. Report denominators and transition counts; distinguish all-item rates from rates conditional on baseline correctness. A small net delta does not mean low churn, and low churn does not mean answers are good.

## Defensible contribution positioning

Suggested framing: “We evaluate Tiny Aya compression as an end-to-end multilingual deployment problem, combining controlled scoring and runtime comparisons, Bangla-focused human assessment, and measured precision allocation under a fixed shipped-byte budget.” This is a proposed scope, not a completed result or a claim of first occurrence.

The necessary evidence goes beyond another 4-bit delta table: separate runtime and precision effects; preserve prompt, sample and quantizer identities; report absolute task success, both churn definitions and language-minus-English changes; cluster uncertainty by source where questions share passages; freeze practical retention margins before finalist selection; compare targeted allocation with equal-byte uniform and random controls; and evaluate frozen finalists on the reserved source-disjoint holdout. Human judgments need coverage, adjudication and uncertainty reporting alongside judge preferences. These controls support credible conclusions even if no language-specific damage or repair benefit appears.

Keep claims bounded to measured models, languages, tasks, formats and devices. Calibration language is a testable factor, not a presumed explanation. Baseline fidelity is distinct from correctness; an intervention that differs from BF16 can improve task success. Observational margin/churn association does not identify a causal tensor mechanism. Planned phone performance, generation damage, precision thresholds and successful repairs remain unmeasured until their gates are met.

## Remaining audit work

Before manuscript positioning, pin FlipEval to a commit and inspect its implementation/paper; pin a dated snapshot of the Unsloth documentation and imatrix release; read the final Dutta proceedings PDF and the relevant full appendices of the 2026 studies; follow primary references on multilingual quantization and calibration; and update the overlap map against the actual completed experiments. This targeted set cannot establish that no other matching study exists. The main synthesis should combine this audit with the broader primary-source and community ledgers, keeping evidence depth visible.
