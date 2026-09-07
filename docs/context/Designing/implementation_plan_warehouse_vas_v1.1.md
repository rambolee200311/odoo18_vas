# Warehouse VAS Implementation Plan v1.1

> 状态：DRAFT — HUMAN REVIEW REQUIRED  
> 模块：`wd_warehouse_value_add`  
> 上游：Frozen SRS v1.0.0、TDD v1.0.0 Frozen、TDD v1.1 Draft  
> 历史基线：CC-01、CC-02、CC-03 已完成并集成

## 1. Purpose and Authority

本计划只定义 TDD v1.1 之后的实施顺序、工作包、依赖、验证和 Closure Gate。
不修改 Frozen SRS/TDD，不重开或回滚 CC-01/02/03，不授权本文件直接编码。

```text
SPIKE-PDA-001 CONDITIONAL PASS
        ↓
TDD v1.1 Revision
        ↓
Human Review / TDD v1.1 Freeze
        ↓
Implementation Plan v1.1
        ↓
CC-04 Draft Review
        ↓
CC-04 Authorization
        ↓
CC-04 Coding
        ↓
Automated Test → Browser Test → Real PDA HVR → Closure
```

## 2. Preserved Baseline

- `wd.vas.order`、`wd.vas.order.line`、`wd.vas.operation.type` 不重写；
- Submit / Unsubmit / Cancel、状态机、锁顺序、快照和服务端校验保留；
- ACL、record rules、action permission 保留；
- Desktop Web list/form/search/menu 保留；
- `attachment_ids`、chatter 和审计保留；
- 不修改三个 Warehouse Order 模型；
- PDA 与 Web 共享同一业务模型、权限和服务端动作。

## 3. PLAN-CC-04 — Dashboard and OWL/JS PDA Frontend

### Goal

实现 Dashboard 入口选择器和专用 OWL/JS PDA Frontend，覆盖已确认 PDA 原型，
不创建第二套业务后端。

### Dependencies

- TDD v1.1 已由 Human Review 冻结；
- SPIKE-PDA-001 证据已回写；
- CC-01/02/03 的回归基线可运行；
- 目标 Android PDA 型号、浏览器版本和 HVR 数据已提供；
- CC-04 独立 Coding Contract 已批准。

### Work Packages

1. Dashboard、PDA action、Web List action 与菜单/直接入口；
2. OWL/JS PDA Header 和当前登录 Operator 只读带出；
3. billno 手工输入、键盘式扫码及解析反馈；
4. Warehouse Order 绑定和 `owner` 客户只读展示；
5. 明细卡片的添加、编辑、删除、数量/工时、Unit；
6. Save Draft、Submit、Submitted/Cancelled 只读；
7. 相机/文件选择、附件上传、展示和删除；
8. sticky bottom action bar、错误通知、状态刷新；
9. 生产级 assets、组件拆分和移动触摸体验。

### Testing

- OWL/JS component/unit tests；
- Browser Test / web tour；
- Backend regression：现有生命周期、安全、锁、快照、附件；
- PDA browser HVR；
- 扫码 HVR；
- 拍照、文件和多附件 HVR；
- Save Draft / reopen / Submit / readonly；
- Web/PDA 数据一致性；
- 弱网失败可感知、不误报成功、可安全重试/刷新；
- 不承诺离线保存、断点续传或自动同步。

### Closure Gates

CC-04 不得 Closure，除非全部满足：

- 自动化测试和 Backend regression 通过；
- Dashboard、PDA 直接入口和 Web List 导航通过；
- PDA 原型要求逐项验证；
- 有效 Warehouse Order Submit、快照和状态刷新通过；
- Submitted / Cancelled 只读通过；
- 真实目标 Android PDA HVR 完成并记录设备矩阵；
- 扫码、相机、文件、多附件验收有明确结果；
- 弱网失败路径不误报成功；
- 无生产范围污染、无新增模型/API/权限/附件系统；
- Closure 证据和 FR 记录完成。

### Stop Conditions

出现以下任一情况立即停止 CC-04 并回到 Review：

- 需要修改现有 Backend 语义、状态机、锁、快照或权限；
- 需要第二套业务模型、独立 PDA Backend/API 或离线同步；
- 生产 PDA 只能绕过现有服务端动作；
- 真实设备无法完成最小保存/提交路径；
- 数据无法在 Web/PDA 间一致读取；
- 发现 TDD v1.1 技术假设不成立。

## 4. Out of Scope

- CC-01/02/03 重开、回滚或修改；
- Warehouse Order 模型修改；
- 计费、审批、Portal、队列、Redis、事件总线；
- 独立业务 API；
- 离线保存、自动同步、断点续传；
- PDA 第一版 Unsubmit；
- 生产编码前宣布 TDD 或 CC-04 Frozen。

## 5. Plan Decision

当前计划状态为 `READY FOR CC-04 DRAFT REVIEW`，不是编码授权。
下一步是 Human Review CC-04 Draft；未经批准不得修改正式模块。
