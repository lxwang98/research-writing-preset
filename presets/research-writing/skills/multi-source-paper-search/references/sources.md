# Sources — invocation, keys, and how to add one

`scripts/fanout.py` owns all retrieval. This file documents each source so you
can reason about coverage gaps and degraded runs, and so adding a fifth source
is a small, contained change rather than a guess.

## The four sources

| Source | Key | Strengths | What it returns |
|---|---|---|---|
| **OpenAlex** | none | 240M+ works, citation counts, always-on | structured records (title/DOI/year/cited_by/authors/abstract) |
| **Semantic Scholar** | optional `S2_API_KEY` | `externalIds` (DOI **and** arXiv id) → best dedup anchor; citation counts | structured records |
| **arXiv (Valyu)** | Valyu key (via `arxiv-search` setup) | preprints, **full text** for claim re-checking | title/url/full-text; no year/cited_by |
| **Perplexity** | `OPENROUTER_API_KEY` | web-grounded synthesis + recent work; academic search mode | a prose narrative + citation list (title/url) |

OpenAlex needs no key and is the floor — at least one source is always live.

## Key detection & degradation

`fanout.py` probes each source and **skips** (never crashes) when a key or
script is missing. Skips are reported in the output under `skipped_sources`
with a reason. The report you write MUST surface this as "used X / 4 sources"
so the reader knows the consensus counts are relative to what actually ran.

- **OpenAlex** — always attempted.
- **Semantic Scholar** — attempted without a key; the unauthenticated pool
  429s readily, so `fanout.py` retries with backoff. Set `S2_API_KEY` to make
  it reliable (free key: https://www.semanticscholar.org/product/api).
- **arXiv** — located via `find ~/.claude/plugins/cache -path "*/arxiv-search/*/scripts/search"`.
  Returns `setup_required` until the Valyu key is configured:
  `<arxiv-search>/scripts/search setup <valyu-key>`.
- **Perplexity** — needs `OPENROUTER_API_KEY`. If absent it skips. The adapter
  calls OpenRouter directly via stdlib `urllib` (no `requests` dependency), so
  it runs on any python3.

**Where to put keys:** drop `OPENROUTER_API_KEY` / `S2_API_KEY` into a `.env`
file in the skill root (copy `.env.example`). `fanout.py` auto-loads it on
startup without overriding your shell env, so the skill is self-contained — no
`source`, no profile edits. arXiv is the exception: it stores its Valyu key in
`~/.valyu/config.json` via `<arxiv-search>/scripts/search setup <key>`.

## Why Perplexity is handled differently

The other three return clean paper lists. Perplexity returns a *synthesized
answer* plus loosely-structured citations. So `fanout.py`:
- adds its citations (title/url) as paper records → they participate in dedup,
  and a paper Perplexity cites that OpenAlex/S2 also returned gets a consensus
  bump (real cross-source corroboration);
- keeps the prose in the top-level `perplexity_narrative` field — that text is
  raw material for the **claim-level** synthesis, not a paper record.

## Adding a fifth source (the extension point)

1. Write a `search_<name>(query, depth) -> (list_of_records, error_or_None)`
   adapter. Build each record with the `_record(...)` helper so it lands in the
   common schema. Populate `doi` / `arxiv_id` whenever the API exposes them —
   that is what makes dedup work.
2. Register it in the `SOURCES` dict.
3. If it needs a key, probe the env var at the top of the adapter and return
   `([], "needs <ENV>")` when absent — that is the whole degradation contract.

Good candidates: Crossref (DOIs + metadata, no key), PubMed/E-utilities
(biomedical), CORE (open-access full text). Avoid nesting `deep-research` —
it is itself a multi-source harness and overlaps Perplexity's web grounding.
