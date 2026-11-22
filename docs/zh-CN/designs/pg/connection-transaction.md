# PostgreSQL 连接与事务管理

本文为待确认的设计方案，确认后开始实现。

## 目标与边界

提供面向异步应用的 PostgreSQL 连接池生命周期、连接借用和显式事务管理，供 Web 服务、后台任务、脚本及后续迁移功能使用。

- 使用现有 `postgres` 可选依赖中的 Psycopg 3 和 `psycopg_pool`，不自行实现连接池或事务协议。
- 参考 PEP 249 的连接、游标、参数绑定和异常分类模型，不承诺完整兼容 DB-API 2.0；默认开启自动提交。
- 首期提供 PostgreSQL 专属入口和原生异步连接。跨数据库统一接口在接入其他数据库时根据实际差异提取。
- 本阶段不增加同步 API、SQL 执行封装、CLI 数据库命令、隐式任务连接、自动事务重试或两阶段提交。

## 公共 API

`BaseDB` 定义异步生命周期、连接借用和事务的公共接口；`DBPostgres` 继承 `BaseDB`，负责 PostgreSQL 实现，并接收 `SettingsPG` 配置对象。

| 接口 | 行为 |
| --- | --- |
| `await db.open()` | 打开连接池并等待就绪 |
| `await db.close()` | 停止借用并关闭池资源 |
| `async with db` | 进入时打开池，退出时关闭池 |
| `async with db.connection(timeout=None) as conn` | 借用原生 `psycopg.AsyncConnection`，退出时清理并归还 |
| `async with db.transaction(timeout=None) as conn` | 借用连接并开启事务，结束事务后归还 |

`timeout` 仅覆盖本次等待借用连接的超时，`None` 表示使用 `acquire_timeout`，不限制 SQL 或事务执行时长。所有接口均在同一事件循环内使用。

### 使用方式

普通操作默认自动提交，多条语句之间不保证原子性：

```python
from dbkeel.postgres import DBPostgres, SettingsPG

async with DBPostgres(SettingsPG()) as db:
    async with db.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            row = await cur.fetchone()
```

需要原子性的操作使用显式事务：

```python
async with db.transaction() as conn:
    await conn.execute(
        "UPDATE accounts SET balance = balance - %s WHERE id = %s",
        (amount, source_id),
    )
    await conn.execute(
        "UPDATE accounts SET balance = balance + %s WHERE id = %s",
        (amount, target_id),
    )
```

也可以在一次连接借用期间顺序执行多个事务，或在同一连接上嵌套事务：

```python
async with db.connection() as conn:
    async with conn.transaction():
        await conn.execute("INSERT INTO jobs (name) VALUES (%s)", (name,))
```

`db.transaction()` 在 `db.connection()` 内部进入 `conn.transaction()`，并增加失败事务退出检查（见事务语义）。两者没有隐式连接传播。事务内调用业务函数时显式传递 `conn`；再次调用 `db.connection()` 或 `db.transaction()` 会独立借用连接，不会加入当前事务，也可能因池耗尽而超时。

## 配置

- `conninfo` 以 `SecretStr` 保存，接受 Psycopg 支持的 PostgreSQL URI 或键值连接字符串，不自行解析或转换，交给驱动时提取原值。数据库、用户、密码、SSL、`application_name` 等通过它配置。
- `min_size >= 1`，`max_size >= min_size`，超时必须为正数，实例化配置类时验证。首期不支持零连接启动或无限等待。
- `connect_timeout` 显式传给驱动，覆盖连接字符串中的同名设置，控制底层连接尝试；`startup_timeout` 限制整个启动就绪等待；`acquire_timeout` 限制调用者等待连接的时间。
- 仅在显式实例化 `SettingsPG` 时读取配置，导入模块不创建配置实例。环境变量使用 `DBKEEL_POSTGRES_` 前缀，例如 `DBKEEL_POSTGRES_CONNINFO`。
- 默认不加载 `.env`，需要时显式使用 `SettingsPG(_env_file=".env")`。配置值默认优先级为显式参数、环境变量、指定 dotenv 文件、指定 secrets 目录、字段默认值，沿用 pydantic-settings 的来源机制。
- 允许共享 `.env` 中的无关字段（`extra="ignore"`）；配置实例不可修改，变更配置需新建实例。校验错误文本隐藏输入值，但结构化错误仍应由调用方筛选后记录。
- Psycopg/libpq 对缺省连接参数的处理保留原有行为。
- 不提供通用 `**kwargs` 透传，避免覆盖 `autocommit` 等受管理参数。后续按真实需求增加明确的配置项。
- 对象展示和 dbkeel 自行生成的错误信息不包含原始连接字符串、密码或 SQL 参数；驱动异常保留，调用方应避免无筛选地记录敏感诊断信息。

## 连接池生命周期

内部以 `open=False` 创建 `AsyncConnectionPool`，在 `open()` 中显式打开并等待达到 `min_size`。借用时使用驱动提供的连接健康检查回调，降低将已断开连接交给调用者的概率；检查不能保证后续执行不会断连。

生命周期为“未打开 → 打开中 → 已打开 → 关闭中 → 已关闭”：

- 构造不创建连接或后台任务。首次 `open()` 绑定当前事件循环。
- 已打开时再次 `open()` 无操作；已关闭时 `close()` 无操作；关闭未打开的对象也会进入已关闭状态。
- 打开失败或被取消时关闭部分创建的资源，对象进入已关闭状态。重试启动需新建对象。
- 关闭后不支持重新打开；未打开、打开中或关闭中的对象不接受连接借用。
- 生命周期方法由应用启动和关闭流程顺序调用，不支持并发 `open()`/`close()` 或嵌套进入同一个 `db` 上下文；冲突调用明确报错。
- 连接池可供同一事件循环中的多个任务并发借用，不跨线程、进程或事件循环共享。跨事件循环调用在进入驱动前报错。

应用应先停止接收新工作，等待正在执行的数据库操作结束，再调用 `close()`。首期关闭不负责排空业务任务，也不强制取消已借出的操作；空闲连接和后台资源被关闭，已借出连接在归还时关闭，不重新入池。`close()` 返回不代表所有业务事务已经结束。

不依赖垃圾回收释放资源。CLI 后续在一次 `asyncio.run()` 内完成创建、使用和关闭。

## 连接借用与归还

内部通过池的 `getconn()`/`putconn()` 管理借用，确保每次成功借用对应一次归还或弃用。默认连接为 `autocommit=True`，借用上下文本身不提交任何残留事务。

退出连接借用时：

1. 正常完成的显式事务应已由事务上下文结束。
2. 如仍有未结束或失败的事务，执行回滚，禁止把残留事务作为正常退出的一部分自动提交。
3. 对仍在执行、状态未知、已断开或无法清理的连接，关闭并交给池弃用；不把不确定状态的连接重新交给其他调用者。
4. 确认可复用后归还连接，由池负责补充失效连接。

返回原生连接意味着调用者可访问驱动扩展能力，但借用范围内不得自行关闭连接、修改自动提交设置，或在事务上下文中手工执行 `BEGIN`、`COMMIT`、`ROLLBACK`。连接和游标不得逃逸到借用上下文之外，也不得交给其他任务并发使用。首期不为原生对象增加代理来拦截所有误用。

归还时清理事务状态，不执行 `DISCARD ALL`，不承诺清除临时表、会话级 `SET` 或 advisory lock。业务避免留下会话状态；事务内临时设置优先使用 `SET LOCAL`，会话级资源由创建方显式释放。需要会话隔离的能力后续另行设计。

## 事务语义

- 非显式事务范围保持自动提交；先前已提交的语句不会因后续 Python 异常而回滚。
- 显式事务正常退出时提交，异常（包括任务取消）退出时回滚，异常继续向外传播。
- 使用 PostgreSQL 默认隔离级别，允许数据库或角色配置决定具体值；首期不增加事务隔离级别、只读或可延迟选项。
- 同一连接嵌套 `conn.transaction()` 复用 Psycopg 保存点行为。内层成功仅释放保存点，外层成功后才最终提交；内层异常退出后，外层捕获异常可以继续执行，否则异常继续向外传播并导致外层回滚。
- SQL 错误应在对应事务上下文之外捕获。`db.transaction()` 在正常退出前检查事务状态，若调用者吞掉 SQL 异常且事务仍为失败状态，抛出 `RuntimeError` 并经驱动上下文回滚，避免调用者误认为已经提交。直接使用原生 `conn.transaction()` 时保留驱动行为，不提供此额外检查。
- 不自动重试 SQL、事务或提交。提交期间断连可能导致结果未知，不能把报错等同于“未提交”；由业务基于幂等性和数据库状态判断后续处理。

事务提交、回滚及保存点操作委托 `conn.transaction()`，dbkeel 不另写事务 SQL 状态机。驱动的 `Rollback` 等专属控制能力保留原生语义，不作为跨数据库公共承诺。

## 异常与取消

- 无效配置使用 Pydantic `ValidationError`（属于 `ValueError`）；生命周期误用和跨事件循环使用采用带明确说明的 `RuntimeError`。
- 数据库和连接池异常保留 Psycopg 原始类型及 SQLSTATE，包括 `IntegrityError`、`OperationalError` 和 `PoolTimeout`；不统一包装成一个丢失诊断信息的异常。
- 等待连接被取消时不得遗留借用；拿到连接后被取消时必须完成回滚、归还或弃用。清理路径需考虑重复取消，必要的异步清理应受到取消保护，并保证保护任务最终被等待。
- 清理失败且已有业务异常或取消时，保留原异常为主，同时通过异常链或日志保留清理失败信息；仅发生清理错误时将其抛出。无法确认连接状态时弃用连接。
- 连接池可按驱动机制补充连接，但 dbkeel 不重放失败的业务操作。

## 代码组织与验证

公共配置放在 `src/dbkeel/settings.py`，PostgreSQL 使用单文件 `src/dbkeel/postgres.py`，包含连接池生命周期、借用上下文和事务便捷入口，不预建驱动注册中心或空包。普通 `import dbkeel` 和 CLI 帮助不加载 PostgreSQL 依赖；配置类仅依赖项目运行依赖 `pydantic-settings`，无需安装驱动即可导入和校验配置；后续数据库对象在使用驱动时检查依赖并提供安装 `dbkeel[postgres]` 的提示，其他导入错误保留原始诊断信息。

配置测试放在 `tests/unit/test_settings.py`，数据库测试放在 `tests/unit/test_postgres.py` 与 `tests/integration/test_postgres.py`，集成测试复用 `devops/docker/postgres.compose.yaml`，fixture 放在最近的 `conftest.py`。覆盖以下行为：

- 配置验证、无构造副作用、生命周期状态、重复关闭、打开失败清理、跨事件循环拒绝、可选依赖隔离。
- 真库读写、自动提交、显式提交与回滚、同一连接多个事务、嵌套保存点与内层异常恢复。
- 事务内部捕获 SQL 异常后的退出行为、未结束事务归还时回滚，后续借用连接可以正常使用。
- 池大小上限、池耗尽超时、等待和执行期间取消后的资源回收、重复取消和清理失败路径。
- 启动不可达、终止数据库后端连接后的弃用与补充、关闭时已有借用连接的归还。

实现后同步补充异步脚本与应用生命周期使用示例，明确连接范围和事务范围的区别。运行 Ruff、mypy、单元测试与真实 PostgreSQL 集成测试。

## 参考

- [Psycopg 连接池 API](https://www.psycopg.org/psycopg3/docs/api/pool.html)：连接池配置与资源管理能力。
- [Psycopg 事务管理](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)：自动提交、显式事务与保存点行为。
- [Psycopg 异步与并发](https://www.psycopg.org/psycopg3/docs/advanced/async.html)：异步连接、共享事务与取消行为。
