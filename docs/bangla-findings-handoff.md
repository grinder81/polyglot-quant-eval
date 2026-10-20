# Tiny Aya Bangla findings and independent review handoff

Prepared for Shoha and an independent reviewing agent on 20 October 2026.
Baseline measurements were completed on 18 October; the qualitative translation
review followed in conversation. This handoff separates recorded measurements
from provisional interpretations and proposed experiments.

## Purpose and current conclusion

The research goal is better Bangla behavior within a mobile deployment budget,
with model-internals investigation and targeted modification as the eventual
contribution. Stage 1 establishes behavior before changing learned weights.

The completed 50-question-per-language comparison found identical predictions
from original BF16/vLLM and converted BF16 GGUF. The official four-bit artifact
scored seven fewer correct answers overall. Bangla lost only one correct answer
net, but seven individual choices changed. Two of those seven have suspected
translation ambiguities. The remaining cases motivate behavioral probes, not
claims about a defective layer or architectural mechanism.

The reviewer should challenge the interpretation, especially translation
judgments, error categories, and any attribution to quantization. No corrected
question experiment, fine-tuning, activation intervention, or architecture change
has been run.

## Primary evidence

All paths below are relative to this repository.

- [Completed baseline report](../results/stage1/fifty-per-language/README.md)
- [Recomputed summary and paired comparisons](../results/stage1/fifty-per-language/summary.json)
- [All 15 changed answers with prompts and scores](../results/stage1/fifty-per-language/changed-answers.json)
- [Schema-compatible accuracy rows](../results/stage1/fifty-per-language/rows.jsonl)
- Raw five-question checkpoints: `results/stage1/fifty-per-language/{bf16-vllm,bf16-gguf,q4}/`.
- Artifact, code hashes and package inventories: the three `*-runtime.json`
  files alongside the checkpoints. Each arm has an `identity.json`.
- [Summary validator](../scripts/summarize_baseline.py)
- [Evidence and accounting test](../tests/test_baseline_summary.py)
- [Merged results change](https://github.com/grinder81/polyglot-quant-eval/pull/12)
- [Earlier ten-question smoke results](../results/stage1/ten-question/README.md)

The fifty-question results supersede the ten-question smoke run for this
comparison. They are not independent of it: the development sample overlaps.

## Measured results

| Language | Original BF16 in vLLM | BF16 GGUF | Q4_K_M GGUF | Q4 minus BF16 | Delta relative to English delta |
|---|---:|---:|---:|---:|---:|
| English | 35/50, 70% | 35/50, 70% | 33/50, 66% | −4 pp | 0 pp |
| Bangla | 31/50, 62% | 31/50, 62% | 30/50, 60% | −2 pp | +2 pp |
| Hindi | 27/50, 54% | 27/50, 54% | 23/50, 46% | −8 pp | −4 pp |
| Overall | 93/150, 62% | 93/150, 62% | 86/150, 57.3% | −4.7 pp | — |

The two BF16 arms agree on all 150 selected choices, not just their accuracy
totals. Their likelihood values differ. Q4 changes 15 choices: nine correct to
wrong, two wrong to correct, four wrong to a different wrong choice.

| Language | Changed choices | Correct to wrong | Wrong to correct | Wrong to another wrong |
|---|---:|---:|---:|---:|
| English | 2 | 2 | 0 | 0 |
| Bangla | 7 | 3 | 2 | 2 |
| Hindi | 6 | 4 | 0 | 2 |

These are descriptive development results. Fifty items per language do not
establish general language rankings, equivalence, or statistically reliable
language-specific compression effects. Matched translations share underlying
questions; uncertainty calculations must account for that dependence.

## Evaluation contract and attribution limits

Belebele revision `7899cdfa4e1e0d733fd77c848e2c273cb1d32be2`;
subsets `eng_Latn`, `ben_Beng`, `hin_Deva`. Frozen first 50 aligned examples
per language, seed 42, zero shots, no chat template, context 8192. The unchanged
upstream harness scores the continuations ` A`, ` B`, ` C`, ` D` and selects
the highest likelihood; reported accuracy is raw `acc`. These are selected
options, not generated explanations.

GGUF uses upstream GGUFLM through llama-cpp-python; original BF16 uses upstream
LocalCompletionsAPI with its HF tokenizer, tokenized requests and BOS. No custom
scoring adapter was introduced. The validator checks unique identities,
matching prompts and targets, finite candidate scores, recomputed accuracy,
runtime manifest hashes, and paired accounting.

The official Q4 artifact's precise source checkpoint and quantizer provenance
remain unknown. Even the same-runtime BF16 versus Q4 comparison is therefore an
audited-artifact comparison, not definitive proof that rounding alone caused
every change. The vLLM client also uses a mixed dependency environment, documented
in the report, rather than a newly consolidated environment lock.

No controlled generation throughput, peak RAM/VRAM, energy, or phone measurements
were made. Evaluation request duration is not a generation-speed benchmark.

## Seven Bangla cases and provisional labels

Document IDs identify saved upstream records, not positions in the sample.
Both BF16 arms made the same choices.

| Document | Subject | Key | BF16 | Q4 | Provisional interpretation |
|---|---|---|---|---|---|
| 873 | Winning goal | A, Bäckström | A | B, Jagr | Person-to-action association |
| 817 | MRI patent year | B, 1974 | B | A, 1977 | Event/date distinction and relative-date inference |
| 866 | Travel group size | B, four people | B | D, six or more | Range/scope interpretation; some wording ambiguity remains |
| 270 | Airline coverage | B, Star Alliance | A, SkyTeam | B | Coverage and negation distinction; Q4 improves |
| 522 | Ice rescue | D, melting ice | A, bad weather | D | Negated question; Q4 improves |
| 462 | Castle features | B, attack-resistant foundation | A, large windows | D, thin walls | Suspected translation-induced question ambiguity |
| 801 | Skiing terrain | C, Alpine style | A, ski hiking | D, ski backpacking | Suspected translation/reference ambiguity; synonymous distractors |

### Winning goal

The passage links Bäckström to the game-winning goal, assisted by Ovechkin.
Jagr appears in a separate historical scoring comparison. Q4 selects Jagr.
This is consistent with an entity/action association error, but the model's
internal cause is unmeasured.

### MRI patent

The passage gives 1970 for the diagnostic-method development and says a patent
was granted four years later. It separately gives 1977 for scanner completion.
BF16 selects 1974; Q4 selects 1977. Possible explanations include confusion
between events, failure to resolve the relative date, or distractor preference.
The evidence cannot distinguish these yet.

### Travel group size

The passage recommends four to six people to reduce cost. BF16 selects four
people; Q4 selects six or more. The latter extends the stated interval beyond
six, but the opening also says larger groups are cheaper. This makes the case
less decisive than a clean bounded-range probe. The earlier conversational
label of a clear range error was too strong; a reviewer should examine the
aligned English wording before treating it as such.

### Airline coverage

The passage says SkyTeam covers none of the ocean crossings and Star Alliance
covers all except one. BF16 selects SkyTeam; Q4 selects Star Alliance, the key.
The Bangla translation is awkward. This is consistent with better handling of
coverage/negation in this one Q4 prediction, not proof of a general improvement.

### Ice rescue

The question asks which condition is NOT a current problem. Bad weather, ice
quantity, and ice density are listed; melting ice is not. BF16 selects bad
weather, Q4 selects melting ice. This single case contradicts a simple narrative
that all observed Q4 changes worsen negation.

## English and Bangla translation review

These observations compare saved aligned prompts; no benchmark labels or scores
have been changed. They have not undergone an independent linguistic review.

### Castle

English asks which feature “would be considered atypical for Kirby Muxloe
Castle.” The passage describes a lightly fortified house whose large windows
and thin walls would not withstand a sustained attack. An attack-resistant
foundation is the intended atypical feature.

Bangla asks:

> সেই সময়ে কিরবি মাক্সলো দুর্গের কোন নির্মাণ বৈশিষ্ট্যটি অন্যান্যদের থেকে আলাদা ছিল?

This reads as which actual feature distinguished the castle from others,
rather than which hypothetical feature would be atypical for it. Both large
windows and thin walls are explicitly mentioned. The English makes the keyed
answer understandable; the Bangla weakens that interpretation.

Proposed diagnostic wording, not applied to the benchmark:

> অনুচ্ছেদে বর্ণিত কির্বি মুক্সলো দুর্গের সঙ্গে নিচের কোন নির্মাণ বৈশিষ্ট্যটি অসংগত হবে?

Choice C also changes “less fortification than some castles” into a statement
about fewer troops. The whole item needs review, not only its question.

### Skiing

English distinguishes ski backpacking from “alpine style ski touring or
mountaineering,” with “the latter ones” done on steep terrain. The question asks
which kind of skiing occurs on steeper terrain; the key is Alpine style.

Bangla says:

> আলপাইন স্কি টুরিংয়ের পদ্ধতি এবং পর্বতারোহণের মধ্যে মিল থাকলেও এটি একে অপরের সঙ্গে জড়িত নয়, দ্বিতীয়টি খাড়া ভুখণ্ডে করতে হয়...

The comparison changes, and “দ্বিতীয়টি” appears to refer only to mountaineering.
The connection to Alpine style is therefore less clear. Neither selected answer
is established as correct by this observation.

The passage calls ski backpacking, backcountry skiing, ski touring and ski
hiking names for the same activity. Thus the A-to-D change switches between
synonymous wrong options and is weak evidence of a substantive change in
understanding.

A spoken intermediate explanation incorrectly described the English question
as asking which activity is unusual. It asks which occurs on steep terrain.
The saved prompt, not that spoken explanation, is authoritative.

## What is not established

- A general Bangla negation weakness, or a consistent worsening from Q4.
- That any particular attention head, MLP, layer, tokenizer component, or
  architectural choice caused these behavioral changes.
- Whether targeted adaptation beats standard LoRA, random component selection,
  improved training data, or ordinary calibration.
- That a plausible label such as fact linking represents one shared mechanism.
- That correcting translations will repair model answers. No such rerun exists.

A causal activation intervention could identify an effective intervention point
without proving architecture was the original cause. Training data and learned
weights jointly shape internal representations.

## Proposed next experiments for reviewer assessment

1. Independently review the seven Bangla items against their aligned English
   versions, especially castle, skiing, and the group-size question.
2. Preserve all official scores. Keep corrected-wording tests separate, with
   original and edited prompts retained.
3. Construct small balanced development probes for person/action binding,
   event/date distinctions, bounded ranges, and affirmative/negated questions.
   Control answer order, distractors, wording, and topic; include English matches.
4. Establish repeatable behavioral differences before internal attribution.
   Inspect attention/MLP activations and test controlled interventions only
   against matched controls.
5. If adaptation follows, compare targeted components with standard and random
   selections under matched trainable-parameter/data/compute budgets, then
   evaluate unseen topics and compression survival.

The independent review should state which claims it confirms, disputes, or
cannot assess, with references to saved examples. Particularly useful outputs
are revised error labels, a translation-quality assessment, and the smallest
experiment that could falsify the fact-linking hypothesis. This handoff does
not itself authorize new model runs or scoring changes.

## Engineering state and contribution opportunities

Our repositories are [tiny-aya-edge](https://github.com/grinder81/tiny-aya-edge)
for artifacts/runtime setup and this repository for evaluation. Local upstream
source copies support two fixes; no upstream contribution PR has been submitted.

- llama.cpp: Tiny Aya digit pre-tokenization split whitespace incorrectly.
  Scoped local fix restored the frozen prompt/candidate token checks.
  [Future contribution tracking](https://github.com/grinder81/tiny-aya-edge/issues/18).
- llama-cpp-python: fixed-size token-to-text buffer accepted a negative
  required-length result and truncated long Bangla tokens. Local fix resizes,
  retries and validates the return.
  [Future contribution tracking](https://github.com/grinder81/tiny-aya-edge/issues/19).
- Python echo ranking: full Python vocabulary sorting dominated likelihood
  requests. Local optimization preserved validated likelihood outputs while
  reducing integration overhead. This was not a change to model inference math
  or benchmark scoring.

All baseline results and engineering fixes are recorded through PRs. Larger
planned evaluations remain open in
[the baseline issue](https://github.com/grinder81/polyglot-quant-eval/issues/5).
The completed run's monitoring automation is paused. No model training or
background evaluation is part of this handoff.
