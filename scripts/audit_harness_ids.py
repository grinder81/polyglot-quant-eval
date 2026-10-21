"""Explain raw doc-ID labels without rewriting evidence or changing scoring."""
import argparse
import json
from pathlib import Path


def label_map(requested):
    if len(requested) != len(set(requested)):
        raise ValueError('Duplicate requested indices')
    # Installed doc_iterator enumerates selected documents in dataset order;
    # evaluator.py maps that ordinal through the original requested sequence.
    return dict(zip(sorted(requested), requested, strict=True))


def audit(root):
    lock = json.loads((root / 'sample-identities.json').read_text(encoding='utf-8'))
    counts = {}
    for lang in ('eng_Latn', 'ben_Beng', 'hin_Deva'):
        explained = mislabeled = total = 0
        for start in range(0, 300, 5):
            members = [g[lang] for g in lock['items'][start:start+5]]
            indices = [m['index'] for m in members]
            expected_labels = label_map(indices)
            keys = {(m['source'], m['question']): m['index'] for m in members}
            data = json.loads((root / 'local-q4' / f'{lang}-{start:03}.json').read_text(encoding='utf-8'))
            seen = set()
            for row in data['samples']['belebele_' + lang]:
                key = row['doc']['link'], row['doc']['question_number']
                if key not in keys or key in seen:
                    raise ValueError('Unexpected or duplicate content identity')
                seen.add(key)
                actual = keys[key]
                total += 1
                explained += row['doc_id'] == expected_labels[actual]
                mislabeled += row['doc_id'] != actual
            if len(seen) != 5:
                raise ValueError('Incomplete shard')
        counts[lang] = dict(total=total, explained_by_order_mapping=explained, mislabeled=mislabeled)
        if explained != total:
            raise ValueError('Unexplained labels; do not attribute all mismatches to this bug')
    return dict(languages=counts, total=sum(r['total'] for r in counts.values()),
                mislabeled=sum(r['mislabeled'] for r in counts.values()),
                explained_by_order_mapping=sum(r['explained_by_order_mapping'] for r in counts.values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2))


if __name__ == '__main__':
    main()
