"""Freeze aligned development items using unchanged upstream task rendering."""
import argparse
import hashlib
import json
import random
import subprocess
from pathlib import Path

import lm_eval
import yaml
from lm_eval.api.task import ConfigurableTask

REVISION = "7899cdfa4e1e0d733fd77c848e2c273cb1d32be2"
LANGUAGES = ["eng_Latn", "ben_Beng", "hin_Deva"]


def tasks():
    root = Path(lm_eval.__file__).parent / "tasks" / "belebele"
    common = yaml.safe_load((root / "_default_template_yaml").read_text())
    result = {}
    for language in LANGUAGES:
        config = common | yaml.safe_load((root / f"belebele_{language}.yaml").read_text())
        config.pop("include")
        config["dataset_kwargs"] = {"revision": REVISION}
        config["num_fewshot"] = 0
        result[language] = ConfigurableTask(config=config)
    return result


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--tokenizer-python", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    loaded = tasks()
    maps = {}
    for language, task in loaded.items():
        maps[language] = {(row["link"], row["question_number"]): i
                          for i, row in enumerate(task.test_docs())}
        assert len(maps[language]) == len(task.test_docs()), "Duplicate item ID"
    keys = sorted(maps[LANGUAGES[0]])
    assert all(set(keys) == set(mapping) for mapping in maps.values())
    random.Random(42).shuffle(keys)
    selected, excluded = [], []
    for key in keys:
        group = {}
        for language, task in loaded.items():
            index = maps[language][key]
            row = task.test_docs()[index]
            prompt = task.fewshot_context(row, num_fewshot=0)
            requests = task.construct_requests(row, prompt)
            candidates = [request.args[1] for request in requests]
            assert candidates == [" A", " B", " C", " D"]
            group[language] = dict(index=index, source=key[0], question=key[1],
                prompt=prompt, prompt_sha256=digest(prompt), candidates=candidates,
                candidate_sha256=[digest(c) for c in candidates],
                target=int(task.doc_to_target(row)))
        selected.append(group)
        if len(selected) == 300:
            break
    assert len(selected) == 300
    rows = [row for group in selected for row in group.values()]
    texts = [text for row in rows for text in
             [row["prompt"]] + [row["prompt"] + c for c in row["candidates"]]]
    code = ("import json,sys; from transformers import AutoTokenizer; "
            "t=AutoTokenizer.from_pretrained(sys.argv[1],local_files_only=True); "
            "print(json.dumps(t(json.load(sys.stdin),add_special_tokens=True)['input_ids']))")
    encoded = json.loads(subprocess.check_output(
        [args.tokenizer_python, "-c", code, args.tokenizer],
        input=json.dumps(texts).encode()))
    for i, row in enumerate(rows):
        prefix, *ids = encoded[i * 5:(i + 1) * 5]
        assert all(tokens[:len(prefix)] == prefix for tokens in ids), "Boundary mismatch"
        assert max(map(len, ids)) < 8192, "Overlength item; stop before selection lock"
        row.update(context_ids=prefix, token_ids=ids)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(revision=REVISION, seed=42, context=8192,
        purpose="development baseline, not reserved final test", pilot_count=50,
        excluded_overlength=excluded, items=selected), ensure_ascii=False), encoding="utf-8")
    print("Locked 300 aligned items; first 50 per language form the pilot.")


if __name__ == "__main__":
    main()
