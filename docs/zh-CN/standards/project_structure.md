# 项目目录结构

本文定义项目的目标目录结构，目录按需创建。

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
├── manage.py
│
├── docs/
│   ├── standards/
│   ├── designs/
│   └── todo-list.md
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

## 示例代码

`src/` 按 HTTPX 功能与使用场景组织示例模块，不预设统一的内部结构。

```text
src/
├── event_hooks/
├── auth/
├── timeouts/
└── ...
```

## 测试

`tests/` 按示例功能组织测试，测试文件使用 `test_` 前缀，目录按需创建。

```text
tests/
├── test_event_hooks.py
├── test_auth.py
└── ...
```
