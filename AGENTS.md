# AGENTS.md

## 规则

- 开始任务前，检查 `docs/zh-CN/standards/` 中适用的开发规范。
- 修改文件前，检查从项目根目录到目标文件所在目录沿途的 AGENTS.md。目录专属规则写在对应目录的 AGENTS.md 中。
- 临时文件存放在 `tmp/<YYYYMMDD>/` 中。

### 文件快速索引

- [分支规范](docs/zh-CN/standards/branching.md)：规定分支模型与命名、日常开发与 PR 合并流程，以及版本 tag 和发布规则。
- [项目目录结构](docs/zh-CN/standards/project_structure.md)：规定目标目录结构、目录职责与代码和测试的组织方式。

## 工具

- 使用 [uv](https://docs.astral.sh/uv/) 管理 Python 包和项目。

## 偏好

### Markdown

- 编写或修改 Markdown 文档时，以简单明了为目标。
- 文档较长、结构不清或内容重复时，整体梳理结构与内容，合并重复表述，精简不必要的章节、表格和细节；局部修改保持范围适度。
