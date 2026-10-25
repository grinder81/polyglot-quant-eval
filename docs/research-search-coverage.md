# Research discovery coverage and supporting resources

Search date: 25 October 2026. This records a targeted community and public-source search, including the immediately preceding discovery pass. It is not a complete export of Discord, a systematic review, or evidence that missing results do not exist. Search rankings, permissions, deleted messages, attachments and mutable pages limit coverage. Raw community messages and private working documents are not public evidence and are not copied here.

## Search coverage

Discord was used to discover topics and public links. Primary papers, author repositories, model/dataset cards and official project pages were then inspected to support the public summaries. General search and secondary pages were discovery tools, not authorities for technical conclusions. No community endorsements are inferred from a shared link.

| Surface | Searches/coverage inspected | Outcome relevant to this review |
|---|---|---|
| Server-wide search | `quantization` first five result pages in the initial pass; `Bangla`, `Bengali`, `tiny`, `tiny aya`, `likelihood`, `llama.cpp`, code-mixing and EvalEval searches | Multilingual quantization paper, local model projects, Bengali resources, evaluation infrastructure. The broad quantization history was not exhausted. |
| Systems and theory | Recent channel messages, `mixed precision` first result page, systems/quantization talk links | Precision training is often conflated with deployment bit allocation; separate them. Public sources include MobileLLM, SpinQuant, TorchAO, VPTQ and quantization tutorials. |
| Local AI | Two result pages in the initial pass | Deployment/configuration and profiling topics; hardware-specific claims need public artifacts and matched settings. |
| NLP | Recent result page plus server-wide multilingual/Bangla searches | Tokenization, multilingual evaluation and small-language-model leads. |
| Indic/South Asian languages | Recent result page; `in:llm-for-indic-languages has:link` first page | IndicPHI, SuperBPE, Token Distillation, public HF organization and benchmark-availability lead. Private annotation sheets and shared working documents excluded. |
| BIRDS | Tiny Aya/tokenization and induction-head discussion discovery; `in:birds has:link` first page | Public implementation-program website and recordings index. Announcement of a replication is not a verified replication result. |
| ML understanding | Two result pages in initial pass; targeted quantization search | Workspace/Jacobian-lens resources. No matching targeted quantization result was returned; this does not establish absence. Unpublished group findings excluded from scientific claims. |
| Safety/alignment and privacy/security | Recent safety results and privacy search results in initial pass; calibration search first page | Safety-compression bibliography, agent/contextual evaluation leads. No inference that these groups endorse the project. |
| ML agents | Recent result page in initial pass | Judge-validity and controlled tool execution as future evaluation concerns. Private proposals excluded. |
| Interesting reads | `in:interesting-reads quantization` | Pruning-versus-quantization primary paper. |
| Research advice/resources | First page of channel search | Research process and mentorship discussion; no additional compression evidence retained from that page. |
| Find collaborators | `in:find-collaborators quantization` | No results returned for that exact query; other terms/history remain unexhausted. |
| Public web and linked citations | Multilingual calibration; language-aware mixed precision; Bangla quantization; answer flips/churn; regional-language quantization; source-ledger follow-ups | Direct overlaps beyond the original Discord pass, notably TASA, Bangla evaluation, Bavarian comparison and FlipEval. |
| Second-pass public web, 25 October | Language-aware repair of quantized models; calibration language in pruning; per-tensor GGUF allocation precedents; K-quant degradation curves; Indic imatrix pilots; Belebele under quantization; multilingual KV-cache quantization; language-neuron-guided allocation | Added Language-Conditional Dequantization, Kurz et al., Unsloth Dynamic GGUFs, the llama.cpp K-quant evaluation of Llama-3.1-8B and the indic-quant pilot; surfaced the Belebele and Hindi tables inside Marchisio et al. Not found: language-neuron-guided precision allocation, any multilingual KV-cache quantization evaluation, any per-language Tiny Aya GGUF benchmark. Absence in this bounded search is not evidence of absence. |

The review stops at an actionable, documented source set with explicit gaps, rather than presenting an unbounded search as complete. Older pages, recordings without inspected transcripts, gated datasets, private documents and external code execution remain outside the verified evidence. Result counts can include quoted replies and change while searching; they are not unique-paper counts.

## Community navigation map

These channel links require community access. They are navigation aids, not public citations for scientific claims. Public calendars are discovery links; schedules and participation availability have not been verified here.

| Best use | Channel | Public entry point |
|---|---|---|
| Runtime/scoring controls, quantization methods | [ML systems and theory](https://discord.com/channels/987824841656791130/991440861848158318) | [Systems calendar](https://luma.com/CLSystemsTheory) |
| Local runtime/device configuration | [Local AI](https://discord.com/channels/987824841656791130/1551603154976645130) | Use the channel's current public-resource links |
| Multilingual tasks, tokenization, judging | [NLP](https://discord.com/channels/987824841656791130/991440413745500210) | [NLP calendar](https://luma.com/CLNLP) |
| Native annotation and code-mixing resources | [Indic languages](https://discord.com/channels/987824841656791130/1471235838464495851) | [South Asian calendar](https://luma.com/CLSouthAsianLanguages), [HF organization](https://huggingface.co/1-800-LLMs) |
| Reproduction and implementation learning | [BIRDS](https://discord.com/channels/987824841656791130/1072977583542632478) | [Public program](https://labscommunity.cohere.com/community-programs/birds), [calendar](https://luma.com/CLBIRDS) |
| Representation probes and intervention interpretation | [ML understanding](https://discord.com/channels/987824841656791130/1384598008016011405) | [Calendar](https://luma.com/CLMLUnderstanding) |
| Future permission/intervention evaluation | [ML agents](https://discord.com/channels/987824841656791130/1380600861604188301) | [Calendar](https://luma.com/CLMLAgents) |
| Future safety endpoints and privacy controls | [Safety/alignment](https://discord.com/channels/987824841656791130/1194399784853831820), [privacy/security](https://discord.com/channels/987824841656791130/1466509362108432587) | [Safety calendar](https://luma.com/CLSafetyAlignment), [privacy calendar](https://luma.com/CLPrivacySecurity) |

This is a suggested topic-to-channel match based on observed channel subjects and public resources, not permission to post or a claim that leads are accepting collaborators. Ask one focused technical question at a time; do not cross-post the same promotion everywhere.

## Supporting sources checked

| Public source | Read depth, finding and limit | Implication |
|---|---|---|
| [Outliers and Calibration Sets have Diminishing Effect, v3](https://arxiv.org/html/2405.20835v3), 5 June 2024 | Relevant §4.3 and §6 text inspected. Modern-model results were more robust than OPT under the tested calibration changes. Language-calibration comparisons use ARC-Challenge/PIQA/WinoGrande aggregate accuracy, not proof of quality retention in all calibration languages. | Counterweight to assuming calibration-language harm is universal. Model, metric and quantizer differences can explain apparent disagreement with later multilingual-perplexity work. |
| [MixQuant, v1](https://arxiv.org/abs/2607.23047v1), 25 July 2026 | Abstract read. Authors report layer sensitivity depends on upstream precision and propose marginalizing distortion over quantized upstream configurations. No quantitative results or implementation audited. | Independent one-layer maps may miss interactions; real-build validation remains necessary. |
| [AlignQuant, v1](https://arxiv.org/abs/2610.07457v1), 5 October 2026 | Abstract read. Allocates precision in GPU-compatible tiles shared by storage and execution; separate prefill/decode calibration. Speedup claims not reproduced. | A bit allocation that saves storage does not automatically produce faster supported kernels or a phone speedup. |
| [Pruning vs Quantization, v2](https://arxiv.org/abs/2307.02973v2), 16 February 2024 | Abstract read; analytical and empirical comparison across eight networks/three tasks generally favors quantization except some very high-compression settings. | Supporting compression context, not evidence selecting a Tiny Aya intervention. |
| [What Do Compressed Multilingual MT Models Forget?](https://aclanthology.org/2022.findings-emnlp.317/), EMNLP 2022 | Publisher abstract read. Language averages can hide under-represented-language losses and some medium-resource improvements; studies FLORES-101, MT-Gender, DiBiMT. | Prior art for disaggregation, not a Tiny Aya causal mechanism. |
| [On the Fairness Impacts of Hardware Selection, v2](https://arxiv.org/abs/2312.03886v2), 30 August 2024 | Abstract read. Studies demographic disparities associated with hardware and training dynamics. | Supports recording hardware; does not establish this project's inference/cache issue or language interaction. |
| [Beyond Perplexity](https://aclanthology.org/2024.findings-emnlp.901/), EMNLP 2024 | Publisher abstract read. Compression effects differ across generation toxicity, representational bias, dialect bias and utility. | Future safety work needs separate endpoints; MCQ accuracy cannot establish safety. |
| [Give Me BF16 or Give Me Death?](https://aclanthology.org/2025.acl-long.1304/), ACL 2025 | Publisher abstract read. Llama3.1-family FP8/INT8/INT4 study includes academic and real-world tasks and generated-text differences. | Quantizer and workload matter; neither reported losslessness nor throughput transfers universally to Tiny Aya. |
| [Awesome LLM Compression Safety](https://github.com/upunaprosk/Awesome-LLM-Compression-Safety) | Public bibliography inspected; links traced to selected primary sources above. Mutable, no commit pinned. | Useful ongoing discovery index, not a source of independently validated aggregate conclusions. |
| [TorchAO](https://github.com/pytorch/ao) | README checked. Includes training/inference/mobile workflows and a notice consolidating new development into torch primitives and consuming frameworks. No installation or code audit. | Recheck maintained integration paths before later backend experiments; old talk instructions may be stale. |
| [VPTQ](https://github.com/microsoft/VPTQ) | README checked; vector quantization and low-bit model examples. Community checkpoints explicitly lack guaranteed performance. | Alternative-format lead; nominal bits do not establish matched bytes, compatible kernels or multilingual quality. |
| [J++ Lens](https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr), 8 October 2026 | Author introduction and Figure 1 description read: improved latent-variable readout recall in tested models. Not a full methods or causal audit. | Representation accessibility is not a causal precision-allocation map; a probe's readout is not model preference. |
| [Workspace Bench](https://github.com/camila-blank/workspace-bench) | Public repository landing verified (redirect from older owner spelling); implementation unread. | Interpretability evaluation lead, not evidence of a compression mechanism. |
| [BIRDS public program](https://labscommunity.cohere.com/community-programs/birds) | Program text and recordings index read; NLP track includes tokenization and multilingual challenges. Recordings not watched. | Reproduction/learning route; no claimed Tiny Aya replication result. |

## Retained discovery leads, not verified findings

These preserve relevant links found during discovery without promoting an announcement, model card or unviewed talk to evidence. They are lower priority than the fully inspected overlaps in the other ledgers.

- [Kelly Marchisio multilingual quantization talk](https://www.youtube.com/watch?v=wjFdFW6KcIw): recording link discovered; paper reviewed separately.
- [Albert Tseng MXFP4 training talk](https://youtu.be/1gcUQ-31Kdw): recording link discovered; training precision is distinct from weight-only deployment allocation.
- [HQQ/GemLite event](https://cohere.com/events/Cohere-Labs-HichamBadri-2025): public retrieval unavailable in this pass; no claims imported.
- [Educational vector-quantization implementations](https://github.com/aniervs/vq-algos): link discovered; web fetch failed. Not used as production validation.
- [GPTQ walkthrough](https://youtu.be/6J_0BDqMFi0), [int8 walkthrough](https://youtu.be/rzMs-wKQU_U), [quantization introduction](https://youtu.be/LK2-lrLvhTA): unviewed learning resources.
- [Tiny Aya Vision](https://labscommunity.cohere.com/blog/2026/tiny-aya-vision/), [simultaneous translation organization](https://github.com/orgs/tiny-aya-simultaneous-translation/): adjacent deployment/adaptation leads; no quality assertions imported.
- [Maverick Unity repository](https://github.com/mcbu-xrlab/Maverick-Unity), [author article](https://huggingface.co/blog/ErenAta00/maverick-4b-unity-xr-agent), [GGUF model card](https://huggingface.co/ErenAta00/Maverick-4B-Unity-XR-Agent-GGUF): small local structured-agent comparison lead; timing/benchmark claims unverified.
- [Tiny Aya Offline app](https://play.google.com/store/apps/details?id=com.reubencf.tinyaya): deployment discovery only; not installed or benchmarked.
- [Induction heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/): foundational primary resource; full retrieval exceeded the web-tool size bound. No causal transfer to Tiny Aya asserted.
- [Goodfire interpretability talk](https://youtu.be/jrApblKyLSQ), [contextual integrity talk](https://www.youtube.com/watch?v=ZXeRjVnVndQ): unviewed recordings; future interpretability/privacy reading.
- [Intel CPU inference paper](https://arxiv.org/abs/2311.00502), [Olmix](https://arxiv.org/abs/2602.12237), [BabyLM multilingual call](https://arxiv.org/abs/2602.20092): discovered scope leads; no quantitative claims retained.

Private annotation trackers, unpublished steering and code-mixing proposals, personal profiles/contact details, meeting credentials, peripheral promotional claims and unrelated discussions were deliberately excluded. We did not establish that a community lead's present availability, a demo's benchmark, or a shared link's license permits reuse. Public availability and scientific validity remain separate checks.

## Unresolved evidence tasks

- Read final publication versions and relevant appendices before quoting abstract-only results in a manuscript; verify apparent prose/table inconsistencies against PDF and supplements.
- Pin mutable code/schema/dataset revisions before adoption. Audit FlipEval's resampling unit against passage dependence and Every Eval Ever's provenance fields.
- Obtain public artifact identities for close Tiny Facade comparisons before interpreting their reported direction against T1.
- Check licenses, semantic equivalence, human validation and pool contamination before adding any Bengali/Indic task. The inaccessible SA-LLM benchmark is a lead, not available evidence.
- Language-Conditional Dequantization covers Hindi but not Bengali, only INT3 GPTQ, and compares against a language-agnostic adapter on one model and four languages; its final version and any Bengali follow-up should be checked before quotation. The Unsloth selection method and imatrix composition are undocumented and unpinned.
- Re-run a focused novelty search against the eventual intervention and completed results. No paper set can certify absence of prior work.

The [main review](research-landscape.md) maps these gaps to the existing experiment gates. No follow-up listed here implies permission for new inference or a protocol change.
