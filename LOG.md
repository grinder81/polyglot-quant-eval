# LOG

## Belebele task/data audit
- Downloaded pinned English, Bangla and Hindi subsets and recorded 900 rows each, label checks, content hashes and installed task definitions in results/stage1/belebele-task-audit.json.
- Confirmed upstream candidates are A/B/C/D; canonical Stage 1 uses zero-shot acc without a chat template. No model scoring or sample lock yet.

Dated entries: what changed, the numbers, open problems.

## 2026-10-16
- Repository created: research question, design decisions, 14-language config, results schema,
  reference-runtime serve script, smoke test, normalize and report scripts (tested on synthetic output).
- Open: first BF16 Belebele run on the reference runtime; confirm upstream task names for
  `global_mmlu_*` and `mgsm_*`.

## 2026-10-16 (later)
- Aligned to the loop baseline, inspect, intervene, measure, explain. report.py now prints the gap
  vs English under every delta table; diagnostic and repaired formats have naming rules.

## 2026-10-17
- Added a reviewable Stage 1 protocol and proposed data-pool intentions; aligned harness
  documentation with adaptation as the broader goal and explicit runtime controls.
- No model runs, downloads or measurements performed. Artifact revisions and sample locks
  remain gates for later tasks. Existing smoke and report scripts need separate fixes.

## 2026-10-20
- Completed local Q4 only on 300 Belebele questions per language: English 226/300, Bangla 189/300, Hindi 176/300. Evidence and caveats: results/stage1/local-q4-three-hundred/README.md. All questions rerun under the join-control-corrected runtime; no other models or performance tests run.
