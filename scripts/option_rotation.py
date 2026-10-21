"""Diagnostic option rotation and source-separated additive letter-offset estimates."""
import hashlib
import math


def rotate_document(doc, shift):
    if shift not in range(4):
        raise ValueError('Expected rotation 0..3')
    result = dict(doc)
    for position in range(4):
        result[f'mc_answer{position + 1}'] = doc[f'mc_answer{(position + shift) % 4 + 1}']
    target = int(doc['correct_answer_num']) - 1
    if target not in range(4):
        raise ValueError('Invalid gold answer')
    result['correct_answer_num'] = str((target - shift) % 4 + 1)
    return result


def original_choice(position, shift):
    if position not in range(4) or shift not in range(4):
        raise ValueError('Invalid option or rotation')
    return (position + shift) % 4


def source_fold(source):
    return int(hashlib.sha256(source.encode()).hexdigest(), 16) % 5


def estimate_offsets(groups):
    """Fit on complete four-rotation groups, without reading correct answers.

    Each group is four score vectors in rotation order. Centering removes a
    context-wide offset. Averaging balanced rotations cancels additive content
    effects; content-position interactions need not cancel and require validation.
    """
    total = [0.0] * 4
    count = 0
    for rotations in groups:
        if len(rotations) != 4:
            raise ValueError('Incomplete rotation group')
        for scores in rotations:
            if len(scores) != 4 or not all(math.isfinite(x) for x in scores):
                raise ValueError('Invalid score vector')
            center = sum(scores) / 4
            for i in range(4):
                total[i] += scores[i] - center
            count += 1
    if not count:
        raise ValueError('Empty fit set')
    return [x / count for x in total]


def cross_fitted_offsets(records):
    """One arm/language at a time; record keys are source, question and rotations."""
    keys = [(r['source'], r['question']) for r in records]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate question identity')
    estimates = {}
    for fold in {source_fold(r['source']) for r in records}:
        fit = [r['rotations'] for r in records if source_fold(r['source']) != fold]
        estimates[fold] = estimate_offsets(fit)
    return {(r['source'], r['question']): estimates[source_fold(r['source'])] for r in records}


def predict(scores, offsets=None):
    if len(scores) != 4 or not all(math.isfinite(x) for x in scores):
        raise ValueError('Invalid score vector')
    offsets = [0.0] * 4 if offsets is None else offsets
    if len(offsets) != 4 or not all(math.isfinite(x) for x in offsets):
        raise ValueError('Invalid offsets')
    return max(range(4), key=lambda i: scores[i] - offsets[i])
