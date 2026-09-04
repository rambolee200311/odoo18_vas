# Warehouse VAS Implementation Plan

> 文档版本：v1.0
> 状态：Implementation Plan v1.0 Approved Execution Baseline / READY TO DRAFT CC-01
> 模块：`wd_warehouse_value_add`
> 基线日期：2026-09-04

## 0. Document Control

| 项 | 内容 |
|---|---|
| 项目 | Warehouse VAS / 仓库库内增值作业单 |
| Frozen SRS | SRS v1.0.0 Frozen |
| Frozen TDD | `tdd_warehouse_vas_v1.0.0.md` v1.0.0 Frozen |
| DDD | SKIP |
| TV | `tv_warehouse_vas_v1.0.md` PASS / READY FOR TDD |
| Odoo | `18.0+e-20250619` |
| 计划范围 | 实施顺序、切片边界、依赖、验证和 Exit Criteria |

本计划不是 Authority 文档，不修改 Frozen SRS 或 Frozen TDD，也不提前生成后续 Coding Contract。

## 1. Purpose & Authority

权威关系：

```text
Frozen SRS → 定义业务 WHAT
Frozen TDD → 定义技术 HOW
Implementation Plan → 只定义实施顺序和切片闭环
Coding Contract → 定义单轮允许修改和验证范围
```

如计划与 Frozen TDD 冲突，以 [Frozen TDD](/Users/lijianqiang/Documents/odoo18e_vas/docs/context/Designing/tdd_warehouse_vas_v1.0.0.md) 为准，并记录为 PLAN BLOCKER；不得通过计划修改 TDD。

## 2. Baseline

- 模块目录当前只有基础 `__init__.py`、`__manifest__.py` 和 `models/__init__.py` 骨架。
- VAS 正式模型、视图、权限、序列和测试尚未实现。
- `worlddepot` 的三个 Warehouse Order 模型及 `world.depot.charge.unit` 是既有依赖。
- 三个既有 Warehouse Order 模型、Charge Item/Unit 既有模型和 Odoo 官方源码均为保护范围。
- Frozen TDD 已决定：
  - 三个显式 Many2one 关联；
  - VAS 独立状态机；
  - `billno` 和 `warehouse` 提交快照；
  - Operation Type 直接引用 Charge Unit；
  - `mail.thread`、原生附件和标准 Web；
  - `FOR UPDATE` 最小行锁，固定顺序为 VAS Order → Warehouse Order。

## 3. Planning Principles

1. Plan all，Contract next，Execute，Verify，Close，Then contract the next slice。
2. 每轮只形成一个垂直、可独立验证的技术能力闭环。
3. 后续 Slice 只能依赖 Frozen TDD 和已合并、已验证的前一轮事实。
4. 每轮必须有 In Scope、Out of Scope、Dependencies、Exit Criteria 和 FR Expectation。
5. 只有 `FR-CC-N = SATISFIED` 才默认进入下一轮。
6. 真实 PDA 设备体验进入后续 HVR，不伪装为自动化测试。
7. 不为流程完整性强制创建 CC-04。

### Re-planning Rule

在任一 FR 完成后，可以根据已验证的实现事实调整后续 Slice 的顺序、合并或拆分后续 Slice、Expected Files 和后续 Exit Criteria。

但不得：

- 改变、删除或绕过 Frozen TDD 技术义务；
- 用 Plan 修复 TDD 设计错误；
- 以重新切片替代 TDD Change/Review。

如实现事实证明 Frozen TDD 的 assumption/decision 不成立，必须标记 `TDD IMPACT`，停止受影响的后续 Slice，并回到 TDD Change/Review。

## 4. Implementation Sequence

```text
TDD v1.0.0 Frozen
        ↓
CC-01 Foundation & Core Model
        ↓
FR-CC01 = SATISFIED
        ↓
CC-02 Lifecycle, Integrity & Audit
        ↓
FR-CC02 = SATISFIED
        ↓
CC-03 Security, Web, PDA & Attachment
        ↓
FR-CC03 = SATISFIED
        ↓
Optional CC-04（仅触发时）
        ↓
PVR / PCR
```

本任务只允许下一步生成：

```text
NEXT CONTRACT: CC-01
```

CC-02、CC-03、CC-04 不是本计划中的正式 Coding Contract，须在前一轮 FR 满足后按当时代码事实重新起草。

## 5. PLAN-CC-01 — Foundation & Core Model

### Proposed Coding Contract

`CC-01 — Foundation & Core Model`

### Goal

建立可安装、可加载、可测试的 VAS 数据骨架，完成三类 Warehouse Order 的显式关联路径和操作类型/单位基础能力。

### TDD Scope

- TDD §2、§4：依赖、模块结构；
- TDD §5：`wd.vas.order`、`wd.vas.order.line`、`wd.vas.operation.type`；
- TDD §6：Option A、TD-001；
- TDD §7：Operation Type → Unit、TD-004；
- TDD §9.1：`ORM-DATA-001`、`ORM-DATA-002`；
- TDD §15：`ir.sequence`、TD-009；
- TDD §17：初始安装结构。

### In Scope

- 补齐模块 manifest、Python imports 和模型文件；
- 建立 `wd.vas.operation.type`，直接引用 `world.depot.charge.unit`；
- 建立 `wd.vas.order` 和 `wd.vas.order.line`；
- 建立 `order_type` 与三个显式 Many2one；
- 建立 `warehouse_order_billno` 输入字段、关系字段和提交快照字段的基础结构；
- 建立 `warehouse_id`、Operator、明细单位快照及基础审计元数据使用；
- 建立 `ir.sequence`；
- 建立类型/关系一致性和基础模型约束；
- 仅建立基础 VAS groups 的 XML identity，供模块安装和后续安全依赖使用；本轮不赋予最终业务访问语义，也不完成 ACL/record rule；
- 编写模型、序列、关联和单位映射的基础自动化测试；
- 验证模块可安装和模型可加载。

### Out of Scope

- `action_submit()`、`action_unsubmit()`、`action_cancel()`；
- Submit 时 Warehouse Order 有效性解析和快照写入；
- `FOR UPDATE`、并发保护和 `write()` 状态保护；
- 完整 ACL、record rules 和 action permission；
- Web/PDA 视图、菜单、附件和 chatter UI；
- 计费、绩效、工资、审批、队列、API、Redis 和独立前端；
- 修改 `worlddepot` 或 Odoo 官方源码。

### Expected Files

以下是计划层级预测，不是正式 Coding Contract allowlist：

- `addons/wd_warehouse_value_add/__manifest__.py`
- `addons/wd_warehouse_value_add/__init__.py`
- `addons/wd_warehouse_value_add/models/__init__.py`
- `addons/wd_warehouse_value_add/models/vas_operation_type.py`
- `addons/wd_warehouse_value_add/models/vas_order.py`
- `addons/wd_warehouse_value_add/models/vas_order_line.py`
- `addons/wd_warehouse_value_add/security/security.xml`
- `addons/wd_warehouse_value_add/data/ir_sequence_data.xml`
- `addons/wd_warehouse_value_add/tests/__init__.py`
- `addons/wd_warehouse_value_add/tests/test_vas_order.py`

不强制创建操作类型业务种子；Frozen TDD 要求安装不依赖现场 Charge Item/Unit 记录。

### Dependencies

`None`

### Verification Target

- Automated Test；
- Odoo module install/load smoke check；
- Static protection check：三个 `worlddepot` 既有模型无修改。

### Exit Criteria

- 模块安装成功，Registry 可加载三个 VAS 模型；
- VAS sequence 能生成唯一作业单号；
- 三类 Warehouse Order 的显式 Many2one 数据结构及类型一致性基础已建立，可供 CC-02 的 Submit 解析与正式绑定使用；
- Operation Type 可直接引用 Charge Unit，明细单位可形成快照；
- 基础模型测试通过；
- Draft 数据骨架可保存，包括零明细；
- 没有修改受保护模型、Frozen SRS 或 Frozen TDD。

### FR Expectation

`FR-CC01 = SATISFIED` 应证明：VAS 核心模型已安装并具备稳定的数据骨架，三类 Warehouse Order、操作类型、单位和基础序列均可被后续生命周期切片安全使用。此处不证明 Draft 已正式绑定 Warehouse Order；正式解析、绑定和快照由 CC-02 完成。

### Risks

- 当前模块骨架中的 manifest/data 仍可能与实际文件布局不一致；
- 三个既有模型字段差异必须限制在显式关系映射内；
- 基础约束不得提前阻止 Draft 不完整数据。

## 6. PLAN-CC-02 — Lifecycle, Integrity & Audit

### Proposed Coding Contract

`CC-02 — Lifecycle, Integrity & Audit`

### Goal

把 VAS 的正式业务出口做硬：提交、反提交、作废、订单校验、快照、服务端不可变性和审计并发形成闭环。

### TDD Scope

- TDD §5：快照字段和审计字段；
- TDD §6、§7：关联解析、订单校验；
- TDD §8：三项 Business Action、TD-002/003；
- TDD §9：Python/action validation；
- TDD §10：tracking 和动作审计、TD-007；
- TDD §16：VAS action 的行锁、锁后重读和 TD-008；
- TDD §18：生命周期、验证、审计和并发测试。

### In Scope

- 实现 `action_submit()`、`action_unsubmit()`、`action_cancel()`；
- Submit 只允许 Draft，校验 Operator、明细、数量/工时和操作类型；
- 按 Order Type + 精确 `billno` 解析三类 Warehouse Order；
- 零条、多条、错误类型和 cancelled 目标显式阻断；
- Submit 时写入 Many2one、`billno` snapshot 和 `warehouse_id` snapshot；
- 记录 submitter/submitted_at、unsubmit 和 cancel 审计；
- 使用 `mail.thread` tracking；
- 对 VAS action 使用最小 `FOR UPDATE`，固定按 `VAS Order → Warehouse Order` 取得本模块所需锁，并在每次加锁后重读状态；
- 基于既有 `worlddepot` Warehouse Order Cancel 的实际源码/运行行为验证 Submit 与 Cancel 并发的 TOCTOU 风险；不得假定受保护模型遵守 VAS 锁协议；
- 在 `write()` 服务端保护 Submitted/Cancelled 核心字段；
- 编写状态、校验、快照、审计和并发自动化测试。

### Out of Scope

- ACL、record rule、菜单和完整 UI；
- PDA 交互和真实设备验收；
- 附件 UI/上传；
- 新人员—仓库授权模型；
- 修改既有 Warehouse Order；
- 直接 SQL 业务写入、队列、外部 API 或复杂锁框架。

### Expected Files

- `addons/wd_warehouse_value_add/models/vas_order.py`
- `addons/wd_warehouse_value_add/models/vas_order_line.py`
- `addons/wd_warehouse_value_add/tests/test_vas_order.py`
- `addons/wd_warehouse_value_add/tests/test_vas_concurrency.py`

### Dependencies

`FR-CC01 = SATISFIED`

### Verification Target

- Automated Test；
- ORM integration test；
- Two-cursor concurrency test；
- Failure-path transaction test。

### Exit Criteria

- Draft → Submitted、Submitted → Draft、Draft → Cancelled 均按 TDD 工作；
- Submitted → Cancelled、Cancelled → Draft 和直接修改锁定数据均失败；
- Draft 零行可保存，Submit 零行失败；
- 无效/多结果/cancelled Warehouse Order 在 Submit 阻断；
- 三类关系、`billno` snapshot 和 warehouse snapshot 正确写入；
- 重复 Submit/Unsubmit 的当前字段和 chatter 结果正确；
- 并发测试证明后取得 VAS 行锁的一方重读 state 后失败；
- 受保护模型和 TDD/SRS 未被修改。

### FR Expectation

`FR-CC02 = SATISFIED` 应证明：核心业务生命周期、提交完整性、订单关联、快照、不可变性、审计和并发状态转换已形成可验证的服务端闭环。若既有 Warehouse Order Cancel 行为无法满足 Frozen TDD 的并发要求，不得修改受保护模型，必须报告 `BLOCKER / TDD IMPACT`，并停止受影响后续 Slice。

### Risks

- Odoo cursor/cache 在锁后必须显式失效并重新读取；
- VAS `action_submit()` 本身必须固定按 `VAS Order → Warehouse Order` 取得锁；不得要求受保护的 Warehouse Order Cancel action 遵守该协议，须先基于既有行为验证并发风险；
- 异常路径不能留下半提交审计或部分快照。

## 7. PLAN-CC-03 — Security, Web, PDA & Attachment

### Proposed Coding Contract

`CC-03 — Security, Web, PDA & Attachment`

### Goal

让已经具备核心业务能力的 VAS 成为可授权、可查询、可在 Web/PDA 使用并可上传附件的完整用户功能。

### TDD Scope

- TDD §4：视图、安全和菜单文件；
- TDD §11：groups、ACL、record rules、action permission、TD-010；
- TDD §12：Web list/form/search/menu；
- TDD §13：标准 Web PDA 交互；
- TDD §14：原生附件；
- TDD §18：安全、附件和 UI/integration test；
- TDD §19：ROLE/NFR/AC 的最终界面落点。

### In Scope

- 完成 `group_vas_user`、`group_vas_manager` ACL 和 record rules；
- 使用 `create_uid = user.id` 实现仓管员自建记录可见性；
- 实现主管全量查看和服务端 action permission；
- 实现操作类型配置视图；
- 实现 VAS list/form/search/menu/action；
- 按状态提供 Draft 编辑、Submitted 只读+Unsubmit、Cancelled 只读；
- 提供小屏 x2many kanban 路径和最小移动字段顺序；
- 允许键盘式扫码输入 billno；
- 实现 `attachment_ids`、标准 `many2many_binary` 和 chatter；
- 编写安全、附件和必要的 Web/integration 自动化测试；
- 进行 Odoo 浏览器层面的核心页面验证（不替代真实 PDA HVR）。

### Out of Scope

- 独立 PDA App、SPA、OWL 专用前端或 PDA API；
- 真实扫码枪、移动浏览器、相机入口的最终验收；
- 新的 Warehouse ↔ Operator 授权模型；
- 自定义附件存储、对象存储、附件配置子系统；
- 计费、绩效、工资、审批、客户 Portal；
- Optional CC-04 hardening。

### Expected Files

- `addons/wd_warehouse_value_add/security/security.xml`
- `addons/wd_warehouse_value_add/security/ir.model.access.csv`
- `addons/wd_warehouse_value_add/views/vas_operation_type_views.xml`
- `addons/wd_warehouse_value_add/views/vas_order_views.xml`
- `addons/wd_warehouse_value_add/views/vas_menus.xml`
- `addons/wd_warehouse_value_add/tests/test_vas_security.py`
- `addons/wd_warehouse_value_add/tests/test_vas_attachment.py`

### Dependencies

`FR-CC02 = SATISFIED`

### Verification Target

- Automated Test；
- Odoo ORM/security integration test；
- Web form/list/search smoke verification；
- Post-implementation Human Verification：真实 PDA、扫码枪、相机/上传体验（仅当验证权威将其标记为本轮 Mandatory/Applicable）。

Coding Closure 不等待后续 HVR，除非 Coding Contract 或 Frozen TDD 明确将该 HVR 标记为本轮 Mandatory/Applicable。若 HVR 属于项目验收阶段的后续验证义务，则不作为 `FR-CC03` 已完成事实，由 PVR/HVR 收集最终证据。

### Exit Criteria

- 仓管员只能查看自己 `create_uid` 创建的记录，主管可查看全部；
- 未授权用户不能通过隐藏按钮或 RPC 直接执行动作；
- Web list/form/search/menu/action 可用；
- Draft/Submitted/Cancelled UI 状态与服务端保护一致；
- 多图片/视频附件可通过原生能力关联、查看和删除（仅允许的状态）；
- 必要自动化测试通过；
- 真实 PDA 体验被明确移交 HVR，不被宣称为自动化测试完成；
- 受保护模型、Frozen SRS/TDD 未被修改。

### FR Expectation

`FR-CC03 = SATISFIED` 应证明：角色隔离、主管范围、标准 Web/PDA 业务入口、查询、状态 UI、原生附件和审计展示已完成 Coding Closure。真实 PDA/扫码/上传体验仅在被标记为本轮 Mandatory/Applicable 时纳入本 FR，否则由后续 PVR/HVR 提供验收证据。

### Risks

- Odoo record rule 与 action method 必须双重保护；
- `ir.attachment` 访问权限必须随业务记录权限一致；
- 小屏 x2many 交互和真实扫码输入仍需 HVR。

## 8. Optional PLAN-CC-04 Trigger

默认状态：

```text
NOT PLANNED
```

只有满足下列至少一项，才在 `FR-CC03 = SATISFIED` 后重新建立 CC-04：

- CC-01~03 产生无法安全并入原 Slice 的跨层缺陷；
- Frozen TDD 中存在尚未落地的集成义务；
- 自动化测试暴露必须单独处理的跨模块一致性问题；
- 安装、升级或真实环境 hardening 需要独立变更边界；
- FR/PVR 明确发现必须独立修复且不适合回补当前 Slice。

CC-04 如触发，必须重新定义 Expected Files、Dependencies、Exit Criteria 和 FR；不得现在预先生成合同。

## 9. TDD-to-Slice Coverage

| TDD Area / TD | Coding Slice |
|---|---|
| §2 Technical Baseline / §4 Module Structure | CC-01 |
| §5 Data Model | CC-01；生命周期字段由 CC-02 完成 |
| §6 Association / TD-001 | CC-01 基础关系；CC-02 解析和绑定 |
| §7 Operation Type / TD-004 | CC-01 |
| §8 State Machine / TD-002/003 | CC-02 |
| §9 Validation & Invariants | CC-01 基础约束；CC-02 action validation |
| §10 Audit & Tracking / TD-007 | CC-02 |
| §11 Security / TD-010 | CC-03 |
| §12 Web UI | CC-03 |
| §13 PDA/Mobile UI / TD-005 | CC-03；真实设备 HVR |
| §14 Attachment / TD-006 | CC-03 |
| §15 Sequence & Master Data / TD-009 | CC-01；业务主数据配置由 CC-03 提供 |
| §16 Transaction & Concurrency / TD-008 | CC-02 |
| §17 Install / Upgrade | CC-01 安装；CC-04 仅在升级 hardening 触发时 |
| §18 Test Design | CC-01/02/03 按各自行为范围 |
| §19 Requirement Traceability | CC-01/02/03 的 FR 逐轮核对 |
| §20 Technical Decision Register | CC-01/02/03 按决策落点实施 |
| §21 Open Questions / Risks | TQ-001 已解决；TQ-002/003 由 CC-03 后 HVR；TQ-004 Release/Operations |
| §22 TDD Freeze Readiness | 已冻结，不属于实施变更 |

Unassigned items：

```text
None
```

## 10. Dependencies & Gates

| Gate | 前置 | 通过条件 | 未通过处理 |
|---|---|---|---|
| CC-01 start | TDD Frozen | 当前计划已明确、无 CC-01 blocker | 不生成合同，先记录 PLAN BLOCKER |
| CC-02 start | `FR-CC01 = SATISFIED` | CC-01 合并且验证事实可复用 | 停止，不机械进入 CC-02 |
| CC-03 start | `FR-CC02 = SATISFIED` | 生命周期/并发/审计闭环通过 | 停止并修复当前 Slice |
| Optional CC-04 | `FR-CC03 = SATISFIED` + 触发条件 | 形成独立 hardening 范围 | 默认不创建 |
| PVR | 所需 FR 完成 | 事实验证记录完整 | 回到对应 Slice/FR |

每轮 FR 必须独立记录 `SATISFIED`、`NOT SATISFIED` 或 `BLOCKED`；后续合同不得假设未验证的实现细节。

## 11. Risks / Plan Blockers

当前 Plan Blockers：

```text
None
```

当前风险不阻塞 CC-01：

- CC-01 只依赖已冻结 TDD、现有模块骨架和 `worlddepot` 已验证模型；
- Operator 范围已由 Human Decision 冻结，不需要新增人员—仓库模型；
- PostgreSQL 生产版本、真实 PDA 和视频体验属于后续 Release/HVR，不阻止实施计划启动。

受保护范围（所有 Slice 继承）：

- 不修改 Odoo 官方源码；
- 不修改三个既有 Warehouse Order 模型或 Charge Item/Unit 模型；
- 不将 VAS 改绑 `stock.picking`；
- 不创建 Warehouse Order 抽象层、独立 PDA App、SPA、第三方前端、Redis、queue、事件总线或独立 API；
- 不创建自定义 Audit Framework 或附件存储；
- 不引入计费、绩效、工资、审批；
- 不改变 Frozen TDD 状态机；
- 不绕过 Business Action 直接写状态；
- 不直接 SQL 写业务数据；Frozen TDD 批准的 SQL 仅限参数化 row lock。

## 12. Next Action

下一步只做一件事：

```text
NEXT CONTRACT: CC-01
```

CC-01 正式 Coding Contract 必须在当前代码事实基础上重新确认实际 allowlist、测试选择、禁止修改文件和变更边界。不得在本计划中起草 CC-02、CC-03 或 CC-04。

## 13. Plan Approval Record

```text
Plan Version: v1.0
Plan Status: APPROVED EXECUTION BASELINE
Approval Decision: Human Final Review after directed corrections
Current Gate: READY TO DRAFT CC-01
```

本基线只表示当前批准的实施顺序、切片边界、依赖和 Gate；后续实现事实仍须遵守 Re-planning Rule，可在 FR 后调整后续计划，但不能借 Plan 修改 Frozen SRS/TDD。

## 14. Plan Gate

```text
READY TO DRAFT CC-01
```

理由：

1. Frozen TDD 已存在且状态为 `v1.0.0 Frozen`；
2. CC-01 的目标、范围、依赖、文件预测和 Exit Criteria 明确；
3. 当前没有影响第一轮实施的未决问题；
4. Frozen TDD 的所有实现义务均已分配到 CC-01、CC-02 或 CC-03；
5. 没有提前生成任何正式 Coding Contract；
6. CC-04 保持默认未计划，仅定义触发条件。
