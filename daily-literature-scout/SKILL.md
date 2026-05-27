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
```

Treat the profile as the source of truth. Do not hard-code the user's research direction inside the skill.

## Search

Use open sources first:

- OpenAlex for broad metadata, abstracts, open-access status, citation counts, and concept matching.
- Semantic Scholar for abstract quality, citation counts, fields of study, and PDF/open access links.
- Crossref for DOI metadata and publication venue checks.
- arXiv only when the topic is compatible with preprints.

Aim for a candidate pool of 30-80 papers before deduplication. Prefer papers from the last 5 years unless the profile states otherwise, but allow older highly relevant or foundational papers when they strongly match the research direction.

## Scoring

Score each candidate out of 100:

- Research relevance: 45
- Method/model inspiration: 20
- Recency: 15
- Influence/source quality: 10
- Accessibility/open PDF likelihood: 10

The top 5 must be selected primarily for research fit. Do not let citation count alone dominate the ranking.

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

## 推荐文献

### 1. Title

- **作者**：
- **年份**：
- **来源**：
- **DOI/链接**：
- **开放获取/PDF**：
- **总分**：/100
- **分项评分**：相关性 /45；方法启发 /20；新近性 /15；影响力 /10；可获取性 /10
- **中文概括**：
- **推荐理由**：
- **与我的研究关联**：
- **方法或实验亮点**：
- **局限/风险**：

## 已记录

本次推荐已写入去重状态文件。
```

Keep summaries in Chinese. Use links or DOI identifiers when available.

## Scripts

- `scripts/search_open_literature.py`: query open APIs and emit normalized candidate JSON.
- `scripts/dedupe_recommendations.py`: filter candidates against the recommendation history and optionally append selected records.

Run scripts with `--help` to inspect arguments before use.
