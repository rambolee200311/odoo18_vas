# Coding Contract — CC-WAREHOUSE-VAS-01

## 0. 文档治理

### 0.1 目的

本 Coding Contract（CC）冻结 Warehouse VAS Foundation & Core Model 这一轮的执行边界：允许修改什么、必须实现什么、禁止实现什么，以及什么证据才能关闭本轮。

### 0.2 核心原则

- 不重新发明 Frozen SRS、Frozen TDD 或 Implementation Plan；
- 只授权本轮 CC-01；
- Plan 是预测，CC 是授权；
- Draft 可保存不完整输入，正式出口留给 CC-02；
- Odoo Native First、Simple Models、Explicit Business Logic、Robust Before Clever；
- 边界外发现必须停止并升级，不得自行补设计。

### 0.3 上游基线

- SRS：冻结业务事实；
- DDD：本项目 SKIP；
- TDD：冻结技术方案；
- Implementation Plan：当前已批准的实施顺序和 Slice 规划基线；不是 Frozen Authority，可在 FR 后根据已验证实现事实重新规划，但不得改变 Frozen SRS/TDD；
- 本文：冻结本次实现授权。

### 0.4 编号体系

本 CC 只使用模板规定的自有编号：

- `CC-CHANGE-*`：本次变更项；
- `CC-PRESERVE-*`：必须保留的既有行为；
- `CC-TEST-*`：本次测试契约项；
- `CC-DEC-*`：本次实现级决策。

SRS、TDD 和 TEST 编号直接引用上游 ID，不另造上游编号。

### 0.5 冻结规则

进入上述编号体系的内容均为本 CC 的执行契约。Human Review 批准前不得执行；批准后不得由 Implementation Agent 静默扩大或改变。本版本已完成 Human Review，正式进入 Frozen 状态。

## 1. 变更概述

| 字段 | 值 |
|---|---|
| Intent ID | `CC-WAREHOUSE-VAS-01` |
| 模块 | `wd_warehouse_value_add` |
| 工作类型 | 新功能 |
| 变更类型 | 结构变更 / 基础模型建设 |
| 目标 | 建立可安装、可加载、可测试的 Warehouse VAS 核心数据骨架 |
| 背景 | Frozen TDD 已确定 VAS 模型、显式 Warehouse Order 关系、单位快照和 sequence；当前模块仍只有骨架，需先完成基础模型后才能进入 CC-02 |

本轮不实现正式 Submit binding、生命周期、安全语义、UI、附件体验或并发控制。

## 2. 上游基线与追溯

### 2.1 SRS 引用

| SRS ID | 标题/内容 | 与本次 CC 的相关性 |
|---|---|---|
| `FR-VAS-01` | VAS 作业单创建和编号 | 在范围内：基础单据和 sequence |
| `FR-VAS-02` | 多明细和单位 | 在范围内：明细结构和 Draft 零行 |
| `FR-VAS-03` | Warehouse Order 关联 | 部分：只建立结构，不实现 Submit binding |
| `BR-VAS-01` | Creator/Operator/Submitter 区分 | 部分：建立结构字段，不实现权限 |
| `BR-VAS-02` | Draft 可暂存不完整数据 | 在范围内：Draft persistence |
| `BR-VAS-09` | 操作类型带出计量单位 | 在范围内：Operation Type → Charge Unit |
| `AC-01` | 可创建 VAS 单据 | 在范围内：模型/sequence |
| `AC-02` | Creator/Operator 结构 | 部分：模型字段 |
| `AC-22` | 操作类型与单位 | 在范围内：基础单位快照 |
| `AC-23` | Draft 可保存零明细 | 在范围内：模型测试 |

未在本次 Scope 声明的 SRS ID 不因本 CC 获得实施授权。

### 2.2 DDD 引用

N/A。项目已明确 DDD SKIP，仅执行：

```text
SRS → TDD → CC → TEST
```

不得虚构 AGG、ENT、INV、DS、DV 或 DD 编号。

### 2.3 TDD 引用

| TDD ID / 章节 | 标题/内容 | 相关性 |
|---|---|---|
| TDD §4 | Module Structure / dependencies | 在范围内 |
| TDD §5.1 | `wd.vas.order` | 在范围内：结构字段 |
| TDD §5.2 | `wd.vas.order.line` | 在范围内：结构字段 |
| TDD §5.3 | `wd.vas.operation.type` | 在范围内 |
| TDD §6 / `TD-001` | 三个显式 Many2one | 在范围内：关系结构 |
| TDD §7 / `TD-004` | Operation Type → Charge Unit / 单位快照 | 在范围内 |
| `ORM-DATA-001` | Operation Type code 唯一 | 在范围内 |
| `ORM-DATA-002` | VAS order name 唯一 | 在范围内 |
| TDD §15 / `TD-009` | `ir.sequence` | 在范围内 |
| TDD §17 | 初始安装结构 | 在范围内 |
| TDD §18 | `TEST-MODEL-001/002/003` | 在范围内 |

`TD-002`、`TD-003`、`TD-005`、`TD-006`、`TD-007`、`TD-008`、`TD-010` 的完整行为不属于本轮；仅在需要保持字段结构时作为上下文引用。

### 2.4 Bug Report / 事件报告

N/A。本轮不是 Bug Fix；不存在以 Issue 或生产事件改变业务语义的授权。

### 2.5 追溯规则

本 CC 新增的行为必须追溯到 §2.1 的 SRS 或 §2.3 的 TDD。仅有实现级局部决策可记录在附录 A 的 `CC-DEC`，且不得改变上游语义、技术边界或本轮 Scope。

## 3. 范围冻结

### 3.1 在范围内

- `CC-CHANGE-001`：模块 manifest/import 和 CC-01 文件加载；
- `CC-CHANGE-002`：`wd.vas.operation.type` 基础模型；
- `CC-CHANGE-003`：`wd.vas.order` 基础模型；
- `CC-CHANGE-004`：`wd.vas.order.line` 基础模型；
- `CC-CHANGE-005`：三个 Warehouse Order 显式 Many2one 关系结构；
- `CC-CHANGE-006`：`wd.vas.order` sequence；
- `CC-CHANGE-007`：基础 structural constraints；
- `CC-CHANGE-008`：基础 VAS group XML identity；
- `CC-CHANGE-009`：CC-01 基础自动化测试。

### 3.2 超出范围

- CC-02 的 Submit/Unsubmit/Cancel 和所有正式状态动作；
- Submit-time Warehouse Order resolution、binding、billno/warehouse snapshot；
- `FOR UPDATE`、lock timeout、并发行为和自定义 SQL；
- 最终 ACL、record rules、action permission；
- Web/PDA views、scan UX、附件 UI、chatter UI；
- 计费、Charge Item、价格、绩效、工资、审批、API、queue、Redis、SPA 和独立 PDA；
- 修改 Odoo 官方源码或既有 `worlddepot` 模型。

### 3.3 非目标

- 不完成 Warehouse VAS；
- 不提供用户可用的完整业务入口；
- 不验证真实 PDA、扫码枪、相机或移动浏览器；
- 不解决 Warehouse Order Cancel 的并发协议；
- 不为操作类型创建依赖现场数据的强制业务种子；
- 不创建 service、adapter、repository、抽象 Warehouse Order 层或自定义 framework。

### 3.4 仅限范围的追溯规则

§3.1 每个纳入的 `CC-CHANGE` 必须在 §5、§11 和 §14 中有对应实现与验证。未纳入本轮的上游需求不因本 CC 自动获得授权。

## 4. 变更边界

### 4.1 允许

| 类型 | 详情 |
|---|---|
| 文件 | `addons/wd_warehouse_value_add/__manifest__.py` |
| 文件 | `addons/wd_warehouse_value_add/__init__.py` |
| 文件 | `addons/wd_warehouse_value_add/models/__init__.py` |
| 新增文件 | `addons/wd_warehouse_value_add/models/vas_operation_type.py` |
| 新增文件 | `addons/wd_warehouse_value_add/models/vas_order.py` |
| 新增文件 | `addons/wd_warehouse_value_add/models/vas_order_line.py` |
| 新增文件 | `addons/wd_warehouse_value_add/security/security.xml` |
| 新增文件 | `addons/wd_warehouse_value_add/data/ir_sequence_data.xml` |
| 新增文件 | `addons/wd_warehouse_value_add/tests/__init__.py` |
| 新增文件 | `addons/wd_warehouse_value_add/tests/test_vas_order.py` |
| 模型 | `wd.vas.operation.type`、`wd.vas.order`、`wd.vas.order.line` |
| 字段 | Frozen TDD §5 定义的 CC-01 结构字段 |
| 方法 | 仅基础 `create`/onchange/compute/constraint 所需实现；不得创建 Business Action |
| XML | CC-01 sequence 和 group identity |

边界精度以本表和 §3.1 `CC-CHANGE` 为准，实际执行不得扩大到其他文件。

### 4.2 禁止

| 类型 | 详情 |
|---|---|
| 状态枚举 | 不得改变 Frozen TDD 的 `draft/submitted/cancelled` |
| 业务动作 | 不得新增或实现 Submit/Unsubmit/Cancel |
| 其他模块 | 不得修改 `worlddepot`、Odoo 官方源码或无关模块 |
| SQL | CC-01 不授权任何自定义 SQL |
| 安全语义 | 不得实现 ACL、record rules、action permission |
| 用户入口 | 不得创建 view、menu、PDA app、SPA、API |
| 关系权威 | 不得使用 `Reference`、裸 billno 跨模型搜索或新抽象层 |
| 领域边界 | 不得引入 Charge Item、计费、价格、绩效或工资 |

## 5. 必需的行为变更

| ID | 当前行为 | 期望行为 | CC-CHANGE ID |
|---|---|---|---|
| 1 | 模块只有骨架且 manifest 引用尚不存在的未来文件 | 模块可按 CC-01 文件集合加载 | `CC-CHANGE-001` |
| 2 | VAS Operation Type 模型不存在 | 创建 name/code/unit/active/sequence，并直接引用 Charge Unit | `CC-CHANGE-002` |
| 3 | VAS Order 模型不存在 | 创建 Frozen TDD §5.1 的结构字段和 `mail.thread` 结构 | `CC-CHANGE-003` |
| 4 | VAS Order Line 模型不存在 | 创建 order/operation/quantity/unit snapshot/note 结构 | `CC-CHANGE-004` |
| 5 | VAS Order 尚不存在 Warehouse Order 关联结构 | 在 `wd.vas.order` 上创建三个显式 Many2one 和基础类型一致性结构 | `CC-CHANGE-005` |
| 6 | 没有 VAS 编号生成 | 使用 code `wd.vas.order` 的 Odoo `ir.sequence` | `CC-CHANGE-006` |
| 7 | 没有基础模型完整性 | 实现两个唯一约束和基础关系/单位一致性 | `CC-CHANGE-007` |
| 8 | 没有 VAS group identity | 仅创建 `group_vas_user`、`group_vas_manager` identity | `CC-CHANGE-008` |
| 9 | 没有 VAS 基础测试 | 创建并执行 CC-01 模型、Draft、sequence 和单位测试 | `CC-CHANGE-009` |

这些变更不包括正式 Submit 解析、绑定、快照或状态动作。

## 6. 必须保持的上游/既有行为

| ID | 行为 / 契约 | 为什么不得改变 | CC-PRESERVE ID |
|---|---|---|---|
| 1 | 三个既有 Warehouse Order 技术模型及其 `billno`、`warehouse`、`state` 字段 | Frozen TV/TDD 依赖既有模型事实 | `CC-PRESERVE-001` |
| 2 | 既有 Warehouse Order 状态 `new/confirm/cancel` | 不得与 VAS 状态混淆 | `CC-PRESERVE-002` |
| 3 | `world.depot.charge.unit` 的 `name`/`description` 模型 | VAS 只复用 Unit，不改变主数据 | `CC-PRESERVE-003` |
| 4 | 既有 `worlddepot` sequence、security、views 和业务行为 | 本轮只新增 VAS，不回归既有模块 | `CC-PRESERVE-004` |
| 5 | Draft 可保存零明细、零数量/工时 | Frozen TDD §9.2 和 SRS Draft 原则 | `CC-PRESERVE-005` |
| 6 | `create_uid/create_date` 作为 Creator 审计来源 | Odoo Native First，禁止 `creator_id` 重复字段 | `CC-PRESERVE-006` |

## 7. 适用的 TDD 防护栏（裁剪，不复制）

Frozen TDD 没有单独的 `T-xxx` 防护栏编号；本轮引用其实际技术决策和约束：

| TDD 防护栏 / 决策 | 适用性 | 本次落实位置 | 验证方式 |
|---|---|---|---|
| `TD-001` 三个显式 Many2one | 适用 | `CC-CHANGE-005` | `CC-TEST-004` |
| `TD-004` Operation Type 直接引用 Unit | 适用 | `CC-CHANGE-002/004` | `TEST-MODEL-003` |
| `TD-009` Odoo sequence | 适用 | `CC-CHANGE-006` | `TEST-MODEL-001` |
| TDD §9.2 Draft 不完整原则 | 适用 | `CC-CHANGE-003/004/007` | `TEST-MODEL-002` |
| `TD-008` row lock | 本轮不适用 | CC-01 不实现 | CC-02 |
| `TD-010` Operator group/active 校验 | 本轮不适用 | CC-01 只建字段结构 | CC-03 |

Guardrail 正文归属 Frozen TDD，本 CC 不复制或改写其规范性正文。

## 8. 数据 / 迁移影响

| 字段 | 值 |
|---|---|
| 需要迁移 | 否 |
| 迁移脚本 | N/A |
| 数据源 | N/A；无 VAS 历史数据 |
| 目标 | 新建 VAS 表结构 |
| 恢复 / 回滚策略 | 本轮为新模块；失败时停止并由人工按 Git 变更回滚，不执行破坏性数据迁移 |
| 验证 | module install/load、模型注册和基础自动化测试 |

不得修改既有 Warehouse Order 数据或执行业务数据 SQL。

## 9. API / 集成影响

| 字段 | 值 |
|---|---|
| 修改的端点 | N/A |
| 向后兼容 | 是；本轮无外部 API |
| Adapter 变更 | N/A |

## 10. 安全 / 权限影响

| 字段 | 值 |
|---|---|
| 新权限 | 仅可创建 `group_vas_user` / `group_vas_manager` XML identity |
| 变更的 ACL | N/A；最终 ACL 属于 CC-03 |
| 敏感数据暴露检查 | 不适用；本轮不输出 SQL、令牌、凭据或本地路径到用户业务界面 |

本轮不得把 group identity 误认为最终授权，也不得实现 record rule 或 action permission。

## 11. 测试契约

| 测试 ID | 对应变更 | 上游来源 | 测试类型 | 预期结果 | 人工验证 | 原因 |
|---|---|---|---|---|---|---|
| `CC-TEST-001` / `TEST-MODEL-001` | sequence 和 Draft 创建 | `FR-VAS-01`、`AC-01`、`TD-009` | Odoo TransactionCase | 生成唯一 VAS name，初始 state 为 draft | 否 | 核心模型基础 |
| `CC-TEST-002` / `TEST-MODEL-002` | Draft 零明细 | `FR-VAS-02`、`BR-VAS-02`、`AC-23` | Odoo TransactionCase | 零行 Draft 保存成功 | 否 | 防止 Draft 被 Submit 规则污染 |
| `CC-TEST-003` / `TEST-MODEL-003` | Operation Type → Unit | `BR-VAS-09`、`AC-22`、`TD-004` | Odoo TransactionCase | 行单位形成持久化快照，直接引用 Charge Unit | 否 | 验证计量结构 |
| `CC-TEST-004` | 三个显式 relation 结构 | `FR-VAS-03`、`TD-001` | Odoo TransactionCase | 三个 comodel 和 order_type 结构正确；不执行 Submit binding | 否 | 防止引入 Reference/抽象层 |
| `CC-TEST-005` | 基础唯一约束 | `ORM-DATA-001/002` | Odoo TransactionCase | 重复 code/name 被阻断 | 否 | 验证基础完整性 |
| `CC-TEST-006` | 负向 Draft 边界 | `TDD §9.2`、`AC-23` | Odoo TransactionCase | 无效目标订单、零数量/工时不会被 CC-01 的 Submit 规则提前阻断 | 否 | 防止越界实现 |

### Smoke / Installation Verification

- 当前仓库 `addons_path` 被显式指定；
- 模块首次安装成功；
- Registry 加载三个 VAS 模型；
- sequence XML 和 group identity XML 可加载；
- manifest 不再引用 CC-01 未授权的缺失文件。

### Deferred Verification

不得把以下内容标记为本轮已验证：

- CC-02：正式生命周期、Submit binding/snapshot、审计、不可变性、并发；
- CC-03：ACL、record rules、Web/PDA、附件、chatter；
- HVR/PVR：真实 PDA、扫码、相机/上传和项目验收。

## 12. 停止条件 / 升级闸门

| ID | 触发条件 | 升级路径 |
|---|---|---|
| 1 | Frozen SRS 与 Frozen TDD 冲突 | → TDD/SRS Review |
| 2 | 需要新增 Frozen TDD 未定义的核心模型或字段语义 | → TDD 修订 |
| 3 | 需要修改 `worlddepot` 或 Odoo 官方源码 | → 停止并人工决定 |
| 4 | 需要提前实现 Submit、状态动作、最终安全或并发 | → CC-01 修订或下一 CC |
| 5 | 需要自定义 SQL、锁、queue、API 或新架构 | → TDD/CC 修订 |
| 6 | manifest/dependency 无法使本轮安全安装 | → CONTRACT BLOCKER |
| 7 | 实际文件超出 §4 allowlist | → CC 修订 |
| 8 | Frozen TDD assumption/decision 被实现事实证明不成立 | → `TDD IMPACT`，停止受影响 Slice |
| 9 | Implementation 开始前，批准时 Baseline 与当前 `HEAD`、`git status --short`、allowlist 文件状态或 protected/pre-existing changes 不一致，且差异不是已记录的 pre-existing changes | → `STOP`；记录 `CONTRACT BASELINE DRIFT`，等待 Human re-baseline |

绝对禁止为了让代码运行而自行补一个设计。出现触发条件时必须记录事实、受影响 Authority、受影响 obligation、阻塞原因和所需 Human/TDD 决策。

## 13. 完成定义 / 关闭标准

本节是未来实施关闭标准，不是执行结果。IHR/ATR 负责提供证据，FR-CC01 负责最终判断。

| ID | 标准 | 闸门类型 |
|---|---|---|
| 1 | 所有 `CC-CHANGE-001` 至 `CC-CHANGE-009` 均有对应实现 | 硬闸门 |
| 2 | 未违反任何禁止区域和 Protected Scope | 硬闸门 |
| 3 | `CC-TEST-001` 至 `CC-TEST-006` 及适用上游 TEST 通过 | 硬闸门 |
| 4 | `CC-PRESERVE-001` 至 `CC-PRESERVE-006` 未改变 | 硬闸门 |
| 5 | module install/load 验证通过 | 硬闸门 |
| 6 | Draft 零明细及 Draft 不完整原则保持 | 硬闸门 |
| 7 | 没有 CC-02/CC-03 行为被提前实现 | 硬闸门 |
| 8 | IHR 已记录文件、模型、constraints、sequence、命令和结果 | 硬闸门 |

本轮不要求 HVR；真实 PDA 体验属于后续验证。

## 14. 追溯矩阵

### 14.1 正向：In-Scope 上游 → CC

| 上游 ID | CC-CHANGE ID | 备注 |
|---|---|---|
| `FR-VAS-01` / `AC-01` | `CC-CHANGE-001/006` | 模块和 sequence |
| `FR-VAS-02` / `AC-23` | `CC-CHANGE-004/007` | 明细和 Draft 零行 |
| `FR-VAS-03` | `CC-CHANGE-005` | 仅关系结构 |
| `BR-VAS-01` | `CC-CHANGE-003` | Creator/Operator/Submitter 结构 |
| `BR-VAS-02` | `CC-CHANGE-003/004/007` | Draft persistence |
| `BR-VAS-09` / `AC-22` | `CC-CHANGE-002/004` | 单位结构 |
| `TD-001` | `CC-CHANGE-005` | 显式 Many2one |
| `TD-004` | `CC-CHANGE-002/004` | Charge Unit 和快照 |
| `TD-009` | `CC-CHANGE-006` | Odoo sequence |
| `ORM-DATA-001/002` | `CC-CHANGE-007` | 基础唯一约束 |

### 14.2 反向：CC → 上游

| CC ID | 上游 ID | 类型 |
|---|---|---|
| `CC-CHANGE-001` | TDD §4/§17 | TDD |
| `CC-CHANGE-002` | TDD §5.3/§7、`TD-004` | TDD |
| `CC-CHANGE-003` | TDD §5.1 | TDD |
| `CC-CHANGE-004` | TDD §5.2/§7 | TDD |
| `CC-CHANGE-005` | TDD §6、`TD-001` | TDD |
| `CC-CHANGE-006` | TDD §15、`TD-009` | TDD |
| `CC-CHANGE-007` | `ORM-DATA-001/002`、TDD §9.2 | TDD |
| `CC-CHANGE-008` | TDD §11 | TDD |
| `CC-CHANGE-009` | TDD §18、`TEST-MODEL-001/002/003` | TDD |

### 14.3 无 DDD 路径

```text
SRS → TDD → CC → TEST
```

DDD：N/A。

## 附录 A — 变更决策（CC-DEC）

| CC-DEC ID | 决策 | 考虑的替代方案 | 理由 |
|---|---|---|---|
| `CC-DEC-001` | 本轮 manifest 只加载 CC-01 授权文件 | 保留所有未来 view/data 引用 | 当前候选文件不存在，保留会阻止基础模块安装 |
| `CC-DEC-002` | 不创建操作类型业务种子 | 在 CC-01 强制创建收费单位/操作类型 seed | Frozen TDD 不要求种子，避免依赖现场主数据 |
| `CC-DEC-003` | 只创建 group XML identity，不实现 ACL | 提前完成权限 | 最终安全语义属于 CC-03 |
| `CC-DEC-004` | Draft relation 字段允许为空，测试只验证结构 | Draft 时强制 Many2one binding | Frozen TDD 将正式 resolution/binding 放在 Submit/CC-02 |

以上均为实现级边界决策，不改变 Frozen SRS/TDD。

## 附录 B — 实现证据要求（IHR）

未来 Implementation Agent 必须记录：

- 实际创建和修改的文件；
- 创建的三个模型、字段和 comodel；
- 基础 constraints 的位置和语义；
- sequence XML、code、prefix、padding 和加载结果；
- 测试文件、测试 ID 和实际命令；
- module install/load 结果；
- `git diff --stat`、protected-file 检查和工作树状态；
- §10 的 pre-existing changes 未被修改或提交的证据；
- 与本 CC 的偏差和 unresolved findings；
- 若触发停止条件，记录 CONTRACT BLOCKER/TDD IMPACT。

本阶段不得创建 IHR。

## 附录 C — 仓库事实

### Current Git Baseline

- 分支：`main`；
- HEAD：`79458d3 Add frozen Warehouse VAS design plan`；
- 远程：`origin` → `git@github.com:rambolee200311/odoo18_vas.git`。

### Current Working Tree Status

```text
M docs/context/Designing/SRS.md
?? docs/context/verification/
?? docs/context/coding_contract/cc_warehouse_vas_01.md
```

合同文件是本次起草产生的新文件。当前 SRS 存在工作树修改，因此 Human Approval 前必须唯一化 Frozen SRS Authority：将当前 working-tree SRS 作为最终 Frozen SRS 提交并更新 CC Baseline；在此之前不得开始 Implementation。`docs/context/verification/` 和本合同文件仍不得纳入 CC-01 实现变更。批准后如发现 Baseline 漂移，适用 §12 的 `CONTRACT BASELINE DRIFT` 停止条件。

### 已检查的依赖事实

- VAS 模块当前只有 `__init__.py`、`__manifest__.py` 和 `models/__init__.py`；
- `world.depot.inbound.order`、`world.depot.outbound.order`、`world.depot.transfer.order` 均提供 `billno`、`warehouse`、`state`；
- `world.depot.charge.unit` 技术名称和基础字段已核对；
- 既有模块使用 XML `ir.sequence`；
- 当前仓库无可直接复用的业务模块 tests 目录；
- `odoo-bin`、`venv/bin/python3` 和已有执行脚本存在；
- `odoo.conf` 默认 `addons_path` 指向其他本地路径，测试时必须显式指定当前仓库路径。

## 附录 D — 版本历史

| 版本 | 日期 | 变更说明 | 状态 |
|---|---|---|---|
| v0.1 | 2026-09-04 | 按 Implementation Plan 起草 CC-01 | Draft |
| v1.1 Draft | 2026-09-04 | 按评审意见修正 Plan Authority、SRS Baseline、Warehouse Order 关系表述、Preserve 语义和 Baseline Drift 停止条件 | Ready for Human Review |
| v1.2 Frozen | 2026-09-04 | Human Review 批准 CC-01，冻结本轮实施授权；SRS 唯一化和执行前 Baseline 检查作为实施前置条件保留 | **Frozen / Approved for Implementation** |

## Contract Gate

```text
CC-WAREHOUSE-VAS-01: FROZEN
APPROVED FOR IMPLEMENTATION
```

Implementation 仍必须先完成附录 C 规定的 SRS Authority 唯一化，并重新记录批准后的 `HEAD`、`git status --short`、allowlist 和 protected/pre-existing changes。通过后只能在本合同 allowlist 和停止条件内实施。
