# Article 2 pilot execution checkpoint

Updated 7 November 2026 after the C8 pilot completed; first written 1 November after the complete T3 curve and an interrupted C8 export. This is a resume guide, not a completion report. [Tracker #47](https://github.com/grinder81/polyglot-quant-eval/issues/47), [evaluation PR #50](https://github.com/grinder81/polyglot-quant-eval/pull/50) and [runtime PR #43](https://github.com/grinder81/tiny-aya-edge/pull/43) own the work.

## Current state

G0 protocol, G1 resources and the bounded G2 task/fidelity curve are complete. The [final T3 report](../results/t3-precision-curve/final/README.md), committed at `34db052fc98de4c15b511d831fe23f77d8c3153f`, selects Q3_K_M at 1,799,740,928 bytes, English 221/300, Bangla 186/300 and Hindi 173/300. The English floor is met exactly; noninferiority is not established. All required stages, including imatrix-free IQ3_S, are complete. Do not recollect them. Broader B5 generation work remains open.

G3's [execution plan](../results/article2-pilot/c8-plan.json) was frozen in that same commit before any comparative outcome. SHA256 is `e7ccdb50be254ee8bdde307f73c58bc9a9c9d68882a40aa453b9b516ec8be64f`. All four restricted equal-byte pairs are eligible, using Q2_K/Q3_K on eight specified tensors. Discovery repetitions 1–2, the frozen nomination (explicit none, committed at `c713006` before repetition 3) and descriptive repetition 3 are complete; the [G4 outcome](../results/article2-pilot/c8/README.md) is **inconclusive** under the frozen taxonomy. The investment verdict on a larger study is the owner's and is not recorded here.

C8 was interrupted on 1 November when host C: exhausted physical space (nine passed exports, one active; export and sampler processes crashed; Ubuntu then failed to start) and completed on 7 November after the [storage incident and recovery gate](https://github.com/grinder81/tiny-aya-edge/tree/codex/article2-pilot/reports/article2-pilot/storage-incident) was satisfied: verified backup of the stopped disk, a recorded recovery receipt closing the interrupted ledger row with its observed 31.38 s, the seven remaining exports under the new backing-volume guard, committed manifests, discovery, nomination and repetition 3. The interruption is neither a language result nor a reason to reset any budget; the ledger retains the failed row.

The user's latest instruction is to continue until weekly allowance falls **below 2% remaining**, then preserve a resumable checkpoint and pause. The latest observed account meter was 94% remaining; it is shared and must be checked afresh. No usage reset was requested or redeemed.

## Locations and identities

- Evaluation worktree: `C:/Users/shoha/Documents/ChatGPT/personal-development/_worktrees/article2-pilot-eval`, branch `codex/article2-pilot`.
- Runtime worktree: sibling `article2-pilot-edge`, same branch name in its separate repository. Original checkouts and the user's unrelated untracked script are preserved.
- Native workspace: `/home/shohag/tiny-aya-stage1/pilot/article2-2026-11-01` in Ubuntu. C8 plan, resource ledger, exports and logs live below `c8/`.
- T3 specification Git blob: `700a0f601e6503d95b485ad5d048c20b4ef96910`. Preserve the sibling `t3-pilot-amendment` checkout referenced by historical build commands.
- C8 scientific design Git blob: `cd43458f25672a0522958a4d1de0e1a88c307dc7`. Private source-pool SHA256: `c17a79fede7ff993f247d4a23cce533ea796887b0ce416c227407bc471997fd3`.
- Completed T3 raw BF16 reference: `t3-fidelity/reference`, manifest SHA256 `9964b004736d733b872e3a4f2e294631f7b4744894d4626b60a928d2f193aa6e`. It contains 185,342,099,456 raw float32 bytes before headers. All six required fidelity endpoints are complete; preserve or verifiably archive the cache rather than recollecting it. Raw logits and weights never enter Git.
- T3 numerical receipt: `torch-fidelity-verification-v3/torch-verification.json`. Native initialization precedes Torch import with one verified host thread. C8 native execution is separate and does not import Torch.

## Resume after storage recovery

Steps 1–6 below were carried out on 6–7 November 2026 and are recorded in the runtime incident record and under `results/article2-pilot/c8/`; step 7's issue reconciliation and the owner's verdict remain. The list is kept as the record of the gate that was applied.

1. Follow the runtime incident's recovery gate. Verify the stopped-distro backup before filesystem repair, exact device identity before any filesystem command, actual backing-host free space and original artifact hashes after recovery. Avoid affecting Docker or other WSL work without the pending approval.
2. Archive the original ledger, active-operation record, diagnostic manifests, failure evidence and resource samples. Resolve the interrupted operation through a separate recorded recovery receipt, retaining conservatively accounted failed time inside the existing native 90-minute and proxy 30-minute caps. The artifact cap remains 400 GB.
3. Freeze the execution guard and any storage relocation before outcomes. The host guard requires the verified backing Windows volume, a 20 GiB reserve plus the next output's bytes, and monitoring during each operation. A changed scientific design would require a separate new protocol, not an unrecorded retry.
4. Validate every completed export against its original manifest and ledger receipt. Resume only missing exports without overwriting failure evidence. Commit actual export manifests before comparative probes. The sibling `run_c8_exports.py` is a one-shot historical driver and cannot simply be relaunched into existing paths.
5. The sibling `run_c8_discovery.py` is prepared but has not run. It requires `--exports-commit`, checks all 16 committed manifests, then collects native reference, native diagnostics and proxies for repetitions 1–2. Use the pinned interpreters, native library environment and gguf import path recorded in the driver. Inspect GPU ownership first; terminate only task-owned processes.
6. Freeze the full `scripts.c8_pilot_decision` nomination, including explicit none, before repetition 3. Only a nominated pair can receive complete-map confirmation. No nominee is inconclusive, not language equivalence. Final reporting requires original linked evidence and passed operation receipts.
7. Complete G4 with measured costs, repeat stability, feasible equal-byte controls and the distinction between fidelity and task benefit. Reconcile issues and run relevant tests/CI. Keep C9/C10/C11, genuine generation review, A4 labels and device work open until their own requirements are met.

Final holdout outcomes and A4-conditioned slices remain sealed. A machine interruption is neither an allocation result nor completion of this goal.
