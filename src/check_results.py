"""Prove results/ regenerates from the code and the corpus in experiments/.

Run: python src/check_results.py

Runs the four runners, compares every regenerated results file with
the committed one, then puts the committed files back. Wall clock
fields (keys containing "latency_ms" or "build_ms", recorded on the study VM) vary
between machines and are the only thing left out of the comparison;
results_learn.json and results_build.json must match byte for byte.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNERS = ("run_learn.py", "run_build.py", "run_deep.py", "run_rigor.py")
NAMES = ("results_learn.json", "results_build.json", "results_deep.json", "results_rigor.json")
BYTE_EXACT = ("results_learn.json", "results_build.json")


def strip_timing(value):
    if isinstance(value, dict):
        return {k: strip_timing(v) for k, v in value.items() if "latency_ms" not in k and "build_ms" not in k}
    if isinstance(value, list):
        return [strip_timing(v) for v in value]
    return value


def timing_filter_self_check():
    # A check that fails if the timing filter drops anything else.
    sample = {"index_build_ms": 1, "b": {"answer_latency_ms_mean": 2, "range_ms": 3, "e": [{"g": 5}]}}
    assert strip_timing(sample) == {"b": {"range_ms": 3, "e": [{"g": 5}]}}


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
                same = fresh == committed[p]
            else:
                same = strip_timing(json.loads(fresh)) == strip_timing(json.loads(committed[p]))
            print(("same      " if same else "DIFFERENT ") + "results/" + name)
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
