# CC-04 — Warehouse VAS Dashboard and OWL/JS PDA Frontend

> 状态：IMPLEMENTATION IN PROGRESS — CLOSURE NOT ELIGIBLE  
> 模块：`wd_warehouse_value_add`  
> 前置：TDD v1.1 正式 Freeze、Implementation Plan v1.1 Review、CC-04 Draft Review  
> 历史基线：CC-01/02/03 Frozen Historical Baseline

## 1. Contract Goal

在不改变既有 Backend 和 Desktop Web 语义的前提下，实现：

- 模块 Dashboard 默认首页；
- PDA 和 Web List 独立入口；
- 专用 OWL/JS PDA 表现层；
- 与现有 `wd.vas.order`、`wd.vas.order.line`、服务端 action 和附件关系连接。

本 Contract 是 Draft，不授权编码。SPIKE Conditional Pass 仅支持本 Draft
完善，不替代 TDD Freeze、Plan Review 或 CC-04 Authorization。

## 1.1 Authorization Gates

编码启动前必须逐项提供可复核记录：

1. TDD v1.1 已正式 Freeze；
2. Implementation Plan v1.1 已完成 Human Review；
3. 有效 Warehouse Order Submit 证据已接受；
4. 本 CC-04 allowlist、工作包和测试编号已批准；
5. 目标 PDA 型号、浏览器版本和扫码方式已登记。

任一项未完成时，CC-04 保持 `NOT AUTHORIZED`。

## 2. In Scope

### Navigation

- Dashboard 仅提供“PDA 作业录入”和“作业单管理”两个入口；
- Dashboard 不提供统计、待办、图表或业务逻辑；
- PDA 可从 Dashboard、菜单和收藏入口直接打开；
- Web List 保留现有 list/form/search 管理入口。

### PDA Interaction

- PDA Header；
- 当前登录 Operator 自动带出并只读；
- inbound/outbound/transfer 类型选择；
- billno 手工输入和键盘式扫码；
- 解析成功/失败反馈；
- Warehouse Order.owner 客户只读展示；
- 明细卡片添加、编辑、删除；
- 数量/工时输入和 Unit 自动展示；
- 拍照入口；
- 相册/文件多选；
- 附件展示和删除；
- Draft 保存；
- Submit；
- Submitted 和 Cancelled 只读；
- sticky bottom action bar；
- 错误通知、状态刷新和安全重试。

## 3. Allowed Files

以下是本 Draft 的精确 allowlist；TDD Freeze 后只能调整为同等粒度的已批准路径。

| Path | Change | Purpose |
|---|---|---|
| `addons/wd_warehouse_value_add/__manifest__.py` | MODIFY | 声明 CC-04 data 和 frontend assets |
| `addons/wd_warehouse_value_add/views/vas_menus.xml` | MODIFY | 增加首页、PDA 和管理入口关系 |
| `addons/wd_warehouse_value_add/views/vas_frontend_actions.xml` | NEW | Dashboard/PDA client action 和菜单 action 数据 |
| `addons/wd_warehouse_value_add/static/src/js/vas_dashboard.js` | NEW | 最低复杂度 Dashboard 入口 |
| `addons/wd_warehouse_value_add/static/src/js/vas_pda_action.js` | NEW | PDA OWL action、状态和服务端调用 |
| `addons/wd_warehouse_value_add/static/src/xml/vas_dashboard.xml` | NEW | Dashboard template |
| `addons/wd_warehouse_value_add/static/src/xml/vas_pda_action.xml` | NEW | PDA template |
| `addons/wd_warehouse_value_add/static/src/scss/vas_pda_action.scss` | NEW | PDA layout、sticky action bar |
| `addons/wd_warehouse_value_add/static/tests/vas_pda_action_tests.js` | NEW | OWL/action 前端测试 |
| `addons/wd_warehouse_value_add/tests/test_vas_pda_integration.py` | NEW | ORM/action/数据一致性回归测试 |
| `addons/wd_warehouse_value_add/tests/__init__.py` | MODIFY | 注册 CC-04 integration test module |
| `addons/wd_warehouse_value_add/tests/test_vas_pda_browser.py` | NEW | Browser/web tour 测试入口 |
| `docs/context/Coding/atr_warehouse_vas_04.md` | NEW | 自动化测试结果 |
| `docs/context/Coding/hvr_warehouse_vas_04.md` | NEW | Browser/PDA HVR 结果 |
| `docs/context/Coding/fr_warehouse_vas_04.md` | NEW | Closure 记录 |

### 3.1 Read-only Existing Files

以下文件只读，不得由 CC-04 修改：

- `addons/wd_warehouse_value_add/models/**`
- `addons/wd_warehouse_value_add/security/**`
- `addons/wd_warehouse_value_add/views/vas_order_views.xml`
- `addons/wd_warehouse_value_add/views/vas_operation_type_views.xml`
- `addons/wd_warehouse_value_add/tests/test_vas_order.py`
- `addons/wd_warehouse_value_add/tests/test_vas_security.py`
- `addons/wd_warehouse_value_add/tests/test_vas_attachment.py`
- `addons/worlddepot/**`
- Odoo 官方源码

除上述明确路径外，任何新增或修改文件都需要重新 Review。

## 4. Forbidden Changes

禁止修改：

- Frozen SRS、TDD v1.0、CC-01/02/03；
- `addons/worlddepot/**`；
- `wd.vas.order`、`wd.vas.order.line`、`wd.vas.operation.type` 的既有业务语义；
- 状态机、Submit/Unsubmit/Cancel、锁顺序、快照；
- ACL、record rules、服务端 action permission；
- 现有 attachment relation；
- Odoo 官方源码。

禁止创建：

- 第二套业务模型；
- 第二套状态机或权限模型；
- 独立 PDA Backend/API；
- 独立附件存储；
- 离线队列、自动同步、断点续传；
- PDA Unsubmit（除非另有业务批准）。

## 5. Server Reuse Rules

- 所有读写通过当前 Odoo session 和标准 ORM/RPC；
- Submit 必须调用现有 `action_submit`；
- 前端不得复制状态校验、锁、快照或权限判断；
- Operator 使用同一个 `operator_id`；
- Desktop Web 代录能力保留；
- 附件使用现有 `attachment_ids` / `ir.attachment` 关系；
- Warehouse Order.owner 只读来源不得新增客户快照。

## 5.1 Accepted Submit Evidence

有效 Submit 前置证据已完成，见：

[spike_pda_001_execution_evidence.md](/Users/lijianqiang/Documents/odoo18e_vas/docs/context/verification/spike_pda_001_execution_evidence.md)

证据中的 follow-up verification 已确认：

```text
Inbound IO202609070001
→ VAS draft VAS/00001
→ one valid line
→ Save Draft
→ action_submit()
→ state=submitted
→ inbound_order_id, warehouse_order_billno, warehouse_id,
  submitter_id, submitted_at persisted
```

该证据只证明服务端有效 Submit 基线，不替代 PDA HVR。

## 5.2 Failure and Recovery Contract

- Submit 请求超时：前端不得显示成功；必须重新读取该 VAS Order 的服务端
  state、snapshot 和 submit audit，再决定显示 Submitted 或可重试；
- Submit 成功后重复点击：按钮必须禁用或请求幂等；不得产生第二次业务提交；
- Submit 返回业务错误/权限错误：保留 Draft，展示可识别错误，不得伪造成功；
- 页面刷新或重新打开：以服务端读取结果为准，不以本地临时状态恢复业务成功；
- 附件上传失败：显示失败文件和可安全重试入口，不得把失败文件标记为已上传；
- 附件成功后重复上传：不得产生重复业务附件结果，需按文件/请求状态处理；
- 并发修改或记录已提交：重新读取服务端状态，停止本地写入并提示用户；
- 不得引入离线队列、自动同步、断点续传或本地业务提交缓存。

重复点击、超时重读、刷新和并发路径必须有自动化或 Browser Test 证据。

## 6. Work Packages and Verification

### WP-01 Dashboard / Navigation

验收编号：`CC04-NAV-01` 至 `CC04-NAV-04`

- 默认根菜单进入 Dashboard；
- Dashboard 只有 PDA 和 Web List 两个入口；
- PDA 可从 Dashboard、菜单、收藏直接进入；
- Web List 继续打开现有管理入口。

### WP-02 PDA Form Foundation

验收编号：`CC04-PDA-01` 至 `CC04-PDA-06`

- OWL action 和 assets 加载；
- Header；
- 当前登录 Operator 只读；
- inbound/outbound/transfer 与 billno 输入；
- Warehouse Order.owner 只读；
- 解析成功/失败反馈。

### WP-03 Line Editing

验收编号：`CC04-LINE-01` 至 `CC04-LINE-06`

- 添加、编辑、删除明细；
- Quantity/Time；
- Unit 自动展示；
- 一条有效明细可保存；
- Draft 可重新打开；
- 不复制服务端校验。

### WP-04 Attachment

验收编号：`CC04-ATT-01` 至 `CC04-ATT-05`

- 拍照入口或明确设备降级；
- 文件/相册多选边界；
- 使用现有 attachment relation；
- 展示和删除；
- 上传失败、重试和刷新结果可识别。

### WP-05 State / Error / Recovery

验收编号：`CC04-STATE-01` 至 `CC04-STATE-08`

- Save Draft；
- Submit；
- Submitted/Cancelled 只读；
- Submit 超时后重读；
- 重复点击；
- 页面刷新；
- 并发修改；
- RPC/权限/业务错误。

### WP-06 Test and HVR

验收编号：`CC04-TEST-01` 至 `CC04-TEST-08`

- OWL/JS component tests；
- ORM/action regression；
- Browser Test；
- Web/PDA 一致性；
- 弱网失败边界；
- 真实设备输入；
- 扫码；
- 相机/文件/多附件。

### Automated

- OWL/JS component tests；
- action/navigation tests；
- ORM/RPC success/error tests；
- 明细 Unit、数量/工时和删除；
- Save Draft / reopen / Submit / readonly；
- attachment relation and delete；
- existing Backend/security regression。

每个工作包必须在对应验收编号全部通过后才能进入下一个工作包；失败项
必须记录为 `FAIL`、`BLOCKED` 或明确的设备限制，不得汇总成 PASS。

### Browser and HVR

- Dashboard → PDA；
- Dashboard → Web List；
- PDA direct entry；
- billno 手工和键盘式扫码；
- 有效 Warehouse Order Submit 与快照；
- 客户只读展示；
- 相机、文件、多附件；
- Android PDA 触摸、键盘、软键盘和固定底栏；
- 弱网失败可感知、不误报成功、可安全重试/刷新；
- Web/PDA 数据一致性。

真实 PDA HVR 记录至少必须包含：

- 设备制造商、型号和 Android 版本；
- 浏览器名称和完整版本；
- 扫码方式：键盘式扫码、摄像头扫码或其他实际方式；
- 相机权限和拍照结果；
- 文件/相册多选结果；
- 网络条件；
- 每个验收编号的截图、日志、实际结果和失败记录。

没有真实目标设备时，可以完成开发、自动化测试和桌面浏览器测试，但不得
关闭 CC-04。

## 7. Stop Conditions

任一情况发生时停止并提交 Review：

- 需要改动既有 Backend 语义；
- 需要绕过 ACL、record rule 或服务端 action；
- 需要独立 API、模型、状态机或附件系统；
- 真实 PDA 无法完成最小 Draft 保存或 Submit；
- Submit 后状态/快照与 Web 不一致；
- 发现 TDD v1.1 未覆盖的业务语义；
- 测试或 HVR 失败且无法在本 Contract 范围内安全修复。

## 8. Closure Criteria

CC-04 Closure 必须同时具备：

1. 自动化测试通过；
2. Backend regression 通过；
3. Browser Test 通过；
4. 真实目标 PDA HVR 完成；
5. 扫码、拍照、文件、多附件结果明确；
6. Save Draft / reopen / Submit / readonly 通过；
7. Web/PDA 数据一致；
8. 弱网边界验证完成；
9. 生产范围无未授权修改；
10. Closure evidence、FR 和 HVR 文档完成。

满足 Closure Criteria 前，不得宣布 CC-04 完成，不得将未验证能力描述为 PASS。

## 9. Current Review Decision

```text
CC-04 Draft Review = ACCEPTED
TDD v1.1 Freeze = COMPLETED
Implementation Plan v1.1 Review = COMPLETED
CC-04 Coding = COMPLETED
CC-04 Closure = APPROVED BY HUMAN REVIEW
```

以下字段必须在编码授权前补入本 Contract 的 Human Review 记录：

```text
Target PDA Model: 东集（Chainway）Cruise GE2
Android Version: Android 11
Browser Name / Version: Firefox — exact version not supplied
Scanner Mode: Not specified; barcode scanning verified
Camera/File Capability: Camera, photo, and gallery multi-select verified
```

Human Review on 2026-09-07 explicitly authorizes CC-04 Closure with the exact
Firefox version and isolated full frontend test run recorded as follow-up
evidence items. The verified Android PDA capabilities are accepted as PASS.

## 10. Closure Decision

```text
Human authorization: GRANTED
Android PDA HVR: PASS
Backend regression: PASS
Browser smoke: PASS
Verified PDA operational scenarios: PASS
Known evidence follow-ups: ACCEPTED BY HUMAN REVIEW
CC-04 Closure: CLOSED
```
