# AGENTS.md

## 规则

- 开始任务前，检查 `docs/standards/` 中适用的开发规范。
- 修改文件前，检查当前目录层级中适用的 `AGENTS.md` 文件。目录专属规则应放在最近的 `AGENTS.md` 中。

| 规范文件 | 适用场景 |
|---|---|
| `branching.md` | 创建或命名分支 |
| `project_structure.md` | 创建、移动或删除文件 |

## 工具

- 使用 [uv](https://docs.astral.sh/uv/) 管理 Python 包和项目。
- 使用 `pytest-asyncio`，并设置 `asyncio_mode = auto`；不要显式添加 `@pytest.mark.asyncio`。
- 临时文件存放在 `tmp/<YYYYMMDD>/` 中。

## Markdown

- 保持内容简洁、结构清晰，避免大段文字。
- 优先级：图表 > 表格 > 简短列表。

| 格式 | 适用场景 |
|---|---|
| Mermaid | 流程、时序、状态、架构、职责、事务 |
| 表格 | 字段、规则、映射、对比 |
| 简短列表 | 简单事实、备注 |

- 不要重复描述图表或表格中已经清晰表达的信息。
