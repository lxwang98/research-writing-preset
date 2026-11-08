# multi-source-paper-search

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill that turns **one** literature request into a **cross-source** scan. It fans out to four academic sources at once, dedupes the results deterministically, and reconciles them into a single cited synthesis — telling you what's corroborated, what's contested, and what only one source saw.

> 一次请求，跨 4 个学术源检索 → 确定性去重（DOI / arXiv-id / 标题并查集）→ 共识 / 分歧 / 独有贡献对齐 → 带引用的综合报告。多源去重与共识对齐是这个 skill 的核心价值，不是手搓拼凑能替代的。

## What it does

Searching one source at a time gives you a partial, source-biased view. This skill:

1. **Expands** your query into a few method-alias variants (recall insurance — dedup across variants is free).
2. **Fans out** to OpenAlex, Semantic Scholar, arXiv (via Valyu), and Perplexity in one shot.
3. **Dedupes deterministically** — `scripts/fanout.py` unions records by DOI / arXiv-id / normalized title (union-find), so a paper seen by 3 sources is counted once with a `consensus = 3`.
4. **Cross-validates claims** — the agent reconciles abstracts and the Perplexity narrative into consensus vs. divergence.
5. **Writes a cited report** — 检索概况 → 共识发现 → 分歧高亮 → 每源独有贡献 → 论文排名表 → 参考文献.

The split is deliberate: **mechanical work** (fan-out, normalization, dedup) lives in the script and is exact; **semantic work** (query expansion, claim-level reconciliation, the report) is the agent's half.

## Sources & keys

| Source | Key | Notes |
|---|---|---|
| **OpenAlex** | none | 240M+ works, citation counts. Always live — this is the floor; at least one source always runs. |
| **Semantic Scholar** | optional `S2_API_KEY` | Works keyless but the unauthenticated pool 429s readily; a [free key](https://www.semanticscholar.org/product/api) makes it reliable. Best dedup anchor (exposes both DOI and arXiv id). |
| **arXiv (Valyu)** | Valyu key | Preprints + **full text** for claim re-checking. Configured via the `arxiv-search` skill's setup (see below), **not** an env var. |
| **Perplexity** | `OPENROUTER_API_KEY` | Web-grounded synthesis + recent work via [OpenRouter](https://openrouter.ai/keys) (needs credits). |

**Graceful degradation:** `fanout.py` probes each source and **skips** any with a missing key/script — it never crashes the run. Skipped sources are reported under `skipped_sources`, and the report always states "used X / 4 sources" so consensus counts are read in the right context. With zero keys you still get a full OpenAlex-only run.

## External dependency — arXiv via `arxiv-search`

The arXiv source is the one piece that isn't self-contained: `fanout.py` shells out to the `arxiv-search` skill's Node locator, found dynamically with:

```bash
find ~/.claude -path "*/arxiv-search/*/scripts/search" -type f | head -1
```

If `arxiv-search` isn't installed, or its Valyu key isn't configured, the arXiv source simply lands in `skipped_sources` and the other three sources produce the report as normal. To enable it:

```bash
SEARCH=$(find ~/.claude -path "*/arxiv-search/*/scripts/search" -type f | head -1)
"$SEARCH" setup <your-valyu-key>   # free $10 credit at https://platform.valyu.ai
```

Everything else (`fanout.py`) is **pure Python stdlib** — no `pip install`, runs on any `python3`.

## Install

```bash
# 1. Drop the skill into your Claude Code skills directory
cp -r multi-source-paper-search ~/.claude/skills/

# 2. Add your keys (optional — OpenAlex works with none)
cd ~/.claude/skills/multi-source-paper-search
cp .env.example .env
# edit .env: set OPENROUTER_API_KEY and/or S2_API_KEY
```

`fanout.py` auto-loads `.env` from the skill root on startup **without** overriding your shell environment — no `source`, no profile edits. `.env` is gitignored; only `.env.example` is committed.

## Usage

**In Claude Code** — just ask, in any language:

> "多源搜一下 retrieval-augmented generation 在临床问答上的论文"
> "find papers on X across sources — what's the consensus vs. what's contested?"

The skill triggers on cross-source literature intent (多源 / 交叉 / triangulated / corroborated …) and prefers itself over any single-source skill when the goal is a literature *scan* rather than fetching one known paper.

**Standalone** — the fan-out script runs on its own:

```bash
python scripts/fanout.py --depth 20 "retrieval augmented generation" "RAG clinical QA"
```

It emits one JSON object: `papers` (deduped, ranked, each with `consensus` = # distinct sources and `per_source_unique`), `sources_used`, `skipped_sources`, and `perplexity_narrative`. Depth defaults to 20/source — drop to ~10 for a quick scan, raise to 30+ for an exhaustive one.

## Repo layout

```
multi-source-paper-search/
├── SKILL.md                      # the skill definition (procedure, anti-patterns, fallbacks)
├── scripts/fanout.py             # deterministic fan-out + dedup (pure stdlib)
├── references/
│   ├── sources.md                # per-source invocation, keys, how to add a 5th source
│   └── report-template.md        # the report structure the agent follows
├── evals/evals.json              # evaluation prompts
├── .env.example                  # key template (copy to .env)
└── LICENSE                       # MIT
```

Adding a fifth source is a contained change — see `references/sources.md` (Crossref / PubMed / CORE are good candidates).

## License

[MIT](LICENSE) © 2026 PlutoLei

---

*by [Lei Yuxuan](https://plutolei.github.io) ([@PlutoLei](https://github.com/PlutoLei))*
