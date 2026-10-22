# Bounded upstream runner smoke

One five-question English plain-letter shard per arm verifies the complete
ConfigurableTask → LocalCompletionsAPI → evaluator → saved-shard validator path.
Both passed against the independently validated cold runtime. A repeat Q4
invocation with `--max-new-shards 0` revalidated its saved shard without new
scored requests. This is plumbing evidence, not the full A3 variant comparison
or an accuracy estimate for selecting a contract.

The source files were frozen before these smokes and are pinned by byte hash in
each identity; upstream git metadata names the preceding repository HEAD because
the reviewed runner had not yet been committed. The full experiment uses merged
source and fresh directories. The unrelated untracked check_llama_echo.py was
preserved and unused.

Live probability correctness and order checks, all languages/variants/rotations,
are in [runtime PR36](https://github.com/grinder81/tiny-aya-edge/pull/36).
The exact request lock and runtime/gate files remain in the recorded WSL root;
no holdout was accessed. These intentionally incomplete directories must not pass
the final report loader's 720-shard-per-arm completeness gate.
