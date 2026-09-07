# Warehouse Value Add

`wd_warehouse_value_add` 是 Odoo 18 的仓库库内增值作业登记模块，支持
Desktop Web 和 Android PDA 两种录入方式。

模块用于记录仓库现场实际发生的贴标、缠膜、换箱、打托、盘点等作业事实。
当前版本不包含增值作业计费、结算或财务核算。

## 功能概览

- Dashboard 统一入口；
- Desktop Web 作业单列表、表单和历史单据查询；
- Android PDA 专用作业录入界面；
- 入库、出库、调拨业务单据关联；
- 关联单据号手工输入或扫码录入；
- 客户、仓库和当前操作员信息展示；
- 一张作业单支持多条作业明细；
- 操作类型自动带出计量单位；
- 数量/工时和明细备注；
- 拍照、相册多选和文件附件；
- 草稿保存、提交和作废；
- 提交后的状态和核心字段只读；
- 服务端状态校验、权限控制、锁和业务快照。

## 依赖和安装

模块依赖：

- `base`
- `mail`
- `web`
- `worlddepot`

安装步骤：

1. 将模块目录放入 Odoo 的 `addons_path`；
2. 更新应用列表；
3. 安装 **Warehouse Value Add**；
4. 为操作人员分配 `VAS User` 权限，为管理人员分配 `VAS Manager` 权限；
5. 配置可用的 VAS 操作类型及其计量单位。

模块安装后，用户可以从 Warehouse 菜单进入 Dashboard、PDA 或 Desktop
Web 列表。

## 权限

### VAS User

普通操作人员可以：

- 创建和编辑自己的草稿；
- 添加、修改和删除草稿明细；
- 上传和删除草稿附件；
- 保存、提交或作废允许操作范围内的作业单；
- 在 PDA 中使用当前登录用户作为操作员。

### VAS Manager

管理人员拥有更高的数据访问和业务管理权限，具体范围以模块中的 ACL、
record rule 和服务端状态校验为准。

所有权限变更和业务数据变更必须通过 Odoo ORM、界面或服务端 action 完成，
不得直接修改 PostgreSQL 数据。

## 业务流程

### Desktop Web

1. 新建作业单；
2. 选择关联对象类型；
3. 输入或解析关联单据号；
4. 选择操作员；
5. 添加一条或多条作业明细；
6. 可选上传作业凭证；
7. 保存草稿；
8. 确认数据后提交；
9. 如需终止草稿，填写原因后作废。

### Android PDA

PDA 页面针对仓库现场操作优化：

- 当前登录操作员自动带出并只读；
- 支持扫描或手工输入关联单据号；
- 支持拍照和相册多选；
- 提供固定底部操作栏；
- Header 显示当前作业单号和状态；
- 已提交或已作废单据进入只读状态。

已完成目标设备验证：

- 设备：东集（Chainway）Cruise GE2；
- Android：11；
- 浏览器：Firefox；
- 扫码、拍照、相册多选：通过；
- 弱网、超时、重复点击、并发修改：通过。

## 状态和单据关联

### 草稿

草稿允许暂时不关联 Warehouse Order，可以先录入作业明细并保存。
这适用于现场先记录作业、稍后补充业务单据的场景。

### 提交

提交时必须：

- 解析并绑定有效的入库、出库或调拨单据；
- 至少存在一条有效作业明细；
- 通过服务端 `action_submit()` 状态校验；
- 写入提交人、提交时间和业务快照。

前端不复制服务端锁、状态机或快照逻辑，所有最终业务校验由服务端完成。

### 作废

草稿可以作废，但必须填写作废原因。已提交或已作废单据不允许通过 PDA
直接修改核心字段。

## 技术结构

模块采用 Odoo 原生模型、视图、ACL、record rule、服务端 action，以及
Odoo 18 OWL/JavaScript 前端实现：

- `models/`：VAS 作业单、作业明细和生命周期逻辑；
- `views/`：Desktop Web 视图、菜单和前端 client action；
- `security/`：用户组、ACL 和 record rule；
- `static/src/js/`：Dashboard 和 PDA OWL action；
- `static/src/xml/`：OWL 模板；
- `static/src/scss/`：PDA 和 Dashboard 样式；
- `static/tests/`：前端 Hoot 测试；
- `tests/`：Python 集成回归测试。

本模块不新增 DDD 分层，不引入独立 PDA 后端、独立 API、第二套状态机
或第二套附件系统。

## 验证

已执行的验证包括：

- Python 语法检查；
- JavaScript 语法检查；
- XML 解析；
- SCSS 编译；
- `git diff --check`；
- 隔离数据库中的提交和补单提交回归；
- Desktop 浏览器 smoke verification；
- Android PDA 人工验证。

前端 Hoot 测试已覆盖状态显示、新建清理、明细必填、未关联 Draft 创建和
作废原因校验。Odoo 全量前端测试页面还包含与本模块无关的浏览器环境测试，
因此不能将其全量结果等同于本模块的独立测试结果。

## 相关文档

- [CC-04 Contract](../../docs/context/Coding/cc_warehouse_vas_04.md)
- [IHR](../../docs/context/Coding/ihr_warehouse_vas_04.md)
- [ATR](../../docs/context/Coding/atr_warehouse_vas_04.md)
- [HVR](../../docs/context/Coding/hvr_warehouse_vas_04.md)
- [TDD v1.1](../../docs/context/Designing/tdd_warehouse_vas_v1.1.md)
