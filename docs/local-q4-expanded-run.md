# Local Q4 expanded evaluation

User authorized the local Q4 arm first at 300 questions per language (900 total), before any larger comparison across other arms. The frozen lock already contains 300 aligned groups. The original 50 per language are development data and remain recorded unchanged.

Preflight found one Bangla prompt mismatch at frozen group 105: the original tokenizer splits the year before a zero-width non-joiner differently from the patched GGUF tokenizer. All 900 contexts and 3,600 candidate sequences were checked; this one context and its four candidates differ. Both paths decode to the same text. Accuracy execution has not started.

The local tokenizer patch explicitly treats the non-joiner as a word continuation; that condition is a candidate cause, not yet a validated fix. Reproduce against the original tokenizer and add regression coverage before adjusting the runtime. Do not edit or omit the benchmark question.

If the runtime changes, do not simply reuse old results under a new manifest. Prefer rerunning all 300 per language under the corrected runtime, or prove unchanged behavior on the old subset and retain separate provenance. No adapter or scoring change is authorized.

The runner now accepts aligned start/count ranges without changing run_pilot.py or upstream scoring. The intended reuse of the first 50 remains conditional on validation and runtime identity.

## Blocker resolved and execution started

The validated local correction in tiny-aya-edge PR 23 removes the incorrect join-control exceptions. Original-tokenizer checks and standalone C++ regressions pass, followed by zero mismatches across all 900 contexts and 3600 candidates. The local-only run now starts at zero for all 300 per language under a new runtime manifest. Earlier 50-question results are preserved, not reused or relabeled. No scoring, model or question changes.
