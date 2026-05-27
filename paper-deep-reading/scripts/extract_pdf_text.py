#!/usr/bin/env python3
"""Extract PDF text with page numbers into UTF-8 JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_with_pypdf(pdf: Path) -> dict[str, Any]:
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(pdf))
    metadata = reader.metadata or {}
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            text = f"[page extraction failed: {exc}]"
        pages.append({"page": index, "text": clean_text(text)})
    title = str(metadata.get("/Title") or pdf.stem)
    authors = str(metadata.get("/Author") or "")
    return {
        "pdf": str(pdf),
        "title": title,
        "authors": authors,
        "page_count": len(pages),
        "pages": pages,
        "text": "\n\n".join(f"[p. {p['page']}]\n{p['text']}" for p in pages),
    }


def extract_with_pdfminer(pdf: Path) -> dict[str, Any]:
    from pdfminer.high_level import extract_text  # type: ignore

    text = clean_text(extract_text(str(pdf)) or "")
    return {
        "pdf": str(pdf),
        "title": pdf.stem,
        "authors": "",
        "page_count": None,
        "pages": [{"page": None, "text": text}],
        "text": text,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--preview-chars", type=int, default=12000)
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    try:
        payload = extract_with_pypdf(args.pdf)
        payload["extractor"] = "pypdf"
    except Exception:
        payload = extract_with_pdfminer(args.pdf)
        payload["extractor"] = "pdfminer"

    payload["preview"] = payload.get("text", "")[: args.preview_chars]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
