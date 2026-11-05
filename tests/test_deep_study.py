"""Unit tests for the Level 3 Deep local against cloud study.

Hand-computed expectations for the token estimator and the
cost model, plus pricing table integrity, verdict structure,
privacy guard, and determinism of the non-timing results.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
from study import (  # noqa: E402
    CLOUD_LATENCY_ASSUMED_MS,
    PRICING_MODELS,
    DeepError,
    audit_deep_sources,
    axis_winners,
    build_cloud_prompt,
    cost_for_tokens,
    cost_table,
    decision_rules,
    estimate_tokens,
    run_local_measurement,
)


class TestTokenEstimator(unittest.TestCase):
    def test_estimate_tokens_hand_computed(self):
        # ceil(words / 0.75): 3 words give 4 tokens, 75 words
        # give 100 tokens, 0 words give 0 tokens.
        self.assertEqual(estimate_tokens(0), 0)
        self.assertEqual(estimate_tokens(3), 4)
        self.assertEqual(estimate_tokens(75), 100)
        self.assertEqual(estimate_tokens(76), 102)

    def test_estimate_tokens_rejects_negative(self):
        with self.assertRaises(DeepError):
            estimate_tokens(-1)

    def test_prompt_shape_contains_instruction_chunks_question(self):
        prompt = build_cloud_prompt(["chunk one text", "chunk two"],
                                    "What is this?")
        self.assertTrue(prompt.startswith("Answer the question"))
        self.assertIn("chunk one text", prompt)
        self.assertIn("Question: What is this?", prompt)


class TestCostModelHandComputed(unittest.TestCase):
    def test_cost_one_million_input_tokens_at_budget_rate(self):
        # gpt-6-luna: 1,000,000 input tokens at 0.10 USD per
        # million and no output cost exactly 0.10 USD.
        model = PRICING_MODELS[0]
        self.assertEqual(model["model"], "gpt-6-luna")
        self.assertAlmostEqual(cost_for_tokens(model, 1000000, 0),
                               0.10, places=12)

    def test_cost_mixed_hand_computed(self):
        # Sonnet class rates 2.00 in and 10.00 out: 500,000 input
        # tokens cost 1.00 and 100,000 output tokens cost 1.00,
        # so the query costs exactly 2.00 USD.
        model = {"input_rate": 2.00, "output_rate": 10.00}
        self.assertAlmostEqual(cost_for_tokens(model, 500000, 100000),
                               2.00, places=12)

    def test_cost_zero_tokens_is_zero(self):
        self.assertEqual(cost_for_tokens(PRICING_MODELS[0], 0, 0), 0.0)

    def test_cost_table_scales_linearly_with_volume(self):
        rows = cost_table(200.0, 40.0)
        for row in rows:
            self.assertAlmostEqual(row["cost_per_1000_queries_usd"],
                                   row["cost_per_query_usd"] * 1000,
                                   places=12)
            self.assertAlmostEqual(row["cost_per_1000000_queries_usd"],
                                   row["cost_per_query_usd"] * 1000000,
                                   places=9)
            self.assertGreater(row["cost_per_query_usd"], 0.0)

    def test_flagship_costs_more_than_budget_per_query(self):
        rows = {r["model"]: r for r in cost_table(200.0, 40.0)}
        self.assertGreater(rows["claude-sonnet-5.5"]["cost_per_query_usd"],
                           rows["gpt-6-luna"]["cost_per_query_usd"] * 10)


class TestPricingTableIntegrity(unittest.TestCase):
    def test_six_models_three_providers_with_sources(self):
        self.assertEqual(len(PRICING_MODELS), 6)
        providers = {m["provider"] for m in PRICING_MODELS}
        self.assertEqual(providers, {"OpenAI", "Anthropic", "Google"})
        for model in PRICING_MODELS:
            self.assertTrue(model["source"].startswith("https://"))
            self.assertGreater(model["input_rate"], 0)
            self.assertGreater(model["output_rate"], model["input_rate"])

    def test_budget_tie_and_flagship_tie_rates(self):
        rates = {m["model"]: (m["input_rate"], m["output_rate"])
                 for m in PRICING_MODELS}
        self.assertEqual(rates["gpt-6-luna"], (0.10, 0.50))
        self.assertEqual(rates["claude-haiku-5.5"], (0.10, 0.50))
        self.assertEqual(rates["gpt-6.1-sol"], (2.00, 10.00))
        self.assertEqual(rates["claude-sonnet-5.5"], (2.00, 10.00))
        self.assertEqual(rates["gemini-3.8-flash"], (0.75, 3.75))


class TestVerdictStructure(unittest.TestCase):
    def test_every_rule_names_a_winner_and_a_reason(self):
        rules = decision_rules()
        self.assertEqual(len(rules), 5)
        for rule in rules:
            self.assertIn(rule["winner"], ("local", "cloud"))
            self.assertTrue(rule["condition"])
            self.assertTrue(rule["reason"])
        winners = {r["winner"] for r in rules}
        self.assertEqual(winners, {"local", "cloud"})

    def test_privacy_rule_is_first_and_local(self):
        first = decision_rules()[0]
        self.assertEqual(first["winner"], "local")
        self.assertIn("must not leave", first["condition"])

    def test_axis_winners_cover_the_four_spec_axes(self):
        axes = {row["axis"] for row in axis_winners()}
        self.assertTrue({"cost", "speed", "privacy"} <= axes)
        self.assertTrue(any(a.startswith("quality") for a in axes))

    def test_cloud_latency_is_labelled_assumption_range(self):
        self.assertEqual(CLOUD_LATENCY_ASSUMED_MS, (1000.0, 3000.0))


class TestMeasuredLocalSide(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measured = run_local_measurement(rounds=2)

    def test_quality_matches_build_eval(self):
        q = self.measured["quality"]
        self.assertEqual(q["top1_accuracy"], 1.0)
        self.assertEqual(q["sentence_accuracy"], 1.0)
        self.assertEqual(q["refusal_precision"], 1.0)
        self.assertEqual(q["refusal_recall"], 1.0)
        self.assertEqual(q["documents"], 24)
        self.assertEqual(q["chunks"], 72)

    def test_token_rows_cover_all_24_questions(self):
        rows = self.measured["per_query"]
        self.assertEqual(len(rows), 24)
        self.assertEqual(sum(1 for r in rows if r["refused"]), 4)
        for row in rows:
            self.assertEqual(row["input_tokens_est"],
                             estimate_tokens(row["prompt_words"]))
            self.assertEqual(row["output_tokens_est"],
                             estimate_tokens(row["output_words"]))
            self.assertGreater(row["prompt_words"], row["output_words"])

    def test_deterministic_part_is_stable_across_runs(self):
        again = run_local_measurement(rounds=2)
        self.assertEqual(again["per_query"], self.measured["per_query"])
        self.assertEqual(again["quality"], self.measured["quality"])
        self.assertEqual(again["mean_input_tokens_est"],
                         self.measured["mean_input_tokens_est"])
        self.assertEqual(again["mean_output_tokens_est"],
                         self.measured["mean_output_tokens_est"])

    def test_timing_block_shape(self):
        timing = self.measured["timing"]
        self.assertEqual(timing["rounds"], 2)
        self.assertEqual(timing["queries_timed"], 48)
        self.assertGreater(timing["answer_latency_ms_mean"], 0.0)
        self.assertGreaterEqual(timing["answer_latency_ms_max"],
                                timing["answer_latency_ms_mean"])


class TestPrivacyGuard(unittest.TestCase):
    def test_deep_sources_pass_the_audit(self):
        here = os.path.join(ROOT, "level-3-deep")
        texts = {}
        for name in ("study.py", "run_deep.py"):
            with open(os.path.join(here, name), encoding="utf-8") as f:
                texts[name] = f.read()
        audit = audit_deep_sources(texts)
        self.assertEqual(audit["files_scanned"],
                         ["run_deep.py", "study.py"])
        self.assertEqual(audit["total_matches"], 0)
        self.assertTrue(audit["passed"])

    def test_results_file_labels_modelled_and_assumed(self):
        path = os.path.join(ROOT, "level-3-deep", "results_deep.json")
        if not os.path.exists(path):
            self.skipTest("results_deep.json not generated yet")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("MODELLED", data["cloud_costs_modelled"]["label"])
        self.assertIn("ASSUMED", data["cloud_latency_assumption"]["label"])
        self.assertFalse(data["ollama"]["available"])


if __name__ == "__main__":
    unittest.main()
