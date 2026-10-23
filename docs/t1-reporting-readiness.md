# T1 reporting and publication readiness

This document prepares the fresh original-order comparator report. It is not a
launch command or authorization for a live smoke, inference, holdout access,
submission or publication. A separate reviewed package and user launch decision
are required. Governing records are the [accepted A3 contract](scoring-contract-a3.md),
[Stage 2 plan](stage2-plan.md), [A4 protocol](negation-review-protocol.md), and
[holdout protocol](final-holdout.md).

## Scientific report boundary

- Require two complete **900-question** fresh arms (300 per English/Bangla/Hindi),
  original order, exact plain-letter requests. This is explicitly **BF16 GGUF**
  versus local Q4_K_M; the canonical original BF16 vLLM reference remains separate.
- Validate the actual new runner's complete shard inventory, request lock,
  source/question identities, official targets, candidate order/score finiteness,
  raw/normalized predictions and frozen runtime/client/gate hashes before analysis.
  Reject mismatches and partial runs; do not silently intersect memberships.
- Report absolute accuracy and paired Q4−BF16 effects, their English-relative
  differences and source-clustered intervals; retain changes, regressions,
  improvements, wrong-to-wrong churn and displayed/gold A/B/C/D counts. Resample
  whole sources jointly across translations and paired arms, 10,000 draws, seed 42.
  Original-order results are not rotation means. Nonsignificance is not equivalence.
- Join each historical A1 arm to its fresh counterpart only after exact membership,
  target, request/candidate bytes and unchanged model artifact are established.
  Describe candidate-loglikelihood delta and margin-change distributions, preserve
  per-question differences and paired outcome uncertainty, and retain both runtime
  identities. These are combined recorded runtime changes, not attribution to one
  patch, universal error bounds or thresholds for a new run.
- Integrate PR40's pure margin-count function only after validation of the **actual
  T1 schema**; label it fresh T1 evidence. Its old historical-only filesystem loader
  is not a fresh-run adapter. Margin bins remain exploratory association, with
  exact denominators, deterministic ties and missingness rejection; they do not
  explain language effects or establish calibrated confidence. No new result is
  claimed by readiness tests.
- If comparing A3 overlap, first establish exact requests/tokens and compatible
  model/runtime/client/settings. Never copy old A3 scores into a fresh collection
  without separate authorization. An aggregate continuation difference is not a
  per-token check unless one-token continuation length is explicitly verified.

## Readiness review and stop conditions

- Tests must cover the new runner's actual shard schema through complete-report
  acceptance and rejection, not only a synthetic score-table function. Reject a
  missing/duplicate question, unexpected shard/task, target/request/candidate-order
  change, nonfinite score, wrong runtime/gate hash and incompatible paired settings.
- Use synthetic data and offline/token checks during readiness. A protocol for a
  bounded end-to-end smoke is a deliverable; executing it remains separately gated.
- Root assembles the private exact launch package: proposed commands, working
  directories, source/lock/model/native/runtime/client/gate hashes, expected files,
  allowed resume behavior, stop conditions and resource ownership. Do not put
  unnecessary personal paths in public prose. CI/review success is not launch approval.
- Stop on correctness, membership or identity failure. Preserve artifacts and
  diagnose; do not loosen a tolerance, relabel an old identity or drop items to
  force success. Historical subset maxima are not bounds on fresh observations.
- T1 completion requires all 1,800 fresh question identities and every candidate
  score validated, source-backed outcomes and raw byte evidence committed/reviewed.
  A4 human Bangla labels remain required before T3/B5 under the current sequence.

## Report interface and retained evidence

`python -m scripts.summarize_t1_baselines --help` describes the explicit offline
report inputs: T1 `--lock` and `--readiness`, `--bf16-directory`/`--q4-directory`
and `--bf16-token-check`/`--q4-token-check`, original `--a3-lock`/`--a3-record`, pinned `--tokenizer`, exact
recorded `--base-url`, the two `--historical-reference`/`--historical-candidate`
evidence roots, and a new `--output`. No endpoint is contacted by reporting.
The runner's `verify_run_identity(..., complete=True)` validates its actual
`t1-original-order-v1` lock and `t1-cold-original-order-v1` saved identity. Saved
scores require the expanded probability/order gate artifacts in that identity;
a readiness proposal without live gates cannot produce a final report.

The `t1-complete-report-v1` JSON preserves:

- `fresh_paired_GGUF`: per-language reference/candidate absolute correct/accuracy,
  histograms, churn decomposition, paired accuracy and English-relative effects,
  and joint-source intervals for absolute accuracy and churn rates. Reference is
  BF16 GGUF; candidate is local Q4_K_M. Rates/deltas serialize as fractions.
- `historical_to_fresh_by_arm`: separate historical→fresh outcome comparison,
  candidate/margin delta distributions and all per-question deltas. Mean-delta
  gaps versus English are labeled point only; descriptive distribution quantiles
  are not confidence intervals. Runtime comparisons are not compression effects.
- `fresh_margin`: PR40 fixed-bin exploratory counts from validated fresh T1
  records, not its historical-only loader. It does not add margin-effect intervals.
- `provenance` and `analysis_source_sha256`: full paired run identities, runtime
  records, each raw shard hash, expanded gates and conditional A3-overlap comparisons,
  historical input hashes and analysis source hashes; `fresh_rows` retains all
  scores, predictions and official targets for audit.

The CLI fixes 10,000 bootstrap draws and seed 42. Synthetic tests use smaller
internal draw counts only to check the arithmetic and boundary; they are not
scientific results. Final report execution still waits for the complete authorized
collection. Keep raw sources unchanged and archive them losslessly after validation.

## Article 1 checklist after complete T1

1. Maintain an evidence-based component/exposure ledger before counting defects:
   component, observed failure or optimization, affected revision/artifact, minimal
   reproduction, exact requests/tasks exposed, exposure check, regression proof,
   and unresolved limits. Tokenizer, detokenization buffer, echo indexing, cache
   history and ranking performance are distinct inspection areas, not automatically
   five established accuracy defects. Do not preselect a “three bugs” headline.
2. Create the main figure **after complete T1** from the validated report. Show
   original-order BF16 GGUF/Q4 accuracy, paired effects with English comparisons
   and churn by language; an explicitly exploratory fresh-margin panel is optional.
   Label historical/rotation data separately and preserve denominators/source
   dependence. Do not visualize partial scores as a final result.
3. Link every numerical, defect and figure claim to exact committed artifacts and
   source versions. State that independent A3 checks reproduced all 18 cells/flip
   decompositions and **36 compression/English-relative intervals**, plus 18 examples;
   do not claim every variant-difference interval was independently recomputed.
4. Keep the argument compression-first. The engineering checkpoint does not prove
   general generation quality, a mechanism, absence of language harm, a validated
   sensitivity map, allocation/repair success, or phone performance. Q3/Q6 and
   generation are optional Article 1 additions with their own gates. A4 remains
   open until supplied human labels are frozen; no keyword/AI proxy labels.
5. Review provenance and reproduction completeness; remove credentials, unnecessary
   personal paths and identifying information from derived public prose. Review
   model/dataset/code license, usage, attribution and quotation obligations. Preserve
   immutable evidence identities rather than silently rewriting archived bytes.
   User line-by-line claim approval and explicit publication authorization are required.

## Upstream proposal gate

Before any future issue or PR, verify then-current primary upstream policy,
templates, existing submissions/duplicates, and substantive human ownership/design
requirements. Historical issue/PR state in earlier records is not a current-policy
check. Prepare a focused **proposed issue** with affected revision, minimal case,
expected/observed behavior and evidence. Complete substantive review and obtain
the user's filing authorization before external submission; this checklist does
not send an issue, comment, message or PR and does not promise acceptance.
