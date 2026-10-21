# Local Q4 expanded evaluation

User authorized the local Q4 arm first at 300 questions per language (900 total), before any larger comparison across other arms. The frozen lock already contains 300 aligned groups. The original 50 per language are development data and remain recorded unchanged.

Preflight initially found one Bangla prompt mismatch at frozen group 105: the original tokenizer split the year before a zero-width non-joiner differently from the patched GGUF tokenizer. This blocked execution until the correction described below passed validation.

The earlier local patch incorrectly treated the non-joiner as a word continuation. Original-tokenizer reproduction and regression coverage established the correction. No benchmark question was edited or omitted.

If the runtime changes, do not simply reuse old results under a new manifest. Prefer rerunning all 300 per language under the corrected runtime, or prove unchanged behavior on the old subset and retain separate provenance. No adapter or scoring change is authorized.

The runner accepts aligned start/count ranges without changing run_pilot.py or upstream scoring. Because the runtime changed, the first 50 were rerun as well.

## Blocker resolved and execution started

The validated local correction in tiny-aya-edge PR 23 removes the incorrect join-control exceptions. Original-tokenizer checks and standalone C++ regressions pass, followed by zero mismatches across all 900 contexts and 3600 candidates. The local-only run now starts at zero for all 300 per language under a new runtime manifest. Earlier 50-question results are preserved, not reused or relabeled. No scoring, model or question changes.

## Completed results

All 900 items completed and validated. English: 226/300 (75.3%); Bangla: 189/300 (63.0%); Hindi: 176/300 (58.7%). See the [raw evidence and report](../results/stage1/local-q4-three-hundred/README.md) for uncertainty, identity checks, and the raw document-ID labeling caveat. Only the authorized local Q4 arm ran; speed/memory and other-model comparisons remain separate.
