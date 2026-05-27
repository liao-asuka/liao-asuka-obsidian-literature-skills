# Obsidian Literature Skills

Two Codex skills for building an Obsidian-based literature workflow:

- `daily-literature-scout`: search open scholarly databases, score papers by research relevance, and generate a daily 5-paper recommendation report.
- `paper-deep-reading`: read a downloaded PDF paper and generate a structured Chinese deep-reading note from an Obsidian template.

The skills are designed for an Obsidian vault with these folders:

```text
vault/
  文献推荐/
  文献原文/
  文献阅读/
  模板文件/
  skills/
```

## Features

- Search open literature sources such as OpenAlex and Semantic Scholar.
- Generate daily Obsidian Markdown recommendation reports.
- Track previously recommended papers with a JSONL history file.
- Extract PDF text with page markers.
- Produce structured Chinese reading notes using `论文精读模板.md`.
- Keep reports and reading notes Obsidian-friendly with YAML frontmatter.

## Installation

Copy both skill folders into your Codex skills directory or into a vault-local `skills/` folder if your Codex setup loads vault-local skills:

```text
daily-literature-scout/
paper-deep-reading/
```

If you use a vault-local workflow, the recommended layout is:

```text
your-vault/
  skills/
    daily-literature-scout/
    paper-deep-reading/
```

## Vault Setup

Create these folders in your vault:

```text
文献推荐/
文献推荐/_state/
文献原文/
文献阅读/
模板文件/
```

Create `文献推荐/研究方向配置.md`. You can start from `examples/研究方向配置.example.md`.

Create `模板文件/论文精读模板.md`. The template should include frontmatter fields such as `title`, `tags`, `created`, `source`, `author`, `year`, `theme`, `study_area`, `methodology`, `key_finding`, and `relevance`.

## Usage

### Daily Literature Scout

Ask Codex:

```text
Use $daily-literature-scout to generate today's 5-paper literature recommendation report.
```

The skill will:

1. Read `文献推荐/研究方向配置.md`.
2. Search open scholarly metadata APIs.
3. Filter out papers already recorded in `文献推荐/_state/recommended_papers.jsonl`.
4. Score candidates with a relevance-first rubric.
5. Write `文献推荐/YYYY-MM-DD 文献推荐.md`.
6. Update the JSONL history after the report is written.

You can also schedule this prompt as a Codex automation, for example every weekday at 08:00.

### Paper Deep Reading

Put a PDF under `文献原文/`, then ask Codex:

```text
Use $paper-deep-reading to create a deep-reading note for 文献原文/path/to/paper.pdf.
```

The skill will:

1. Extract PDF text with page markers.
2. Read `模板文件/论文精读模板.md`.
3. Fill the reading-note sections in Chinese.
4. Save the note under `文献阅读/`.

## Scripts

`daily-literature-scout/scripts/search_open_literature.py`

```powershell
python .\daily-literature-scout\scripts\search_open_literature.py --profile ".\文献推荐\研究方向配置.md" --out ".\文献推荐\_state\candidates.json" --limit 80
```

`daily-literature-scout/scripts/dedupe_recommendations.py`

```powershell
python .\daily-literature-scout\scripts\dedupe_recommendations.py --candidates ".\文献推荐\_state\candidates.json" --state ".\文献推荐\_state\recommended_papers.jsonl" --out ".\文献推荐\_state\deduped.json"
```

`paper-deep-reading/scripts/extract_pdf_text.py`

```powershell
python .\paper-deep-reading\scripts\extract_pdf_text.py --pdf ".\文献原文\paper.pdf" --out ".\文献阅读\_extracted\paper.json"
```

For PDF extraction, use a Python environment with `pypdf` installed. Codex Desktop's bundled Python often already includes it.

## Notes

- These skills intentionally keep paper downloading manual. Put promising PDFs in `文献原文/`, then run `$paper-deep-reading`.
- All Markdown and JSON files should be read and written as UTF-8.
- The default report language is Chinese.
- The scoring rubric favors research relevance over citation count.

## License

MIT
