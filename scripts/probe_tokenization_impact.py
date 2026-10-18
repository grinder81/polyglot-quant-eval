"""Fixed-weight diagnostic of differing prompt tokens; not a benchmark adapter."""
import argparse
import json
from pathlib import Path

import numpy as np
from llama_cpp import Llama


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    wanted = {(row["language"], row["index"]) for row in audit["context_mismatches"]}
    model = Llama(model_path=args.model, n_gpu_layers=-1, n_ctx=8192,
                  logits_all=True, verbose=False, seed=42)
    results = []
    for group in lock["items"][:50]:
        for language, row in group.items():
            if (language, row["index"]) not in wanted:
                continue
            candidate_ids = [ids[len(row["context_ids"]):] for ids in row["token_ids"]]
            assert all(len(ids) == 1 for ids in candidate_ids), "Only single-token diagnostic"
            variants = dict(original=row["context_ids"],
                            gguf=model.tokenize(row["prompt"].encode(), add_bos=True))
            scores = {}
            for name, tokens in variants.items():
                model.reset()
                model.eval(tokens)
                logits = model.scores[model.n_tokens - 1].astype(np.float64)
                assert np.isfinite(logits).all() and np.ptp(logits) > 0, "Invalid logits"
                maximum = logits.max()
                normalizer = maximum + np.log(np.exp(logits - maximum).sum())
                values = [float(logits[ids[0]] - normalizer) for ids in candidate_ids]
                scores[name] = dict(logprobs=values, selected=int(np.argmax(values)),
                                    token_count=len(tokens))
            results.append(dict(language=language, index=row["index"],
                                target=row["target"], scores=scores))
    args.output.write_text(json.dumps(dict(results=results,
        scope="Five affected prompts, identical BF16 GGUF weights; diagnostic only"),
        indent=2), encoding="utf-8")
    print(f"Completed {len(results)} fixed-weight comparisons.")


if __name__ == "__main__":
    main()
