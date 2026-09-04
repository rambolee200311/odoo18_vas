# Warehouse VAS Technical Detailed Design

> 文档版本：v1.0.0 Frozen
> 状态：TDD FROZEN
> 模块：`wd_warehouse_value_add`
> 基线日期：2026-09-04
> 技术负责人：Copilot

## 0. Document Control

| 项 | 内容 |
|---|---|
| 项目 | 仓库库内增值作业单（Warehouse VAS） |
| Odoo | `18.0+e-20250619` |
| Python | `3.11.9`（项目 `venv`） |
| 数据库 | PostgreSQL，具体部署版本待环境确认 |
| 上游业务基线 | SRS v1.0.0 Frozen |
| 领域基线 | DDD SKIP |
| 技术论证 | `tv_warehouse_vas_v1.0.md`，READY FOR TDD |
| 下游 | Coding Contract、Implementation、Test |

本文是已冻结的技术详细设计契约，不是实现代码。技术实现不得改变 Frozen SRS 的业务语义。

## 1. Purpose & Authority

本 TDD 将 SRS 的 Warehouse VAS 需求转换为 Odoo 18 的模型、动作、视图、权限和测试契约。

权威顺序：

1. Frozen SRS：业务 WHAT；
2. TV：已验证的 Odoo/worlddepot 技术事实；
3. 本 TDD：技术 HOW；
4. 实际实现和测试必须服从本 TDD 与后续 Coding Contract。

本项目不建立 DDD，不生成 `AGG-*`、`ENT-*`、`DS-*`、`INV-*` 或 `DV-*` 编号。

## 2. Inputs & Technical Baseline

### 2.1 已验证技术事实

- 业务关联对象是 `world.depot.inbound.order`、`world.depot.outbound.order`、`world.depot.transfer.order`，不是库存执行层模型。
- 三个模型都以 `billno` 作为 `_rec_name`，没有统一父类，也没有 SQL 唯一约束。
- 订单识别必须保留 Order Type + `billno` 上下文。
- 三个既有模型不得修改。
- Odoo 18 标准 Web Form、x2many 和原生附件能力足以承载 Web/PDA 共用流程。
- `ir.attachment`、ORM 元数据、`mail.thread` 和 tracking 足以提供原生附件与审计基础。

### 2.2 依赖

| 依赖 | 用途 | 必需 |
|---|---|---|
| `base` | ORM、用户、序列、基础权限 | 是 |
| `mail` | chatter、tracking、附件基础能力 | 是 |
| `web` | 标准后台表单和移动尺寸渲染 | 是 |
| `worlddepot` | 三类 Warehouse Order、Charge Unit | 是 |
| 第三方模块 | 无 | 否 |

本模块不引入 queue、Redis、独立 API、事件总线、第三方前端框架或独立 PDA 后端。

## 3. Architecture Overview

采用单一 Odoo 模块、单一业务模型和标准 Web 视图：

```text
Odoo Web Form（桌面/PDA）
          |
          v
wd.vas.order  ----  wd.vas.order.line
      |  \              |
      |   \             v
      |    \      wd.vas.operation.type
      |     \             |
      |      v            v
      |  Warehouse Order  Charge Unit
      |
      +---- ir.attachment
      +---- mail.thread / tracking
```

所有业务动作通过模型方法执行，提交、反提交和作废不能通过直接写 `state` 绕过。

## 4. Module Structure

目标目录：

```text
addons/wd_warehouse_value_add/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── vas_operation_type.py
│   ├── vas_order.py
│   └── vas_order_line.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   ├── ir_sequence_data.xml
│   └── vas_operation_type_data.xml
├── views/
│   ├── vas_operation_type_views.xml
│   ├── vas_order_views.xml
│   └── vas_menus.xml
└── tests/
    ├── __init__.py
    ├── test_vas_order.py
    └── test_vas_security.py
```

不创建 `services/`、`adapters/`、`queue/`、`schemas/` 或 `static/`，因为本模块无外部接口、无异步流程，且标准 Web 已足够。

Manifest：

- `name`: Warehouse Value Add；
- `version`: `1.0.0`；
- `depends`: `base`, `mail`, `web`, `worlddepot`；
- `data` 按安全、序列、主数据、视图顺序加载；
- `installable=True`、`application=True`；
- 不声明自定义 assets。

## 5. Data Model

### 5.1 `wd.vas.order`

| Field | Type | Required | Readonly | Tracking | Default | Purpose |
|---|---|---:|---:|---:|---|---|
| `name` | Char | 是 | 是 | 否 | `ir.sequence` | VAS 作业单号 |
| `state` | Selection | 是 | 视状态 | 是 | `draft` | `draft/submitted/cancelled` |
| `order_type` | Selection | 是 | Submitted/Cancelled | 是 | 无 | `inbound/outbound/transfer` |
| `inbound_order_id` | Many2one | 否 | Submitted/Cancelled | 否 | 无 | 入库订单显式关系 |
| `outbound_order_id` | Many2one | 否 | Submitted/Cancelled | 否 | 无 | 出库订单显式关系 |
| `transfer_order_id` | Many2one | 否 | Submitted/Cancelled | 否 | 无 | 调拨订单显式关系 |
| `warehouse_order_billno` | Char | 是 | Submitted/Cancelled | 否 | 无 | 用户录入/扫描的 `billno` |
| `warehouse_order_display` | Char computed | 否 | 是 | 否 | 计算 | 当前已解析订单的显示名 |
| `warehouse_id` | Many2one | 是 | Submitted/Cancelled | 否 | 由订单带出 | 作业仓库 |
| `operator_id` | Many2one `res.users` | 是 | Submitted/Cancelled | 是 | 当前用户 | 实际操作员 |
| `submitter_id` | Many2one `res.users` | 否 | 是 | 是 | 提交动作写入 | 当前一次提交人 |
| `submitted_at` | Datetime | 否 | 是 | 是 | 提交动作写入 | 当前一次提交时间 |
| `unsubmitted_by` | Many2one `res.users` | 否 | 是 | 是 | 反提交动作写入 | 最近一次反提交人 |
| `unsubmitted_at` | Datetime | 否 | 是 | 是 | 反提交动作写入 | 最近一次反提交时间 |
| `cancelled_by` | Many2one `res.users` | 否 | 是 | 是 | 作废动作写入 | 作废人 |
| `cancelled_at` | Datetime | 否 | 是 | 是 | 作废动作写入 | 作废时间 |
| `cancel_reason` | Text | 否 | Cancelled 后只读 | 是 | 无 | 作废原因 |
| `line_ids` | One2many | 否 | Submitted/Cancelled | 否 | 空 | 作业明细 |
| `attachment_ids` | Many2many `ir.attachment` | 否 | Submitted/Cancelled | 否 | 空 | 图片/视频附件 |
| `notes` | Text | 否 | Submitted/Cancelled | 是 | 无 | 备注 |
| `create_uid/create_date` | ORM metadata | 系统 | 是 | 否 | ORM | 创建审计 |
| `write_uid/write_date` | ORM metadata | 系统 | 是 | 否 | ORM | 最后修改审计 |

模型定义：

- `_name = 'wd.vas.order'`；
- `_description = 'Warehouse Value Add Order'`；
- `_inherit = ['mail.thread']`；
- `_rec_name = 'name'`；
- `_order = 'create_date desc, id desc'`。

`create_uid` 直接作为 Creator，创建时由 Odoo ORM 写入且不可人工修改。`warehouse_order_billno` 是允许草稿先录入的输入值；显式 Many2one 是提交成功后的实体关系。提交时将目标订单的 `billno` 复制到 `warehouse_order_billno`，此后该字段是作业发生时的订单号历史快照，不跟随目标订单未来的编号修改；Many2one 仍是当前实体关系权威。`warehouse_order_display` 为非存储计算字段，避免重复保存显示名。

### 5.2 `wd.vas.order.line`

| Field | Type | Required | Readonly | Tracking | Purpose |
|---|---|---:|---:|---:|---|
| `order_id` | Many2one `wd.vas.order` | 是 | 是 | 否 | 所属作业单，`ondelete='cascade'` |
| `sequence` | Integer | 否 | 否 | 否 | 稳定显示顺序 |
| `operation_type_id` | Many2one `wd.vas.operation.type` | 是 | Submitted/Cancelled | 否 | 操作类型 |
| `quantity_time` | Float | 否 | Submitted/Cancelled | 否 | 统一数量/工时数值，Submit 时必须大于零 |
| `unit_id` | Many2one `world.depot.charge.unit` | 是 | 是 | 否 | 提交/选择时带出的单位快照 |
| `note` | Text | 否 | Submitted/Cancelled | 否 | 明细备注 |

`unit_id` 是明细快照，不使用非存储 related 字段；这样操作类型主数据后续变更不会改写历史作业事实。数量/工时使用 `Float(digits=(16, 4))`，Draft 可以为空或为零，只有 Submit 才要求大于零。草稿允许零行，但每个已提交订单必须至少有一行。

### 5.3 `wd.vas.operation.type`

| Field | Type | Required | Readonly | Purpose |
|---|---|---:|---:|---|
| `name` | Char | 是 | 否 | 操作类型名称 |
| `code` | Char | 是 | 否 | 稳定编码 |
| `unit_id` | Many2one `world.depot.charge.unit` | 是 | 否 | 直接维护作业计量单位 |
| `active` | Boolean | 是 | 否 | 停用而不删除历史主数据 |
| `sequence` | Integer | 否 | 否 | 下拉显示顺序 |

操作类型仅表达作业分类和计量单位，不增加价格、费率、客户合同、会计科目、绩效系数或工资规则。它直接引用既有收费单位模型，但不引用 `world.depot.charge.item`，从而保持作业事实主数据与收费项目解耦。

## 6. Warehouse Order Association Design

### 6.1 Alternatives

| 维度 | Option A：三显式 Many2one | Option B：Reference/model+res_id | Option C：新抽象层 |
|---|---|---|---|
| Referential integrity | 强，目标模型由 ORM 约束 | 弱，需手工校验模型和 ID | 可强但需新模型 |
| ORM usability | 高，标准 relation/domain | 中，通用但使用和访问检查复杂 | 中 |
| Domain/filter | 高，按三个字段分别过滤 | 低，动态 domain 复杂 | 中 |
| View usability | 高，按类型显示一个字段 | 中，Reference 输入不够现场友好 | 中 |
| PDA usability | 高，选择类型后输入 billno | 中 | 中 |
| Search/reporting | 高，三个关系可直接聚合 | 中，需要动态解析 | 高但成本高 |
| Security | 高，标准模型访问检查 | 中，需额外逐模型检查 | 中 |
| Maintainability | 高，显式且容易理解 | 中 | 低 |
| Existing model impact | 零修改 | 零修改 | 可能诱发修改 |
| Complexity | 低到中 | 中 | 高 |

### 6.2 Authority Decision: Option A

选择 **Option A：三个显式 Many2one**。这是本 TDD 的唯一权威方案。

原因：

1. 不修改三个既有 Warehouse Order 模型；
2. 保留真实 ORM 外键和标准访问控制；
3. 适配固定三类订单类型；
4. 便于表单、搜索、报表和测试；
5. 避免 Reference 字段的动态权限、domain 和数据完整性复杂度；
6. 不创建新的 Warehouse Order 抽象层。

`order_type` 与三个关系字段必须满足“类型对应一个关系，其余为空”。三字段均使用 `ondelete='restrict'`。`warehouse_order_billno` 负责草稿输入，Submit 成功时必须与解析出的关系的 `billno` 完全一致。

`warehouse_id` 在 Submit 时从被解析 Warehouse Order 的 `warehouse` 字段复制为 VAS 事实快照。入库、出库和调拨三种既有模型都提供该字段；本模块不推断调拨单的来源仓/目标仓语义，只记录既有订单明确提供的 warehouse。目标订单后续变更不反向改写已提交 VAS 的 warehouse 快照。

## 7. Operation Type Design

操作类型从 `wd.vas.operation.type` 下拉选择。其 `unit_id` 直接指向 `world.depot.charge.unit`。该引用只复用计量单位主数据，不建立与收费项目的业务依赖。

选择操作类型后：

1. 客户端 onchange 立即把单位带到明细；
2. 服务端 create/write 再次根据操作类型设置 `unit_id`；
3. 客户端传入的任意手工单位被忽略或拒绝；
4. 操作类型停用后不得新选，但历史明细仍可查看；
5. 提交时重新验证操作类型有效且单位存在。

这只是 `Operation Type → Unit` 的主数据映射，不是自动计费。

## 8. State Machine & Business Actions

### 8.1 状态

```text
draft --action_submit--> submitted
submitted --action_unsubmit--> draft
draft --action_cancel--> cancelled
```

`cancelled` 是终态。既有 Warehouse Order 的 `new/confirm/cancel` 不复用为 VAS 状态。

### 8.2 `action_submit()`

只允许 `draft`，并在同一 Odoo 事务中依次执行。所有状态动作和受保护 `write()` 固定按 `VAS Order → Warehouse Order` 的顺序加锁：

1. 对当前 VAS Order 行加锁并重新读取 `state`；
2. 检查当前用户具有提交权限；
3. 检查 `order_type`、`warehouse_order_billno`、`operator_id`；
4. 检查明细数至少一行，每行操作类型、单位和数值有效；
5. 按 `order_type` 在对应模型以精确 `billno` 搜索；
6. 找不到或找到多条时阻断；
7. 解析出唯一目标 Warehouse Order；
8. 对目标 Warehouse Order 行加锁并重新读取其 `state`；
9. 目标 Warehouse Order 为 `state='cancel'` 时阻断；
10. 写入唯一对应的 Many2one、订单的 `warehouse` 快照和目标订单的 `billno` 快照；
11. 写入 `submitter_id=env.user`、`submitted_at=fields.Datetime.now()`；
12. 写入 `state='submitted'`，由 tracking 记录变化。

Draft 保存不执行上述业务订单有效性阻断，但 `warehouse_order_billno` 仍为必填输入。提交时不使用 `reference`、`stock.picking.name` 或数据库 ID 匹配。

### 8.3 `action_unsubmit()`

只允许 `submitted`，检查用户具有反提交权限后，在同一事务中：

- 写入 `unsubmitted_by` 和 `unsubmitted_at`；
- 将 `state` 改回 `draft`；
- 保留 `submitter_id`、`submitted_at` 作为最近一次提交事实；
- 不清空已解析的 Many2one、订单号、明细或附件；
- 由 chatter/tracking 保留本次反提交历史。

重新提交时覆盖当前提交人/时间，但历史动作仍可从 chatter/tracking 追溯。

### 8.4 `action_cancel()`

只允许 `draft`，要求非空 `cancel_reason`，检查权限后写入 `cancelled_by`、`cancelled_at`、`state='cancelled'`，由 tracking 记录。禁止 `submitted → cancelled`，禁止 `cancelled → draft` 或任何恢复动作。

## 9. Validation & Invariants

### 9.1 SQL constraints

| 编号 | 定义 |
|---|---|
| `ORM-DATA-001` | `wd.vas.operation.type.code` 唯一 |
| `ORM-DATA-002` | `wd.vas.order.name` 唯一 |

不为 Warehouse Order 的 `billno` 增加约束；既有模型无全局唯一保证，VAS 通过类型上下文和 Submit 时的单模型唯一结果处理。

### 9.2 Python constraints

- `order_type` 只能为 `inbound/outbound/transfer`；
- 三个关系字段必须与 `order_type` 一一对应；
- `warehouse_order_billno` 非空且去除首尾空白后保存；
- 明细单位必须与操作类型当前单位一致；
- `quantity_time` 只在 Submit 时要求大于零；Draft 可为空或为零；
- Draft 允许零明细，不能仅因零明细触发 `@api.constrains` 阻止保存；
- Submitted/Cancelled 的业务字段不能通过普通 `write()` 修改。

### 9.3 Business Action validation

订单有效性、取消订单阻断、至少一行、操作员有效性、作废原因和状态转换均放入对应 action。不能把只在 Submit 时适用的规则塞进通用 `@api.constrains`。

## 10. Audit & Tracking

采用 `mail.thread` + 关键字段 `tracking=True` + 显式业务审计字段，不创建 audit model。

| 事实 | 实现 |
|---|---|
| 创建人/时间 | `create_uid/create_date` |
| 提交人/时间 | `submitter_id/submitted_at` |
| 反提交 | `unsubmitted_by/unsubmitted_at` + state tracking/chatter |
| 作废 | `cancelled_by/cancelled_at/cancel_reason` + state tracking/chatter |
| 最后修改 | `write_uid/write_date` |

`submitter_id`、`submitted_at`、`unsubmitted_by`、`unsubmitted_at` 表示最近一次相应动作；多次 Submit → Unsubmit → Submit 的历史由 chatter/tracking 保留。当前状态字段不承担完整历史表职责。

## 11. Security

### 11.1 Groups

- `group_vas_user`：仓管员，对应 `ROLE-VAS-01`；
- `group_vas_manager`：仓库主管，对应 `ROLE-VAS-02`，隐含继承仓管员能力。

### 11.2 ACL and record rules

| 角色 | Read | Create | Write | Unlink |
|---|---:|---:|---:|---:|
| 仓管员 | 是 | 是 | 是（自己的 Draft） | 否 |
| 主管 | 是 | 是 | 是（全部 Draft） | 否 |

- 仓管员 record rule：`create_uid = user.id`；
- 主管 record rule：全部 VAS 记录；
- 删除统一禁止，以保留作废和审计事实；
- 明细和操作类型通过父单/主数据权限保护；
- `action_submit/unsubmit/cancel` 仍在服务端检查群组和当前状态，不依赖按钮隐藏。

Creator、Operator、Submitter 永远是三个独立字段。PDA 不建立独立数据或权限路径。

Operator 的第一版合法范围已由 Human Decision 确定为 active 且属于 `group_vas_user` 或 `group_vas_manager` 的 `res.users`。本期不建立 Warehouse ↔ Operator 授权关系，也不限制 Operator 与 Warehouse 的所属关系；服务端必须执行该范围检查，不得仅依赖客户端 domain。

## 12. Web UI

提供最小菜单、action、list、form、search 和操作类型配置视图。

### 12.1 List

显示：VAS 单号、状态、订单类型、订单号、仓库、Operator、Creator、Submitter、创建时间、提交时间。支持按单号、订单类型、订单号、Operator、状态、日期筛选。

### 12.2 Form

- Header：Submit、Unsubmit、Cancel，按状态和权限显示；
- 表头：订单类型、订单号、解析后的订单显示、仓库、Operator、Notes；
- 明细：`operation_type_id`、`quantity_time`、只读 `unit_id`、`note`；
- 附件：标准 `many2many_binary`；
- Chatter：标准 `<chatter/>`；
- Draft 可编辑；
- Submitted 只读并显示 Unsubmit；
- Cancelled 全部业务字段只读。

UI readonly 仅用于体验，不能代替 `write()` 服务端保护。

## 13. PDA/Mobile UI

采用同一 Odoo Web Form，不创建独立 PDA App、SPA、API 或数据模型。

移动表单顺序：

1. Order Type；
2. billno 输入/键盘式扫码；
3. Operator；
4. 作业明细；
5. 附件；
6. Notes；
7. Save Draft / Submit。

x2many 提供适合小屏的 kanban 子视图；桌面和移动端操作同一 `wd.vas.order`。实际扫码枪、浏览器和拍照入口属于后续 Human/Acceptance Verification，不伪装成单元测试已验证。

## 14. Attachment

采用 `attachment_ids = fields.Many2many('ir.attachment', ...)` 与标准 `many2many_binary`，并使用 Odoo 原生附件关联能力。

- 可选；
- 支持多个图片/视频；
- 关联到单一 `wd.vas.order`；
- Web/PDA 通过同一表单上传和查看；
- 不创建自定义文件服务器、对象存储或附件配置子系统；
- 不在 SRS 未规定时新增固定大小、数量或格式白名单。

附件字段也属于 Submitted/Cancelled 的不可变业务数据，删除或新增附件必须走 Draft；附件文件的原生访问权限服从业务记录访问权限。

## 15. Sequence & Master Data

### 15.1 VAS sequence

使用 `ir.sequence`：

| 项 | 设计 |
|---|---|
| Code | `wd.vas.order` |
| Prefix | `VAS%(year)s%(month)s%(day)s` |
| Padding | `5` |
| Number next | `1` |

格式是技术设计决策，不是新增业务需求。

### 15.2 Seed data

模块安装不强制写入业务操作类型种子，也不依赖部署现场的 Charge Item 或 Unit 记录；管理员在操作类型配置视图中维护名称、编码和直接引用的收费单位。若后续提供可选种子，必须只引用安装基线中确定存在的单位 XML ID，不能因现场缺少收费项目而阻止安装。操作类型可停用，不物理删除被历史明细使用的记录。

## 16. Transaction & Concurrency

不引入复杂锁框架、分布式事务或队列。对每张 VAS Order 的状态转换使用最小行级锁；锁定后必须重新读取 state，再执行动作。

| 场景 | 策略 |
|---|---|
| 两窗口同时 Submit | 对 VAS 行执行 `SELECT id FROM wd_vas_order WHERE id = ANY(%s) FOR UPDATE`，锁后刷新 state；先取得锁者成功，后者发现非 Draft 后显式失败 |
| Submitted 后旧窗口 write | `write()` 先取得同一行锁并刷新 state，再拒绝核心字段 |
| Unsubmit 与 edit | action/write 都先取得行锁并重检 state；非 Draft 写入失败 |
| Warehouse Order 同时取消 | VAS 行锁定后，在同一事务重新读取目标 `state`；已取消目标阻断 |

行锁 SQL 仅用于并发保护，所有业务数据写入仍使用 ORM；SQL 必须参数化。每个动作事务设置 `SET LOCAL lock_timeout = '5s'`，锁不得跨越外部 IO，临界区不执行长耗时操作。

Runtime Spike（2026-09-04，非业务数据）使用 Odoo 18 Registry 的两个独立 cursor 对同一 `ir.model` 行执行只读 `SELECT ... FOR UPDATE`：第二 cursor 在第一 cursor 回滚前保持阻塞，释放后成功取得锁。结果为 `row_lock_blocks_contender=True`、`contender_acquires_after_release=True`。该结果支持“锁后重新读取 state”的设计，但不替代后续模块并发集成测试。

## 17. Install / Upgrade

这是新 VAS 模块，初始版本：

- 安装新模型、ACL、record rule、序列、菜单和视图；操作类型业务主数据按上线前置条件维护；
- 不迁移既有 Warehouse Order；
- 不修改 `worlddepot` 四个受保护模型；
- 无历史 VAS 数据，因此 `No Migration required for initial release`；
- 升级必须保留 VAS 业务记录、附件和 chatter；
- 若后续改变字段语义，先升级 TDD 版本并提供迁移/校验方案。

## 18. Test Design

本阶段只定义测试矩阵，不编写测试代码。

| TEST | 场景 | 预期 |
|---|---|---|
| `TEST-MODEL-001` | 创建 Draft | 生成序列号、Creator 和 Draft |
| `TEST-MODEL-002` | Draft 允许 0 行 | 保存成功 |
| `TEST-MODEL-003` | 操作类型带单位 | 行单位自动设置且不可手改 |
| `TEST-ASSOC-001` | 有效 inbound billno | Submit 成功并绑定入库单 |
| `TEST-ASSOC-002` | 有效 outbound billno | Submit 成功并绑定出库单 |
| `TEST-ASSOC-003` | 有效 transfer billno | Submit 成功并绑定调拨单 |
| `TEST-ASSOC-004` | 无效 billno | Submit 阻断，Draft 保存不因无效而阻断 |
| `TEST-ASSOC-005` | 取消 Warehouse Order | Submit 阻断 |
| `TEST-ASSOC-006` | wrong type / duplicate billno | 阻断并给出明确业务错误 |
| `TEST-STATE-001` | Draft → Submitted | 成功，写入提交审计 |
| `TEST-STATE-002` | Submitted → Draft | 成功，写入反提交审计 |
| `TEST-STATE-003` | Draft → Cancelled | 成功并要求原因 |
| `TEST-STATE-004` | Submitted → Cancelled | 失败 |
| `TEST-STATE-005` | Cancelled → Draft | 失败 |
| `TEST-STATE-006` | Submitted/Cancelled write | 核心业务字段写入失败 |
| `TEST-VALID-001` | Submit 0 行 | 失败 |
| `TEST-VALID-002` | 缺 Operator | 失败 |
| `TEST-VALID-003` | 非正数量/工时 | 失败 |
| `TEST-AUDIT-001` | 重复 Submit/Unsubmit | 当前字段正确，chatter 可追溯每次动作 |
| `TEST-SEC-001` | 仓管员查看自己的记录 | 成功 |
| `TEST-SEC-002` | 仓管员查看他人记录 | 被过滤/拒绝 |
| `TEST-SEC-003` | 主管查看全部 | 成功 |
| `TEST-SEC-004` | 未授权 action | 服务端拒绝 |
| `TEST-ATTACH-001` | 多附件/无附件 | 均可正常保存，附件关联正确 |
| `TEST-CONC-001` | 两事务同时 Submit 同一 Draft | 先取得 VAS 行锁者成功，后者重读 state 后失败 |
| `TEST-CONC-002` | Submit 与 Warehouse Order Cancel 并发 | 目标订单行锁后按串行化结果明确成功/失败 |
| `TEST-NFR-001` | 提交事务异常 | 不产生半提交状态或损坏记录 |

真实 PDA 设备 UX 不在自动化测试中，留给 Human/Acceptance Verification。

## 19. Requirement Traceability

| SRS | TDD 落点 | Planned Test |
|---|---|---|
| FR-VAS-01 | §5、§15、§12 | `TEST-MODEL-001` |
| FR-VAS-02 | §5.2、§9 | `TEST-MODEL-002/003`, `TEST-VALID-001` |
| FR-VAS-03 | §6、§7 | `TEST-ASSOC-001~006` |
| FR-VAS-04 | §5.1、§11 | `TEST-VALID-002`, `TEST-SEC-001~004` |
| FR-VAS-05 | §14 | `TEST-ATTACH-001` |
| FR-VAS-06 | §8.2 | `TEST-STATE-001`, `TEST-VALID-001~003` |
| FR-VAS-07 | §8.3 | `TEST-STATE-002` |
| FR-VAS-08 | §8.4 | `TEST-STATE-003~005` |
| FR-VAS-09 | §12 | `TEST-SEC-001~004` |
| FR-VAS-10 | §12、§14 | `TEST-ATTACH-001` |
| BR-VAS-01 | §5.1、§11 | `TEST-MODEL-001`, `TEST-VALID-002` |
| BR-VAS-02 | §5.2、§8.2、§9.3 | `TEST-MODEL-002`, `TEST-VALID-001` |
| BR-VAS-03 | §6 | `TEST-ASSOC-001~003` |
| BR-VAS-04 | §8.2、§9.3 | `TEST-ASSOC-004/005` |
| BR-VAS-05 | §8.2、§9.3 | `TEST-ASSOC-004` |
| BR-VAS-06 | §8.2/8.3、§12 | `TEST-STATE-001/002/006` |
| BR-VAS-07 | §8.4 | `TEST-STATE-004` |
| BR-VAS-08 | §8.4 | `TEST-STATE-003/005` |
| BR-VAS-09 | §5.2/5.3、§7 | `TEST-MODEL-003`, `TEST-VALID-003` |
| BR-VAS-10 | §5.1、§11 | `TEST-VALID-002`, `TEST-SEC-004` |
| BR-VAS-11 | §9.2、§12 | `TEST-MODEL-002`, `TEST-STATE-006` |
| ROLE-VAS-01 | §11 | `TEST-SEC-001/002/004` |
| ROLE-VAS-02 | §11 | `TEST-SEC-003/004` |
| NFR-VAS-01 | §11 | `TEST-SEC-001~004` |
| NFR-VAS-02 | §10 | `TEST-AUDIT-001` |
| NFR-VAS-03 | §13 | Human/Acceptance Verification |
| NFR-VAS-04 | §16、§18 | `TEST-NFR-001` |
| AC-01 | §5、§15 | `TEST-MODEL-001` |
| AC-02 | §5.1、§11 | `TEST-MODEL-001`, `TEST-SEC-001` |
| AC-03 | §8.2、§9.3 | `TEST-VALID-001` |
| AC-04 | §8.2 | `TEST-ASSOC-004` |
| AC-05 | §8.2 | `TEST-ASSOC-004` |
| AC-06 | §8.2 | `TEST-STATE-001` |
| AC-07 | §8.3 | `TEST-STATE-002` |
| AC-08 | §8.4 | `TEST-STATE-003` |
| AC-09 | §8.4 | `TEST-STATE-004` |
| AC-10 | §8.4 | `TEST-STATE-005` |
| AC-11 | §11/§12 | `TEST-SEC-001` |
| AC-12 | §11/§12 | `TEST-SEC-003` |
| AC-13 | §11 | `TEST-SEC-002` |
| AC-14 | §10 | `TEST-AUDIT-001` |
| AC-18 | §5.1/§11 | `TEST-VALID-002`, `TEST-SEC-004` |
| AC-19 | §13 | Human/Acceptance Verification |
| AC-20 | §16 | `TEST-NFR-001` |
| AC-21 | §12、§14 | `TEST-ATTACH-001` |
| AC-22 | §5.2/5.3、§7 | `TEST-MODEL-003` |
| AC-23 | §9.2/§12 | `TEST-MODEL-002`, `TEST-STATE-006` |

Coverage count: 10 FR mapped；11 BR mapped；2 ROLE mapped；4 NFR mapped；20 AC mapped；`NOT MAPPED = 0`。NFR-VAS-03 的真实设备体验不由单元测试伪造覆盖，而由后续验收验证覆盖。

## 20. Technical Decision Register

| TD | Decision | Alternatives | Reason | SRS/TV Basis |
|---|---|---|---|---|
| `TD-001` | 采用三个显式 Many2one 关联 | Reference；新抽象层 | 强 ORM 完整性、domain、报表和可维护性 | TV-01；FR-VAS-03 |
| `TD-002` | VAS 使用独立 `draft/submitted/cancelled` 状态 | 复用 Warehouse Order state | 避免混淆两个业务生命周期 | SRS §7；TV-01 |
| `TD-003` | billno 作为输入，Submit 时解析并写入关系 | Draft 即强制绑定；裸号跨模型搜索 | 保留 Draft 可保存，类型上下文消歧 | FR-VAS-01/03；TV-01 |
| `TD-004` | 操作类型直接引用 Charge Unit，明细保存单位快照 | 引用 Charge Item；自动计费 | 复用计量单位但不建立收费依赖 | BR-VAS-09；TV-01 |
| `TD-005` | 标准 Odoo Web 同时承载 Web/PDA | 独立 PDA App/SPA | TV 已确认标准 Web 足够 | NFR-VAS-03；TV-02 |
| `TD-006` | Many2many `ir.attachment` + 标准 widget | 自定义存储；自定义附件模型 | 原生能力满足多媒体和关联 | FR-VAS-05；TV-03A |
| `TD-007` | mail.thread/tracking + 显式最近动作字段 | 自定义 audit model | 原生能力满足审计历史 | NFR-VAS-02；TV-03B |
| `TD-008` | 状态转换和受保护 write 使用单行 `FOR UPDATE`，锁后重检 state | 仅 ORM 状态重检；复杂锁框架/队列 | Odoo ORM 事务内以最小行锁保证状态转换前提 | NFR-VAS-04 |
| `TD-009` | `ir.sequence` 生成 VAS 单号 | 手工编号 | 保证系统生成、不可人工修改 | FR-VAS-01 |
| `TD-010` | Operator 为 active VAS User / VAS Manager，不按 Warehouse 限制 | 建立 Warehouse ↔ Operator 授权关系 | 当前无权威关系，避免无业务依据新增人员主数据 | ROLE-VAS-01；Human Decision |

## 21. Open Questions / Risks

| ID | 分类 | 问题 | 状态 | 影响 |
|---|---|---|---|---|
| `TQ-001` | BUSINESS DECISION | Operator 为 active VAS User / VAS Manager，本期不建立 Warehouse ↔ Operator 授权关系 | **RESOLVED** | 已由 Human Decision 关闭；服务端仅按 VAS 授权组和 active 状态校验 |
| `TQ-002` | VERIFICATION QUESTION | 真实 PDA/扫码枪是否将回车稳定送入 billno 字段？ | Non-blocking for TDD Freeze | 后续 HVR/Acceptance Verification |
| `TQ-003` | VERIFICATION QUESTION | 视频是否只需标准查看/下载，还是要求内嵌播放？ | Non-blocking for TDD Freeze | 后续 HVR；SRS 未要求独立播放器 |
| `TQ-004` | TECHNICAL QUESTION | 部署 PostgreSQL 的准确版本和附件容量策略是什么？ | Non-blocking for TDD Freeze | 纳入 Release/Operations baseline，不改变当前设计 |

风险：

- 三个既有模型没有 `billno` SQL 唯一约束，因此 Submit 搜索必须对零条和多条结果都显式失败；
- 当前数据库没有 VAS 历史数据，安装版不需要迁移；
- UI readonly 不是安全边界，所有状态保护必须在服务端执行。

## 22. TDD Freeze Readiness

当前结论：

```text
TDD FROZEN
```

本稿已完成模型、关联、状态、校验、审计、权限、UI、附件、序列、并发、安装和测试矩阵设计，且不存在会改变当前技术设计的未决阻塞问题。

`TQ-001` 已由 Human Decision 关闭。`TQ-002`、`TQ-003` 属于后续 HVR/Acceptance，`TQ-004` 属于 Release/Operations baseline，均不阻止 TDD Freeze。当前文档已由 Human Final Review 冻结为 `TDD FROZEN`。

本 TDD 不创建正式实现，不修改 Frozen BRD/SRS，不修改 Odoo 官方源码，不修改三个既有 Warehouse Order 模型。

### 22.1 Freeze Record

| 项 | 内容 |
|---|---|
| Frozen Version | `v1.0.0` |
| Freeze Date | 2026-09-04 |
| Freeze Authority | Human Final Review |
| Upstream | SRS v1.0.0 Frozen；DDD SKIP；TV READY FOR TDD |
| Downstream | Coding Contract → Implementation → Test |

冻结后仅允许勘误或不改变业务语义的技术修订；任何业务需求变化必须先更新 SRS，任何技术方案变化必须升级 TDD 版本并保留变更记录。

## Appendix A. Terms

| 术语 | 含义 |
|---|---|
| Creator | 创建 VAS Order 的登录用户 |
| Operator | 实际执行作业的人员 |
| Submitter | 执行 Submit 动作的登录用户 |
| Warehouse Order | 入库、出库或调拨业务订单 |
| Draft | 尚未正式确认的可编辑记录 |
| Submitted | 已确认且核心字段锁定的记录 |
| Cancelled | 仅由 Draft 作废形成的终态记录 |

## Appendix B. Coding Contract Baseline

本模块实现时至少裁剪以下门禁：

| 编号 | 约束 |
|---|---|
| `T-SEC-001` | 敏感信息不得写入日志 |
| `T-SEC-002` | 所有外部/用户输入必须校验 |
| `T-ORM-001` | 数据库唯一约束必须有明确 SRS/数据完整性来源 |
| `T-CONC-001` | Submit/Unsubmit/write 必须明确状态并发策略 |
| `T-OBS-001` | Submit、Unsubmit、Cancel 必须可审计 |
| `T-MIG-001` | 初始版本明确 No Migration；后续变更评估迁移 |

实现阶段的单次 Coding Contract 还必须列出允许修改文件、禁止修改的四个既有模型、测试选择和变更边界。
