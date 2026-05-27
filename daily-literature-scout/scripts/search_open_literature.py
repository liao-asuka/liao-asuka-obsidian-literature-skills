#!/usr/bin/env python3
"""Search open literature APIs and emit normalized paper candidates as JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def read_profile(path: Path) -> dict[str, list[str] | str]:
    text = path.read_text(encoding="utf-8")
    sections: dict[str, list[str] | str] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current and line:
            value = line.lstrip("-*0123456789. ").strip()
            if value:
                assert isinstance(sections[current], list)
                sections[current].append(value)
    return sections


def profile_terms(profile: dict[str, list[str] | str]) -> list[str]:
    terms: list[str] = []
    for key in ("研究主题", "核心关键词", "同义词与扩展词", "重点方法/模型", "重点材料/对象", "重点应用场景"):
        values = profile.get(key, [])
        if isinstance(values, str):
            values = [values]
        for value in values:
            cleaned = re.sub(r"^[#\-*\s]+", "", value).strip()
            if cleaned and "待填写" not in cleaned:
                terms.append(cleaned)
    return terms


def is_latin_heavy(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    latin = [char for char in letters if ord(char) < 128]
    return len(latin) / len(letters) >= 0.7


def build_queries(terms: list[str]) -> list[str]:
    latin_terms = [term for term in terms if is_latin_heavy(term)]
    preferred = latin_terms or terms
    queries: list[str] = []
    if preferred:
        queries.append(" ".join(preferred[:6]))
    for index in range(0, min(len(preferred), 12), 3):
        query = " ".join(preferred[index : index + 3])
        if query and query not in queries:
            queries.append(query)
    return queries[:5]


def request_json(url: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "obsidian-literature-scout/1.0 (mailto:example@example.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def inverted_abstract(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in index.items():
        for loc in locs:
            positions.append((loc, word))
    return " ".join(word for _, word in sorted(positions))


def normalize_openalex(item: dict[str, Any]) -> dict[str, Any]:
    authors = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])[:8]]
    location = item.get("primary_location") or {}
    source = (location.get("source") or {}).get("display_name") or item.get("host_venue", {}).get("display_name") or ""
    oa = item.get("open_access") or {}
    return {
        "id": item.get("id", ""),
        "source_api": "OpenAlex",
        "title": item.get("title") or item.get("display_name") or "",
        "year": item.get("publication_year"),
        "authors": [a for a in authors if a],
        "venue": source,
        "doi": item.get("doi") or "",
        "url": item.get("doi") or item.get("id") or "",
        "abstract": inverted_abstract(item.get("abstract_inverted_index")),
        "citation_count": item.get("cited_by_count") or 0,
        "is_open_access": bool(oa.get("is_oa")),
        "pdf_url": oa.get("oa_url") or "",
    }


def search_openalex(query: str, per_page: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "search": query,
        "per-page": per_page,
        "sort": "publication_date:desc",
    })
    data = request_json(f"https://api.openalex.org/works?{params}")
    return [normalize_openalex(item) for item in data.get("results", [])]


def normalize_semantic(item: dict[str, Any]) -> dict[str, Any]:
    open_access_pdf = item.get("openAccessPdf") or {}
    authors = [a.get("name", "") for a in item.get("authors", [])[:8]]
    external = item.get("externalIds") or {}
    doi = external.get("DOI") or ""
    return {
        "id": item.get("paperId", ""),
        "source_api": "Semantic Scholar",
        "title": item.get("title") or "",
        "year": item.get("year"),
        "authors": [a for a in authors if a],
        "venue": item.get("venue") or "",
        "doi": f"https://doi.org/{doi}" if doi and not doi.startswith("http") else doi,
        "url": item.get("url") or "",
        "abstract": item.get("abstract") or "",
        "citation_count": item.get("citationCount") or 0,
        "is_open_access": bool(open_access_pdf.get("url")),
        "pdf_url": open_access_pdf.get("url") or "",
    }


def search_semantic(query: str, limit: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "query": query,
        "limit": min(limit, 100),
        "fields": "title,year,authors,venue,externalIds,url,abstract,citationCount,openAccessPdf",
    })
    data = request_json(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}")
    return [normalize_semantic(item) for item in data.get("data", [])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--source", choices=["all", "openalex", "semantic"], default="all")
    args = parser.parse_args()

    profile = read_profile(args.profile)
    terms = profile_terms(profile)
    if not terms:
        raise SystemExit(f"No search terms found in {args.profile}")

    queries = build_queries(terms)
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    per_query = max(10, min(args.limit, 80) // max(1, len(queries)))
    for query in queries:
        if args.source in ("all", "openalex"):
            try:
                candidates.extend(search_openalex(query, per_query))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"OpenAlex [{query}]: {exc}")
        if args.source in ("all", "semantic"):
            try:
                time.sleep(1)
                candidates.extend(search_semantic(query, per_query))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Semantic Scholar [{query}]: {exc}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"queries": queries, "candidate_count": len(candidates), "errors": errors, "candidates": candidates}
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
