# SPIKE-PDA-001 — Execution Evidence

> 版本：v1.0  
> 状态：CONDITIONAL PASS — awaiting TDD v1.1 write-back and Human Review  
> 执行日期：2026-09-07  
> 实验环境：隔离 PostgreSQL 数据库 `vas_spike_pda_001_20260907`（已删除）  
> 生产数据库：未修改  
> 正式模块：未修改  

## 1. Environment

| Item | Result |
|---|---|
| Odoo | 18.0+e-20250619 |
| Python | 3.11.9 |
| PostgreSQL | 16 |
| Odoo port | 8092，仅用于隔离 Spike |
| Addons | Odoo core、当前项目 addons、临时 Spike addon |
| Browser | Integrated browser, Chromium-based |
| Android PDA | 未提供，真实目标设备 HVR 未执行 |
| Temporary code | `/tmp/warehouse_vas_spike_addons/`，已删除 |

临时数据库由空数据库初始化，并安装 `base`、`web`、`mail`、
`worlddepot`、`wd_warehouse_value_add` 和临时 `wd_vas_pda_spike` addon。
测试创建的 VAS 订单、明细、操作类型、计量单位和附件均位于该隔离数据库。

## 2. Experiment Results

| Experiment | Result | Evidence |
|---|---|---|
| EXP-001 Dashboard / Action Entry | PASS | Client actions 载入；Dashboard 显示 PDA 和 Web List 两个入口。 |
| EXP-002 OWL/JS Asset Loading | PASS | OWL client action、XML template、SCSS 在 Odoo Web 会话中渲染。 |
| EXP-003 Read Existing VAS Record | PASS | 使用 `orm.searchRead` 读取 `wd.vas.order`，显示单号、状态和 Operator。 |
| EXP-004 One Line and Save/Submit | CONDITIONAL PASS | 一条明细、Save Draft 和 `action_submit` 调用路径已验证；后续在有效 Warehouse Order 隔离数据上完成 Submitted 和快照闭环。 |
| EXP-005 Input and Media | CONDITIONAL PASS | billno 文本输入、文件选择和一个附件写入现有 `attachment_ids` 关系成功；摄像头拍照及摄像头扫码未在目标 Android PDA 上验证。 |
| EXP-006 Bottom Action and Device | CONDITIONAL PASS | Draft 底部 Save Draft / Submit 固定栏在浏览器可见；Submitted/Cancelled 只读分支未在最小实验页面实现验证；真实 Android PDA 兼容性待 HVR。 |

### 2.1 Follow-up Valid Submit Verification

在第二个隔离数据库 `vas_spike_pda_001_submit_20260907` 中补做了有效
Warehouse Order 闭环。该数据库已在实验结束后删除。

| Step | Result |
|---|---|
| 创建 inbound Warehouse Order | PASS，`billno = IO202609070001`，`warehouse_id = 1` |
| Warehouse Order 客户 | PASS，`owner = SPIKE Customer` |
| 创建 VAS Draft | PASS，`VAS/00001`，`state = draft` |
| 创建一条有效明细 | PASS，`quantity_time = 1`，Unit 自动为 `Piece` |
| Save Draft | PASS |
| `action_submit()` | PASS |
| 重新读取 Submitted | PASS，`state = submitted` |
| 关系绑定 | PASS，`inbound_order_id = 1` |
| 快照 | PASS，`warehouse_order_billno = IO202609070001`，`warehouse_id = 1` |
| 提交审计 | PASS，`submitter_id = 1`，`submitted_at` 已写入 |

服务端未返回错误。该结果只证明现有 ORM/action Submit 路径在隔离数据上
可以完成有效提交，不证明完整 PDA 页面或真实设备验收。

## 3. Verified Technical Facts

本次隔离实验确认：

1. Odoo 18 client action 可以通过 `ir.actions.client` 与 OWL registry action tag 连接。
2. Dashboard 可以只负责入口选择，并通过 action service 导航到 PDA action。
3. PDA action 可以通过菜单直接进入，不要求先经过 Dashboard。
4. JavaScript、XML template 和 SCSS 可以通过临时 addon 的 backend assets 加载。
5. 前端可以通过标准 `orm` service 读取 `wd.vas.order`。
6. 前端可以调用现有 `wd.vas.order.action_submit`，不复制状态机或提交校验。
7. 一条 `wd.vas.order.line` 可以通过现有模型创建，服务端自动设置 Unit。
8. 文件可以通过浏览器选择并写入现有 `ir.attachment` 和 VAS 附件关系。
9. 隔离环境中的测试附件记录为 `res_model = wd.vas.order`、`res_id = 1`，清理时随数据库删除。

## 4. Unverified or Deferred Capabilities

以下能力不能根据本次实验宣布已完成：

- 真实目标 Android PDA 型号和浏览器兼容性；
- 摄像头扫码；
- 摄像头拍照；
- 多文件选择在目标 PDA 上的行为；
- Submitted / Cancelled 页面完整只读分支；
- 真实目标 PDA 上的 Warehouse Order 解析和 `owner` 客户展示；
- 生产级错误通知、重试、刷新和弱网行为；
- 完整 PDA 页面、明细卡片和附件管理。

这些内容进入 TDD v1.1 Revision、CC-04 和 CC-04 Closure 前 HVR。

## 5. Safety and Cleanup

- 未修改现有业务数据库；
- 未修改 Frozen SRS、TDD v1.0 或 CC-01/02/03；
- 未修改正式 `wd_warehouse_value_add` 代码、manifest、views、security 或 tests；
- 临时 Odoo 服务已停止；
- 隔离数据库 `vas_spike_pda_001_20260907` 已删除；
- 临时 addon 和测试附件文件已删除；
- 临时代码未合入正式模块。

## 6. Decision

**CONDITIONAL PASS**。

关键 OWL/JS、导航、assets、ORM/RPC、明细、草稿保存和附件关系路径已验证，
但真实 Android PDA 设备能力、相机能力、有效 Warehouse Order Submit 以及完整
业务 HVR 尚未验证。因此本结果只授权将已验证事实回写 TDD v1.1，
不授权冻结 TDD v1.1，不授权创建或实施 CC-04。
