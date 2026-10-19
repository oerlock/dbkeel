# 分支规范

分支命名采用以下格式：

```text
<type>/<scope>-<summary>
```

| 类型 | 用途 | 示例 |
| --- | --- | --- |
| `feature` | 新增示例 | `feature/event-hooks` |
| `fix` | 修复问题 | `fix/timeout-example` |
| `docs` | 文档修改 | `docs/installation` |
| `refactor` | 代码重构 | `refactor/client-setup` |
| `test` | 测试相关 | `test/event-hooks` |
| `chore` | 项目维护 | `chore/upgrade-deps` |

## 基本约定

- 使用小写英文字母、数字和连字符 `-`。
- 分支名称应简洁、明确，能够体现变更目的。
- 每个分支尽量聚焦单一目标。
- 不使用 `temp`、`test1` 等含义模糊的名称。
