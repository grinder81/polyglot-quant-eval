# Article 2 pilot execution checkpoint

1 November 2026. This is a resume guide, not a completion report. [Tracker47](https://github.com/grinder81/polyglot-quant-eval/issues/47) owns the bounded pilot; [evaluation PR50](https://github.com/grinder81/polyglot-quant-eval/pull/50) and [runtime PR43](https://github.com/grinder81/tiny-aya-edge/pull/43) contain its implementation and evidence. G0 protocol and G1 resource issues are complete. Full precision collection, C8 and the decision report remain open.

The user instructed a clean checkpoint and stop if weekly allowance falls below 10%. Read the current account meter rather than estimating from task tokens; the latest check was 16% remaining. Do not consume an allowance reset. A pause is not an experimental failure or a completed pilot.

## Locations and immutable evidence

- Evaluation worktree: `C:/Users/shoha/Documents/ChatGPT/personal-development/_worktrees/article2-pilot-eval`, branch `codex/article2-pilot`.
- Runtime worktree: the sibling `article2-pilot-edge`, same branch name in its separate repository. Preserve the original checkouts and the user's unrelated untracked script.
- Native workspace: `/home/shohag/tiny-aya-stage1/pilot/article2-2026-11-01` in WSL Ubuntu.
- Local sequential driver: `C:/Users/shoha/Documents/ChatGPT/personal-development/_worktrees/run_t3_stage1.py`. Its current log is `t3-readiness/stage1-driver-checkpointed.log` under the native workspace. It owns only its own server and stops it in `finally`.
- The stop flag is `STOP-AFTER-CHECKPOINT` under the native workspace. The driver checks it before each new operation. It collects task shards in batches of20 and fidelity questions in batches of30, using unchanged frozen implementations. Do not restart this one-shot driver from the beginning when readiness outputs already exist; resume the remaining operation explicitly.
- T3 specification Git blob: `700a0f601e6503d95b485ad5d048c20b4ef96910`. The original freeze checkout is the sibling `t3-pilot-amendment`; retain it while build commands reference its specification.
- C8 design Git blob: `cd43458f25672a0522958a4d1de0e1a88c307dc7`. Private pool SHA256: `c17a79fede7ff993f247d4a23cce533ea796887b0ce416c227407bc471997fd3`. No C8 comparative outcome has been collected at this checkpoint.

## Completed and current collection

Q6 task and full KL evidence are [published together](../results/t3-precision-curve/diag-q6k/README.md). Q6 has900questions, accuracy counts EN233/BN188/HI185 and a separate full KL run covering176,756content-token distributions. Its fresh fidelity directory is `t3-fidelity/diag-q6k-host1`; the earlier partial `diag-q6k` directory is preserved and excluded. Do not mix them.

The BF16 raw reference cache is complete at `t3-fidelity/reference`, manifest SHA256 `9964b004736d733b872e3a4f2e294631f7b4744894d4626b60a928d2f193aa6e`. Never put its raw `.npy` arrays or model weights in Git. The verified numerical receipt used for comparisons is `torch-fidelity-verification-v3/torch-verification.json`. The active core and wrapper must not change during a run; native backend initialization must precede Torch import, with the verified one host thread.

Q3_K_M passed vocabulary, direct, client, reversed-order and offline identity checks. Its config is the sibling worktree file `t3-q3km-config.json`; task output is `t3-collection/diag-q3km`. The first100questions completed in242.34seconds. Read the latest completed shard files and driver log for current progress; this document deliberately does not freeze a transient count. The original build manifest and its actual-inventory supplement were committed before Q3 inference.

## Resume sequence

First inspect running processes, the stop flag, current account allowance and the last completed operation. Never start a second GPU owner or terminate unrelated desktop/user work. Clear a user-requested pause only after a later instruction authorizes resumption.

For Q3 task continuation, use its saved runtime's exact server command and library environment. The frozen client interpreter is `/home/shohag/tiny-aya-stage1/a3-api-client/client/bin/python`; run `python -m scripts.run_t3_baselines` from the evaluation worktree with its existing config and collection directory. An invocation without `--collect` validates saved evidence. Continue with `--collect --max-new-shards 20`; it skips only already validated shards under the identical saved identity. Preserve any partial/error files for inspection rather than deleting or silently replacing them. Full collection requires180shards and a final complete validation.

After stopping the owned scoring server, compare Q3 and then existing local Q4 against the complete BF16 cache through `builds.run_verified_fidelity`, using the v3 numerical receipt and unchanged core. The local driver contains the exact arguments. It accepts complete-question batches; only a full900-question manifest plus its verified sidecar qualifies for the fidelity endpoint. Package task and KL evidence with the repository archive tools.

Commit the complete Stage1 report before starting Stage2. Follow the frozen descent rule and actual-byte ordering: IQ3_S is larger than Q3_K_S and Q2_K, so a Stage2 failure does not automatically exclude it. Attach actual inventories and commit every new build manifest before inference. Finish the required curve before the English-only operating-point decision.

Then derive and freeze the C8 execution plan mechanically, including formats, pair eligibility and exact bytes. All G3 builds/probes and proxies must use the persistent cumulative resource ledger. Complete discovery repetitions1–2, freeze the full nomination receipt including explicit none, and only then collect repetition3. A promising verdict requires the nominated complete native maps to reproduce opposite BN/EN directions on that independent sample. An absent nomination is inconclusive, not language equivalence. The reporter requires passed final budget operations and original evidence linkage; a report file alone is insufficient.

Finish with the G4 decision report, CI and issue reconciliation. Keep full C9/C10/C11, genuine generation review, A4 labels, device work and all other unfinished legacy scopes open. Final holdout outcomes and A4-conditioned slices remain sealed throughout.
