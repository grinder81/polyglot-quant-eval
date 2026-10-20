"""Validate and compare the local Q4 arm against the completed baseline."""
import argparse
import json
from pathlib import Path

from summarize_baseline import LANGS, load


def compare(local_root, baseline_root):
    identity, local = load(local_root, "local-q4")
    result = {"n_per_language": 50, "correct": {
        lang: sum(s["acc"] for k, s in local.items() if k[0] == lang)
        for lang in LANGS}, "comparisons": {}}
    for arm in ("q4", "bf16-gguf", "bf16-vllm"):
        old_identity, old = load(baseline_root, arm)
        assert identity["lock"] == old_identity["lock"]
        assert identity["runner"] == old_identity["runner"]
        assert local.keys() == old.keys()
        for key in local:
            assert local[key]["arguments"] == old[key]["arguments"]
            assert local[key]["target"] == old[key]["target"]
        stats = {}
        for lang in LANGS:
            pairs = [(old[k], local[k]) for k in local if k[0] == lang]
            stats[lang] = {
                "changed_choices": sum(a["prediction"] != b["prediction"] for a, b in pairs),
                "right_to_wrong": sum(a["acc"] == 1 and b["acc"] == 0 for a, b in pairs),
                "wrong_to_right": sum(a["acc"] == 0 and b["acc"] == 1 for a, b in pairs),
                "delta_pp": 2 * sum(b["acc"] - a["acc"] for a, b in pairs),
                "max_absolute_likelihood_difference": max(
                    abs(x[0] - y[0]) for a, b in pairs
                    for x, y in zip(a["filtered_resps"], b["filtered_resps"])),
            }
        for lang in LANGS:
            stats[lang]["delta_gap_vs_english_pp"] = stats[lang]["delta_pp"] - stats["eng_Latn"]["delta_pp"]
        result["comparisons"][arm] = stats
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("local_root", type=Path)
    p.add_argument("baseline_root", type=Path)
    args = p.parse_args()
    print(json.dumps(compare(args.local_root, args.baseline_root), indent=2))
