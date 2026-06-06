---
name: daily-literature-scout
description: Search open scholarly databases and generate daily Obsidian literature recommendation reports. Use when the user asks to scout, search, recommend, monitor, or summarize recent papers for their research interests, especially to create a daily 5-paper report in an Obsidian vault while avoiding papers recommended before.
---

# Daily Literature Scout

## Workflow

Generate a daily recommendation report for the current Obsidian vault. Treat the current working directory as the vault root unless the user provides another vault path.

1. Read the research profile from `<vault>/文献推荐/研究方向配置.md`.
2. Search open scholarly sources with `scripts/search_open_literature.py`.
3. Remove papers already recorded in `<vault>/文献推荐/_state/recommended_papers.jsonl` by running `scripts/dedupe_recommendations.py`.
4. Score remaining candidates with a relevance-first rubric and select the top 5.
5. Write the report to `<vault>/文献推荐/YYYY-MM-DD 文献推荐.md`.
6. Append the selected papers to the state file after the report is successfully written.

Use UTF-8 for all Markdown and JSONL reads/writes.

## Research Profile

If `<vault>/文献推荐/研究方向配置.md` does not exist, create it from this structure before searching:

```markdown
# 研究方向配置

## 研究主题

## 核心关键词

## 同义词与扩展词

## 排除词

## 重点方法/模型

## 重点材料/对象

## 重点应用场景

## 优先年份范围

## 语种偏好

## 期刊或领域偏好

## 期刊质量硬性要求
```

Treat the profile as the source of truth. Do not hard-code the user's research direction inside the skill.

## Search

Use open sources first:

- OpenAlex for broad metadata, abstracts, open-access status, citation counts, and concept matching.
- Semantic Scholar for abstract quality, citation counts, fields of study, and PDF/open access links.
- Crossref for DOI metadata and publication venue checks.
- arXiv only when the topic is compatible with preprints.

Aim for a candidate pool of 30-80 papers before deduplication. Prefer papers from the last 5 years unless the profile states otherwise, but allow older highly relevant or foundational papers when they strongly match the research direction.

## Journal Quality Gate

Apply journal quality filtering before scoring and recommendation:

- Do not recommend papers from journals lower than SCI/SCIE 2区.
- Treat this as a hard gate, not a scoring preference. A highly relevant paper from a lower-ranked or unverified venue must not enter the top 5.
- Accept a paper only when its venue can be verified as at least one of:
  - JCR Q1 or Q2 in a relevant subject category.
  - 中科院 1 区 or 2 区 in a relevant subject category.
  - A clearly equivalent SCI/SCIE 1区/2区 status required by the user's institution.
- If JCR and 中科院分区 differ, keep the paper only if at least one trusted current source places it in Q1/Q2 or 1/2 区, and explicitly state which system was used.
- If the journal's current SCI/SCIE or quartile status cannot be verified from reliable current sources, mark it as `分区待核验` and do not include it in the recommended top 5.
- Conference papers, proceedings series, preprints, book chapters, and non-SCI venues should be excluded from daily recommendations unless the user explicitly asks for exceptions.
- Use current sources when checking journal status because indexing, impact factors, and quartiles change over time. Prefer Web of Science/JCR, 中科院分区表 if available, publisher journal pages, Scopus/SJR, or the user's library database. Do not guess from memory.
- In `## 今日概览`, include a short note such as `期刊质量门槛：仅推荐已核验 SCI/SCIE 1区或2区来源；低于2区或分区待核验者已排除。`
- For every recommended paper, immediately after `**来源**`, include `**期刊等级**` with the journal quartile/zone and top-journal judgment.
- Format `**期刊等级**` like this: `JCR Q1 / 中科院 1区；顶刊判断：是，岩土/水文/多孔介质方向顶刊；核验来源：JCR/中科院分区/出版社或数据库页面。`
- If it is Q2 or 中科院 2区, write `顶刊判断：否，主流高质量期刊` unless there is a discipline-specific reason to call it top-tier.
- Only mark `顶刊判断：是` for journals that are widely recognized as top-tier in the relevant field, typically Q1/中科院 1区 with strong field reputation. Do not call all Q1 journals 顶刊.
- In the source-quality score, give strong credit only after the venue passes this gate. The score should distinguish Q1/top field journals from Q2/mainstream journals, but never revive a paper that failed the gate.

## Scoring

Score each candidate out of 100:

- Research relevance: 45
- Method/model inspiration: 20
- Recency: 15
- Influence/source quality: 10
- Accessibility/open PDF likelihood: 10

The top 5 must be selected primarily for research fit. Do not let citation count alone dominate the ranking.

## Journal Learning Section

Every daily report must include a `## 期刊了解` section after `## 推荐文献` and before `## 已记录`.

Build this section from the venues of the recommended papers:

- First give a compact `### 本次推荐来源速览` list or table covering every distinct source venue in the report.
- The source overview table must include the journal's verified quartile/zone and whether it is a top journal.
- Then choose one venue as `### 今日重点期刊：Journal Name` for a deeper introduction.
- Prefer the venue that appears most often in today's recommendations. If there is a tie, choose the venue that is most important for the user's research direction or least familiar to a beginner.
- Explain journal status cautiously. Include whether it is commonly treated as SCI/SCIE, Scopus, EI, or field-important only when verified from reliable current sources or the journal/publisher page. If not verified, write `待核验` rather than guessing.
- Do not rely on impact factor alone. Teach how to judge the journal using scope fit, publisher/society, indexing, quartile/ranking when available, representative article types, audience, and usefulness for the user's research.
- Keep the section educational and beginner-friendly: explain terms like SCI/SCIE, JCR 分区, 中科院分区, CiteScore, SJR, and EI only as needed for the sources that appear that day.
- For the focus journal, include these fields:
  - **期刊定位**：一句话说明它主要发表什么类型的研究。
  - **收录/指标**：SCI/SCIE、Scopus、EI、影响因子、CiteScore、JCR/中科院分区等；不确定则标注待核验。
  - **在本领域的重要性**：顶刊/主流期刊/专门期刊/交叉期刊/普通来源中的谨慎判断。
  - **适合关注的原因**：它为什么和用户的 SWRC、非饱和土、孔隙尺度 CFD/PNM/LBM/CT 研究有关。
  - **读刊建议**：以后看到这个期刊的文章时，优先看哪些栏目或判断点。
  - **今日小结**：1-2 句把这份期刊知识转成可记忆的判断。

## Report Format

Use this report structure:

```markdown
---
title: "YYYY-MM-DD 文献推荐"
date: "YYYY-MM-DD"
tags:
  - literature-recommendation
  - daily-scout
---

# YYYY-MM-DD 文献推荐

## 今日概览

- 检索主题：
- 候选数量：
- 去重后数量：
- 推荐数量：5
- 期刊质量门槛：仅推荐已核验 SCI/SCIE 1区或2区来源；低于2区或分区待核验者已排除。

## 推荐文献

### 1. Title

- **作者**：
- **年份**：
- **来源**：
- **期刊等级**：JCR Q / 中科院 区；顶刊判断：是/否；核验来源：
- **DOI/链接**：
- **开放获取/PDF**：
- **总分**：/100
- **分项评分**：相关性 /45；方法启发 /20；新近性 /15；影响力 /10；可获取性 /10
- **中文概括**：
- **推荐理由**：
- **与我的研究关联**：
- **方法或实验亮点**：
- **局限/风险**：

## 期刊了解

### 本次推荐来源速览

| 期刊/来源 | 本次文章 | 分区/等级 | 是否顶刊 | 初步定位 | 核验来源 |
| --- | ---: | --- | --- | --- | --- |
|  |  | JCR Q / 中科院 区 | 是/否 |  | JCR/中科院分区/出版社或数据库页面 |

### 今日重点期刊：Journal Name

- **期刊定位**：
- **收录/指标**：
- **在本领域的重要性**：
- **适合关注的原因**：
- **读刊建议**：
- **今日小结**：

## 已记录

本次推荐已写入去重状态文件。
```

Keep summaries in Chinese. Use links or DOI identifiers when available.

## Scripts

- `scripts/search_open_literature.py`: query open APIs and emit normalized candidate JSON.
- `scripts/dedupe_recommendations.py`: filter candidates against the recommendation history and optionally append selected records.

Run scripts with `--help` to inspect arguments before use.
