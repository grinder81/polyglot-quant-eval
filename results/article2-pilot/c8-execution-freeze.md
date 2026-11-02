# C8 execution freeze before comparative outcomes

The [complete T3 decision](../t3-precision-curve/final/README.md) selects Q3_K_M at 1,799,740,928 bytes. The [mechanically derived execution plan](c8-plan.json) has SHA256 `e7ccdb50be254ee8bdde307f73c58bc9a9c9d68882a40aa453b9b516ec8be64f`. It binds the full actual operating inventory, native library/source hashes, fixed private pool, source membership, eight tensors, artifact paths and cumulative caps. No C8 comparative outcome was collected before this freeze.

The operating gate tensor is Q3_K. The frozen rule therefore chooses real native **Q2_K and Q3_K** diagnostics, with no importance matrix and all other diagnostic tensors unchanged from BF16. Each restricted complete-map pair locks all other tensor types to the operating-point inventory. Both orientations have exactly equal predicted bytes and are within the operating budget:

| Prespecified pair | Bytes for each orientation | Eligible |
| --- | ---: | --- |
| Attention V blocks 0/3 | 1,799,224,832 | Yes |
| MLP down blocks 0/17 | 1,788,644,864 | Yes |
| MLP down blocks 17/35 | 1,791,462,912 | Yes |
| MLP gate/up block 17 | 1,797,451,264 | Yes |

The matched comparison is between the two orientations of the nominated pair; these maps need not equal the operating point's bytes. Actual exports must match their predictions, satisfy the ceiling and have identical nonpair payloads. No padding supplies equality.

The [frozen scientific design](../../docs/c8-bounded-pilot.md) remains Git blob `cd43458f25672a0522958a4d1de0e1a88c307dc7`. Construction and probe sources are disjoint across three repetitions, with 192 content tokens per individual-language or pooled arm in each repetition. Repetitions 1–2 discover at most one nominee in fixed pair order; a full hash-bound nomination, including explicit none, is frozen before repetition 3. Only the nominated actual complete maps can confirm opposite BN/EN directions on the independent source sample. This is an investment screen, not an allocation task-benefit claim.

Native builds/probes have a cumulative 90-minute cap; proxies have 30 minutes; all C8 artifacts have a 400 GB cap. The persistent ledger enforces them and final reporting requires passed operation receipts. Resource sampling records observed global GPU and owned-process RAM use; global GPU readings include desktop apps and sampled maxima are lower bounds on continuous peak. Proxy Torch allocation peaks are reported separately. Holdout outcomes and A4 slices remain sealed.
