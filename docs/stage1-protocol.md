# Stage 1 baseline protocol

Status: protocol for review; no model measurements performed. Implements the planning
portion of [Stage 1.1](https://github.com/grinder81/polyglot-quant-eval/issues/2).
Artifact and dataset locks are execution gates, not fabricated values in this document.

## Purpose and scope

Establish reproducible English, Bangla and Hindi baselines before changing model weights.
The broader research goal is to identify where to adapt Tiny Aya for Bangla and test
whether gains survive compression under a mobile deployment budget. Compare targeted
adaptation against standard and random selection with matched budgets in later stages.
Precision allocation, calibration and QAT remain candidate methods, not a mandated order.
Keep the existing fourteen-language configuration and results schema unchanged.

Stage 1 does not establish native-speaker quality, a language-specific causal mechanism,
or phone performance. It does not train, prune or repair a model. The eventual candidate
limit is 2,200,000,000 total shipped bytes: model, tokenizer and any adapters, counted once.
Bits per weight is descriptive, not an additional acceptance threshold. Diagnostic and
reference builds may exceed the limit. The primary phone is iPhone 15; Mac M2 Pro is the
build host and optional MLX smoke target. Android hardware is not a prerequisite.

## Starting repository audit

| Repository | Inspected main commit | Ownership |
|---|---|---|
| polyglot-quant-eval | `870e7ea1a4ff9e11eeb2bba15789971d5d094fbb` | scoring, data partitions, reports |
| tiny-aya-edge | `8c171d0b4b652b89cf0f5c7a7fb06f037cc61b46` | artifacts, runtime setup, device measurements |

The harness checkout started clean. README, CLAUDE.md, task/language configuration,
smoke and report scripts were inspected. Companion README and CLAUDE.md were inspected
at its recorded revision through GitHub; no companion working checkout was modified.

Resolved here: adaptation is the broader direction; shipped bytes govern candidate size;
vLLM remains the canonical reference. Companion documentation still describes compression
as primary and an additional 5-bit limit; reconcile it in a separate companion PR.

Known implementation gates, deliberately outside this documentation PR:
- The smoke script currently applies a chat template; canonical Stage 1 MCQ scoring must not.
- The reporter currently groups by format and averages runs. It must distinguish runtime,
  sample manifest, scoring settings and reference before producing baseline deltas.
- Task names and endpoint logprob support are unverified. The setup brief assumes Linux;
  choose and record a supported execution environment on the Windows RTX host first.

## Three comparison arms

| Arm | Weights | Runtime | Interpretation |
|---|---|---|---|
| A | original Global BF16 | vLLM, RTX CUDA | canonical study reference |
| B | BF16 GGUF converted from exactly A | llama.cpp, RTX CUDA | conversion/runtime control |
| C | official Global Q4_K_M GGUF | same llama.cpp commit as B | downloaded deployment baseline |

Report C minus A as the end-to-end deployment difference, B minus A as the
conversion/runtime difference, and C minus B as the same-runtime compressed difference.
C minus B is not a clean quantizer-only causal estimate unless base revisions and
conversion provenance are established. Unknown official provenance stays unknown.
If needed, a locally quantized matched build is a separately approved follow-up arm.
Do not silently replace A with B if vLLM fails. Do not assume both servers fit at once.

Pin `CohereLabs/tiny-aya-global` and `CohereLabs/tiny-aya-global-GGUF` to immutable
Hub commits before downloading artifacts. Record filenames, SHA-256 and exact bytes;
tokenizer files and chat template hash; conversion command and converter commit;
runtime commit/version and launch arguments. Verify the downloaded model configuration.
Record official quantizer version and calibration as null/unknown unless evidenced;
the serving runtime commit does not establish how an official file was quantized.
If Q4_K_M is absent, report available formats and revise the protocol before substituting.

## Scoring and sample lock

Canonical task: Belebele, zero-shot, upstream `acc`, `loglikelihood_mcq`, no chat template.
Use the upstream task's exact candidate text and scoring rule; do not substitute generated
letter answers or length-normalized scores. Audit all three language tasks in the pinned
lm-eval installation. Global-MMLU is conditional: add five-shot accuracy only after all
three task definitions, splits and scoring paths are confirmed. MGSM is registry audit
only in this stage. Do not silently change the broader task configuration.

Before the first scored run, commit a small lock manifest under `results/stage1/` containing:
- Immutable dataset revisions, configurations, split names and lm-eval commit/version.
- Ordered sample IDs and source-document IDs with content hashes. Select 300 examples
  per language deterministically using seed 42, preserving aligned item identities where
  the dataset provides them. The first 50 are the smoke subset, not an independent sample.
- For five-shot tasks, five fixed demonstrations per evaluated item, their IDs and hashes,
  drawn only from the designated upstream demonstration split, excluding evaluated items
  and source documents. If this cannot be ensured, keep that task excluded and report why.
- Python, NumPy, framework and few-shot seeds all set to 42; effective CLI/config recorded.
- Exact rendered prompt and candidate hashes, tokenizer revision, special-token/BOS/EOS
  policy, candidate-boundary tokenization, request adapter and context settings.

Use identical prompts, candidates and ordered items across arms. Compare token IDs and
candidate boundaries on the smoke subset across the HF and GGUF tokenizer paths; a
mismatch blocks a controlled comparison until explained. Context limit is 8192 for this
protocol. Do not silently truncate: identify overlength items before locking samples,
exclude them consistently across arms and record exclusions. Replacements follow the
same seeded order. Record actual n, not just requested limit.

MCQ likelihood scoring has no sampling temperature. A separate Bangla chat smoke uses
the pinned chat template, greedy decoding and a maximum of 40 new tokens. Keep its text
and outputs as plumbing observations, not benchmark evidence or a fluency score.

All repeatedly inspected Stage 1 examples are development/baseline data, even if the
upstream split is called test. Reserve a separate final test pool before adaptation.
The intentions in `configs/data_pools.yaml` do not claim that disjointness is verified.

## Reporting contract

Keep existing JSONL schema and append-only rows. Preserve run ID, model revision, runtime,
mode, fewshot, seed, sample count and source-file references. Put additional provenance
in the linked run manifest and refer to it from notes; do not invent measurements.
Keep smoke and full runs separate. Never average A and B because both have format bf16.
For each reference R and language L, report 100 * (accuracy(candidate,L) - accuracy(R,L))
in percentage points. Also report delta(L) minus delta(English) for that same comparison.
Include absolute accuracy, n and available uncertainty. Small deltas are exploratory;
an observed gap alone does not establish language-specific compression damage.

## Gates and small-PR sequence

1. This PR: protocol, pool intentions and documentation alignment only.
2. [RTX environment](https://github.com/grinder81/tiny-aya-edge/issues/2), then
   [artifact locks](https://github.com/grinder81/tiny-aya-edge/issues/3): C1 requires
   environment evidence, model configuration and provenance manifests.
3. [Runtime arms](https://github.com/grinder81/tiny-aya-edge/issues/4) and
   [scoring audit](https://github.com/grinder81/polyglot-quant-eval/issues/3): C2 requires
   task audit, sample lock, valid likelihoods and canonical reference smoke results.
4. [Report separation](https://github.com/grinder81/polyglot-quant-eval/issues/4) precedes
   [matched baseline runs](https://github.com/grinder81/polyglot-quant-eval/issues/5).
5. [Stage report](https://github.com/grinder81/polyglot-quant-eval/issues/6): C3 reviews
   raw results, manifests, comparisons and limitations. Mac and CUDA microbenchmark
   evidence are separate supporting tasks in the companion tracker, not language evidence.

Stop after each PR for user review. Stop dependent measurements when a correctness or
comparability gate fails; record the failure rather than silently changing the experiment.
No model weights, credentials or machine-specific model paths belong in Git.
