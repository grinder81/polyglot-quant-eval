"""Download pinned Belebele subsets and record installed task definitions; no scoring."""
import argparse
import hashlib
import importlib.metadata
import json
from datetime import date, datetime
from pathlib import Path

import lm_eval
from datasets import load_dataset

REVISION = "7899cdfa4e1e0d733fd77c848e2c273cb1d32be2"
LANGUAGES = ("eng_Latn", "ben_Beng", "hin_Deva")


def encode_extra(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    task_dir = Path(lm_eval.__file__).parent / "tasks" / "belebele"
    definitions = {}
    for name in ["_default_template_yaml"] + [f"belebele_{lang}.yaml" for lang in LANGUAGES]:
        data = (task_dir / name).read_bytes()
        definitions[name] = {"sha256": hashlib.sha256(data).hexdigest(), "text": data.decode()}
    subsets = {}
    for language in LANGUAGES:
        dataset = load_dataset("facebook/belebele", language, revision=REVISION, split="test")
        digest = hashlib.sha256()
        for row in dataset:
            if str(row["correct_answer_num"]) not in {"1", "2", "3", "4"}:
                raise ValueError("Invalid target")
            digest.update((json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=encode_extra) + "\n").encode())
        subsets[language] = {"rows": len(dataset), "columns": dataset.column_names,
                             "ordered_rows_sha256": digest.hexdigest()}
    result = {"dataset": "facebook/belebele", "revision": REVISION,
              "lm_eval_version": importlib.metadata.version("lm_eval"),
              "datasets_version": importlib.metadata.version("datasets"),
              "split": "test", "use": "development/baseline; not reserved final test",
              "task_definitions": definitions, "subsets": subsets,
              "status": "dataset and task audit only; sample lock and runtime scoring unverified"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Pinned subsets and task definitions audited; no model scoring performed.")


if __name__ == "__main__":
    main()
