# Lossless packaging after the complete T1 report

`scripts/archive_t1_baselines.py` packages a **trusted, complete report produced by
the frozen T1 scientific command**. It does not run that command, score models,
recompute scientific metrics, read partial results to choose endpoints, or change
any scientific source/input. The root process owns collection and report execution.
Structural completeness checks here do not independently validate the statistical
methods or authenticate an arbitrary user-created report.

Wait until both fresh arms and their live gates are complete, the exact frozen
report command succeeds, and its report and final execution-record SHA-256 values
are recorded. The execution record is a reviewed historical receipt containing
the original `report_command` and runtime references, not an instruction to start
processes or evidence of current authorization/server state. Run packaging where
the recorded original source paths are accessible. Do not rewrite frozen metadata
to make relocated source files pass.

## Package and proof

The new destination contains only:

```text
archive-manifest.json
bf16-gguf.tar.gz
local-q4.tar.gz
validation.tar.gz
validated-report.json.gz
```

Each arm archive contains exactly 180 original five-question shards and one run
identity, under `raw/ARM/`. Every shard must match its final report byte hash.
**Identity proof differs:** the frozen T1 report stores the full identity object,
not the identity file's original byte hash. The packager requires exact **typed
JSON** equality (so `1`, `1.0` and `true` are distinct), then records and preserves
the original selected identity file's bytes/hash. It does not claim that a
previous report-bound identity byte hash existed.

The validation archive has a fixed whitelist: each arm's expanded direct oracle,
client and reverse-order JSON; exact validator and protocol; runtime manifest and
vocabulary-token check; shared preparation receipt and the reviewed execution
record. The gates/token/preparation/runtime source bytes must match hashes in the
complete report's identity. Runtime JSON must also match the report's full runtime
object. The execution record and final report must match their explicitly supplied
trusted byte hashes. There is no broad filesystem or log-directory collection.

There are 379 original evidence files in this layout: 360 shards, two identities,
16 validation/provenance files and one report. Hashes and byte lengths are stored
for every original member and every compressed archive. Gzip uses an empty filename
and `mtime=0`; tar member ordering and metadata are deterministic. The source
originals are never deleted, reserialized or overwritten. A new destination is
mandatory; interrupted output remains for inspection rather than being replaced.

The request lock, tokenizer/model/native binaries, historical A1 evidence and A3
evidence are **references**, not duplicated payloads. Their recorded identities
remain in the report, preparation/execution receipts and the existing committed
evidence. This package does not bundle weights, credentials, holdout data or raw
server logs. Preserve any required log hashes/pointers separately in the reviewed
execution receipt. Review metadata for privacy and license/attribution requirements
before external sharing; sanitize derived public prose without modifying immutable
scientific bytes or silently omitting required provenance.

The final root receipt must include the agreed completion ledger, derived from
actual evidence only (the earlier readiness proposal or raw ops log alone fails):

```json
{
  "archive_completion": {
    "schema": "t1-completed-execution-receipt-v1",
    "collection_complete": true,
    "report_exit_code": 0,
    "report_sha256": "ACTUAL_COMPLETE_REPORT_SHA256",
    "report_bytes": 0,
    "arms": {
      "bf16-gguf": {"validated_shards": 180, "validated_questions": 900,
                    "runner_exit_code": 0, "server_stopped": true},
      "local-q4": {"validated_shards": 180, "validated_questions": 900,
                   "runner_exit_code": 0, "server_stopped": true}
    }
  }
}
```

This is a **schema illustration**, not a completed receipt: replace the checksum
and byte-count placeholder with actual report evidence; no such completion is
claimed here. Retain the top-level `report_command`, per-arm `runtime_manifest`
and `runtime_manifest_sha256` source references plus audited process history.
Strict booleans/integers, successful exits, both complete arm counts, stopped
servers, and report hash/length equality are required. The packager checks the
reviewed historical receipt; it never queries or stops a live process itself.

## Commands (offline packaging only)

```text
python -m scripts.archive_t1_baselines create \
  --report COMPLETE_FROZEN_REPORT.json --report-sha256 TRUSTED_REPORT_SHA256 \
  --execution-record REVIEWED_EXECUTION_RECORD.json \
  --execution-record-sha256 TRUSTED_EXECUTION_RECORD_SHA256 \
  --destination NEW_PACKAGE_DIRECTORY

python -m scripts.archive_t1_baselines verify PACKAGE_DIRECTORY \
  --report-sha256 TRUSTED_REPORT_SHA256 \
  --execution-record-sha256 TRUSTED_EXECUTION_RECORD_SHA256
```

Verification streams fixed, regular tar members without filesystem extraction;
it rejects duplicate, traversal, link, unexpected or missing members. It verifies
compressed and decompressed hashes/lengths and derives original proofs from the
archived report and execution metadata. It does **not** need the original machine
paths or a model environment. Supply independently retained expected report and
execution hashes when checking those trust anchors; an index is an integrity
receipt, not a cryptographic signature or external peer review.

## Results PR and article boundaries

Once actual complete evidence exists, a small results PR can add the five package
files, a source-backed README/LOG entry and a reviewed execution receipt. Link
the complete report and archive index. Preserve all languages and English-relative
effects; distinguish fresh original-order BF16 GGUF/Q4 outcomes from historical
runtime comparisons and from A3 rotation means. Report margin association as
exploratory. Do not relabel the original BF16 vLLM reference or historical A1/A2.

Numerical prose, tables and any figure wait for the complete validated report and
independent review. No current T1 result is asserted by this utility or its synthetic
tests. A4 and later experiment gates remain separate. User publication approval,
privacy/provenance/license checks and external submission gates are unchanged.
