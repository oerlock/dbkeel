# 项目目录结构

本文定义项目的目标目录结构，目录按需创建。

## 原则

- 技术解耦：目录命名尽量采用通用职责名称，具体技术选型由内部实现决定。

- 渐进式拆分：初期保持简单，只有职责复杂度确实增加时才拆分目录和模块。

- Module 与 Package：初期优先使用单文件（Module），只有职责独立且持续扩展时才拆分为同名包（Package）。

  行数可作为参考：

  - 300～800 行：常见范围。
  - 超过 1000 行：建议检查是否存在职责过多的问题。
  - 行数不是硬性标准，职责边界才是主要依据。

## 目录总览

```text
/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── pytest.ini
├── .coveragerc
├── .gitattributes
│
├── docs/
│   ├── standards/
│   ├── designs/
│   └── TODO.md
│
├── src/                    # 按功能组织的示例代码
├── tests/                  # 测试
├── requirements/           # 依赖快照（按需）
│
├── .example.env.d/         # 环境配置示例
├── .example.support/       # 运行支持文件示例（按需）
├── .env.d/                 # 本地环境配置（忽略）
├── .support/               # 本地运行支持文件（忽略）
├── experiments/            # 持续性实验（按需，忽略）
└── tmp/                    # 临时文件（忽略）
```
