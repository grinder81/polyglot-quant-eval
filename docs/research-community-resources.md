# Public community resource ledger

Reviewed 2026-10-25. This is a curated source map for multilingual quantization evaluation, not an experimental result or an exhaustive literature review. Community discovery leads were checked against public author, maintainer, or publisher pages. No private Discord messages, member identities, screenshots, or quotations are retained. No downloaded code, model, benchmark, or experiment was executed; repository implementation and result artifacts were not audited. URLs below are mutable unless a version is specified.

## How to use this ledger

“Read” identifies the actual evidence inspected: a README, article body, dataset/model card, or arXiv abstract and metadata. An author-reported finding is not independently reproduced. A repository's existence does not validate its scores. Abstract-only entries are leads for full methods review before reuse. Before adopting any task, inspect license, split construction, translation and annotation provenance, scoring, contamination risk, and exact revision.

The strongest immediate connections are evaluation metadata (Every Eval Ever), runtime confounds (Mozilla), and structured multilingual tool calling (Tiny Facade). Bengali resources broaden the error taxonomy beyond translated multiple-choice accuracy. They do not establish that this project's quantization effects generalize across tasks, languages, models, or hardware.

## Infrastructure and multilingual model leads

### Every Eval Ever

- Public sources: [repository](https://github.com/evaleval/every_eval_ever), [launch article, February 17, 2026](https://evalevalai.com/infrastructure/2026/02/17/everyevalever-launch/).
- Read: rendered README schema examples, validation and agentic-evaluation sections; launch article problem framing and shared-schema/database description.
- Verified scope: a shared reporting schema and crowdsourced database covering results from different frameworks. README examples include sample-level answers, extraction attribution, scores, generation configuration, tools, evaluation limits, and sandbox metadata.
- Relevance: a useful interoperability target for future exports. Preserve the project's model revision, quantization artifact, runtime/build, prompt/template, scoring contract, dataset revision, and sample trace even if an external schema cannot express all of them directly.
- Limits: standardizing metadata cannot make differently configured runs comparable. Schema version and actual field definitions must be pinned before implementation. No database coverage or submitted result quality was audited.

### alma

- Public source: [saifhaq/alma](https://github.com/saifhaq/alma).
- Read: README overview and `benchmark_model` usage/configuration examples.
- Verified scope: a PyTorch inference-speed library advertising more than 90 conversion options, including compilation/export and accelerator paths. Examples distinguish model-only inference time from elapsed time and report samples/second.
- Relevance: a possible later conversion/backend exploration tool; reinforces separating host overhead from model execution.
- Limits: this is not a multilingual language-quality benchmark or evidence that one GGUF quantization improves accuracy. README examples are illustrative, hardware-dependent measurements. Conversion coverage, numerical parity, dependencies, and compatibility with the project's models remain untested.

### Mozilla local-server comparison

- Public sources: [Mozilla article, September 17, 2026](https://blog.mozilla.ai/benchmarking-local-llm-servers-llama-cpp-llamafile-lm-studio-and-ollama/), [linked benchmark repository](https://github.com/mozilla-ai/exp-llama-benchy).
- Read: article methods, main results, practical interpretation, and limitations; repository was identified through the article/search, not implementation-audited.
- Author-reported scope: llama.cpp, llamafile, LM Studio, and Ollama with shared GGUF weights on Apple Metal, NVIDIA L40S CUDA, and Steam Deck Vulkan. Prompt processing and generation are separate metrics. Builds, shader toolchains, speculative decoding, batching defaults, and timing source affect the comparison.
- Relevance: record runtime commit, backend, build flags, offload, context, batching, speculation, and timing boundary alongside model and quantization. Separate matched-configuration tests from product-default tests.
- Limits: this is throughput evidence on those setups, not a universal server ranking or quantized-quality result. The article explicitly describes practical configurations rather than perfectly controlled backend implementations. No inference to this Windows machine or unseen hardware is justified without local measurement.

### Tiny Facade

- Public sources: [community article, April 20, 2026](https://huggingface.co/blog/Bronsn/tiny-facade), [model collection](https://huggingface.co/collections/Bronsn/tiny-facade-multilingual-tool-calling-models).
- Read: article's experiment description and findings sections; collection listing. Model weights, per-item outputs, and scorer implementation were not inspected.
- Author-reported finding: four Tiny Aya variants, 53 evaluated languages, fp16/4-bit settings, and four temperatures on MASSIVE-Agents. The article reports 4-bit advantages for regional models and temperature-dependent structured-call degradation.
- Relevance: an unusually close public lead for task-specific multilingual quantization comparisons. It motivates checking template/parser correctness and distinguishing JSON validity, tool selection, and argument semantics.
- Limits: “70+ languages” support in the title is not 70+ evaluated languages. Reported quantization gains and deployment prescriptions remain author claims; do not generalize them to other quants, tasks, or devices. Exact artifacts, runtime/template parity, scoring, pairing, uncertainty, and per-language sample construction require full verification. The collection is a distribution/discovery surface, not independent validation.

### Official Tiny Aya sources

- Public sources: [Cohere launch blog](https://cohere.com/blog/cohere-labs-tiny-aya), [official report repository](https://github.com/Cohere-Labs/tiny-aya-tech-report), [report PDF](https://github.com/Cohere-Labs/tiny-aya-tech-report/blob/main/tiny_aya_tech_report.pdf), [arXiv 2603.11510](https://arxiv.org/abs/2603.11510).
- Read: official blog title/date/attribution, repository landing page/file presence, and arXiv abstract/metadata. The blog extraction omitted substantive body text; the PDF's full methods/tables were not read.
- Verified scope: the abstract describes a 3.35B family trained on 70 languages, with a foundation model, global instruction variant, and three region-specialized variants. It describes multilingual understanding, translation, and target-language generation evaluation.
- Relevance: primary provenance for model family and regional specialization; required context before treating variants as interchangeable baselines.
- Limits: the official release does not independently validate Tiny Facade's downstream results. No claim here about Bengali superiority, tool-calling training, phone performance, or quantization robustness is inferred from the abstract. The GitHub report and later arXiv version should be compared and pinned before citation of detailed numbers.

### GharBench

- Public source: [connectwithub/gharbench](https://github.com/connectwithub/gharbench).
- Read: README overview, architecture, deterministic/offline replay description, and current validation caveats.
- Verified scope: simulated Indian real-estate sales conversations, buyer personas, grounding documents, six typed tools, and an environment that executes calls while recording transcripts, manifests, and costs. The README distinguishes reported live runs from shipped artifacts and says its judge panel is a later phase.
- Relevance: design reference for environment-controlled tool execution, typed validation, replayability, and domain-specific conversational evaluation.
- Limits: not evidence of broad multilingual or Bengali competence, and not a substitute for a paired quantization study. Seeded deterministic violations validate those checks, not complete judge validity or realistic buyer behavior. Live-score claims were not reproduced or artifact-audited.

## Bengali, Indic, and code-mixing leads

| Source and public URL | Actually read and supported scope | Relevance and limits |
| --- | --- | --- |
| [BanglaSafe project](https://banglallm.github.io/banglasafe/), [paper 2608.22335](https://arxiv.org/abs/2608.22335) | Project-page text and abstract: 879 prompts, 17 harm categories, language/register/authority conditions. Authors report register-sensitive harmful compliance and difficulty judging Bengali safety. | Add register and culturally grounded error analysis. Project explicitly says it has no benign controls and cannot measure over-refusal. Judge calibration and prompt provenance need methods review; not independently reproduced. |
| [Alo-70M model card](https://huggingface.co/spitfire4794/Alo-70m) | Card architecture, SFT, evaluation table, limitations: approximately 69M parameters, 1,024-token context, Bengali continuation-log-probability comparisons across seven named benchmarks. | Small Bengali-centric baseline lead; distinguishes forced-choice scoring from instruction following. Card reports SFT declines versus base on some tasks. Scores and causal explanations are author assertions; paper marked forthcoming. No quantization parity or deployment quality established. |
| [IndicPHI dataset card](https://huggingface.co/datasets/Sidharth1743/indicphi) | Card, displayed schema, construction and limitations: synthetic clinical PHI/PII span labels; 26,536 documents, 22 scheduled languages plus English, 50 entity types. Separate document and GLiNER-window configurations. | Structured extraction and script/token-boundary stress-test lead. Card documents a Latin-centric tokenizer problem and replacement windowing. Fully synthetic, model-generated/translated and model-judged; not clinical validation or a human gold standard. Inspect language coverage, surrogate/template leakage and persona grouping before split reuse. |
| [BenHalluEval 2605.31483](https://arxiv.org/abs/2605.31483) | Current arXiv v4 abstract/metadata: Bengali QA, Bangla-English code-mixed QA, summarization, reasoning; synthetic hallucinated candidates; separate true-instance false positives and hallucination detection. | Useful paired false-positive/detection framing. Full datasets, human validation and metric implementation were not inspected. Detection of generated hallucinations is a different construct from generation-time factual reliability. |
| [BanglaVeilGuard 2608.21880](https://arxiv.org/abs/2608.21880) | Abstract: standard, Romanized, Banglish, mixed, noisy and dialectal forms; unsafe, safe and safe-sensitive prompts; normalization and prompt gate. Authors identify benign noisy/dialectal over-refusal as a cost. | Candidate representation/robustness taxonomy. Model-specific safety gains are unverified here and rely on the paper's scoring. Review held-out grouping and normalization effects before reuse. |
| [Bengali benchmark paper 2507.23248](https://arxiv.org/abs/2507.23248), [linked project](https://github.com/BengaliAI/bn-llm-benchmark) | Current arXiv v2 abstract/metadata; repository was only identified as a lead. Current title is *Script Fragmentation and Format: What Drives the English-Bengali Performance Gap in Open LLMs?* Authors describe eight translated benchmarks and format-dependent apparent gaps. | Direct reason to separate answer correctness, format adherence, tokenization and extraction. Search indexes may show the earlier title; cite exact version. Full methods, translated examples and judge reliability remain unread. |
| [Multilingual-BFCL dataset card](https://huggingface.co/datasets/qualgo-technologies/Multilingual-BFCL) | Public card/top-level metadata: English, Vietnamese and Thai function-calling, refusal and hallucination evaluation. Access to data files requires accepting conditions. | Related structured-tool evaluation lead, not Bengali coverage. No gated files accessed, conditions accepted, code executed, or reported scores validated. |
| [CodeMixLab](https://github.com/tahaBU/CodeMixLab) | Public maintainer README text surfaced in search: Bengali/English/Romanized language identification, normalization and switch metrics; explicitly describes synthetic demonstration evaluation. | Tooling lead for annotating code-mixing, not evidence of real-world LLM performance. Full repository, artifacts, data and implementation not audited. |
| [indic-quant pilot](https://github.com/ashutosh-rath02/indic-quant), added 25 October | Public README: a planned Gemma 3 4B (and Qwen3-4B) study of English versus Indic-mix (Hindi, Bengali, Tamil, Telugu, Marathi) imatrix calibration at equal token budget across 19 llama.cpp types including Q2_K and IQ2_M; per-language KL to BF16 on FLORES+, MILU accuracy, chrF++ translation, tokenizer fertility; a preregistered decision rule for a "strong signal". No results: weights not downloaded, GPU mode not run, CPU smoke tests only. | The calibration arm this project plans for C11 has already been designed elsewhere, unexecuted. A design to compare against and a possible collaborator; it is evidence of neither direction. Licence not shown; repository mutable and unpinned. |

## Broader evaluation cautions from public papers

### Computer-use goal-directedness

[Just Do It!? Computer-Use Agents Exhibit Blind Goal-Directedness, 2510.01670](https://arxiv.org/abs/2510.01670) was read at abstract/metadata level. Authors introduce BLIND-ACT, 90 OSWorld-based tasks addressing contextual reasoning, ambiguous decisions, and infeasible or contradictory goals. They report high blind-goal-directedness rates and LLM-judge/human agreement in their study.

Relevance is methodological: agent evaluation should measure whether to act and how to handle ambiguity, not only task completion. This does not establish behavior of local multilingual models or effects of quantization; the paper's task mix and judge validation must be reviewed before adopting scores. No full paper, environment or traces were inspected.

### Capability removal

[Beyond Data Filtering: Knowledge Localization for Capability Removal in LLMs, 2512.05648](https://arxiv.org/abs/2512.05648) was read at abstract/metadata level. Authors study Selective GradienT Masking during training, including synthetic bilingual-language removal and biology-knowledge removal, with retain/forget and adversarial-finetuning evaluations.

Relevance is the need to assess retained ability, targeted losses, and recovery separately. This is training-time intervention research, not post-training quantization evidence. Its reported robustness cannot support claims that low-bit models selectively lose languages, or that observed score drops prove knowledge removal. Full methods and artifacts remain unread.

## Tokenizer adaptation and public community availability

### SuperBPE

[SuperBPE: Space Travel for Language Models, arXiv v3 2503.13423](https://arxiv.org/abs/2503.13423v3) was read at abstract/metadata level. It introduces a BPE pretokenization curriculum that learns subwords and then tokens crossing whitespace. Authors report controlled from-scratch 8B pretraining comparisons with fixed model size, vocabulary size and training compute, and downstream/encoding-efficiency improvements.

This is relevant to token-length and vocabulary design as separate experimental factors. It is not evidence that replacing an existing model's tokenizer preserves its learned behavior, nor that token compression explains this project's paired low-bit score changes. Full training data, language-specific breakdowns and methods were not reviewed.

### Token Distillation

Read the [ICLR 2026 proceedings abstract](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e3cd4c3748274cfde024873d4ae91600-Abstract-Conference.html) and [official README overview](https://github.com/konstantinjdobler/token-distillation). Konstantin Dobler, Desmond Elliott and Gerard de Melo propose learning input embeddings for new tokens by distilling representations produced with the original tokenization. The README explicitly distinguishes input embeddings from output embeddings, for which it implements next-token-prediction learning. Search results for [arXiv 2505.20133](https://arxiv.org/abs/2505.20133) can retain the earlier name *AweDist*; pin the intended version/title.

This is a concrete adaptation-method lead if tokenizer intervention becomes a separately trained experiment. It does not authorize silently swapping a tokenizer during a quantization comparison. Full methods, output-embedding treatment, model compatibility and Bengali transfer performance remain unverified; no adaptation was performed.

### South Asian community surfaces

- [1-800-LLMs public Hugging Face organization](https://huggingface.co/1-800-LLMs): organization card and visible model/dataset listings were read. It identifies multilingual/Indic work and self-curated synthetic data. This establishes a public discovery surface, not benchmark validity or suitability.
- [SA-LLM-Benchmarks dataset lead](https://huggingface.co/datasets/1-800-LLMs/SA-LLM-Benchmarks): browser retrieval failed and an unauthenticated public Hub API check returned HTTP 401. Its contents and public availability could not be verified; the response does not distinguish private, removed, renamed, or otherwise unavailable resources. No private sheet or authenticated workaround was opened.
- [South Asian languages Luma calendar](https://luma.com/CLSouthAsianLanguages): browser text retrieval failed; an unauthenticated HTTP check returned 200. Reachability is confirmed, but calendar contents, events, dates and participation terms were not verified. Treat as a community follow-up lead, not a research source.

## Practical follow-up priorities

1. Keep this project's paired scoring and provenance intact; map an export to a pinned Every Eval Ever schema only after inspecting its definitions.
2. Review Tiny Facade's actual artifacts, task construction, parser and runtime settings before comparing its quantization direction with this project's observations. Treat it as related work, not confirmation.
3. Audit Bengali representation and score extraction with paired native-script, Romanized, mixed and register-varied examples. Native review and semantic equivalence matter; translation alone does not establish a valid control.
4. Add safety, tool use or extraction only as separately scoped future evaluations with task-appropriate metrics and benign controls where needed. Avoid combining unrelated metrics into a single language-quality claim.
5. For any future speed study, measure this deployment's hardware and distinguish prompt processing, generation, end-to-end latency and correctness. Record revisions and matched configuration before interpreting differences.

These sources show substantial existing multilingual evaluation and community experimentation. They support a narrowly documented project contribution, not a claim of being first or of universal quantization behavior.
