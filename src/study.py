"""Local against cloud study, Level 3 Deep.

The local side is measured: the Build pipeline answers its 24
labelled questions on this machine, with per query latency, the
Build quality metrics, and the privacy audit. The cloud side is
modelled, never measured: no API is called, no key is used, and
every cloud cost figure is computed in code from published
pricing (sources and check date in DEEP-SPEC.md) and stated
token assumptions. Cloud quality and cloud latency are not
measured at all; the study compares capability and carries one
labelled latency assumption instead. Standard library only.
"""
import math
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from assistant import ChunkIndex, build_questions, evaluate, ingest_directory  # noqa: E402
from local_first import audit_sources  # noqa: E402

PRICING_CHECKED = "2026-11-05"
INSTRUCTION = ("Answer the question using only the context below. "
               "Cite the source for each fact. If the context does "
               "not contain the answer, say you do not know.")
WORDS_PER_TOKEN = 0.75
CLOUD_LATENCY_ASSUMED_MS = (1000.0, 3000.0)
VOLUMES = (1, 1000, 100000, 1000000)

PRICING_MODELS = [
    {"model": "gpt-6-luna", "provider": "OpenAI",
     "input_rate": 0.10, "output_rate": 0.50,
     "source": "https://developers.openai.com/api/docs/pricing"},
    {"model": "claude-haiku-5.5", "provider": "Anthropic",
     "input_rate": 0.10, "output_rate": 0.50,
     "note": "prompts up to 100,000 tokens",
     "source": "https://platform.claude.com/docs/en/about-claude/pricing"},
    {"model": "gemini-3.5-flash-lite", "provider": "Google",
     "input_rate": 0.30, "output_rate": 2.50,
     "source": "https://ai.google.dev/gemini-api/docs/pricing"},
    {"model": "gemini-3.8-flash", "provider": "Google",
     "input_rate": 0.75, "output_rate": 3.75,
     "note": "rate through 2026-12-31, doubles 2027-01-01",
     "source": "https://ai.google.dev/gemini-api/docs/pricing"},
    {"model": "gpt-6.1-sol", "provider": "OpenAI",
     "input_rate": 2.00, "output_rate": 10.00,
     "source": "https://developers.openai.com/api/docs/pricing"},
    {"model": "claude-sonnet-5.5", "provider": "Anthropic",
     "input_rate": 2.00, "output_rate": 10.00,
     "source": "https://platform.claude.com/docs/en/about-claude/pricing"},
]


class DeepError(Exception):
    """Named error for Deep level failures."""


def estimate_tokens(word_count):
    """Estimated tokens for a word count: ceil(words / 0.75).

    Stated assumption, not a provider tokenizer: 1 token is
    about 0.75 words of English text.
    """
    if not isinstance(word_count, int) or word_count < 0:
        raise DeepError("word_count must be a non-negative integer")
    return int(math.ceil(word_count / WORDS_PER_TOKEN))


def build_cloud_prompt(chunk_texts, question):
    """The prompt a cloud answer would send, built locally only.

    Shape: the instruction line, the retrieved chunk texts as
    context, then the question. Nothing is sent anywhere.
    """
    parts = [INSTRUCTION, "Context:"]
    parts.extend(chunk_texts)
    parts.append("Question: " + question)
    return "\n".join(parts)


def cost_for_tokens(model, input_tokens, output_tokens):
    """Modelled cost in USD for one query at published rates.

    cost = (input tokens / 1,000,000) times input rate plus
    (output tokens / 1,000,000) times output rate.
    """
    return (input_tokens / 1000000.0) * model["input_rate"] + \
        (output_tokens / 1000000.0) * model["output_rate"]


def cost_table(mean_input_tokens, mean_output_tokens):
    """Modelled cost rows per model at the named volumes."""
    rows = []
    for model in PRICING_MODELS:
        per_query = cost_for_tokens(model, mean_input_tokens,
                                    mean_output_tokens)
        row = {"model": model["model"], "provider": model["provider"],
               "input_rate": model["input_rate"],
               "output_rate": model["output_rate"],
               "source": model["source"],
               "cost_per_query_usd": per_query}
        for volume in VOLUMES:
            row["cost_per_%d_queries_usd" % volume] = per_query * volume
        rows.append(row)
    return rows


def decision_rules():
    """The verdict as an ordered, testable rule list."""
    return [
        {"condition": "the data must not leave the device, or the "
                      "work must run offline",
         "winner": "local",
         "reason": "the cloud prompt carries the question and the "
                   "retrieved private chunks to the provider; the "
                   "local pipeline sends nothing anywhere"},
        {"condition": "the question needs paraphrase, synonyms, "
                      "facts combined across documents, or general "
                      "knowledge the documents do not hold",
         "winner": "cloud",
         "reason": "the local core is extractive and exact token "
                   "matching only; it cannot do any of these, and "
                   "refuses or misses instead"},
        {"condition": "the question is a lookup whose answer is a "
                      "sentence inside the local documents, at any "
                      "volume",
         "winner": "local",
         "reason": "measured local quality on the eval set is "
                   "perfect and the marginal API cost is zero, "
                   "while every cloud query carries a modelled "
                   "fee and a data transfer"},
        {"condition": "the corpus is large, messy, or in formats "
                      "beyond plain text",
         "winner": "cloud",
         "reason": "the local ingest reads plain text files with "
                   "a Title first line only; hosted models accept "
                   "far more, at the modelled price and with the "
                   "privacy transfer named above"},
        {"condition": "a fluent written answer matters more than "
                      "a verbatim cited sentence",
         "winner": "cloud",
         "reason": "the local core returns copied sentences and "
                   "cannot write; a generative model writes, and "
                   "can also write without evidence, which the "
                   "local refusal rule exists to prevent"},
    ]


def axis_winners():
    """One winner per axis, each with its evidence kind named."""
    return [
        {"axis": "cost", "winner": "local",
         "evidence": "local marginal API cost is zero by "
                     "construction; cloud costs are modelled "
                     "from published pricing"},
        {"axis": "speed", "winner": "local",
         "evidence": "local latency is measured on this corpus; "
                     "the cloud figure is a labelled assumed "
                     "range, so the win is order of magnitude "
                     "only and corpus bound"},
        {"axis": "quality_on_eval_set", "winner": "local",
         "evidence": "measured on the Build eval set only; cloud "
                     "quality is not measured in this study"},
        {"axis": "quality_capability", "winner": "cloud",
         "evidence": "capability comparison, not a measurement: "
                     "generation, paraphrase, synthesis, and "
                     "general knowledge against extraction only"},
        {"axis": "privacy", "winner": "local",
         "evidence": "source audit with zero network pattern "
                     "matches and no data transfer by "
                     "construction, against a prompt transfer "
                     "to the provider by construction"},
    ]


def run_local_measurement(rounds=5):
    """Measure the Build pipeline and build the token model.

    Returns a dict with a deterministic part (quality, token
    counts, per query rows) and a timing part (latency samples
    summarised). Latency is wall clock and varies between runs;
    it is the named determinism exclusion.
    """
    if not isinstance(rounds, int) or rounds < 1:
        raise DeepError("rounds must be a positive integer")
    docs = ingest_directory(os.path.join(ROOT, "experiments", "corpus"))
    questions = build_questions()
    build_samples_ms = []
    index = None
    for _ in range(rounds):
        start = time.perf_counter()
        index = ChunkIndex(docs)
        build_samples_ms.append((time.perf_counter() - start) * 1000.0)
    quality = evaluate(index, questions)["summary"]
    chunk_text = {c["chunk_id"]: c["text"] for c in index.chunks}
    latency_samples_ms = []
    per_query = []
    for item in questions:
        ranked = index.retrieve_chunks(item["question"], top_k=3)
        texts = [chunk_text[e["chunk_id"]] for e in ranked]
        prompt = build_cloud_prompt(texts, item["question"])
        samples = []
        result = None
        for _ in range(rounds):
            start = time.perf_counter()
            result = index.answer(item["question"])
            samples.append((time.perf_counter() - start) * 1000.0)
        latency_samples_ms.extend(samples)
        prompt_words = len(prompt.split())
        output_words = len(result["answer_text"].split())
        per_query.append({
            "question_id": item["id"], "refused": result["refused"],
            "prompt_words": prompt_words, "output_words": output_words,
            "input_tokens_est": estimate_tokens(prompt_words),
            "output_tokens_est": estimate_tokens(output_words),
        })
    mean_in = sum(r["input_tokens_est"] for r in per_query) / len(per_query)
    mean_out = sum(r["output_tokens_est"] for r in per_query) / len(per_query)
    timing = {
        "rounds": rounds,
        "queries_timed": len(latency_samples_ms),
        "index_build_ms_mean": statistics.mean(build_samples_ms),
        "index_build_ms_min": min(build_samples_ms),
        "index_build_ms_max": max(build_samples_ms),
        "answer_latency_ms_mean": statistics.mean(latency_samples_ms),
        "answer_latency_ms_median": statistics.median(latency_samples_ms),
        "answer_latency_ms_min": min(latency_samples_ms),
        "answer_latency_ms_max": max(latency_samples_ms),
        "note": "timing fields vary between runs and are excluded "
                "from the determinism check",
    }
    return {"quality": quality, "per_query": per_query,
            "mean_input_tokens_est": mean_in,
            "mean_output_tokens_est": mean_out, "timing": timing}


def audit_deep_sources(source_texts):
    """Privacy scan over Deep sources, reusing the Learn audit."""
    return audit_sources(source_texts)
