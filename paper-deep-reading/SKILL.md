---
name: paper-deep-reading
description: Read a downloaded scholarly PDF and generate a structured Chinese Obsidian deep-reading note from the vault template. Use when the user asks to analyze,精读, summarize, read, or create a literature note for a specific paper in the Obsidian `文献原文` folder.
---

# Paper Deep Reading

## Workflow

Create a deep-reading note for one PDF already downloaded by the user. Treat the current working directory as the Obsidian vault root unless the user provides another vault path.

1. Identify the target PDF. If the user does not provide a path, choose from `<vault>/文献原文`.
2. Read the template at `<vault>/模板文件/论文精读模板.md`.
3. Extract text and page markers with `scripts/extract_pdf_text.py`.
4. Read enough of the paper to cover metadata, abstract, introduction, methods, results, discussion, conclusion, figures/tables captions when available, and key formulas.
5. Fill the template in Chinese, replacing `{{title}}` and `{{date}}`.
6. Save the note to `<vault>/文献阅读/YYYY - Title.md`; if the year is unknown, save `Title.md`.

Use UTF-8 for all Markdown. Preserve Obsidian-friendly Markdown and YAML frontmatter.

Prefer the Codex bundled Python when available because it includes PDF tooling:

```powershell
python "<vault>\skills\paper-deep-reading\scripts\extract_pdf_text.py" --pdf "path\to\paper.pdf" --out "<vault>\文献阅读\_extracted\paper.json"
```

## Reading Standards

- Fill every required template section: 基本信息, 一句话摘要, 研究对象, 研究方法, 数据来源, 研究结论, 我的判断.
- Prefer concise Chinese explanation over long translated passages.
- Include page numbers for key findings whenever the PDF extraction makes them available.
- Quote only short source excerpts when useful; do not paste long copyrighted passages.
- For formulas, include only the core formulas that matter to understanding the method, then explain symbols and the role of the formula.
- If extraction is incomplete, state the limitation in the note instead of pretending the missing section was read.

## Long Papers

For long PDFs, read in passes:

1. Metadata, abstract, keywords, and conclusion.
2. Introduction and research gap.
3. Methods, model, experiment, data, or simulation setup.
4. Results, discussion, tables, figures, and limitations.
5. Synthesize the final note.

The final note should be coherent rather than a section-by-section dump.

## Output Naming

Sanitize Windows-invalid filename characters. Use title case as provided by the paper metadata when possible. Avoid overwriting an existing note; append `-2`, `-3`, and so on when needed.

## Script

Use `scripts/extract_pdf_text.py` to extract text:

```powershell
python "<vault>\skills\paper-deep-reading\scripts\extract_pdf_text.py" --pdf "path\to\paper.pdf" --out "<vault>\文献阅读\_extracted\paper.json"
```

The script outputs JSON with title, author metadata when available, page count, per-page text, and a combined text preview.
