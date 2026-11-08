# Website project page copy: local-first-ai

Site: jesunahmadushno.com
Status: COPY ONLY, draft for the project page. Dated 2026-11-05.
Nothing on any website was changed by this file.

## Headline

local-first-ai: a measured local against cloud study, with the local side offline by construction

## Summary

local-first-ai is an open local-first assistant study built by
Jesun Ahmad Ushno as project P15 in Roadmap v3. It indexes local
documents with TF-IDF, answers with cited extracted sentences,
refuses below a named threshold, and compares the measured local
core against cloud costs modelled from published pricing. It runs
on the Python standard library only, with no network call in the
local pipeline.

Two scope facts, stated plainly. There is no Ollama and no
language model in any level: Ollama was rechecked unavailable on
2026-11-05, so the assistant is an extractive core. The cloud
side is modelled only, never measured.

Status: v1.0, 2026-11-05. Learn, Build, and Deep are done.
Total tests: 62, plus the scaffold smoke test.

## Results

| Level | Set | Key result | Notes |
| --- | --- | --- | --- |
| Learn | 8 docs, 10 questions | Top-1 1.000, recall at 3 1.000, sentence 1.000 | Privacy audit clean; 21 tests |
| Build | 24 docs, 72 chunks, 24 questions | Top-1 1.000, chunk recall at 3 1.000, sentence 1.000, refusal precision and recall 1.000 | Threshold 0.30; session memory; 42 tests in total |
| Deep | Build eval set plus pricing model | Local top-1 1.000, latency 0.3326 ms mean; modelled cloud 0.000031 to 0.000621 USD per query | Cloud modelled only, not measured; 62 tests in total |

The perfect local scores are weak evidence: the corpus is
synthetic with distinct topics.

## Honest limits

- No Ollama, no LLM, no embeddings, no generation or paraphrase.
- Synthetic corpus only; no real private files evaluated.
- Cloud quality and latency not measured; latency is an assumed
  1,000 to 3,000 ms range, labelled as assumed.
- Token counts are a word based estimate, not provider tokenizers.
- Run on the Muse VM (CPU), not the assigned BlackBox node.

## Links

- GitHub repo: https://github.com/JesunAhmadUshno/local-first-ai
- Release v0.1 (Learn): https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v0.1
- Release v0.5 (Build): https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v0.5
- Release v1.0 (Learn, Build, Deep): https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v1.0
- Tutorial: fanout/tutorial.md in the GitHub repo
- Blog post draft: fanout/blog-post.md in the GitHub repo

## License note

Code: Apache-2.0. Tutorials: CC BY 4.0.
