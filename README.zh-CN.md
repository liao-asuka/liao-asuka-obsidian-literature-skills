# Obsidian Literature Skills 使用说明

这个仓库包含两个面向 Obsidian 文献工作流的 Codex Skills：

- `daily-literature-scout`：根据研究方向自动检索开放文献数据库，每日推荐 5 篇论文，并记录历史推荐避免重复。
- `paper-deep-reading`：读取已下载 PDF，套用 Obsidian 论文精读模板，生成中文精读笔记。

## 推荐目录结构

```text
vault/
  文献推荐/
  文献推荐/_state/
  文献原文/
  文献阅读/
  模板文件/
  skills/
    daily-literature-scout/
    paper-deep-reading/
```

## 快速开始

1. 将两个 skill 文件夹复制到 Codex 可发现的 skills 目录。
2. 在 Obsidian vault 中创建 `文献推荐/研究方向配置.md`，可参考 `examples/研究方向配置.example.md`。
3. 在 `模板文件/论文精读模板.md` 放入精读模板，可参考 `examples/论文精读模板.example.md`。
4. 运行：

```text
Use $daily-literature-scout to generate today's literature recommendation report.
```

或：

```text
Use $paper-deep-reading to create a deep-reading note for 文献原文/path/to/paper.pdf.
```

## 输出

- 每日推荐报告：`文献推荐/YYYY-MM-DD 文献推荐.md`
- 推荐历史：`文献推荐/_state/recommended_papers.jsonl`
- 精读笔记：`文献阅读/YYYY - Title.md`

## 设计原则

- 开放数据库优先，不依赖登录数据库。
- 推荐排序优先研究相关性，而不是单纯引用量。
- PDF 下载保持手动，精读流程自动化。
- 所有 Markdown 和 JSON 使用 UTF-8。
