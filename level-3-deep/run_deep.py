"""Run the Deep study and write results_deep.json.

Run: python level-3-deep/run_deep.py

The deterministic part of the output (quality, token model,
modelled cloud costs, privacy, verdict) is identical across
runs. The timing part (index build and answer latency, wall
clock) varies and is the named exclusion from that check.
No cloud call is made: cloud figures are computed from the
published pricing table in study.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from study import (  # noqa: E402
    CLOUD_LATENCY_ASSUMED_MS,
    PRICING_CHECKED,
    audit_deep_sources,
    axis_winners,
    cost_table,
    decision_rules,
    run_local_measurement,
)

SOURCE_FILES = ("study.py", "run_deep.py")
ROUNDS = 5


def main():
    measured = run_local_measurement(rounds=ROUNDS)
    source_texts = {}
    for name in SOURCE_FILES:
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            source_texts[name] = f.read()
    audit = audit_deep_sources(source_texts)
    costs = cost_table(measured["mean_input_tokens_est"],
                       measured["mean_output_tokens_est"])
    out = {
        "scenario": "local against cloud study: local side measured "
                    "with the Build pipeline on its 24 labelled "
                    "questions (latency, quality, privacy audit); "
                    "cloud side modelled from published pricing "
                    "and stated token assumptions only, no API call",
        "pricing_checked": PRICING_CHECKED,
        "ollama": {"available": False,
                   "check": "no ollama binary on PATH and no server "
                            "on localhost port 11434, rechecked "
                            "2026-11-05 on the Muse VM; the local "
                            "core stays extractive"},
        "local_quality_measured": measured["quality"],
        "token_model": {
            "estimator": "estimated tokens = ceil(words / 0.75), "
                         "a stated assumption, not a provider "
                         "tokenizer",
            "prompt_shape": "instruction line plus the top 3 "
                            "retrieved chunk texts plus the "
                            "question, built locally, never sent",
            "output_proxy": "word count of the local answer for "
                            "the same question",
            "mean_input_tokens_est": measured["mean_input_tokens_est"],
            "mean_output_tokens_est": measured["mean_output_tokens_est"],
            "per_query": measured["per_query"],
        },
        "cloud_costs_modelled": {
            "label": "MODELLED from published pricing, not measured",
            "local_marginal_api_cost_usd": 0.0,
            "local_cost_note": "no API fee by construction; "
                               "electricity and hardware excluded",
            "rows": costs,
        },
        "cloud_latency_assumption": {
            "label": "ASSUMED, unverified, not measured",
            "range_ms": list(CLOUD_LATENCY_ASSUMED_MS),
            "note": "planning range for a hosted API answer "
                    "(network round trip plus generation); used "
                    "only for the order of magnitude comparison",
        },
        "privacy": {
            "local_audit_build": "2 source files scanned, 7 "
                                 "network patterns, 0 matches, "
                                 "passed (level-2-build results)",
            "local_audit_deep": audit,
            "local_data_transfer": "none by construction: inputs "
                                   "and outputs are local files",
            "cloud_data_transfer": "the prompt and the retrieved "
                                   "private chunks leave the "
                                   "machine to the provider by "
                                   "construction",
            "google_tier_note": "the Google pricing page states "
                                "free tier content is used to "
                                "improve products and paid tier "
                                "content is not",
        },
        "verdict": {"axis_winners": axis_winners(),
                    "decision_rules": decision_rules()},
        "timing": measured["timing"],
    }
    q = measured["quality"]
    t = measured["timing"]
    print(f"Local quality: top1 {q['top1_correct']}/"
          f"{q['evidence_questions']} = {q['top1_accuracy']}; "
          f"sentence {q['sentence_correct']}/"
          f"{q['evidence_questions']} = {q['sentence_accuracy']}; "
          f"refusal precision {q['refusal_precision']}, recall "
          f"{q['refusal_recall']}")
    print(f"Tokens (estimated): mean input "
          f"{measured['mean_input_tokens_est']:.2f}, mean output "
          f"{measured['mean_output_tokens_est']:.2f}")
    for row in costs:
        print(f"Modelled {row['model']}: "
              f"${row['cost_per_query_usd']:.6f} per query, "
              f"${row['cost_per_100000_queries_usd']:.2f} per 100k")
    print(f"Timing: index build mean {t['index_build_ms_mean']:.3f} ms; "
          f"answer latency mean {t['answer_latency_ms_mean']:.4f} ms, "
          f"median {t['answer_latency_ms_median']:.4f} ms, max "
          f"{t['answer_latency_ms_max']:.4f} ms over "
          f"{t['queries_timed']} timed answers")
    print(f"Deep audit passed={audit['passed']} "
          f"total={audit['total_matches']}")
    path = os.path.join(HERE, "results_deep.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
