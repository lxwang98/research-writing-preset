#!/usr/bin/env python3
"""
fanout.py — multi-source paper search: fan out, normalize, dedup-align.

Does the *deterministic* half of the skill. The LLM-driven half (query
expansion, claim-level cross-validation, report synthesis) lives in SKILL.md.

Pipeline:
  1. Probe which sources are reachable (key present / script installed).
  2. Run every (source, query-variant) pair concurrently.
  3. Normalize each hit into a common schema.
  4. Cluster duplicates across variants AND sources with union-find over
     three identity signals: DOI, arXiv id, normalized title.
  5. Merge each cluster into one record carrying `consensus` (# distinct
     sources that hit it) and `per_source_unique`, then rank.

Usage:
  python fanout.py [--depth 20] "query 1" ["query 2" ...]

Output: a single JSON object on stdout (see bottom of file for shape).
Why JSON to stdout: the caller (Claude, following SKILL.md) reads it back and
does the semantic synthesis. Keeping this script pure-data keeps the boundary
clean — deterministic dedup here, judgement there.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

OPENALEX_MAILTO = "agent@kortix.ai"  # polite-pool email -> 10 req/s instead of 1
HTTP_TIMEOUT = 40


def _load_local_env():
    """Load KEY=VALUE lines from a .env next to the skill (../.env from here),
    without overriding anything already in the environment. This makes the skill
    self-contained for keys: drop OPENROUTER_API_KEY / S2_API_KEY into that file
    once and every future run picks them up — no shell profile, no `source`."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


_load_local_env()


# --------------------------------------------------------------------------- #
# Normalization helpers — the identity logic the whole dedup rests on.
# --------------------------------------------------------------------------- #
def norm_title(t):
    if not t:
        return ""
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def norm_doi(d):
    if not d:
        return ""
    d = d.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.strip()


_ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")


def extract_arxiv_id(*candidates):
    for c in candidates:
        if not c:
            continue
        m = _ARXIV_RE.search(str(c))
        if m:
            return m.group(1)
    return ""


def reconstruct_abstract(inverted_index):
    """OpenAlex stores abstracts as an inverted index {word: [positions]}."""
    if not inverted_index:
        return ""
    positions = []
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def _http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _record(source, title, authors=None, year=None, doi="", arxiv_id="",
            url="", cited_by=None, abstract="", relevance=None):
    return {
        "source": source,
        "title": (title or "").strip(),
        "authors": authors or [],
        "year": year,
        "doi": norm_doi(doi),
        "arxiv_id": arxiv_id or "",
        "url": url or "",
        "cited_by": cited_by,
        "abstract": (abstract or "").strip(),
        "relevance": relevance,
    }


# --------------------------------------------------------------------------- #
# Source adapters — each returns (list[record], error_or_None).
# Reuse existing skill scripts where they exist; don't re-implement API logic.
# --------------------------------------------------------------------------- #
def search_openalex(query, depth):
    q = urllib.parse.quote(query)
    url = (f"https://api.openalex.org/works?search={q}"
           f"&per_page={depth}&mailto={OPENALEX_MAILTO}")
    try:
        data = _http_json(url)
    except Exception as e:  # noqa: BLE001
        return [], f"openalex request failed: {e}"
    out = []
    for w in data.get("results", []):
        authors = [a.get("author", {}).get("display_name", "")
                   for a in w.get("authorships", [])]
        out.append(_record(
            "openalex",
            title=w.get("title") or w.get("display_name"),
            authors=[a for a in authors if a],
            year=w.get("publication_year"),
            doi=w.get("doi") or "",
            arxiv_id=extract_arxiv_id(w.get("doi"), (w.get("primary_location") or {}).get("landing_page_url")),
            url=(w.get("primary_location") or {}).get("landing_page_url") or w.get("id", ""),
            cited_by=w.get("cited_by_count"),
            abstract=reconstruct_abstract(w.get("abstract_inverted_index")),
            relevance=w.get("relevance_score"),
        ))
    return out, None


def search_semantic_scholar(query, depth):
    fields = "title,abstract,year,authors,citationCount,externalIds,url"
    q = urllib.parse.quote(query)
    url = (f"https://api.semanticscholar.org/graph/v1/paper/search"
           f"?query={q}&limit={min(depth, 100)}&fields={fields}")
    headers = {}
    if os.getenv("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    # The unauthenticated shared pool 429s readily; a couple of backed-off
    # retries recover most transient limits without a key.
    data, last_err = None, None
    for attempt in range(3):
        try:
            data = _http_json(url, headers=headers)
            break
        except Exception as e:  # noqa: BLE001
            last_err = e
            if "429" in str(e) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            break
    if data is None:
        return [], f"semantic_scholar request failed: {last_err}"
    out = []
    for p in data.get("data", []) or []:
        ext = p.get("externalIds") or {}
        out.append(_record(
            "semantic_scholar",
            title=p.get("title"),
            authors=[a.get("name", "") for a in (p.get("authors") or [])],
            year=p.get("year"),
            doi=ext.get("DOI", ""),
            arxiv_id=ext.get("ArXiv", "") or extract_arxiv_id(p.get("url")),
            url=p.get("url", ""),
            cited_by=p.get("citationCount"),
            abstract=p.get("abstract") or "",
        ))
    return out, None


def _find_arxiv_script():
    for base in (os.path.expanduser("~/.claude/plugins/cache"),
                 os.path.expanduser("~/.claude/skills")):
        for root, _dirs, files in os.walk(base):
            if "arxiv-search" in root and "scripts" in root and "search" in files:
                cand = os.path.join(root, "search")
                if os.access(cand, os.X_OK):
                    return cand
    return None


def search_arxiv(query, depth):
    script = _find_arxiv_script()
    if not script:
        return [], "arxiv-search script not found"
    # The arxiv-search script is a Node program that does
    # `console.log(bigJSON); process.exit()`. Node flushes stdout
    # asynchronously to a PIPE, so process.exit() truncates large output
    # mid-write (~60KB) when captured via a pipe — but writes to a regular
    # FILE synchronously. So redirect stdout to a temp file and read it back,
    # sidestepping the Node pipe-flush footgun rather than fighting it.
    try:
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            tmp_path = tf.name
        with open(tmp_path, "w", encoding="utf-8") as out_fh:
            subprocess.run([script, query, str(depth)], stdout=out_fh,
                           stderr=subprocess.DEVNULL, timeout=120, check=False)
        with open(tmp_path, encoding="utf-8") as in_fh:
            data = json.loads(in_fh.read() or "{}")
    except Exception as e:  # noqa: BLE001
        return [], f"arxiv invocation failed: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except (OSError, NameError):
            pass
    if not data.get("success"):
        if data.get("setup_required"):
            return [], "arxiv needs Valyu API key (setup_required)"
        return [], f"arxiv error: {data.get('error', 'unknown')}"
    out = []
    for r in data.get("results", []):
        content = r.get("content") or ""
        out.append(_record(
            "arxiv",
            title=r.get("title"),
            url=r.get("url", ""),
            arxiv_id=extract_arxiv_id(r.get("url"), r.get("title")),
            abstract=content[:1500],
            relevance=r.get("relevance_score"),
        ))
    return out, None


def search_perplexity(query, _depth):
    """Perplexity Sonar via OpenRouter, in academic search mode. Pure-stdlib
    (urllib) so the skill carries no non-stdlib dependency. Mirrors the behavior
    of the research-lookup skill (academic mode + citation extraction) rather
    than importing it, which would drag in `requests`. Appends the synthesized
    prose to _PPLX_NARRATIVE for the LLM's claim-level step."""
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return [], "perplexity needs OPENROUTER_API_KEY"
    body = json.dumps({
        "model": "perplexity/sonar-pro-search",
        "messages": [
            {"role": "system", "content": "You are an academic research assistant. "
             "Use scholarly sources (peer-reviewed papers, journals). Prioritize "
             "2020-2026 literature and give complete citations with DOIs."},
            {"role": "user", "content":
             f"Summarize the academic literature on: {query}. Cover key findings, "
             "the strongest methods, and any conflicting evidence. 400-700 words, "
             "with citations."},
        ],
        "max_tokens": 6000,
        "temperature": 0.1,
        "search_mode": "academic",
        "search_context_size": "high",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return [], f"perplexity request failed: {e}"
    choice = (data.get("choices") or [{}])[0]
    narrative = (choice.get("message") or {}).get("content", "")
    if narrative:
        _PPLX_NARRATIVE.append({"query": query, "narrative": narrative})
    # Citations live in search_results (new) or citations (legacy).
    results = (data.get("search_results")
               or choice.get("search_results")
               or (choice.get("message") or {}).get("search_results") or [])
    out = []
    for s in results:
        title, url = s.get("title", ""), s.get("url", "")
        if not (title or url):
            continue
        out.append(_record("perplexity", title=title, url=url,
                            arxiv_id=extract_arxiv_id(url),
                            doi=norm_doi(url) if "doi.org" in url else ""))
    for c in (data.get("citations") or choice.get("citations") or []):
        url = c if isinstance(c, str) else (c.get("url", "") if isinstance(c, dict) else "")
        if url:
            out.append(_record("perplexity", title="", url=url,
                                arxiv_id=extract_arxiv_id(url),
                                doi=norm_doi(url) if "doi.org" in url else ""))
    # sonar-pro-search often returns NO structured search_results, embedding
    # citations in the prose instead. Mine DOIs / arXiv ids from the text so
    # Perplexity hits can still merge (by DOI) with the other sources' records.
    out.extend(_citations_from_text(narrative))
    return out, None


_DOI_RE = re.compile(r"(?:doi[:\s]*|https?://(?:dx\.)?doi\.org/)(10\.\d{4,}/[^\s\)\]\,\[<>\"']+)", re.I)
_ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)


def _citations_from_text(text):
    out, seen = [], set()
    for doi in _DOI_RE.findall(text or ""):
        d = norm_doi(doi.rstrip(".,;:)]"))
        if d and d not in seen:
            seen.add(d)
            out.append(_record("perplexity", title="", doi=d,
                               url=f"https://doi.org/{d}"))
    for aid in _ARXIV_URL_RE.findall(text or ""):
        if aid not in seen:
            seen.add(aid)
            out.append(_record("perplexity", title="", arxiv_id=aid,
                               url=f"https://arxiv.org/abs/{aid}"))
    return out


_PPLX_NARRATIVE = []

SOURCES = {
    "openalex": search_openalex,
    "semantic_scholar": search_semantic_scholar,
    "arxiv": search_arxiv,
    "perplexity": search_perplexity,
}


# --------------------------------------------------------------------------- #
# Union-find dedup across all (source, variant) records.
# --------------------------------------------------------------------------- #
def identity_tokens(rec):
    toks = set()
    if rec["doi"]:
        toks.add("doi:" + rec["doi"])
    if rec["arxiv_id"]:
        toks.add("arxiv:" + rec["arxiv_id"])
    nt = norm_title(rec["title"])
    if len(nt) > 10:  # skip trivial titles to avoid false merges
        toks.add("title:" + nt)
    return toks


def cluster_records(records):
    parent = list(range(len(records)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    first_seen = {}
    for i, rec in enumerate(records):
        for t in identity_tokens(rec):
            if t in first_seen:
                union(i, first_seen[t])
            else:
                first_seen[t] = i

    groups = {}
    for i in range(len(records)):
        groups.setdefault(find(i), []).append(records[i])
    return list(groups.values())


def merge_cluster(group):
    def longest(field):
        return max((g[field] for g in group), key=lambda v: len(v or ""), default="")

    def first(field):
        for g in group:
            if g[field]:
                return g[field]
        return None

    def maxnum(field):
        vals = [g[field] for g in group if isinstance(g[field], (int, float))]
        return max(vals) if vals else None

    sources = sorted({g["source"] for g in group})
    authors = max((g["authors"] for g in group), key=len, default=[])
    doi = first("doi") or ""
    arxiv_id = first("arxiv_id") or ""
    url = ""
    for g in group:  # prefer a resolvable, canonical URL
        if g["url"]:
            url = g["url"]
            if "doi.org" in g["url"] or "arxiv.org" in g["url"]:
                break
    return {
        "title": longest("title"),
        "authors": authors,
        "year": first("year"),
        "doi": doi,
        "arxiv_id": arxiv_id,
        "url": url or (f"https://doi.org/{doi}" if doi else
                       (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "")),
        "cited_by": maxnum("cited_by"),
        "abstract": longest("abstract"),
        "sources": sources,
        "consensus": len(sources),
        "per_source_unique": len(sources) == 1,
    }


def rank_key(p):
    return (-p["consensus"],
            -(p["cited_by"] or 0),
            -len(p["abstract"]))


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Multi-source paper fan-out + dedup")
    ap.add_argument("queries", nargs="+", help="One or more query variants")
    ap.add_argument("--depth", type=int, default=20, help="Top-N per source per query")
    args = ap.parse_args()

    tasks = [(name, fn, q) for name, fn in SOURCES.items() for q in args.queries]
    all_records = []
    per_source_counts = {}
    errors = {}     # source -> first error seen (any variant)
    ran = set()     # sources that returned successfully on >=1 variant

    with ThreadPoolExecutor(max_workers=min(8, len(tasks))) as ex:
        futs = {ex.submit(fn, q, args.depth): (name, q) for name, fn, q in tasks}
        for fut in as_completed(futs):
            name, q = futs[fut]
            try:
                recs, err = fut.result()
            except Exception as e:  # noqa: BLE001
                recs, err = [], f"{name} crashed: {e}"
            if err:
                errors.setdefault(name, err)
            else:
                ran.add(name)  # success — even with 0 records (e.g. Perplexity
                               # returns a narrative but no structured papers)
            if recs:
                all_records.extend(recs)
                per_source_counts[name] = per_source_counts.get(name, 0) + len(recs)

    # "Used" = ran successfully at least once (decoupled from record count, so a
    # narrative-only Perplexity counts). "Skipped" = errored on every variant
    # and never ran. Computed at the end so the verdict is independent of which
    # variant's future resolved first.
    skipped = {name: err for name, err in errors.items() if name not in ran}

    clusters = cluster_records(all_records)
    papers = sorted((merge_cluster(g) for g in clusters), key=rank_key)

    out = {
        "queries": args.queries,
        "depth": args.depth,
        "sources_used": sorted(ran),
        "per_source_counts": per_source_counts,
        "skipped_sources": [{"source": s, "reason": r} for s, r in sorted(skipped.items())],
        "n_raw": len(all_records),
        "n_deduped": len(papers),
        "perplexity_narrative": _PPLX_NARRATIVE,
        "papers": papers,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
