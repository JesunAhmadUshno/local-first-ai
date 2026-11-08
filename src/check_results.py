"""Prove results/ regenerates from the code and the corpus in experiments/.

Run: python src/check_results.py

Runs the four runners, compares every regenerated results file with
the committed one, then puts the committed files back. Wall clock
fields (keys containing "latency_ms" or "build_ms", recorded on the study VM) vary
between machines and are the only thing left out of the comparison.
On Python 3.12, the version the results were recorded with,
results_learn.json and results_build.json must match byte for byte.
Python 3.11 sums floats without compensation (3.12 changed sum()), so
there every float is compared to a relative tolerance of 1e-9 instead.
"""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNERS = ("run_learn.py", "run_build.py", "run_deep.py", "run_rigor.py")
NAMES = ("results_learn.json", "results_build.json", "results_deep.json", "results_rigor.json")
BYTE_EXACT = ("results_learn.json", "results_build.json") if sys.version_info >= (3, 12) else ()
FLOAT_TOL = 0.0 if sys.version_info >= (3, 12) else 1e-9


def strip_timing(value):
    if isinstance(value, dict):
        return {k: strip_timing(v) for k, v in value.items() if "latency_ms" not in k and "build_ms" not in k}
    if isinstance(value, list):
        return [strip_timing(v) for v in value]
    return value


def first_difference(a, b, where="$"):
    """Path of the first difference, or None; floats within FLOAT_TOL count as equal."""
    if isinstance(a, float) and isinstance(b, float):
        return None if math.isclose(a, b, rel_tol=FLOAT_TOL, abs_tol=FLOAT_TOL) else where
    if type(a) is not type(b):
        return where
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return where + " keys"
        for k in a:
            d = first_difference(a[k], b[k], f"{where}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return where + " length"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_difference(x, y, f"{where}[{i}]")
            if d:
                return d
        return None
    return None if a == b else where


def timing_filter_self_check():
    # A check that fails if the timing filter drops anything else.
    sample = {"index_build_ms": 1, "b": {"answer_latency_ms_mean": 2, "range_ms": 3, "e": [{"g": 5}]}}
    assert strip_timing(sample) == {"b": {"range_ms": 3, "e": [{"g": 5}]}}
    assert first_difference({"x": [1.0, "s"]}, {"x": [1.5, "s"]}) == "$.x[0]"
    assert first_difference({"x": "s"}, {"x": "t"}) == "$.x"


def main():
    timing_filter_self_check()
    paths = [os.path.join(ROOT, "results", n) for n in NAMES]
    committed = {}
    for p in paths:
        with open(p, "rb") as f:
            committed[p] = f.read()
    failures = []
    try:
        for r in RUNNERS:
            subprocess.run([sys.executable, os.path.join(ROOT, "src", r)], check=True, stdout=subprocess.DEVNULL)
        for p in paths:
            with open(p, "rb") as f:
                fresh = f.read()
            name = os.path.basename(p)
            if name in BYTE_EXACT:
                diff = None if fresh == committed[p] else "bytes"
            else:
                diff = first_difference(strip_timing(json.loads(committed[p])), strip_timing(json.loads(fresh)))
            same = diff is None
            print(("same      " if same else "DIFFERENT ") + "results/" + name + ("" if same else " at " + diff))
            if not same:
                failures.append(name)
    finally:
        for p, data in committed.items():
            with open(p, "wb") as f:
                f.write(data)
    if failures:
        sys.exit("results do not regenerate from the evidence: " + ", ".join(failures))
    print("results regenerate from the evidence (wall clock fields excluded)")


if __name__ == "__main__":
    main()
