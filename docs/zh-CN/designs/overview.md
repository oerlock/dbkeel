# dbkeel 设计总览

## 原则

- 以异步 API 为主，参考 [PEP 249（Python DB-API 2.0）](https://peps.python.org/pep-0249/)的连接、游标、参数绑定和异常分类等接口模型，不承诺完整兼容 DB-API 2.0。
- 异步调用、连接与连接池的生命周期、事务默认行为由项目另行设计，不直接继承 PEP 249 的同步接口和默认事务约定。

## 文档索引

- [CLI 基础约定](./cli.md)
- [PostgreSQL 实施计划](./pg/plan.md)
