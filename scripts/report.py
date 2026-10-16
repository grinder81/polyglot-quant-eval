#!/usr/bin/env python3
"""Per-language table and deltas vs the BF16 reference.

Usage: python scripts/report.py results/rows.jsonl [--task belebele] [--metric acc] [--ref-format bf16]
"""
import argparse, json
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows")
    ap.add_argument("--task", default=None)
    ap.add_argument("--metric", default=None)
    ap.add_argument("--ref-format", default="bf16")
    a = ap.parse_args()
    df = pd.DataFrame([json.loads(l) for l in open(a.rows) if l.strip()])
    if a.task:
        df = df[df.task == a.task]
    if a.metric:
        df = df[df.metric == a.metric]
    if df.empty:
        raise SystemExit("no rows after filtering")
    for (task, metric), g in df.groupby(["task", "metric"]):
        piv = g.pivot_table(index="language", columns="format", values="value", aggfunc="mean")
        print(f"\n== {task} / {metric} (mean over runs) ==")
        print(piv.round(3).to_string())
        if a.ref_format in piv.columns:
            delta = piv.sub(piv[a.ref_format], axis=0).drop(columns=[a.ref_format])
            if not delta.empty:
                print(f"\n-- delta vs {a.ref_format} (points) --")
                print((delta * 100).round(1).to_string())
                print("\n-- mean delta by format (points) --")
                print((delta.mean() * 100).round(2).to_string())
                if "en" in delta.index:
                    gap = delta.sub(delta.loc["en"], axis=1).drop(index=["en"])
                    print("\n-- gap vs English (points; negative = this language loses more than English) --")
                    print((gap * 100).round(1).to_string())

if __name__ == "__main__":
    main()
