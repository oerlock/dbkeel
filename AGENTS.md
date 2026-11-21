# AGENTS.md

## 规则

- 开始任务前，检查 `docs/zh-CN/standards/` 中适用的开发规范。
- 修改文件前，检查当前目录层级中适用的 `AGENTS.md` 文件。目录专属规则应放在最近的 `AGENTS.md` 中。

### 文件快速索引

- [分支规范](docs/zh-CN/standards/branching.md): -

## 工具

- 使用 [uv](https://docs.astral.sh/uv/) 管理 Python 包和项目。
- 使用 `pytest-asyncio`，并设置 `asyncio_mode = auto`；不要显式添加 `@pytest.mark.asyncio`。
- 临时文件存放在 `tmp/<YYYYMMDD>/` 中。
