import importlib.util, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("mfa", os.path.join(ROOT, "scripts", "margin_flip_analysis.py"))
mfa = importlib.util.module_from_spec(spec); spec.loader.exec_module(mfa)


def test_bins_and_flips():
    ref = {("t", "s1", "1"): ([0.0, -0.1, -5, -6], 0),   # near tie, margin 0.1
           ("t", "s1", "2"): ([0.0, -3.0, -5, -6], 0),   # confident, margin 3
           ("t", "s2", "1"): ([-0.7, 0.0, -5, -6], 1)}   # margin 0.7
    cand = {("t", "s1", "1"): ([-0.2, 0.0, -5, -6], 0),  # flipped
            ("t", "s1", "2"): ([0.0, -2.9, -5, -6], 0),  # same
            ("t", "s2", "1"): ([-0.6, 0.0, -5, -6], 1)}  # same
    res = mfa.analyze(ref, cand)["t"]
    assert res["n"] == 3 and res["total_flips"] == 1
    by = {tuple(b["margin_nats"]): b for b in res["bins"]}
    assert by[(0.0, 0.25)]["flips"] == 1 and by[(0.0, 0.25)]["n"] == 1
    assert by[(2.0, None)]["n"] == 1 and by[(2.0, None)]["flips"] == 0
    assert abs(res["share_margin_below_1_nat"] - 2 / 3) < 1e-9
