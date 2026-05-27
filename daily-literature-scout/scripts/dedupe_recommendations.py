#!/usr/bin/env python3
"""Deduplicate literature candidates against a JSONL recommendation history."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", title.lower(), flags=re.UNICODE)).strip()


def paper_key(paper: dict[str, Any]) -> str:
    doi = str(paper.get("doi") or "").strip().lower()
    if doi:
        return "doi:" + doi.replace("https://doi.org/", "")
    source_api = str(paper.get("source_api") or "").lower()
    pid = str(paper.get("id") or "").strip().lower()
    if pid:
        return f"{source_api}:{pid}"
    title = normalize_title(str(paper.get("title") or ""))
    return "title:" + hashlib.sha256(title.encode("utf-8")).hexdigest()


def load_seen(path: Path) -> set[str]:
    seen: set[str] = set()
    if not path.exists():
        return seen
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = record.get("key")
        if key:
            seen.add(str(key))
    return seen


def append_records(path: Path, papers: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for paper in papers:
            record = {
                "date": date.today().isoformat(),
                "key": paper_key(paper),
                "title": paper.get("title", ""),
                "doi": paper.get("doi", ""),
                "id": paper.get("id", ""),
                "source_api": paper.get("source_api", ""),
                "year": paper.get("year"),
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--append-selected", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.candidates.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", payload if isinstance(payload, list) else [])
    seen = load_seen(args.state)
    kept: list[dict[str, Any]] = []
    local_seen: set[str] = set()
    for paper in candidates:
        key = paper_key(paper)
        if key in seen or key in local_seen:
            continue
        local_seen.add(key)
        paper["dedupe_key"] = key
        kept.append(paper)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"input_count": len(candidates), "kept_count": len(kept), "candidates": kept}, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.append_selected:
        selected_payload = json.loads(args.append_selected.read_text(encoding="utf-8-sig"))
        selected = selected_payload.get("selected", selected_payload if isinstance(selected_payload, list) else [])
        append_records(args.state, selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
