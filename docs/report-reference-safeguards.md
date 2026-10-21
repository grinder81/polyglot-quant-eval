# Generic aggregate-report safeguards

The old reporter averaged by `format`, which could silently combine BF16 vLLM and
BF16 llama.cpp or different sample counts. The reporter now prints distinct run
rows without aggregation. Duplicate run/task/metric/language rows are rejected,
including accidental re-appends. A run ID may not contain multiple model/runtime
configurations. Existing rows remain readable for absolute-result display.

Delta reporting requires explicit identities:

```sh
python scripts/report.py results/rows.jsonl --task belebele --metric acc \
  --canonical-run BF16_VLLM_RUN --control-run BF16_GGUF_RUN --candidate-run LOCAL_Q4_RUN
```

The canonical reference must be BF16 in vLLM. The control is a separately identified
BF16 run; same-runtime compression comparisons require matching runtime/version.
The report prints control minus canonical (runtime/conversion), candidate minus
control (same-runtime compression), and candidate minus canonical (total difference).
For every language, it prints the corresponding English delta and the difference
from that English delta. Values stay in the metric's native units; accuracy .01
means one percentage point. Interpretation of a favorable sign depends on the metric.

All compared rows must match task/metric/language coverage, model source revision,
mode, few-shot count, n, sample-set hash, scoring-contract hash, backend/device and
OS metadata. Unknown required comparison fields are rejected. A missing English
row rejects that comparison instead of silently omitting the English control.
Use task/metric filters when coverage differs. `--ref-format` cannot select a reference.

The normalizer accepts `--model-revision`, `--sample-set-hash` and
`--scoring-contract-hash`. These are verified provenance supplied by the run owner,
not inferred from n or a model filename. The sample manifest must identify exact
source/question membership. The scoring contract must cover task revision, prompt
template, chat-template setting, candidate rendering, normalization, seeds and
decoding settings. The report compares declared identities; it does not independently
authenticate their source manifests. Do not invent missing hashes to enable deltas.
Older normalized rows without this provenance intentionally yield no delta table.

## Uncertainty

Print n and any supplied aggregate standard error. The standard error is not
presented as a paired or passage-clustered delta interval. Aggregate rows do not
contain the covariance or item/source membership needed to calculate such intervals.
Every delta explicitly states that limitation. Use the dedicated per-item paired
baseline analysis for the stored Stage 2 evidence, with passage-cluster resampling;
do not reconstruct paired uncertainty from marginal standard errors.

Synthetic regression coverage distinguishes two different BF16 results, tests all
three comparison directions and their English gaps, rejects n=50/n=300 and template,
mode, sample, runtime-version mismatches, and rejects duplicate rows/missing English.
No live inference script or saved model result is changed by these safeguards.
