# Rotation preflight evidence

Both pinned GGUF arms match the original tokenizer on all 1,200 diagnostic contexts
and 4,800 candidate sequences, including exact decoded text. The two reports record
the same generated lock hash and their respective model/runtime file hashes.
The lock is reproducible from the frozen source lock and committed rotation specification
using `scripts/prepare_rotation_lock.py`; its working copy is stored under the experiment
root's `pilot/rotation-control/rotation-lock.json` (9,459,690 bytes).

Checks used vocabulary-only CPU loading with the existing patched runtime. The warning
about the temporary vocabulary-only context exceeding zero training context appeared;
no inference was requested and all token/text comparisons passed. This is tokenizer
compatibility evidence, not a rotation accuracy result or speed measurement.

`scripts/check_rotation_harness.py --lock ROTATION_LOCK` passed five Bangla documents
at shift one through the unchanged upstream evaluator with its own DummyLM. Raw dummy
scores are temporary and deleted, never included as model results. The test validates
source membership, rendered prompts, remapped targets and score/accuracy consistency.
The scorer endpoint is replaced only inside this test; operational scoring uses the
unchanged installed GGUFLM integration. Real rotation scoring awaits A1 completion.
