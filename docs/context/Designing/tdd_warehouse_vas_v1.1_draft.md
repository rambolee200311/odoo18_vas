# Warehouse VAS Technical Detailed Design

> 文档版本：v1.1.0 Draft  
> 状态：TDD DRAFT — NOT FROZEN  
> 模块：`wd_warehouse_value_add`  
> 基线日期：2026-09-07  
> 技术负责人：Copilot  
> 上游：Frozen SRS v1.0.0、TDD v1.0.0 Frozen  
> 下游：SPIKE-PDA-001、Implementation Plan v1.1、CC-04（待创建）

本文是 Warehouse VAS PDA Frontend Gap Impact Assessment 之后的技术设计草案。
本文不授权编码，不创建 Coding Contract，不改变 Frozen SRS、TDD v1.0.0 或
CC-01/02/03。本文必须经过 Human Review，并在冻结前完成本稿列出的
SPIKE 和未决问题。

---

## 0. Document Control

| 项 | 内容 |
|---|---|
| 项目 | 仓库库内增值作业单（Warehouse VAS） |
| Odoo | 18.0 Enterprise，具体前端实现能力待 SPIKE 验证 |
| 模块 | `wd_warehouse_value_add` |
| 上游业务基线 | SRS v1.0.0 Frozen |
| 上游技术基线 | TDD v1.0.0 Frozen |
| 领域基线 | DDD SKIP |
| 已完成实现 | CC-01、CC-02、CC-03 已完成并集成 |
| 本稿范围 | PDA Frontend、Dashboard、导航、测试和设备验收 |
| 本稿状态 | Draft，不是实施授权 |

### 0.1 Authority

权威顺序保持不变：

1. Frozen SRS：业务 WHAT；
2. 已验证技术事实和 SPIKE 证据；
3. 本 TDD：技术 HOW；
4. 后续 Implementation Plan 和 CC-04：实施边界；
5. 实际实现和测试必须服从冻结后的 TDD 与 CC。

### 0.2 不在本稿中冻结的内容

PDA 采用专用 OWL/JS 表现层，属于本稿已确定的技术架构。
在 SPIKE-PDA-001 完成后，以下项目已取得最小技术证据；生产级实现和设备
边界仍需 CC-04/HVR：

- 生产级 client action、Dashboard action 和 PDA action 的最终 XML ID；
- 完整 OWL component 拆分和生产级注册方式；
- 生产 JS module 和 asset bundle 的最终命名；
- 具体前端目录（包括是否创建 `static/`）；
- 生产级 ORM/RPC 错误处理和刷新策略；
- barcode service 或设备扫码 API；
- camera capture API；
- 完整 attachment upload/delete 交互；
- 目标 Android PDA 浏览器的完整兼容边界。

---

## 1. Baseline and Impact

### 1.1 保持不变的基线

- Frozen SRS v1.0.0 保持不变；
- TDD v1.0.0 Frozen 作为历史版本保留；
- CC-01、CC-02、CC-03 已完成并集成；
- CC-03 不重开、不回滚、不修改；
- `wd.vas.order`、`wd.vas.order.line`、`wd.vas.operation.type` 保留；
- Submit / Unsubmit / Cancel 保留；
- Warehouse Order association、billno/warehouse snapshot 保留；
- VAS Order 和 Warehouse Order locking 保留；
- ACL、record rules、服务端 action permission 保留；
- Desktop Web list/form/search/menu 保留；
- `attachment_ids` 关系保留；
- chatter、tracking 和显式审计字段保留。

### 1.2 Impact Conclusion

```text
TDD IMPACT = YES
SRS CHANGE = NO（当前不需要修改 Frozen SRS）
CC-03 = HISTORICAL BASELINE
PDA FRONTEND = 后续增量能力
TDD v1.1 = Draft，尚未冻结
```

当前已确认的是：

```text
CC-03 的标准 Web Form 实现不能证明满足已确认的 PDA 现场交互要求。
```

当前尚未验证的是：

```text
完整 PDA Frontend 的最终 Odoo 18 技术落地细节。
```

PDA 专用 OWL/JS 表现层是已确定的技术架构；具体 Odoo 18 API、入口注册、
资源声明、ORM/RPC service 和设备能力必须以 SPIKE-PDA-001 证据为准。

---

## 2. v1.0 → v1.1 Change Log

| 区域 | v1.0 Frozen | v1.1 Draft 修订 |
|---|---|---|
| PDA 定义 | 标准 Odoo Web Form 小屏适配 | PDA 专用 OWL/JS 表现层 |
| 技术确定性 | 标准 Web 被视为足够 | OWL/JS 架构已确定，具体 Odoo 18 落地方式待 SPIKE |
| 首页 | 模块进入后直接进入 Web List | 从模块根菜单进入时打开 Dashboard |
| PDA 入口 | 与 Web Form 共用 | Dashboard 进入，且允许直接菜单/收藏进入 |
| Web List | 标准管理入口 | 保留为独立 Web List Action |
| 业务模型 | 单一 VAS 模型 | 保持单一 `wd.vas.order` |
| Operator | 统一服务端字段 | Desktop Web 支持代录；PDA 当前登录用户只读带出 |
| 附件 | 标准 `many2many_binary` | 保留关系，新增 PDA 拍照/文件选择交互设计 |
| 测试 | 真实 PDA UX deferred | 真实目标 PDA HVR 必须在 CC-04 Closure 前完成 |
| 测试范围 | Backend/Web 为主 | 增加 JS/OWL、Browser、PDA HVR、设备能力验证 |
| Spike 证据 | 未执行 | 最小 OWL/JS 路径 Conditional Pass；有效 Submit/快照已在隔离库补验证 |
| 状态 | Frozen | Draft，已回写 Spike 证据，等待 Human Review |

---

## 3. Requirement and Design Inputs

### 3.1 SRS 追溯

本稿继续追溯到 Frozen SRS：

- `FR-VAS-01`：Web/PDA 创建 Draft；
- `FR-VAS-02`：添加和删除明细；
- `FR-VAS-03`：关联对象和 billno；
- `FR-VAS-04`：Operator / 代录；
- `FR-VAS-05`：图片/视频附件；
- `FR-VAS-06`：Submit；
- `FR-VAS-07`：Unsubmit；
- `FR-VAS-08`：Cancel；
- `FR-VAS-09`：Web 查询；
- `FR-VAS-10`：详情查看；
- `NFR-VAS-03`：手持终端可用性；
- `NFR-VAS-04`：数据完整性。

本稿不新增业务状态，不修改 SRS 的 Operator 业务事实，也不新增客户、
计费、审批或独立业务域语义。

### 3.2 已确认的 PDA 原型输入

原型文件：

- `docs/context/Designing/pda_form.drawio`
- `docs/context/Designing/pda_form_detail.drawio`

原型要求覆盖：

- PDA Header；
- 当前登录 Operator 自动带出并只读；
- 关联订单类型；
- billno 输入和扫码入口；
- 解析成功/失败反馈；
- 客户信息自动带出并只读；
- 作业明细卡片；
- 添加、编辑、删除明细；
- 数量/工时；
- 单位自动展示；
- 拍照；
- 相册/文件多选；
- 附件展示与删除；
- 保存草稿；
- 提交；
- Submitted 只读；
- 底部固定操作栏。

---

## 4. Architecture Overview

### 4.1 Target Architecture

```text
                    ┌──────────────────────────────┐
                    │ Warehouse VAS Dashboard      │
                    │ 入口选择，不承载业务逻辑     │
                    └──────────────┬───────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
                 ▼                                   ▼
      ┌────────────────────┐              ┌────────────────────┐
      │ PDA Action          │              │ Web List Action     │
      │ OWL/JS presentation │              │ Standard Odoo Web  │
      │ PDA Form            │              │ list/form/search    │
      └─────────┬──────────┘              └──────────┬─────────┘
                │                                    │
                └────────────────┬───────────────────┘
                                 ▼
                    ┌──────────────────────────────┐
                    │ Shared Odoo Backend           │
                    │                               │
                    │ wd.vas.order                  │
                    │ wd.vas.order.line             │
                    │ wd.vas.operation.type         │
                    │                               │
                    │ same actions / permissions    │
                    │ same locking / snapshots      │
                    │ same attachments / chatter    │
                    └──────────────────────────────┘
```

### 4.2 Architecture Rules

PDA 和 Desktop Web 必须共享：

```text
同一个 wd.vas.order
同一个 wd.vas.order.line
同一个 operator_id
同一个状态机
同一个 ACL / record rule
同一个 Submit / Unsubmit / Cancel
同一个附件关系
同一个锁和快照语义
```

PDA Frontend 不得创建：

- 第二套业务模型；
- 第二套状态机；
- 第二套权限模型；
- 第二套附件关系；
- 独立 PDA Backend；
- 未经 SPIKE 证明必要性的独立业务 API。

### 4.3 技术方案状态

已确定的技术架构为：

```text
专用 OWL/JS 表现层
```

具体业务实现仍受以下前置条件约束：

```text
SPIKE-PDA-001 必须验证 Odoo 18 的入口、资源、ORM/RPC 和设备能力。
```

SPIKE 已验证最小技术路径：`ir.actions.client` 可连接 OWL registry action
tag；JS/XML/SCSS 可通过 backend assets 加载；组件可使用标准 `orm` service
读取 `wd.vas.order`、创建明细、写入 Draft、调用 `action_submit`，并通过
现有 `attachment_ids` 关系写入附件。具体生产目录、bundle 命名、完整组件
拆分和设备能力仍须在 CC-04 实施与 HVR 中冻结。

---

## 5. Module Entry and Navigation

### 5.1 User Navigation

```text
库内增值作业
      │
      ▼
   Dashboard
      │
      ├── PDA 作业录入
      │       └── PDA Action
      │            └── PDA Form
      │
      └── 作业单管理
              └── Web List Action
                   ├── 查询 / 筛选
                   ├── 查看详情
                   ├── 编辑草稿
                   └── 管理员操作
```

### 5.2 Menu Structure

```text
库内增值作业
├── 首页
├── 作业单管理
│   └── 作业单
└── 配置
    └── 作业项目
```

菜单职责：

| 菜单 | 目标 | 说明 |
|---|---|---|
| 首页 | Dashboard | 默认首页，仅选择工作入口 |
| 作业单 | Web List Action | 复用现有 Web 管理入口 |
| 作业项目 | Operation Type Action | 复用现有配置入口 |

### 5.3 Dashboard Action

从“库内增值作业”模块根菜单进入时，默认打开 Dashboard。Dashboard 只展示
两个入口：

```text
PDA 作业录入
现场录入、扫码、拍照、提交作业单

作业单管理
查询、筛选、查看和管理已有作业单
```

Dashboard 不提供：

- 统计；
- 图表；
- 待办；
- 草稿列表；
- 业务聚合；
- 直接保存或提交；
- 第二套权限判断；
- 第二套业务逻辑。

Dashboard 采用最低复杂度实现，不要求 Dashboard 本身必须使用 OWL。
SPIKE 已证明 Dashboard 可使用 `ir.actions.client` 与 OWL registry action
tag 作为最低复杂度入口，并通过 action service 跳转 PDA 和 Web List。
生产 action XML ID、目录和 bundle 名称仍由 CC-04 allowlist 冻结。

### 5.4 PDA Action

PDA Action 负责启动 PDA Frontend，不要求用户先进入 Web List。

PDA Action 必须支持：

- 从 Dashboard 进入；
- 从菜单或直接入口进入；
- 被用户收藏后直接打开；
- 在现有 Odoo 会话和权限上下文中运行。

PDA Action 不得依赖 Dashboard 保存业务状态。Dashboard 关闭或绕过
不应影响 PDA 业务流程。

### 5.5 Web List Action

Web List Action 保留当前 CC-03 实现：

- list；
- form；
- search；
- 查询和筛选；
- 草稿编辑；
- 管理员操作；
- Operation Type 配置入口。

不因增加 Dashboard 或 PDA Action 而改变现有 Web List 的业务语义。

### 5.6 Action 技术未知项

以下 Dashboard/PDA 导航落地细节等待 SPIKE：

- PDA 使用专用 OWL/JS 表现层，并可通过独立 client action 进入；
- action registry 的最小注册方式已验证为 `registry.category("actions").add(...)`；
- OWL template 的最小资源加载方式已验证；
- 菜单到 action 的生产 XML/API 组合；
- 直接 PDA 收藏入口的技术实现；
- Dashboard 与 Web List/PDA Action 的返回导航方式。

---

## 6. Shared Backend Preservation

本节只声明保留边界，不重新设计已完成 Backend。

### 6.1 Models

保留：

- `wd.vas.order`；
- `wd.vas.order.line`；
- `wd.vas.operation.type`。

### 6.2 Lifecycle

保留：

```text
draft --action_submit--> submitted
submitted --action_unsubmit--> draft
draft --action_cancel--> cancelled
```

PDA 只调用现有服务端动作，不在前端复制状态转换规则。

### 6.3 Association, Snapshot and Locking

保留：

- `order_type` 与三个显式 Many2one；
- `warehouse_order_billno`；
- Submit 时的 Warehouse Order 解析；
- billno snapshot；
- warehouse snapshot；
- `VAS Order → Warehouse Order` 锁顺序；
- 锁后重新读取状态；
- Submitted/Cancelled 写保护。

PDA 扫码只是 billno 的输入方式，不改变服务端解析和绑定权威。

### 6.4 Security

保留：

- VAS User / VAS Manager；
- ACL；
- record rules；
- 服务端 action permission；
- UI 隐藏不能替代服务端保护。

PDA 的 ORM/RPC 请求必须使用当前用户上下文，不能用前端自行判断权限
替代服务端授权。

### 6.5 Operator

两种入口共享 `operator_id`：

| 入口 | Operator 行为 |
|---|---|
| Desktop Web | 保留代录能力，可选择实际 Operator |
| PDA | 当前登录 Operator 自动带出并只读 |

PDA 不删除服务端代录能力。Submitter 与 Operator 仍可不同。

### 6.6 Attachment and Audit

保留：

- `attachment_ids`；
- `ir.attachment`；
- Draft 可维护附件；
- Submitted/Cancelled 受保护；
- chatter；
- tracking；
- 显式审计字段。

PDA 只新增媒体输入和移动展示方式，不新增附件业务关系。

---

### 6.7 Retained v1.0 Technical Baseline

以下 v1.0 技术设计继续有效，并由 PDA Frontend 复用：

| Model | Retained responsibility |
|---|---|
| `wd.vas.order` | VAS header, state, order type, billno, warehouse, operator, audit |
| `wd.vas.order.line` | Operation Type, quantity/time, unit snapshot, note |
| `wd.vas.operation.type` | Operation name, code, charge unit, active and sequence |

`wd.vas.order` 的关键字段语义保持：

| Field | Design |
|---|---|
| `name` | `ir.sequence` 生成且不可人工修改 |
| `state` | `draft/submitted/cancelled` |
| `order_type` | `inbound/outbound/transfer` |
| `inbound_order_id` / `outbound_order_id` / `transfer_order_id` | 按 `order_type` 只绑定一个显式关系 |
| `warehouse_order_billno` | Draft 输入，Submit 时解析并形成历史快照 |
| `warehouse_order_display` | 当前已解析 Warehouse Order 的显示名 |
| `warehouse_id` | Submit 时从 Warehouse Order 写入的事实快照 |
| `operator_id` | 实际操作员；Desktop Web 支持代录，PDA 默认当前登录用户 |
| `submitter_id` / `submitted_at` | 最近一次 Submit 审计 |
| `unsubmitted_by` / `unsubmitted_at` | 最近一次 Unsubmit 审计 |
| `cancelled_by` / `cancelled_at` / `cancel_reason` | Cancel 审计 |
| `line_ids` | VAS 明细，Draft 可为零行，Submit 至少一行 |
| `attachment_ids` | 现有 `ir.attachment` 多附件关系 |
| `notes` | Draft 可编辑备注 |

`wd.vas.order.line` 的关键语义保持：

- `quantity_time` 是统一数量/工时数值字段；
- `unit_id` 根据 Operation Type 自动带出并保存为单位快照；
- Draft 可以为空或为零；
- Submit 时必须大于零；
- Submitted/Cancelled 后不能通过普通写入修改。

### 6.8 Retained Business and Security Decisions

以下 v1.0 决策不因 PDA Frontend 改变：

1. Warehouse Order 仍使用三个显式 Many2one，不修改既有 Warehouse Order 模型；
2. `order_type + billno` 是 Draft 输入和 Submit 解析上下文；
3. Submit 时必须得到零条或一条明确结果，重复匹配阻断；
4. VAS Order → Warehouse Order 是动作和写保护的锁顺序；
5. 所有业务写入使用 ORM，锁 SQL 只用于并发保护；
6. VAS User 只能访问自己创建的订单，Manager 可访问全部；
7. 未授权用户不能通过 RPC 直接调用 Submit/Unsubmit/Cancel；
8. UI readonly 不是安全边界；
9. Submitted/Cancelled 核心字段、明细和附件关系不可普通修改；
10. Chatter/tracking 与显式审计字段共同保留动作历史；
11. PDA 不创建新的授权模型、状态或数据存储。

### 6.9 Retained Module Baseline

当前模块继续依赖：

```text
base
mail
web
worlddepot
```

当前已集成的安全、数据、视图和测试基线继续保留。PDA Frontend 需要的
前端资源、Action 和测试文件属于后续 CC-04 的增量，不在本 Draft 中
授权创建。

---

## 7. PDA Frontend Design

本节定义目标交互和服务端边界，不冻结具体 Odoo 18 API。

### 7.1 PDA Header

目标：

- 显示“库内增值作业”；
- 提供返回/导航入口；
- 明确当前 PDA 工作上下文；
- 不承载业务写入。

具体返回导航和组件实现：

```text
UNKNOWN / SPIKE REQUIRED
```

### 7.2 Operator

PDA 打开新建作业单时：

```text
当前登录用户自动作为 operator_id
PDA 页面只读展示
```

服务端仍执行现有 Operator 合法性校验。PDA 不允许在界面切换
Operator，但 Desktop Web 继续支持代录。

### 7.3 Warehouse Order Type and Billno

PDA 必须提供：

- 关联订单类型；
- billno 输入；
- 手工输入 fallback；
- 扫码入口；
- 解析中状态；
- 解析成功反馈；
- 解析失败反馈；
- 解析后的订单显示；
- 客户只读显示（来源为 `Warehouse Order.owner`）。

扫码结果必须最终进入现有 `warehouse_order_billno` 和服务端解析路径。
前端成功提示不能替代 `action_submit()` 的正式校验。

手工 billno 输入和标准 ORM/RPC 写入路径已在隔离 Spike 验证。扫码服务、
相机扫码和生产级解析反馈的技术方式：

```text
UNKNOWN / SPIKE REQUIRED
```

### 7.4 Customer Information

原型要求客户信息自动带出并只读。

已核查当前仓库中三类 Warehouse Order 的既有客户字段：

| Warehouse Order | 客户字段 | 来源 |
|---|---|---|
| `world.depot.inbound.order` | `owner` | `related='project.owner'` |
| `world.depot.outbound.order` | `owner` | `related='project.owner'`，stored |
| `world.depot.transfer.order` | `owner` | `related='project.owner'` |

因此三类订单采用统一客户来源：

```text
Warehouse Order.owner → res.partner
```

不新增 VAS 客户字段，不新增客户快照，不复制客户数据。PDA 在订单解析
成功后读取被解析 Warehouse Order 的 `owner`，只读展示其名称；提交后的
业务权威仍是现有显式 Warehouse Order 关系，客户展示不成为第二套关联权威。

本稿定义交互目标：

```text
解析成功后展示客户信息；
用户不可直接修改；
客户信息不成为第二套订单关联权威。
```

以下实现细节仍需在 SPIKE/冻结前确认：

- Draft 阶段解析成功后如何通过 OWL/JS 读取目标订单；
- `owner` 为空时的只读显示和提示策略；
- 客户名称使用 `display_name` 还是其他既有展示值。

客户来源决策已收口：

```text
Customer source = Warehouse Order.owner
Customer snapshot = NOT CREATED
Customer source decision = CLOSED
```

### 7.5 Line Cards

PDA 以移动卡片展示明细，每张卡片至少显示：

- Operation Type；
- Quantity / Time；
- Unit；
- Note；
- 编辑入口；
- 删除入口。

PDA 提供：

- 添加作业行；
- 编辑作业行；
- 删除作业行；
- 零行 Draft；
- Submit 前至少一行校验。

卡片使用标准组件、专用组件或组合方式：

```text
UNKNOWN / SPIKE REQUIRED
```

### 7.6 Quantity / Time and Unit

继续使用现有 `quantity_time` 和 `unit_id`：

- Operation Type 选择后自动展示 Unit；
- Unit 不由人工输入；
- Draft 允许为空或零；
- Submit 时由服务端校验大于零；
- PDA 不复制服务端数值校验。

PDA 是否根据 Operation Type 改变“数量/工时”显示提示，属于表现层
设计；业务字段语义不改变。

### 7.7 Attachments

PDA 目标交互：

- 拍照入口；
- 相册/文件多选入口；
- 附件列表；
- 附件名称/类型展示；
- Draft 删除；
- Submitted 只读；
- 上传状态和失败反馈。

底层仍使用现有 `attachment_ids`。

以下能力必须通过目标设备验证：

- camera capture；
- gallery multi-select；
- file multi-select；
- image/video；
- upload failure；
- delete protection。

### 7.8 Save Draft

Save Draft 只保存当前 Draft 数据，不执行 Submit 完整性阻断。

保存后：

- 保留同一个 `wd.vas.order`；
- 保留当前明细和附件关联；
- 可重新打开；
- 可从 PDA 或 Web List 读取；
- 服务端 write 规则仍然有效。

### 7.9 Submit

PDA Submit 调用现有服务端提交能力：

- 由服务端校验 Operator；
- 校验明细；
- 校验 billno；
- 解析并绑定 Warehouse Order；
- 写入 snapshot；
- 执行锁和状态转换；
- 写入审计字段。

前端只负责：

- 防止重复点击；
- 展示 loading；
- 展示成功；
- 展示服务端错误；
- 刷新 Submitted 状态。

### 7.10 Submitted Readonly

Submitted 后 PDA 必须：

- 禁止编辑表头；
- 禁止编辑/删除明细；
- 禁止新增附件；
- 禁止删除附件；
- 提供只读展示；
- PDA 第一版不提供 Unsubmit；
- 从服务端刷新真实状态。

### 7.11 Bottom Action Bar

Draft 目标操作：

```text
保存草稿 | 提交
```

Submitted 目标操作：

```text
只读
```

Cancelled 目标操作：

```text
只读
```

第一版 PDA 不提供 Unsubmit。服务端 Unsubmit 和 Desktop Web 的反提交能力
继续保留；如果未来业务明确要求 PDA 反提交，另行确认并更新 TDD/CC。

隔离 Spike 已验证最小 sticky bottom action bar 可渲染。生产级 SCSS、软键盘、
横竖屏和小屏遮挡边界仍需 CC-04/HVR。

### 7.12 Error and Refresh

PDA 必须能区分并反馈：

- 业务校验失败；
- billno 解析失败；
- Submit 失败；
- 权限拒绝；
- 网络/RPC 失败；
- 附件上传失败；
- 会话失效；
- 记录已被其他入口更新。

所有最终业务状态以服务端重新读取结果为准。

---

## 8. Module Structure Draft

当前已存在的目录继续保留：

```text
addons/wd_warehouse_value_add/
├── models/
├── security/
├── data/
├── views/
└── tests/
```

PDA Frontend 可能需要新增前端资源目录，但具体结构未冻结：

```text
UNKNOWN / SPIKE REQUIRED
```

可能的设计元素包括：

- OWL components；
- XML templates；
- JavaScript modules；
- SCSS；
- frontend asset declaration；
- Dashboard action；
- PDA action。

不得在 SPIKE 前把其中任一具体路径或 API 当作已验证事实。

Manifest 当前的 Backend 依赖和既有 data 加载顺序原则上保留。
是否需要新增前端资源声明由 SPIKE 和 TDD v1.1 Freeze 决定。

---

## 9. KEEP / REVIEW / NEW

### 9.1 KEEP

- 三个 VAS 模型；
- Submit / Unsubmit / Cancel；
- Warehouse Order association；
- billno 和 warehouse snapshot；
- locking；
- ACL；
- record rules；
- action permission；
- Desktop Web list/form/search/menu；
- attachment relation；
- chatter/audit；
- Operation Type 配置；
- CC-03 浏览器已验证的 Web 行为。

### 9.2 REVIEW

- Dashboard action 技术实现；
- PDA action 技术实现；
- Web List action 与菜单关系；
- customer display fallback when `owner` is empty；
- 扫码能力；
- 相机/文件选择；
- x2many 卡片复用方式；
- 底部固定操作栏；
- Android PDA 浏览器兼容边界；
- 直接 PDA 菜单/收藏入口；
- 弱网和上传失败反馈。

### 9.3 NEW

- Dashboard 入口表现层；
- PDA OWL/JS 表现层；
- PDA Action；
- PDA Header；
- PDA line cards；
- PDA media input；
- PDA attachment interaction；
- PDA bottom action bar；
- JS/OWL 或等价 frontend tests；
- PDA browser tests；
- 真实目标 PDA HVR。

### 9.4 不需要 REWORK 的内容

当前没有证据要求重写：

- Backend models；
- 状态机；
- 服务端动作；
- 锁；
- 快照；
- ACL / record rules；
- Desktop Web List；
- 既有 attachment relation。

若后续发现字段或客户来源需要调整，必须逐项评估迁移风险后再决定。

---

## 10. Test Design

### 10.1 Backend Regression

继续保留并回归：

- model creation；
- Draft zero-line；
- Operation Type → Unit；
- Warehouse Order association；
- snapshot；
- Submit / Unsubmit / Cancel；
- state protection；
- locking；
- ACL；
- record rules；
- action permission；
- attachment protection；
- chatter/audit；
- 数据完整性。

PDA 测试不得替代这些 Backend 测试。

### 10.2 JS/OWL or Equivalent Frontend Tests

SPIKE 确认技术路径后，新增最小测试设计：

- Dashboard 渲染两个入口；
- Dashboard 到 PDA Action；
- Dashboard 到 Web List Action；
- PDA Action 独立打开；
- Operator 自动带出且只读；
- billno 输入；
- 解析反馈；
- 一条明细添加和编辑；
- Unit 展示；
- Save Draft；
- Submit 调用和错误显示；
- Submitted readonly；
- 底部操作栏状态。

具体测试框架和 API：

```text
UNKNOWN / SPIKE REQUIRED
```

### 10.3 Browser Test

至少覆盖：

- 默认首页为 Dashboard；
- Dashboard → PDA；
- Dashboard → Web List；
- PDA 直接菜单/收藏入口；
- Web List 直接入口；
- 同一记录在 PDA 与 Web List 可见；
- PDA 创建 Draft，Web 查看；
- Web 修改 Draft，PDA 重新读取；
- PDA Submit，Web 查看 Submitted；
- Web Unsubmit，PDA 重新读取 Draft。

### 10.4 PDA HVR

真实目标 PDA HVR 必须在 CC-04 Closure 前完成，不能无限期 deferred。

至少覆盖：

- PDA 登录和入口；
- Header；
- Operator；
- 关联订单类型；
- billno 手工输入；
- 扫码；
- 成功/失败反馈；
- 客户展示；
- 明细添加/编辑/删除；
- 数量/工时；
- Unit；
- 拍照；
- 相册/文件多选；
- 多附件展示；
- Draft 删除附件；
- Save Draft；
- Reopen；
- Submit；
- Submitted readonly；
- Unsubmit；
- 错误提示；
- 底部固定操作栏。

### 10.5 Device Capability HVR

单独验证：

- Android PDA 浏览器；
- 触摸；
- 软键盘；
- 相机权限；
- 文件权限；
- 扫码输入；
- 图片/视频选择；
- 上传失败；
- 网络中断；
- 页面刷新；
- 返回和重新打开。

### 10.6 Web/PDA Data Consistency

必须验证：

```text
PDA 创建 Draft → Web 可见
Web 编辑 Draft → PDA 可见
PDA Submit → Web 为 Submitted
Web Unsubmit → PDA 为 Draft
PDA 上传附件 → Web 可见
Web 上传附件 → PDA 可见
Submitted 后两端均不可直接编辑核心字段
```

### 10.7 Weak Network and Upload Failure

只验证失败可感知、不误报成功、可安全重试或刷新。至少人工验证：

- RPC 延迟；
- Submit 重复点击；
- 上传中离开页面；
- 上传失败时明确失败，不显示成功；
- 用户可安全重试或刷新后重新读取；
- 网络恢复后重新读取；
- 不产生半提交状态；
- 已提交数据不因前端失败而损坏。

本稿不承诺：

- 离线保存；
- 断点续传；
- 自动同步；
- 离线队列；
- 无网络条件下提交。

---

## 11. HVR and Closure Rules

### 11.1 SPIKE 阶段

SPIKE 只验证：

- 入口；
- 最小 ORM/RPC；
- 一条明细；
- 保存/提交路径；
- 扫码能力边界；
- 相机/文件能力边界；
- 一个附件；
- 底部操作栏；
- Android 浏览器兼容边界。

SPIKE 不执行完整业务验收。

### 11.2 CC-04 Closure 前

以下必须完成：

- PDA Frontend 自动化测试；
- Dashboard 和导航测试；
- Browser Test；
- PDA HVR；
- 扫码 HVR；
- 拍照/文件上传 HVR；
- 多附件 HVR；
- Save Draft / Reopen / Submit / Readonly；
- Web/PDA 一致性；
- 弱网和上传失败基本验证；
- 真实目标 PDA 设备 HVR。

`Real PDA HVR` 不得以“后续再验证”无限期延期。

---

## 12. SPIKE-PDA-001 Dependency and UNKNOWN List

SPIKE-PDA-001 已取得 CONDITIONAL PASS。下表只保留尚未验证或必须进入
CC-04/HVR 的项目：

| 项目 | 状态 |
|---|---|
| Dashboard action 注册 | 已验证最小 `ir.actions.client` 路径；生产实现待 CC-04 |
| PDA action 注册 | 已验证最小独立 client action 路径；生产实现待 CC-04 |
| action registry | 已验证 `registry.category("actions").add(...)` |
| frontend assets | 已验证 JS/XML/SCSS backend assets 可加载 |
| OWL component registration | 已验证最小组件渲染；完整拆分待 CC-04 |
| ORM/RPC service | 已验证标准 `orm` service 读取、写入和 action call |
| billno barcode input | 手工输入已验证；真实扫码设备待 HVR |
| camera capture | UNKNOWN / SPIKE REQUIRED |
| gallery/file multi-select | UNKNOWN / SPIKE REQUIRED |
| attachment upload | 已验证一个附件写入现有关系；完整交互待 CC-04 |
| attachment delete interaction | UNKNOWN / SPIKE REQUIRED |
| sticky bottom action bar | UNKNOWN / SPIKE REQUIRED |
| Android PDA browser support | UNKNOWN / SPIKE REQUIRED |
| Dashboard direct navigation | 已验证最小入口跳转 |
| PDA direct menu/favorite entry | 菜单直接入口已验证；收藏入口待 CC-04/HVR |

本稿不得把这些项目表述为当前 Odoo 18 已验证能力。

---

## 13. CC-04 Recommended Scope

CC-04 建议作为后续独立 Coding Contract，范围至少包括：

### In Scope

- Dashboard 入口；
- PDA Action；
- PDA OWL/JS 表现层；
- PDA Header；
- Operator 自动带出只读；
- 关联订单类型；
- billno 输入和扫码路径；
- 解析反馈；
- 客户只读展示；
- 明细卡片；
- 添加/编辑/删除明细；
- 数量/工时和单位；
- 拍照/文件选择；
- 附件展示/删除；
- Save Draft；
- Submit；
- Submitted readonly；
- 底部固定操作栏；
- 错误提示和状态刷新；
- Dashboard/Web List/PDA 导航；
- JS/OWL、Browser、PDA HVR；
- 真实目标 PDA HVR。

### Out of Scope

- 第二套业务模型；
- 第二套状态机；
- 第二套权限模型；
- 计费；
- 审批；
- 独立 PDA Backend；
- 离线同步；
- Redis/queue/event bus；
- 客户价格和财务结算；
- 修改 CC-01/02/03；
- 修改既有 Warehouse Order 模型。

CC-04 的最终 allowlist、测试编号和停止条件必须在本稿冻结后另行起草，
本文件不创建 CC-04。

---

## 14. Freeze Preconditions

TDD v1.1 在冻结前必须解决：

1. SPIKE-PDA-001 完成并产生证据；
2. Dashboard action 技术路径确认；
3. PDA action 技术路径确认；
4. 菜单和直接入口关系确认；
5. OWL/JS 资源加载方式确认；
6. ORM/RPC 访问方式确认；
7. 扫码输入方案和降级方案确认；
8. 相机/文件选择方案确认；
9. attachment upload/delete 方案确认；
10. Android PDA 浏览器目标和版本确认；
11. `owner` 为空时的客户只读显示和提示策略确认；
12. Operator PDA 只读、Desktop 代录口径确认记录；
13. 底部操作栏实现方式确认；
14. PDA 与 Web 数据一致性验证路径确认；
15. 自动化测试技术栈确认；
16. 真实 PDA HVR 范围确认；
17. 有效 Warehouse Order Submit 隔离验证完成；
18. Human Review 批准本稿；
19. TDD v1.1 Revision 完成并冻结；
20. 随后创建 Implementation Plan v1.1；
21. 冻结版本和变更记录完成。

---

## 15. Document Actions

| 文档 | 本稿建议 |
|---|---|
| Frozen SRS v1.0.0 | 保持不变 |
| TDD v1.0.0 Frozen | 保留为历史版本，不修改 |
| TDD v1.1 | 本稿为 Draft，已回写 Spike 证据，待 Human Review |
| Implementation Plan | v1.1 Draft 已起草，待 Human Review |
| CC-01 | 保持 Frozen，不修改 |
| CC-02 | 保持 Frozen，不修改 |
| CC-03 | 保持 Frozen，Historical Baseline，不重开 |
| CC-04 | 后续创建，本稿不创建 |
| SPIKE-PDA-001 | v1.0 CONDITIONAL PASS，证据已回写 |

---

## 16. Draft Decision

本稿提出但尚未冻结的设计决策：

```text
采用专用 OWL/JS PDA 表现层作为目标方向；
Dashboard 作为默认模块首页和工作入口选择器；
PDA Action 与 Web List Action 独立；
PDA 不强制经过 Dashboard；
PDA 与 Desktop Web 共享同一业务模型和服务端能力；
Desktop Web 保留代录；
PDA 当前登录 Operator 自动带出并只读；
真实目标 PDA HVR 是 CC-04 Closure 前置条件。
```

本稿不是实施授权，不是 TDD FROZEN，不是 CC-04，不代表 SPIKE 已完成。

```text
TDD v1.1 STATUS = DRAFT — WAITING FOR HUMAN REVIEW
```
