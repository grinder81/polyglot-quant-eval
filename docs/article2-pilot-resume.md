# Article 2 pilot execution checkpoint

1 November 2026. This is a resume guide, not a completion report. [Tracker #47](https://github.com/grinder81/polyglot-quant-eval/issues/47) owns the bounded pilot; [evaluation PR #50](https://github.com/grinder81/polyglot-quant-eval/pull/50) and [runtime PR #43](https://github.com/grinder81/tiny-aya-edge/pull/43) contain its implementation and evidence. G0 protocol and G1 resource issues are complete. Full precision collection, C8 and the decision report remain open.

The user's latest instruction replaces the earlier 10% threshold: continue and make a clean checkpoint and stop only if weekly allowance falls **below 2% remaining**. Read the current account meter rather than estimating from task tokens; the latest check was 10% remaining while Q4 KL was collecting. Do not consume an allowance reset. A pause is not an experimental failure or a completed pilot.

## Locations and immutable evidence

- Evaluation worktree: `C:/Users/shoha/Documents/ChatGPT/personal-development/_worktrees/article2-pilot-eval`, branch `codex/article2-pilot`.
- Runtime worktree: the sibling `article2-pilot-edge`, same branch name in its separate repository. Preserve the original checkouts and the user's unrelated untracked script.
- Native workspace: `/home/shohag/tiny-aya-stage1/pilot/article2-2026-11-01` in WSL Ubuntu.
- Local sequential helpers: the sibling `run_t3_stage1.py` supplies the reusable collection functions; `run_t3_stage2.py` is the current driver. Its log is `t3-readiness/stage2-collection-driver.log` under the native workspace. It owns only its own server and stops it in `finally`.
- The stop flag is `STOP-AFTER-CHECKPOINT` under the native workspace. The driver checks it before each new operation. It collects task shards in batches of 20 and fidelity questions in batches of 30, using unchanged frozen implementations. Do not restart this one-shot driver from the beginning when readiness outputs already exist; resume the remaining operation explicitly.
- T3 specification Git blob: `700a0f601e6503d95b485ad5d048c20b4ef96910`. The original freeze checkout is the sibling `t3-pilot-amendment`; retain it while build commands reference its specification.
- C8 design Git blob: `cd43458f25672a0522958a4d1de0e1a88c307dc7`. Private pool SHA256: `c17a79fede7ff993f247d4a23cce533ea796887b0ce416c227407bc471997fd3`. No C8 comparative outcome has been collected at this checkpoint.

## Completed and current collection

Q6 task and full KL evidence are [published together](../results/t3-precision-curve/diag-q6k/README.md). Q6 has 900 questions, accuracy counts EN 233 / BN 188 / HI 185 and a separate full KL run covering 176,756 content-token distributions. Its fresh fidelity directory is `t3-fidelity/diag-q6k-host1`; the earlier partial `diag-q6k` directory is preserved and excluded. Do not mix them.

The BF16 raw reference cache is complete at `t3-fidelity/reference`, manifest SHA256 `9964b004736d733b872e3a4f2e294631f7b4744894d4626b60a928d2f193aa6e`. Never put its raw `.npy` arrays or model weights in Git. The verified numerical receipt used for comparisons is `torch-fidelity-verification-v3/torch-verification.json`. The active core and wrapper must not change during a run; native backend initialization must precede Torch import, with the verified one host thread.

Q3_K_M passed all readiness gates, all 900 task questions, separate complete validation and all 900 full-KL comparisons. Its [combined checkpoint and verified archives](../results/t3-precision-curve/diag-q3km/README.md) are published. Accuracy is EN 221 / BN 186 / HI 173. English meets the frozen development floor exactly; the descent stop is not triggered and the later precision stages remain required. No operating point is selected. Q3's original build manifest and actual-inventory supplement preceded inference.

Q4 full KL is also complete. The [Stage 1 report](../results/t3-precision-curve/stage1/README.md) was committed at `2cf037118581078f0b94d0be6f3d4699d00f8f23` before Stage 2 builds. No Q4 task recollection was performed. Q6/Q3/Q4 fresh fidelity directories and verified sidecars are complete; preserve them without recollection or mixing.

Stage 2 Q3_K_S/Q2_K actual builds, inventories, runtime bindings and vocabulary checks were committed before inference at runtime commit `d737c6897c9cd21f06d9770a1e49f04cd373eaa8`. Actual bytes are 1,660,984,832 and 1,481,973,248, exactly matching every predicted tensor type/payload. Q3_K_S passed all live numerical and offline identity gates and began task collection. The current sequential driver completes its task/fidelity before Q2_K. The sibling helper `pilot_status.py` reports latest counts without reading outcomes. Read that status and the latest driver log rather than treating transient counts as frozen here.

## Resume sequence

First inspect running processes, the stop flag, current account allowance and the last completed operation. Never start a second GPU owner or terminate unrelated desktop/user work. Clear a user-requested pause only after a later instruction authorizes resumption.

Q3 task collection is complete and needs no continuation. For later new precision arms, use the saved runtime's exact server command and library environment. The frozen client interpreter is `/home/shohag/tiny-aya-stage1/a3-api-client/client/bin/python`; run `python -m scripts.run_t3_baselines` from the evaluation worktree with that arm's config and collection directory. An invocation without `--collect` validates saved evidence. Collect with `--collect --max-new-shards 20`; it skips only already validated shards under the identical saved identity. Preserve any partial/error files for inspection rather than deleting or silently replacing them. Full collection requires 180 shards and a final complete validation.

For a partially collected new arm, resume only its missing task shards or KL questions after inspecting saved identities. KL uses `builds.run_verified_fidelity`, the v3 numerical receipt and unchanged core. The local driver's `fidelity` function contains the exact arguments, but its one-shot log names must not overwrite prior batch logs. Use a fresh log name with the same arm directory, runtime, reference, receipt and `--max-new-questions 30`; the immutable engine verifies existing question identities and skips them. Only a full 900-question manifest plus its verified sidecar qualifies for the endpoint. Package complete evidence with the repository archive tools. Stage 1's verified archives are already published and must be preserved.

Commit the complete Stage 1 report before starting Stage 2. Follow the frozen descent rule and actual-byte ordering: IQ3_S is larger than Q3_K_S and Q2_K, so a Stage 2 failure does not automatically exclude it. Attach actual inventories and commit every new build manifest before inference. Finish the required curve before the English-only operating-point decision.

Then derive and freeze the C8 execution plan mechanically, including formats, pair eligibility and exact bytes. All G3 builds/probes and proxies must use the persistent cumulative resource ledger. Complete discovery repetitions 1–2, freeze the full nomination receipt including explicit none, and only then collect repetition 3. A promising verdict requires the nominated complete native maps to reproduce opposite BN/EN directions on that independent sample. An absent nomination is inconclusive, not language equivalence. The reporter requires passed final budget operations and original evidence linkage; a report file alone is insufficient.

Finish with the G4 decision report, CI and issue reconciliation. Keep full C9/C10/C11, genuine generation review, A4 labels, device work and all other unfinished legacy scopes open. Final holdout outcomes and A4-conditioned slices remain sealed throughout.
