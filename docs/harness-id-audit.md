# Saved document-ID investigation

The installed lm-eval 0.4.13 has a selection-order logging mismatch. Its
`Task.doc_iterator` filters the full dataset by requested membership, preserving
dataset order, then enumerates those selected documents from zero. In
`evaluator.py`, `doc_id_true = indices[doc_id]` uses that ordinal to index the
original caller-provided sample list, which can be shuffled.

For requested indices `[4, 1, 3]`, actual documents iterate as `[1, 3, 4]`, but
their saved labels become `[4, 1, 3]`. Request grouping and `process_results` both
use the same enumerated document order. The incorrect value is assigned to the
logged `doc_id`; the corresponding question, requests and target are not changed
by this assignment.

## Evidence and limits

The five-record reproduction in `harness-id-reproduction.json` runs the installed
upstream evaluator with its DummyLM on known development questions. All five
prompt/target checks pass while the saved labels exhibit the order mismatch.
It records hashes of the inspected `evaluator.py` and `api/task.py` sources.
No real model calls or scores are included in that evidence.

`scripts/audit_harness_ids.py results/stage1/local-q4-three-hundred` checks every
saved content identity and predicts its raw label from the ordering rule:

| Language | Records explained | Mislabeled indices |
|---|---:|---:|
| English | 300/300 | 236 |
| Bangla | 300/300 | 237 |
| Hindi | 300/300 | 234 |
| Total | 900/900 | 707 |

The independent expanded-run validator already checks content identities, prompt
hashes, targets, candidate scores and recomputed accuracy. Together these checks
explain the logging issue without changing the reported local-Q4 accuracy. This
does not establish that all possible harness sampling modes are unaffected.

## Handling

Keep raw logs intact. Continue joining by `(language, doc.link, doc.question_number)`
and retain both raw and verified dataset indices in derived rows. Do not cite a
raw document ID as a stable benchmark identifier. The active BF16 run stays on
its existing runner and records the same caveat; no mid-run changes or adapter
are introduced.

An upstream repair would make iterator order and original-index logging agree,
with unsorted-sample regression coverage. A caller-side future mitigation could
sort sample indices before invoking the evaluator, but changing run identities
must be explicit. Neither repair is applied in this investigation. The rotation
runner evaluates a five-document diagnostic dataset without the `samples` option,
so this specific unsorted-list mapping is not used there.

Reproduce with the pinned evaluation environment and existing development lock:

```sh
python scripts/reproduce_harness_id_order.py --lock SOURCE_LOCK --output NEW_EVIDENCE
python scripts/audit_harness_ids.py results/stage1/local-q4-three-hundred
```
