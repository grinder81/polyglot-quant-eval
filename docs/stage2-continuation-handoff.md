# Tiny Aya Stage 2 — continuation handoff

Prepared 22 October 2026 (America/Los_Angeles). Audience: the agent taking over execution.

## Read this first

The study is compression-first: measure per-language damage under deployment formats, validate a sensitivity map, and test precision allocation at matched shipped bytes. Adaptation/LoRA is secondary and requires a user decision after compression evidence. Do not reinterpret the objective as attention adaptation or Bangla fine-tuning.

A1 (matched BF16 baseline), A2 (rotation control), and B7 (holdout reservation) are complete. The next experiment is A3, scoring-format validation. A3 has extensive offline preparation but no completed live variant comparison. The user asked the current agent to pause after A2; that pause was honored. This document is for transferring continuation, not a record that execution resumed. Have the receiving agent's user instruction establish resumption; once resumed, execute the approved sequence until a real decision gate or blocker. Do not invent permission for custom adapters, holdout exploration, or objective changes.

The active goal is paused. Its monitor `continue-approved-tiny-aya-stage-2` was deleted after completion. No evaluator or llama-cpp-python server was found in the live process check at handoff preparation. Inspect again before launching anything. Historical session IDs 47843, 51537 and 38761 are obsolete; do not use them to infer a live run.

## Workspace and ownership

Windows root: `C:/Users/shoha/Documents/ChatGPT/personal-development`.
WSL distribution: Ubuntu. Evidence/environment root: `/home/shohag/tiny-aya-stage1`.
Hardware: RTX 5090 in WSL. Do not confuse Windows RAM with GPU VRAM.

| Repository | Responsibility | Verified main at handoff |
|---|---|---|
| [polyglot-quant-eval](https://github.com/grinder81/polyglot-quant-eval) | Sample locks, upstream harness execution, statistics and quality evidence | `2079c21d24c965f3f77a4f70c3345ac0aaf7aa04` |
| [tiny-aya-edge](https://github.com/grinder81/tiny-aya-edge) | Runtime patches, pinned environments, quantized builds and device protocols | `aa8ec39` (resolve full SHA locally) |
| `llama-cpp-python-upstream` local checkout | Existing upstream decoding fix submission | Preserve branch/work; PR remains open |
| WSL native llama.cpp checkouts | Pinned quantizer and patched tokenizer library | Use manifests, not whichever checkout looks newest |

Read each repository's CLAUDE.md and applicable AGENTS.md before editing. `docs/stage2-plan.md` is identical in both repositories and governs the objective. Its historical 'Completed starting evidence' paragraph predates A1/A2; use the results and tracker below for current completion, not that paragraph as a live status report.

Evaluation repo has a pre-existing untracked `scripts/check_llama_echo.py`. Leave it untouched unless its ownership and use are explicitly established. Runtime repo was clean. No extra worktrees were present. All code/document changes go through small PRs. Standing user approval allows ready PRs to merge after CI passes; attach every created PR, update linked issues, and clean only associated merged branches/worktrees. Never commit weights or tokens.

## Completed evidence and what it means

### Initial reproducibility

Original BF16 in vLLM and BF16 GGUF in llama.cpp agreed on the original 150-question sample. Local Q4_K_M reproduced the official Q4's 150 answers and 600 candidate scores. That is observed behavioral reproduction on a sample, not identical files or universal parity. Original n=50/language runs retain their original runtime identity and must not be relabeled after tokenizer changes.

### A1: matched 300 per language

[PR24](https://github.com/grinder81/polyglot-quant-eval/pull/24), issue5 closed. Read `results/stage2/bf16-three-hundred/` and its report.

| Language | BF16 GGUF | Local Q4 | Q4 minus BF16, percentage points | Paired 95% interval |
|---|---:|---:|---:|---|
| English | 230/300 = 76.67% | 226/300 = 75.33% | -1.33 | [-3.83, 1.02] |
| Bangla | 188/300 = 62.67% | 189/300 = 63.00% | +0.33 | [-2.77, 3.64] |
| Hindi | 184/300 = 61.33% | 176/300 = 58.67% | -2.67 | [-6.29, 0.99] |

Overall 602/900 versus 591/900. Bangla-minus-English compression interaction +1.67 pp, CI [-2.33, 5.61]; Hindi-minus-English -1.33 pp, CI [-5.21, 2.61]. Intervals include zero, not proof of equivalence or absence of damage.

Answer changes: English17 (9 regressions,5 improvements,3 wrong-to-wrong), Bangla36 (12,13,11), Hindi37 (19,11,7). Net accuracy hides churn. These are BF16 GGUF comparisons; do not merge them with the vLLM reference or imply vLLM ran n=300.

### A2: option-rotation control

[PR35](https://github.com/grinder81/polyglot-quant-eval/pull/35), issue17 closed; report `results/stage2/rotation-control/README.md`, full machine-readable `validated-report.json`.

100 matched development questions per language, four cyclic option orders, two arms. Per arm: 1,200 contexts, 4,800 candidate scores, 240 shards. These are 300 unique questions, not 1,200 independent questions. Both arms completed; all 480 shards validated.

| Language | BF16 mean accuracy | Q4 mean accuracy | Q4-BF16 pp, paired 95% CI | BF16 / Q4 all-four content consistency |
|---|---:|---:|---|---|
| English | 76.75% | 76.25% | -0.50 [-2.78, 1.75] | 67% / 66% |
| Bangla | 60.00% | 60.50% | +0.50 [-2.23, 3.25] | 43% / 47% |
| Hindi | 57.75% | 55.25% | -2.50 [-6.12, 0.75] | 52% / 46% |

Content consistency maps predictions back to the original answer index. It does not require that answer to be correct. Rotations preserve content, so changing content selection is position sensitivity under this protocol. It does not localize a defective layer.

Raw A/B/C/D totals across 400 predictions per arm/language:

| Arm | English | Bangla | Hindi |
|---|---|---|---|
| BF16 | 141/89/90/80 | 193/71/73/63 | 168/69/83/80 |
| Q4 | 146/87/84/83 | 173/78/75/74 | 186/66/75/73 |

Gold totals are100 each. Cross-fitted letter-offset correction is diagnostic only: English mean BF16/Q4 79.25/77.75%; Bangla64/59%; Hindi62.25/58.50%. It helps BF16 Bangla but hurts Q4 Bangla, so do not adopt it as a universal fix or attribute all churn to a shifted letter prior. Canonical raw scoring is unchanged.

Statistics use 96 source clusters jointly across languages/arms, 10,000 bootstrap draws, seed42, refitting offsets per draw; zero invalid empty-fold replicates. Full report includes per-rotation results, paired flips, correction intervals, and differences of compression deltas versus English. Multiple development endpoints are exploratory; do not cherry-pick an interval excluding zero as confirmatory proof.

Raw evidence is committed beside the report; WSL source is `/home/shohag/tiny-aya-stage1/pilot/rotation-control`. Server logs remain there. Q4 resumed after interruption from94 completed shards with identical runtime/scoring and revalidated saved shards. Scoring checkout5212caf was retained throughout inference; reporting code is unchanged at157957f. Reports are complete, not pending.

### Interpretation to carry forward

The base model has a substantial English/Bangla gap on these reading-comprehension samples. Q4 Bangla damage relative to English has not been established. Option-position sensitivity is demonstrated in both precisions. Informal fact-binding/negation categories remain hypotheses, not established internal targets. Some examples have translation/reference ambiguity; keep original benchmark scoring and label separate human reviews. No final optimized model, phone speed claim, broad generation-quality result, or validated sensitivity map exists yet.

## First task for the receiving agent: A3

Issue [eval18](https://github.com/grinder81/polyglot-quant-eval/issues/18). Read:
- `docs/scoring-variant-control.md`
- `docs/chat-template-preflight.md` and `docs/chat-echo-boundary-probe.json`
- `docs/scoring-variant-render-check.json`, `docs/scoring-variant-bf16-tokens.json`, `docs/scoring-variant-q4-tokens.json`
- `scripts/prepare_scoring_variants.py`, `scripts/check_scoring_variant_tokens.py`
- Runtime `setup/probe_a3_client.py`, `results/a3-client-offline.json`, `results/a3-client-setup/README.md`, `setup/stage2_client_setup.sh`.

Three variants: unchanged plain prompt + letter; original chat template + letter; plain prompt + complete option text. Same100 questions/language and four rotations, BF16 GGUF and localQ4. Not a full chat-by-answer-format factorial. Primary prediction sums continuation log probabilities. Report upstream character-normalized acc_norm separately; normalization is Unicode character count of choice text, not tokens or UTF-8 bytes. Preserve delimiter, spaces, candidates and labels.

Prepared lock: `/home/shohag/tiny-aya-stage1/pilot/scoring-control/request-lock.json`, SHA256 `75486c22c0c25f7c6c9d3da6abfaaa0165babf4a5de24970147ab9d1488d9844`.
3,600 contexts/14,400 candidates per arm across variants; max717 tokens. Offline HF/GGUF token and roundtrip checks passed. Isolated API client at `/home/shohag/tiny-aya-stage1/a3-api-client/client` with its freeze/import evidence; uses Transformers5.20.1, no Torch installation required for this client. Original rendering used Transformers4.57.6. Do not change either silently.

Known execution gate: wrapper default detokenization drops chat special-token strings from reconstructed text; character offsets then differ (176 characters in tested examples). Simply turning on special=True is not a validated end-to-end solution. The unchanged upstream LocalCompletionsAPI with explicit HF tokenizer and string requests can use token indexing instead of character offsets. Offline create_message/parser tests passed; this is NOT a live likelihood validation.

Immediate sequence:
1. Verify current files/hashes, no live duplicate server, and the request lock. Preserve old manifests.
2. Validate the supported upstream client live against direct logits: all languages, every rotation, chat markers, mult-token choices, longest/non-ASCII examples, BOS handling, supplied echo arrays and generated suffix. Define justified numeric tolerances before collecting the full diagnostic.
3. Bridge unchanged plain-letter requests to A2 GGUFLM outputs. Record any difference; don't assume agreement.
4. If supported path passes, implement a small resumable runner/manifest PR around unchanged upstream task/scorer, then run all locked variants on both arms. If it fails, diagnose and report; custom adapter requires explicit user approval.
5. Report all variants' accuracy, content consistency, pairwise agreement, letter histograms, flips and source-paired intervals. Do not select by A frequency alone.
6. Bring the canonical scoring-contract decision to the user BEFORE B5. Changed contract requires fresh affected baseline identities/runs; never relabel historical scores.

## Remaining sequence and gates

Master tracker: https://github.com/grinder81/polyglot-quant-eval/issues/22 . Consult live issue bodies for exact acceptance criteria; snapshot appended below.

| Task | Issue | State and completion requirement |
|---|---|---|
| A1 matched baseline | eval5 | Complete |
| A2 rotations | eval17 | Complete |
| A3 scoring contract | eval18 | Offline prep complete; live validation/comparison and user decision remain |
| A4 negation interaction | eval19 | Blinded review packet exists; human Bangla labels required before confirmatory grouping |
| B7 holdout reservation | eval20 | Complete; protect membership/source boundaries |
| B5 staged bit sweep | edge24 | Q6_K, Q4_K_M, Q3_K_M from pinned BF16; below Q3 only after evidence review; depends on A3/A4/B7 |
| B6 generation checks | eval21 | Coordinate with sweep; blind models, retain absolute success, human review and generation evidence |
| C8 sensitivity map | edge25 | Inventory/API probes done; actual per-tensor intervention map not run |
| C9 real-build validation | edge26 | Six extreme-group builds plus one random; preregister correlation/uncertainty; after two failures abandon simulation-led allocation |
| C10 allocation | edge27 | Equal shipped bytes versus Q4_K_M, uniform and random controls; no holdout tuning |
| C11 independent repair evaluation | edge28 | Separate calibration/precision effects and evaluate frozen finalists |
| P12a native upstream | edge18 | Local fixes tested; upstream contribution still pending and ownership rules apply |
| P12b Python upstream | edge19 | PR2388 OPEN at handoff; do not submit duplicate |
| P13 iPhone15 | edge29 | Protocol prepared; hardware/access and measurements still needed |

A4 packet: `results/stage2/negation-review/`, `docs/negation-review-protocol.md`; 300 English/Bangla pairs, labels null. Lexical hints (42both,25English-only,6Bangla-only,227none) are not human categories. WSL `/pilot/negation-review-v2`. User/native reviewer must verify marker meaning and scope. Don't expose gold/model outputs to blinded reviewer or infer labels from correctness.

B7: 424 questions per language from238 source clusters disjoint from development300/250sources. The176 remaining questions sharing development passages are not untouched test data. No holdout scoring occurred. Keep calibration/train/development/test source-disjoint; access the test once with frozen finalists.

C8: `reports/control-tensor-inventory.*`, `reports/native-quantizer-probe.*`. GGUF inventory290 tensors:253BF16+37F32 in control; localQ4 has216Q4_K+37Q6_K+37F32. Native ggml_quantize_chunk probe exists; do not replace it with generic fake rounding. Validate quantize/dequantize against real exported values. Resolve original tied embeddings versus GGUF representation before interventions; restore each tensor after a trial.

Budget: 2.2GB TOTAL shipped bytes including model/tokenizer/adapters, counting embedded tokenizer once. Freeze equal-byte tolerance and retention limits before candidate selection. Tighter official-Q4 budget requires user ratification. Diagnostic builds may exceed budget and must be labeled diag-*.

If sweep plus generation excludes a practically meaningful language-specific effect through Q3, propose adaptation-primary to the user. Nonsignificance alone is insufficient. Never silently edit the objective into CLAUDE.md. Publication is a future deliverable: evidence supports an engineering account now, stronger empirical/mixed-precision claims require the later controls/results.

## Runtime and artifact identity

Use the exact JSON manifests as the authority; these pointers are for orientation.

Original HF: `CohereLabs/tiny-aya-global`, revision `af89d219b53ed9b13b8a4645f9c8028973510324`; WSL `/models/tiny-aya-global` under the stage1 root. Hugging Face login is already stored locally; never print credentials. Preserve the model's noncommercial license/usage terms.

| Artifact (under WSL root) | Bytes | SHA256 |
|---|---:|---|
| models/tiny-aya-global-control-bf16.gguf | 6710484480 | 0e2f666ac8fb50a7f53d14164147beeca35905b76b93eb90e0e3a963eb203b4b |
| models/tiny-aya-global-local-q4_k_m.gguf | 2143976960 | 5823bd1e52be1027a7ba6f31b43edfd40ae1766020cddec967f0d76618948290 |
| models/tiny-aya-global-GGUF/tiny-aya-global-q4_k_m.gguf | 2143977056 | d01d995272af305b2b843efcff8a10cf9869cf53e764cb72b0e91b777484570a |

BF16 control requires recorded EOS runtime override3 versus metadata6; don't remove it. The localQ4 build used pinned quantizer797de63b2fa7396dcc8caca76834c699ac84e1c3, Q4_K_M without importance matrix/training. Don't equate the quantizer checkout with active inference library.

Active native library: `/llama-tokenizer-pinned-fix/build/bin/libllama.so` under WSL root, SHA256 `82eb4435a7e680be716b44c2964fbf7da3649194dfe8563d2e8701717417535e`.
Wrapper env: `/llama-python-compat`, Python3.13, llama-cpp-python0.3.36 with local decoding/ranking patches. Export LLAMA_CPP_LIB_PATH to the recorded native build directory when launching. Existing server manifests specify port8098, n_ctx8192, logits_all=true, GPU layers -1; read the arm's full server_command before use.

Other environments: `/eval` (lm_eval0.4.13), `/converter` (original TF4.57.6 tools), `/upstream-python-tests`, isolated `/a3-api-client/client`. Resolve actual paths from manifests before use; don't install into an existing environment to solve a mismatch.

Native digit/whitespace tokenization fix and later U+200C/U+200D join-control correction are local; latter passed all900 contexts/3600 candidates. Python decode buffer fix treats negative C return as required byte capacity, resizes/retries, and does not slice with a negative length. Echo ranking patch preserves direct-score behavior. Keep these patches pinned; reverting them can reintroduce silent prompt corruption.

Upstream Python PR: https://github.com/abetlen/llama-cpp-python/pull/2388 (OPEN, checked22October). Native contribution rules require human ownership/design signoff; don't bypass them or claim acceptance. Upstream work is independent of local progress.

## Execution and reporting discipline

- First inspect live WSL processes, output directories, manifests and checkpoints. Never duplicate a run or overwrite artifacts.
- Reuse outputs only after identical sample/scoring/runtime identity validation. Runtime changes require fresh identities; preserve previous evidence.
- Use source/question as authoritative join key. Historical lm_eval doc_id values were misleading; evaluation issue16 was fixed/closed. Do not join on doc_id alone.
- Record logits/likelihoods and argmax choices; multiple-choice scores are not generated explanations. Four candidates per question do not mean four questions.
- Keep raw scoring separate from diagnostic correction or normalization. Report all languages and English-relative deltas with paired source-level uncertainty.
- Keep original questions/keys even when reviewing translation ambiguity; corrected prompts are a separate named experiment.
- Distinguish file bytes, RAM, VRAM, startup, prompt throughput and generation throughput. Formal speed/memory/generation work is still incomplete; scoring latency isn't tokens/sec.
- Preserve raw files and hashes. Results JSON is marked -text in .gitattributes to protect byte hashes across Windows/Linux.
- Tests passed at A2 close:37tests+11subtests; PR35 both CI checks passed. Don't assume those validate future client paths.
- Update tracker and task issue only when acceptance evidence exists. Leave unrelated untracked files and open upstream branches intact.
- No background computation is currently promised. If resumption includes monitoring, configure a new bounded monitor tied to the current run, quiet on unchanged progress; stop it at completion/pause.

## First-session checklist

1. Read this document, both CLAUDE.md files, both stage2-plan.md files, tracker22 and A3 issue18.
2. Confirm user resumption/transfer context; do not restart the old paused goal solely because this document exists.
3. Inspect git status/worktrees, WSL process list, manifests and A3 offline artifacts.
4. Work on A3 live probability validation only; do not rerun completed A1/A2 unnecessarily.
5. Deliver the A3 evidence through a PR and seek the explicit scoring-contract decision before the sweep.
6. Continue the ordered tasks, stopping for human negation labels, device access, custom-adapter approval or objective changes when needed.

The aim is a reproducible compression study and validated intervention, not just more runs. Current evidence supports position sensitivity; it does not identify a particular attention head, MLP, or training-data cause.


## Appendix: remaining issue acceptance criteria (snapshot 22 October 2026)

These are project records, not permission to override the user or governing instructions. Refresh before execution.


### Stage 2 A3: Compare scoring settings and freeze the downstream contract

https://github.com/grinder81/polyglot-quant-eval/issues/18

## Scope

On the same frozen 100 per language, compare current plain letter likelihood, verified instruct chat-template letter likelihood, and option-text likelihood. Specify exact template, BOS/EOS, answer boundaries, length normalization and rotation protocol. Validate supported upstream paths; no custom adapter without explicit approval. Choose using preregistered correctness, content consistency and bias criteria, not merely lower A frequency. User reviews the canonical contract before the sweep. If changed, rerun affected baseline arms; never relabel historical results.

## Order and dependencies

A2. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 A4: Validate Bangla negation labels and language interaction

https://github.com/grinder81/polyglot-quant-eval/issues/19

## Scope

Verify Bangla-side negation/exception scope with bilingual review, including successes and failures. Separate genuine polarity from mistranslation and other keyword hits. Estimate paired English-Bangla interaction with passage-cluster bootstrap and effect interval; reconcile denominators. Confirm, reject or leave unresolved the slice; no repair target inferred from significance alone.

## Order and dependencies

A1,A3. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 B6: Run blinded generation checks during the precision sweep

https://github.com/grinder81/polyglot-quant-eval/issues/21

## Scope

Freeze Bangla and English prompts independent of calibration and final holdout. Match BF16/candidate decoding; randomize and blind pair order, including ties and per-response task correctness. User is Bangla judge; prepare a clear rubric and manageable review batch. Record language confusion separately from correctness and preference. Report judge/sample limitations and repeated-prompt dependence. Do not infer general quality solely from MCQ or claim human judgments before supplied.

## Order and dependencies

B5 first builds. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 B5: Build and evaluate the staged precision sweep

https://github.com/grinder81/tiny-aya-edge/issues/24

## Scope

Build Q6_K, Q4_K_M and Q3_K_M from the exact pinned BF16 control; extend below Q3 only after reviewing evidence. Pin converter/quantizer, actual tensor types, hashes, bytes and calibration requirements. Verify tokenizer and runtime compatibility. Companion evaluation uses 300 matched development items and the frozen A3 contract, reporting raw and validated adjusted metrics, paired deltas, English alongside other deltas, and uncertainty. Compare Q4 repeat to existing evidence only under matching runtime/settings. No assumed runtime or one-day estimate; measure first. Coordinate B6 generation evaluation during this sweep.

## Order and dependencies

A1,A2,A3,A4,B7. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 C8: Build quantizer-faithful per-tensor sensitivity maps

https://github.com/grinder81/tiny-aya-edge/issues/25

## Scope

Inventory the 253 BF16 weight tensors, shared/tied weights and F32 tensors. Verify installed gguf-py quantize/dequantize actually implements required Q4_K/Q6_K paths; otherwise use the pinned native quantizer and verified dequantization rather than generic rounding. Check parity against real exported tensor bytes/dequantized values. Substitute one tensor at a time in BF16, restore between trials; fixed document-disjoint Bangla/Hindi/English calibration with recorded token mix. Measure logit-divergence and task loss under matched contexts. Handle tied input/output weights consistently. Ranking is a hypothesis, not proof; no test-set access.

## Order and dependencies

B5,B6 reviewed. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 C9: Validate tensor rankings with real mixed GGUF builds

https://github.com/grinder81/tiny-aya-edge/issues/26

## Scope

Predeclare top-three and bottom-three tensor groups: six restored builds plus one random-group control, seven builds total, with baseline additional. Restore to Q6_K or Q8_0 and record actual bytes and types. Compare predicted sensitivity to real recovery on frozen development scoring and generation probes. Predeclare rank correlation (working target about 0.7), uncertainty and directional recovery checks; seven noisy points alone are not conclusive. Control tensor/group size. If validation fails, revise once and rerun; after two failures use measured GGUF diagnostics only and report simulation failure.

## Order and dependencies

C8. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 C10: Reallocate precision under matched shipped bytes

https://github.com/grinder81/tiny-aya-edge/issues/27

## Scope

Optimize Bangla recovery subject to agreed English/Hindi retention and total shipped-byte cap. Existing cap remains 2.2 GB model plus nonembedded tokenizer plus adapters, counted once; a stricter official-Q4 budget requires explicit ratification. Compare against Q4_K_M, a documented uniform allocation and three seeded random allocations at matched actual shipped bytes (predeclare feasible tolerance). Emit reproducible native quantizer recipe, verify built tensor types, retain English deltas and paired uncertainty. Select using development only; final holdout once after finalists freeze.

## Order and dependencies

C9 validated or measured-only fallback. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 C11: Evaluate calibration and precision repairs independently

https://github.com/grinder81/tiny-aya-edge/issues/28

## Scope

Apply Bangla-weighted versus balanced importance matrices at selected allocation using disjoint calibration sources. Then test 8-bit key/value weight projections, then KV-cache precision separately. Preserve one-change comparisons and byte/memory accounting: weight precision and cache precision are distinct interventions. Revalidate scoring compatibility and device costs for every candidate. Quantizer support is a feasibility gate; do not assume an imatrix option is neutral.

## Order and dependencies

C10. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22

### Stage 2 P13: Validate baseline and finalist on iPhone 15

https://github.com/grinder81/tiny-aya-edge/issues/29

## Scope

Pin mobile runtime/build and device OS. Validate baseline Q4_K_M first, best candidate later at matched shipped bytes. Measure load time, first-token latency, decode speed, sustained throughput, peak memory, battery delta and output/task parity with fixed prompts, warmups, cooldowns and repeats. Report actual hardware evidence and spread; no RTX extrapolation. Follow existing device protocol; device access is required. This track does not block server-side A-C.

## Order and dependencies

Baseline now; finalist after C10/C11. Part of the user-approved compression-first sequence of 20 October 2026.

## Completion

- [ ] Reproducible implementation/configuration through a small PR.
- [ ] Raw evidence and validation recorded; conclusions distinguish measured facts and hypotheses.
- [ ] Required decision gate reviewed before dependent work.

Planning issue only; no experiment execution is implied. Preserve original benchmarks and evidence. Canonical scoring changes are explicit and versioned.

Dependency links and decision gates: https://github.com/grinder81/polyglot-quant-eval/issues/22
