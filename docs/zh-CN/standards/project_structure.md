# 项目目录结构

本文定义项目的目标目录结构，目录按需创建。

## 原则

- 技术解耦：目录命名尽量采用通用职责名称，具体技术选型由内部实现决定。

- 渐进式拆分：初期保持简单，只有职责复杂度确实增加时才拆分目录和模块。

  优先使用单文件模块，只有职责独立且持续扩展时才拆分为同名包。以职责边界为依据，不设固定行数门槛。
  行数参考：

  - 300～800 行：常见范围。
  - 超过 1000 行：建议检查是否存在职责过多的问题。

## 目录总览

```text
/
├── AGENTS.md              # AI 编码助手的仓库工作规则
├── README.md
├── LICENSE
├── pyproject.toml         # 项目元数据、依赖与工具配置
├── uv.lock                # uv 依赖锁文件
├── .gitignore
├── docs/                  # 开发规范、设计说明与使用指南
├── src/                   # 可发布的库源码
├── tests/                 # 单元测试与集成测试
├── examples/              # 独立脚本与使用者迁移脚本示例
├── devops/                # 开发、测试与发布支持文件
│   └── docker/            # 集成测试数据库的容器配置
└── tmp/                   # 临时文件，按 YYYYMMDD/ 存放（不纳入 git 管理）
```

## docs/

```text
docs/
├── zh-CN/
│   ├── standards/     # 开发规范
│   ├── designs/       # 设计说明
│   └── guides/        # 使用指南
└── en/               # 英文文档
```

## src/

```text
src/
└── dbkeel/
    ├── __init__.py         # 公共 API 导出
    ├── connection.py       # 连接与连接池的通用接口及生命周期
    ├── execution.py        # SQL 执行、参数绑定与结果读取
    ├── transaction.py      # 事务接口与通用流程
    ├── migration.py        # SQL 迁移发现、版本记录与执行流程
    ├── exceptions.py       # 通用异常
    └── drivers/            # 具体数据库与底层 Python 驱动适配
        └── __init__.py
```

## devops/docker/

主要为集成测试提供数据库服务。

```text
devops/docker/
├── mysql.compose.yaml
├── postgres.compose.yaml
└── example.env.d/
    ├── mysql.env
    └── postgres.env
```

## test/

测试统一放在 `tests/`，按是否依赖真实数据库分层，各层内部按被测模块或数据库组织。

```text
tests/
├── conftest.py             # 跨测试目录共享的 fixture
├── unit/
│   ├── test_connection.py
│   ├── test_execution.py
│   ├── test_transaction.py
│   └── test_migration.py
└── integration/
    ├── conftest.py         # 数据库连接、初始化与清理 fixture
    └── drivers/            # 按数据库组织真实数据库测试
```

- `unit/`：不依赖真实数据库，验证核心接口与通用流程，必要时使用替身模拟驱动行为。
- `integration/`：使用真实数据库验证驱动适配、SQL 执行、事务提交与回滚，以及迁移流程。
- fixture 放在最近的 `conftest.py` 中，仅将跨目录共享的内容提升到上层。SQL 脚本等测试数据靠近对应测试存放，按需建立 `fixtures/`。
