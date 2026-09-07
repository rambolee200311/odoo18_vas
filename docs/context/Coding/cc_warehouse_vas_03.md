# Coding Contract — CC-WAREHOUSE-VAS-03

## 0. 文档治理

### 0.1 目的

本 Coding Contract（CC）是 Warehouse VAS 第三轮实施草案，限定 Security, Web, PDA & Attachment 的实现范围：本轮允许修改什么、必须实现什么、禁止实现什么，以及什么证据才能关闭本轮。

本文当前为 **v1.0 Frozen**，已获得 Human Review 批准，可作为 CC-03 的唯一实施授权来源。

### 0.2 核心原则

- 不重新发明 Frozen SRS、Frozen TDD 或 Implementation Plan；
- 只授权 CC-03 权限、安全、标准 Web/PDA 入口、附件和相关验证；
- CC-02 已完成并集成的服务端生命周期规则必须继续保留；
- ACL、record rule、action permission 必须形成纵深防御，不能只依赖按钮隐藏；
- Odoo Native First、Simple Models、Explicit Business Logic、Robust Before Clever；
- 不创建独立 PDA App、SPA、PDA API、第三方前端、附件存储子系统或新授权模型；
- 发现 TDD 设计不足、Protected Scope 冲突或基线漂移时，必须停止并升级。

### 0.3 上游基线

- SRS：v1.0.0 Frozen；
- DDD：SKIP；
- TDD：[tdd_warehouse_vas_v1.0.0.md](../Designing/tdd_warehouse_vas_v1.0.0.md)，v1.0.0 Frozen；
- Implementation Plan：[implementation_plan_warehouse_vas_v1.0.md](../Designing/implementation_plan_warehouse_vas_v1.0.md)，Current / Approved Execution Baseline；
- CC-01：v1.2 Frozen，`FR-CC01 = SATISFIED`；
- CC-02：v1.0 Frozen，`FR-CC02 = SATISFIED`，Human Review = APPROVED FOR INTEGRATION；
- CC-02 集成提交：`d589ecf Implement Warehouse VAS lifecycle`；
- 当前上游分支：`main`，CC-02 已推送到 `origin/main`。

Implementation 开始前必须重新确认 HEAD、`git status --short`、allowlist 和受保护文件状态。若与本草案所依据的基线不一致，必须触发 `CONTRACT BASELINE DRIFT`，不得静默继续。

### 0.4 编号体系

本 CC 只使用模板规定的自有编号：

- `CC-CHANGE-*`：本次变更项；
- `CC-PRESERVE-*`：必须保持的既有行为；
- `CC-TEST-*`：本次测试契约项；
- `CC-DEC-*`：实现级局部决策。

SRS、TDD 和 TEST 编号直接引用上游 ID，不另造上游编号。

### 0.5 冻结规则

本 CC 中进入正式编号体系的内容，在 Human Review 冻结后不得被 Implementation Agent 静默修改。冻结前的评审意见必须通过版本修订记录。

---

## 1. 变更概述

| 字段 | 值 |
|---|---|
| Intent ID | `CC-WAREHOUSE-VAS-03` |
| 模块 | `wd_warehouse_value_add` |
| 工作类型 | 新功能 / UI 调整 / 安全实现 |
| 变更类型 | 权限、安全、标准 Web/PDA 入口、附件能力 |
| 目标 | 让已完成 CC-02 生命周期闭环的 VAS 具备角色隔离、标准 Odoo Web 入口、移动尺寸表单和原生附件能力 |
| 背景 | CC-02 只完成模型服务层，没有 ACL、record rules、菜单、视图或附件 UI，当前无法通过浏览器进入和操作 VAS |
| 前置条件 | `FR-CC02 = SATISFIED`，CC-02 已集成并推送 |
| 当前状态 | v1.0 Frozen — Implementation Authorized |

本轮不改变 VAS 业务状态机、Warehouse Order 模型、计费语义或 Frozen TDD 的技术边界。

---

## 2. 上游基线与追溯

### 2.1 SRS 引用

| SRS ID | 标题 / 内容 | 与本次 CC 的相关性 |
|---|---|---|
| `ROLE-VAS-01` | 仓管员 | 在范围内：自建记录、草稿编辑、提交、反提交、草稿作废 |
| `ROLE-VAS-02` | 仓库主管 | 在范围内：查看全部、草稿管理、查询与审计 |
| `FR-VAS-01` | 创建作业单草稿 | 在范围内：Web/PDA 共用表单 |
| `FR-VAS-02` | 添加/删除作业明细 | 在范围内：x2many Web/PDA 交互 |
| `FR-VAS-03` | 选择关联对象与单据号 | 在范围内：表单字段和查询筛选 |
| `FR-VAS-04` | 选择操作员 / 代录 | 在范围内：Operator 选择和显示 |
| `FR-VAS-05` | 上传附件 | 在范围内：原生多附件能力 |
| `FR-VAS-06` | 提交作业单 | 在范围内：按钮、权限和服务端 action permission |
| `FR-VAS-07` | 反提交作业单 | 在范围内：按钮、权限和只读状态 |
| `FR-VAS-08` | 作废作业单 | 在范围内：按钮、权限和只读状态 |
| `FR-VAS-09` | Web 查询作业单列表 | 在范围内：list/search/menu/action |
| `FR-VAS-10` | 查看作业单详情 | 在范围内：form、附件和 chatter 展示 |
| `NFR-VAS-01` | 权限隔离 | 在范围内：ACL 和 record rule |
| `NFR-VAS-02` | 审计留痕 | 在范围内：chatter 和只读审计字段展示 |
| `NFR-VAS-03` | PDA 可用性 | 部分：标准 Web 小屏表单；真实设备体验不在本轮最终验收 |

### 2.2 DDD 引用

N/A。项目已明确 DDD SKIP，仅执行：

```text
SRS → TDD → CC → TEST
```

### 2.3 TDD 引用

| TDD ID / 章节 | 标题 / 内容 | 与本次 CC 的相关性 |
|---|---|---|
| TDD §4 | 模块安全、视图和菜单文件 | 在范围内 |
| TDD §11 / `TD-010` | Groups、ACL、record rules、action permission | 在范围内 |
| TDD §12 | 标准 Web list/form/search/menu | 在范围内 |
| TDD §13 / `TD-005` | 标准 Web 同时承载桌面和 PDA | 在范围内 |
| TDD §14 / `TD-006` | `ir.attachment` + `many2many_binary` | 在范围内 |
| TDD §10 / `TD-007` | Chatter / tracking 展示 | 在范围内 |
| TDD §8 / `TD-002` | 既有状态动作保持不变 | 回归边界 |
| TDD §18 | Security、附件和 UI/integration test | 在范围内 |
| TDD §19 | ROLE / NFR / AC 追溯 | 在范围内 |

### 2.4 追溯规则

本 CC 不新增业务语义。权限、视图、附件和页面交互必须追溯到 Frozen SRS/TDD；实现级局部选择记录在 `CC-DEC`，不得扩大角色、数据范围或技术架构。

---

## 3. 范围冻结

### 3.1 在范围内

- `CC-CHANGE-001`：完成 `group_vas_user` 和 `group_vas_manager` 的最终安全语义；
- `CC-CHANGE-002`：为 VAS Order、VAS Order Line、Operation Type 配置 ACL；
- `CC-CHANGE-003`：配置仓管员自建记录可见、主管全量可见的 record rules；
- `CC-CHANGE-004`：在 `action_submit()`、`action_unsubmit()`、`action_cancel()` 增加服务端角色权限检查，并保留 CC-02 状态检查；
- `CC-CHANGE-005`：实现 VAS Order list/form/search/menu/action；
- `CC-CHANGE-006`：实现 Operation Type 配置 list/form/search/menu/action；
- `CC-CHANGE-007`：按 Draft、Submitted、Cancelled 状态实现 UI 编辑性、按钮可见性和只读展示；
- `CC-CHANGE-008`：实现适合小屏的标准 Web 表单、明细 x2many kanban 路径和键盘式 billno 输入；
- `CC-CHANGE-009`：实现 `attachment_ids` 的标准 `many2many_binary` 展示、上传、查看和 Draft 状态下维护；
- `CC-CHANGE-010`：在界面展示 chatter、动作审计字段和必要的系统字段；
- `CC-CHANGE-011`：补充安全、附件、视图和必要的 Web/integration 自动化测试；
- `CC-CHANGE-012`：执行浏览器层面的核心页面人工验证，验证 Web 入口、角色可见性、状态 UI 和附件操作；
- `CC-CHANGE-013`：更新 manifest，使安全、ACL、主数据配置视图、业务视图按依赖顺序加载。

### 3.2 超出范围

- 独立 PDA App、SPA、OWL 专用前端或 PDA API；
- 自定义 JS 扫码组件、扫码枪驱动、相机专用入口；
- 真实移动浏览器、真实 PDA、扫码枪和相机的最终验收；
- 新增 Warehouse ↔ Operator 授权模型；
- 修改 `world.depot.inbound.order`、`world.depot.outbound.order`、`world.depot.transfer.order` 或 `world.depot.charge.unit`；
- 修改 CC-02 的状态枚举、快照、锁策略或动作语义；
- 计费、绩效、工资、审批、客户 Portal；
- 自定义附件模型、对象存储、文件服务器或附件配置子系统；
- 外部 API、queue、Redis、事件总线或第三方前端；
- Optional CC-04 hardening；
- 通过隐藏按钮替代 ACL、record rule 或服务端 action permission；
- 修改 Frozen SRS、Frozen TDD 或已完成的 CC-01/CC-02 证据文档。

### 3.3 非目标

- 不宣称真实 PDA 设备验收已完成；
- 不宣称真实扫码枪、移动相机或视频采集已完成；
- 不创建新的业务状态或修改状态转换；
- 不通过浏览器验证替代 ORM、安全和自动化测试；
- 不在本轮决定项目 Release。

---

## 4. 变更边界

### 4.1 允许

| 类型 | 详情 |
|---|---|
| 文件 | `addons/wd_warehouse_value_add/__manifest__.py` |
| 文件 | `addons/wd_warehouse_value_add/models/vas_order.py` |
| 文件 | `addons/wd_warehouse_value_add/security/security.xml` |
| 新增文件 | `addons/wd_warehouse_value_add/security/ir.model.access.csv` |
| 新增文件 | `addons/wd_warehouse_value_add/views/vas_operation_type_views.xml` |
| 新增文件 | `addons/wd_warehouse_value_add/views/vas_order_views.xml` |
| 新增文件 | `addons/wd_warehouse_value_add/views/vas_menus.xml` |
| 文件 | `addons/wd_warehouse_value_add/tests/__init__.py` |
| 新增文件 | `addons/wd_warehouse_value_add/tests/test_vas_security.py` |
| 新增文件 | `addons/wd_warehouse_value_add/tests/test_vas_attachment.py` |
| 模型 | `wd.vas.order`、`wd.vas.order.line`、`wd.vas.operation.type` |
| 方法 | 三项既有 action 的服务端 group/permission guard；仅限 CC-03 权限语义 |
| 字段 | 已存在的 `attachment_ids`、审计字段、状态字段的视图和权限属性 |
| XML | VAS 自有 groups、ACL、record rules、actions、menus、views |

`vas_order.py` 只允许增加安全权限检查或与 UI 权限直接相关的最小逻辑，不得改写 CC-02 生命周期实现。

### 4.2 禁止

| 类型 | 详情 |
|---|---|
| 受保护模型 | 不得修改任何 `worlddepot` 或 Odoo 官方模型源码 |
| 状态枚举 | 不得修改 `draft/submitted/cancelled` |
| 业务动作 | 不得改变 Submit、Unsubmit、Cancel 的业务规则、锁顺序或快照语义 |
| 数据范围 | 不得引入 Warehouse ↔ Operator 新授权关系 |
| 前端架构 | 不得新增 SPA、独立 PDA App、外部 API、第三方 JS 框架 |
| 存储 | 不得新增自定义附件模型、对象存储或文件服务器 |
| 数据库 | 不得新增 SQL unique constraint，不得直接 SQL 写业务数据 |
| 其他模块 | 不得修改 allowlist 之外的应用代码或文档 |

---

## 5. 必需的行为变更

| ID | 当前行为 | 期望行为 | CC-CHANGE ID |
|---|---|---|---|
| 1 | VAS groups 只有 identity，没有最终访问语义 | 仓管员和主管拥有 TDD 定义的角色权限 | `CC-CHANGE-001` |
| 2 | VAS 模型没有正式 ACL | ACL 允许授权用户读写，统一禁止删除 | `CC-CHANGE-002` |
| 3 | 没有数据隔离 | 仓管员只能查看自己 `create_uid` 创建的记录，主管可查看全部 | `CC-CHANGE-003` |
| 4 | action 没有最终角色校验 | 未授权用户无法通过 RPC 直接调用动作 | `CC-CHANGE-004` |
| 5 | 没有 Web 入口 | 提供标准菜单、action、list、form、search | `CC-CHANGE-005` |
| 6 | 没有状态相关 UI | Draft 可编辑，Submitted/Cancelled 正确只读并显示允许动作 | `CC-CHANGE-007` |
| 7 | 没有小屏交互布局 | 标准 Web 表单支持小屏字段顺序和 x2many kanban | `CC-CHANGE-008` |
| 8 | 没有附件 UI | 使用原生 `many2many_binary` 维护多个附件 | `CC-CHANGE-009` |
| 9 | 没有操作类型配置入口 | 主管可维护 Operation Type 和 Charge Unit 映射 | `CC-CHANGE-006` |
| 10 | 没有安全/UI 自动化证据 | 测试和浏览器人工验证覆盖 CC-03 行为 | `CC-CHANGE-011/012` |

---

## 6. 既有行为保留（回归边界）

| ID | 行为 / 契约 | 为什么不得改变 | CC-PRESERVE ID |
|---|---|---|---|
| 1 | CC-02 三项 action 的状态转换 | Frozen TDD 和已集成业务事实 | `CC-PRESERVE-001` |
| 2 | Submit 时按类型和 billno 绑定 Warehouse Order | 已完成生命周期契约 | `CC-PRESERVE-002` |
| 3 | billno / warehouse snapshot 和动作审计语义 | 审计和历史事实依赖 | `CC-PRESERVE-003` |
| 4 | Submitted / Cancelled 服务端不可变性 | 防止绕过 UI 修改核心事实 | `CC-PRESERVE-004` |
| 5 | VAS Order → Warehouse Order 锁顺序和锁后重读 | TDD §16 并发契约 | `CC-PRESERVE-005` |
| 6 | CC-01 sequence、基础模型、Draft 零行行为 | 已集成基础骨架 | `CC-PRESERVE-006` |
| 7 | Creator、Operator、Submitter 三个概念独立 | Frozen SRS/TDD 语义 | `CC-PRESERVE-007` |
| 8 | Protected Warehouse Order 模型和行为 | Protected Scope | `CC-PRESERVE-008` |
| 9 | 附件字段的 Draft 可维护、Submitted/Cancelled 不可变语义 | TDD §14 | `CC-PRESERVE-009` |

---

## 7. 适用的 TDD 防护栏

| TDD 防护栏 / 决策 | 适用性 | 本次落实位置 | 验证方式 |
|---|---|---|---|
| `TD-005` 标准 Web 同时承载 Web/PDA | 适用 | 标准 Odoo XML views、响应式表单和 x2many kanban | `CC-TEST-007/008`、浏览器验证 |
| `TD-006` 原生附件能力 | 适用 | `many2many_binary`、原生 `ir.attachment` 权限 | `CC-TEST-006`、浏览器验证 |
| `TD-007` chatter/tracking 审计 | 适用 | form chatter 和审计字段只读展示 | `CC-TEST-007` |
| `TD-010` active VAS User / Manager | 适用 | groups、ACL、record rules、action permission | `CC-TEST-001~004` |
| TDD §11 ACL / record rules | 适用 | `ir.model.access.csv`、`security.xml` | `CC-TEST-001~004` |
| TDD §12 Web UI | 适用 | list/form/search/menu/action XML | `CC-TEST-005/007` |
| TDD §14 attachment immutability | 适用 | 状态属性和服务端现有保护 | `CC-TEST-006` |
| TDD §18 Security/UI test design | 适用 | security、attachment、integration test | `CC-TEST-001~008` |

CC 不复制 TDD 防护栏正文；Frozen TDD v1.0.0 是唯一技术规范来源。

---

## 8. 数据 / 迁移影响

| 字段 | 值 |
|---|---|
| 需要迁移 | 否 |
| 迁移脚本 | N/A |
| 数据源 | N/A；CC-01/CC-02 已有结构继续使用 |
| 目标 | 新增安全、视图和菜单元数据 |
| 恢复 / 回滚策略 | 卸载/回退本轮 XML 和代码；不得删除业务记录 |
| 验证 | 模块升级、ACL/record rule 测试、菜单/视图加载和现有 CC-01/CC-02 回归 |

---

## 9. API / 集成影响

| 字段 | 值 |
|---|---|
| 修改的外部端点 | N/A |
| 模型业务 API | 仅增加 action 的 group/permission guard，不改变方法签名 |
| 向后兼容 | 是；既有 ORM action 语义保持 |
| Adapter 变更 | N/A |
| 独立 PDA API | 不创建 |

---

## 10. 安全 / 权限影响

### 10.1 Groups

- `group_vas_user`：仓管员，对应 `ROLE-VAS-01`；
- `group_vas_manager`：仓库主管，对应 `ROLE-VAS-02`，继承仓管员能力。

### 10.2 ACL

| 模型 | 仓管员 | 主管 |
|---|---|---|
| `wd.vas.order` | read/create/write；unlink 禁止 | read/create/write；unlink 禁止 |
| `wd.vas.order.line` | 通过父单权限使用；unlink 禁止 | 通过父单权限使用；unlink 禁止 |
| `wd.vas.operation.type` | read | read/create/write；unlink 按主数据历史保护要求禁止 |

ACL 不负责表达“只能修改 Draft”；状态和服务端 action/write protection 继续由模型逻辑保证。

### 10.3 Record Rules

- 仓管员：`create_uid = user.id`；
- 主管：全部 VAS Order；
- 明细：通过父 `wd.vas.order` 权限保护；
- 附件：访问权限必须与业务记录权限一致；
- 不建立 Warehouse ↔ Operator 授权关系。

### 10.4 Action Permission

- Submit、Unsubmit：`group_vas_user` 或 `group_vas_manager`；
- Cancel：角色权限和既有 Draft 状态校验同时生效；
- 未授权用户即使直接调用 RPC，也必须被服务端拒绝；
- UI 按钮隐藏不能替代服务端校验。

---

## 11. 测试契约

| 测试 ID | 对应变更 | 上游来源 | 测试类型 | 预期结果 | 人工验证 | 原因 |
|---|---|---|---|---|---|---|
| `CC-TEST-001` | Groups / ACL | `ROLE-VAS-01/02`, TDD §11 | ORM security | 仓管员和主管拥有准确模型权限，删除被禁止 | 否 | 验证基础访问边界 |
| `CC-TEST-002` | Record rules | `NFR-VAS-01`, TDD §11 | ORM security | 仓管员只能看到自己创建的记录，主管可看全部 | 否 | 防止数据越权 |
| `CC-TEST-003` | Action permission | `ROLE-VAS-01/02`, TDD §11 | ORM integration | 未授权用户不能通过 RPC 执行 Submit/Unsubmit/Cancel | 否 | 按钮隐藏不是安全边界 |
| `CC-TEST-004` | Operator domain / server validation | `TD-010` | ORM integration | Operator 必须 active 且属于 VAS User/Manager | 否 | 防止客户端绕过 |
| `CC-TEST-005` | Menus / actions / views | `FR-VAS-09/10`, TDD §12 | XML/module load | 菜单、action、list/form/search 可加载且引用正确模型 | 否 | 页面入口基础验证 |
| `CC-TEST-006` | Attachment access and immutability | `FR-VAS-05`, `TD-006` | ORM integration | Draft 可增删附件，Submitted/Cancelled 不能维护附件，权限与父单一致 | 否 | 防止附件越权和历史篡改 |
| `CC-TEST-007` | Status UI and chatter | `FR-VAS-06~10`, `NFR-VAS-02` | View/integration | 三种状态显示正确，按钮/只读属性与服务端规则一致，审计可见 | 是 | 页面行为需要人工确认 |
| `CC-TEST-008` | Small-screen Web path | `NFR-VAS-03`, `TD-005` | Browser smoke | 桌面浏览器和小屏尺寸可完成创建、编辑、查询和动作入口 | 是 | 标准 Web/PDA 共用入口 |
| `CC-TEST-009` | CC-01/CC-02 regression | `CC-PRESERVE-001~009` | Regression | 既有基础、生命周期、并发和审计测试继续通过 | 否 | 防止安全/UI 回归服务层 |

### 11.1 Browser Human Verification Contract

本 CC 要求进行 **Odoo 浏览器核心页面人工验证**，至少覆盖：

1. 仓管员登录后只能看到自己创建的 VAS Order；
2. 主管登录后可以查询并查看全部 VAS Order；
3. Draft 表单可创建、编辑、增删明细和上传附件；
4. Operation Type 选择后显示正确的单位；
5. Submit 后界面转为只读并显示允许的动作；
6. Unsubmit 后恢复 Draft 编辑能力；
7. Draft Cancel 要求原因并进入只读 Cancelled；
8. list/search 能按单号、订单类型、billno、Operator、状态和日期筛选；
9. chatter 和审计字段可查看；
10. 未授权用户无法通过菜单或页面执行受保护动作。

真实 PDA、扫码枪、移动相机和真实视频采集仍属于后续 PVR/HVR，除非另有明确授权将其纳入本 CC。

---

## 12. 停止条件 / 升级闸门

出现以下任一情况时，必须停止自行扩展：

| 触发条件 | 升级路径 |
|---|---|
| 角色权限与 Frozen SRS/TDD 不一致 | → SRS/TDD Change Review |
| 需要新增 Warehouse ↔ Operator 授权关系 | → STOP，TDD IMPACT |
| record rule 无法同时满足仓管员自建和主管全量可见 | → STOP，报告 SECURITY BLOCKER |
| 需要修改 Protected Warehouse Order 或 Odoo 官方源码 | → STOP，Protected Scope violation |
| 需要改变 CC-02 action、状态、快照或锁语义 | → STOP，CC-02/TDD impact |
| 原生 Web 不能满足小屏路径而需要独立前端 | → STOP，TDD/CC revision |
| 原生附件权限无法与业务记录一致 | → STOP，SECURITY BLOCKER |
| 需要 SQL constraint、直接 SQL 写业务数据或自定义存储 | → STOP，超出 CC |
| 浏览器验证发现业务行为与自动化测试不一致 | → STOP，建立 finding 并修复/升级 |
| 需要修改 allowlist 之外的文件 | → CC 修订 |
| 实施前 HEAD、工作树或上游基线发生未记录变化 | → `CONTRACT BASELINE DRIFT` |
| 需要提前实现 CC-04 hardening | → STOP，CC 修订 |

不得为了“让页面显示出来”绕过 ACL、record rule 或服务端 action permission。

---

## 13. 完成定义 / 关闭标准

CC-03 只有同时满足以下条件才可申请 Coding Closure：

1. 所有 `CC-CHANGE-001` 至 `CC-CHANGE-013` 均已实现；
2. 所有 `CC-PRESERVE-001` 至 `CC-PRESERVE-009` 均有验证证据；
3. ACL、record rules、action permission 的自动化测试通过；
4. Web list/form/search/menu/action 可加载并可使用；
5. Draft、Submitted、Cancelled UI 与 CC-02 服务端保护一致；
6. 附件在 Draft 可维护，Submitted/Cancelled 不可绕过保护；
7. CC-01/CC-02 回归测试通过；
8. 浏览器核心页面人工验证有真实 HVR 证据；
9. 真实 PDA、扫码枪、相机和视频体验明确标记为 deferred 或由后续 PVR/HVR 验证，不得冒充已完成；
10. 没有 Protected Scope violation、SECURITY BLOCKER、TDD IMPACT 或 baseline drift；
11. 没有独立 PDA App、SPA、外部 API、第三方前端或自定义附件存储；
12. IHR、ATR 和 HVR 记录真实文件、权限、视图、测试、浏览器环境和结果；
13. FR-CC03 对所有契约义务给出明确结论；
14. Human Review 批准前不得提交、推送或进入 CC-04。

---

## 14. 追溯矩阵

| 上游 ID | CC-CHANGE ID | 备注 |
|---|---|---|
| `ROLE-VAS-01/02` | `CC-CHANGE-001~004` | Groups、ACL、规则和 action permission |
| `NFR-VAS-01` | `CC-CHANGE-002/003/004` | 权限隔离和服务端防绕过 |
| `FR-VAS-01~04` | `CC-CHANGE-005/007/008` | 创建、编辑、关联对象和 Operator UI |
| `FR-VAS-05` / `TD-006` | `CC-CHANGE-009` | 原生附件 |
| `FR-VAS-06~08` | `CC-CHANGE-004/007` | 状态动作和 UI |
| `FR-VAS-09/10` | `CC-CHANGE-005/006/010` | 列表、查询、详情和审计 |
| `NFR-VAS-02` / `TD-007` | `CC-CHANGE-010` | Chatter/tracking 展示 |
| `NFR-VAS-03` / `TD-005` | `CC-CHANGE-008/012` | 标准 Web 小屏路径 |
| TDD §18 | `CC-CHANGE-011/012` | 自动化和浏览器验证 |

本项目无 DDD，仅执行：

```text
SRS → TDD → CC → TEST
```

---

## 附录 A — 实现决策（CC-DEC）

| CC-DEC ID | 决策 | 考虑的替代方案 | 理由 |
|---|---|---|---|
| `CC-DEC-001` | 使用 Odoo 原生 ACL、record rule、XML view、action、menu 和 chatter | 自定义权限层或前端权限层 | 符合 Odoo Native First 和 TDD §11~14 |
| `CC-DEC-002` | 仓管员可见性按 `create_uid`，主管通过独立 manager rule 全量可见 | 按 Operator 或 Warehouse 隔离 | Frozen SRS 明确按 Creator 隔离，TDD 禁止新增授权关系 |
| `CC-DEC-003` | 只在现有 action 中增加最小 group guard，不重写 CC-02 action | 新增 service / controller | 保持服务端生命周期和锁策略不变 |
| `CC-DEC-004` | 使用标准 Web form 同时承载桌面和小屏 PDA 路径 | 独立 PDA App / SPA | Frozen TDD `TD-005` 已确定 |
| `CC-DEC-005` | 附件使用既有 `attachment_ids` 和 `many2many_binary` | 自定义附件模型或存储 | Frozen TDD `TD-006` 已确定 |
| `CC-DEC-006` | 浏览器人工验证覆盖核心页面；真实设备体验延期 | 将浏览器检查宣称为真实 PDA 验收 | 避免把页面 smoke test 冒充设备 HVR |

---

## 附录 B — Human Review 与文档状态

```text
Human Review Decision: APPROVED FOR IMPLEMENTATION
Reviewed By: Human Reviewer
Review Date: 2026-09-07
Contract Status: FROZEN
Implementation Authorization: GRANTED FOR CC-03 ONLY
Merge / Release Decision: NOT MADE
```

冻结说明：

- 本次冻结只授权 CC-03；
- 允许实施本文件明确的代码、XML、安全和视图范围；
- 不授权 CC-04 或项目 Release；
- 若实施前基线、Scope 或 allowlist 发生漂移，必须停止并记录 `CONTRACT BASELINE DRIFT`。

### 版本历史

| 版本 | 日期 | 变更说明 | 状态 |
|---|---|---|---|
| v0.1 | 2026-09-07 | 基于 Frozen TDD、Implementation Plan、CC-02 集成事实起草 CC-03 | Draft |
| v1.0 | 2026-09-07 | Human Review 批准，冻结 CC-03 实施范围 | Frozen |

## Contract Gate

```text
Current Status: FROZEN
Human Review: APPROVED
Implementation Authorization: GRANTED FOR CC-03 ONLY
Next Step: Re-baseline and implement CC-03
```
