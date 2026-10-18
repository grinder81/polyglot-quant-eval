"""Compare real pilot request tokens; no inference or adapter implementation."""
import argparse
import json
from pathlib import Path
from llama_cpp import Llama


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    model = Llama(model_path=args.model, vocab_only=True, verbose=False)
    count = 0
    failures = []
    for group in lock["items"][:50]:
        for language, row in group.items():
            prefix = model.tokenize(row["prompt"].encode(), add_bos=True)
            if prefix != row["context_ids"]:
                first = next((i for i, (a, b) in enumerate(zip(prefix, row["context_ids"]))
                              if a != b), min(len(prefix), len(row["context_ids"])))
                failures.append(dict(language=language, index=row["index"],
                    prompt_sha256=row["prompt_sha256"], first_difference=first,
                    expected_length=len(row["context_ids"]), actual_length=len(prefix),
                    expected_slice=row["context_ids"][max(0, first-3):first+8],
                    actual_slice=prefix[max(0, first-3):first+8]))
            for candidate, expected in zip(row["candidates"], row["token_ids"]):
                actual = model.tokenize((row["prompt"] + candidate).encode(), add_bos=True)
                count += int(actual == expected)
    args.output.write_text(json.dumps({"passed_requests": count, "total_requests":600,
                           "context":8192, "context_mismatches":failures},indent=2),
                           encoding="utf-8")
    if failures or count != 600:
        raise ValueError(f"Pilot blocked: {len(failures)} context mismatches, {count}/600 requests match")
    print(f"Matched {count} candidate requests against the original tokenizer.")


if __name__ == "__main__":
    main()
