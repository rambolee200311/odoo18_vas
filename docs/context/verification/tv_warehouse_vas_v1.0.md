# Technical Verification — Warehouse VAS

## 1. Metadata

- Project: 仓库库内增值作业单（VAS Order）
- Odoo Version: 18.0+e-20250619
- Verification Date: 2026-09-04
- SRS Baseline: SRS v1.0.0 Frozen
- Verification Scope: TV-01 Warehouse Order Binding; TV-02 PDA Feasibility; TV-03A Attachment; TV-03B Audit
- Investigator: Copilot
- DDD: SKIP（本项目不需要 DDD）

本记录是 Technical Verification，不是 TDD、完整技术方案或实现计划。本文只记录验证得到的事实及其对 TDD 的约束。

## 2. Executive Summary

| TV | Topic | Result | Evidence Level | TDD Impact |
|----|------|--------|----------------|------------|
| TV-01 | Warehouse Order Binding | VERIFIED | CODE VERIFIED + RUNTIME VERIFIED | VAS 必须把三类 Warehouse Order 作为业务关联对象；使用模型类型和 `billno` 识别，不能替换为 `stock.picking`。 |
| TV-02 | PDA Feasibility | STANDARD WEB SUFFICIENT | CODE VERIFIED + INFERRED | 优先使用 Odoo 18 标准 Web Form；小屏 x2many 和原生文件输入已有支持，不需要独立 PDA App。 |
| TV-03A | Attachment | NATIVE SUFFICIENT | CODE VERIFIED + RUNTIME VERIFIED | 使用 `ir.attachment` 原生关联和标准附件上传能力，不设计自定义文件存储。 |
| TV-03B | Audit | NATIVE + SMALL EXTENSION | CODE VERIFIED + RUNTIME VERIFIED | 使用 Odoo 元数据和 `mail.thread` tracking；VAS 自身的提交/反提交/作废审计字段和动作由 TDD 明确定义，不建立自定义 Audit Framework。 |

## 3. TV-01 Warehouse Order Binding

### Findings

#### 3.1 三个目标模型真实存在

三个模型均已在当前运行的 Odoo 18 Registry 中注册，所属模块均为 `worlddepot`：

| Model | Python Class | `_name` | Module | `_rec_name` |
|-------|--------------|---------|--------|-------------|
| 入库订单 | `InboundOrder` | `world.depot.inbound.order` | `worlddepot` | `billno` |
| 出库订单 | `OutboundOrder` | `world.depot.outbound.order` | `worlddepot` | `billno` |
| 调拨订单 | `TransferOrder` | `world.depot.transfer.order` | `worlddepot` | `billno` |

三个类的源码都显式继承：

```python
["mail.thread", "mail.activity.mixin"]
```

Runtime 中三个模型的 `ir.model.is_mail_thread` 和 `is_mail_activity` 均为 `True`。

#### 3.2 没有统一 Warehouse Order 抽象

CODE VERIFIED：

- 三个模型分别直接继承 `models.Model`；
- 没有共同的项目内父类、Mixin 或抽象 Warehouse Order 模型；
- `model._inherits` 在 Runtime 中均为空；
- 三个模型的 `_sql_constraints` 均为空；
- 没有发现统一的 Warehouse Order 查询接口或统一的 `name_get` 实现。

因此，不能因为三个模型都有相似字段，就在 TV 阶段假设它们已经共享统一父类或公共接口。

#### 3.3 Odoo 18 的显示名来源

CODE VERIFIED：

- 三个模型都设置 `_rec_name = 'billno'`；
- 当前源码没有自定义 `name_get`；
- Runtime 中三个模型均没有独立的 `name_get` 方法，`name_search` 使用 `BaseModel.name_search`；
- Runtime 的 `display_name` 是非存储只读字段，业务模型的显示名依据 `_rec_name` 解析到 `billno`。

因此，面向用户的订单显示值和标准 Many2one 搜索显示，应以 `billno` 为业务订单号，而不是 `reference`、`stock.picking.name` 或数据库 ID。

### Evidence

#### 入库订单

- File: `addons/worlddepot/models/inbound_order.py`
- `InboundOrder._name`：第 10-14 行
- `billno`：第 28 行
- `project`、`owner`、`warehouse`：第 34-49 行
- `reference`：第 52 行
- `state`：第 75-83 行
- `create()` 通过 `ir.sequence` 生成 `billno`：第 201-206 行
- `action_confirm`、`action_cancel`、`action_unconfirm`：第 220-320 行
- 入库单按 `project + reference` 的 Python constraint 检查非取消记录重复：第 160-175 行

#### 出库订单

- File: `addons/worlddepot/models/outbound_order.py`
- `OutboundOrder._name`：第 19-23 行
- `billno`：第 37 行
- `project`、`owner`、`warehouse`：第 41-48 行
- `reference`：第 52 行
- `state`：第 110-118 行
- `create()` 通过 `ir.sequence` 生成 `billno`：第 234-241 行
- `action_confirm`、`action_cancel`、`action_unconfirm`：第 243-334 行

#### 调拨订单

- File: `addons/worlddepot/models/transfer_order.py`
- `TransferOrder._name`：第 10-14 行
- `billno`：第 31 行
- `project`、`owner`、`warehouse`：第 35-46 行
- `reference`：第 49 行
- `state`：第 61-69 行
- `create()` 通过 `ir.sequence` 生成 `billno`：第 78-82 行
- `action_confirm`、`action_cancel`、`action_unconfirm`：第 91-145 行
- `reference` 的项目内非取消重复检查：第 155-167 行

#### 运行时验证

验证方法：

```text
venv/bin/python odoo-bin shell -c odoo.conf --no-http
```

通过 Odoo ORM 读取 Registry 和 `ir.model`，未直接连接 PostgreSQL。

实际观察结果：

- 三个模型均可通过 `env[model_name]` 取得；
- 三个模型的 `_module` 均为 `worlddepot`；
- `_rec_name` 均为 `billno`；
- 三个模型均包含 `billno`、`reference`、`project`、`owner`、`warehouse`、`state`、`create_uid`、`create_date`、`write_uid`、`write_date`；
- 入库和出库包含 `status`，调拨没有 `status`；
- 三个模型的 `state` 值分别为：
  - 入库：`new / confirm / cancel`
  - 出库：`new / confirm / cancel`
  - 调拨：`new / confirm / cancel`
- 三个模型的 `_sql_constraints` 均为空；
- 三个模型的 `_inherits` 均为空；
- 当前数据库中三个模型的记录数均为 `0`。

### Model Comparison

| Fact | Inbound | Outbound | Transfer | TDD Relevance |
|------|---------|----------|----------|---------------|
| Business model | `world.depot.inbound.order` | `world.depot.outbound.order` | `world.depot.transfer.order` | 必须按模型分别关联或分别验证 |
| Order number | `billno` | `billno` | `billno` | 推荐业务识别字段 |
| Other reference | `reference` | `reference` | `reference` | 不是安全的跨模型主识别字段 |
| Project | Required Many2one | Required Many2one | Required Many2one | 可作为业务归属上下文 |
| Owner/customer-like field | `owner` related from project | `owner` related/stored from project | `owner` related from project | 不应把它误认为 VAS Operator |
| Warehouse | Stored Many2one | Stored Many2one | Stored Many2one | 当前模型具备仓库归属字段，但直接 Many2one 关联不依赖它才能定位 |
| Company | No explicit model field found | No explicit model field found | No explicit model field found | 不能假设存在显式公司隔离字段 |
| State | `new/confirm/cancel` | `new/confirm/cancel` | `new/confirm/cancel` | 不能复用为 VAS 状态 |
| Secondary status | Present | Present | Absent | TDD 必须按模型差异处理 |
| Chatter/activity | Yes | Yes | Yes | 可作为既有记录的追踪能力 |
| SQL unique constraint | None | None | None | 订单号不能仅依赖数据库唯一约束 |

### Risks / Differences

#### 3.4 订单号字段和唯一性风险

CODE VERIFIED：

- 三个模型的业务订单号字段均为 `billno`；
- `billno` 由 `ir.sequence` 生成且只读；
- 序列定义分别使用：
  - 入库：`seq.inbound.order`，前缀 `IO%(year)s%(month)s%(day)s`
  - 出库：`seq.outbound.order`，前缀 `OO%(year)s%(month)s%(day)s`
  - 调拨：`seq.transfer.order`，前缀 `TO%(year)s%(month)s%(day)s`
- 三个模型没有 SQL 唯一约束。

结论：

- 在当前序列配置下，自动生成的 `billno` 带有不同类型前缀，跨三类模型发生自动生成同号的风险较低；
- 但系统没有跨模型或单模型数据库唯一约束，不能把“唯一”当成已经由数据库绝对保证；
- `reference` 不是可靠的跨模型识别字段：入库和调拨有不同范围的 Python 检查，出库未发现同等的 reference 唯一 constraint；
- 当前数据库为空，无法用真实记录验证历史数据是否存在重复号。

TDD 应采用“关联对象类型 + `billno`”作为扫码/输入的业务识别上下文。不能仅凭裸订单号在三个模型之间盲查。

#### 3.5 warehouse / company 上下文

CODE VERIFIED + RUNTIME VERIFIED：

- 三个模型都有 `warehouse`；
- 三个模型都有必填 `project`，并通过项目获得 `owner`；
- 三个模型没有显式 `company_id` 字段；
- 直接的模型类型和 `billno` Many2one 关系可以唯一确定目标记录，不需要依靠 warehouse/company 才能完成 ORM 定位。

INFERRED：

- 如果未来不使用显式 Many2one，而只保存订单号字符串，则 warehouse 或其他业务上下文可能需要参与消歧；
- 当前 SRS 要求用户先选择关联对象类型，因此“类型 + 订单号”比“订单号全局搜索”更可靠。

#### 3.6 取消/无效语义

CODE VERIFIED：

- 三个模型均有 `cancel` 状态；
- 入库、出库、调拨的取消动作只允许在各自模型定义的业务条件满足时执行；
- 入库和出库在已确认订单存在已完成库存执行时可能阻止取消；
- 调拨也有自身取消限制和库存单据处理。

因此：

- `state = cancel` 可以被识别为既有 Warehouse Order 的取消/无效状态；
- `new` 和 `confirm` 是既有 Warehouse Order 的自身生命周期，不能直接映射成 VAS 的 `draft` 和 `submitted`；
- SRS 没有要求 VAS 订单随 Warehouse Order 状态自动变化，TDD 不得自行增加该联动。

#### 3.7 订单号定位和扫码

CODE VERIFIED：

- 现有模型的标准搜索字段包括 `billno`、`reference`、`project` 和 `warehouse`；
- 未发现这三个 Warehouse Order 上的 `barcode` 或 `qr_code` 字段；
- 未发现针对这三个模型的统一扫码解析逻辑；
- `stock_barcode` 是 `worlddepot` 的依赖，但该依赖不证明 Warehouse Order 已具备订单号扫码业务。

INFERRED：

- PDA 扫描设备作为键盘输入，将字符和回车送入标准文本输入框时，可以沿用普通输入路径；
- 实际扫码枪、浏览器和设备配置尚未在本次 TV 中运行验证。

### Conclusion

**TV-01: VERIFIED / PASS**

VAS 可以可靠关联这三类 Warehouse Order，但可靠性来自：

```text
关联对象类型 + billno
```

以及对应的明确模型关系，而不是来自 `stock.picking`、裸字符串或 `reference` 的全局唯一性。

明确结论：

1. VAS 的业务关联对象是：
   - `world.depot.inbound.order`
   - `world.depot.outbound.order`
   - `world.depot.transfer.order`
2. 推荐业务识别字段为各模型的 `billno`；
3. 不得把 `stock.picking`、`stock.move` 或 `stock.quant` 替换为 VAS 的业务关联对象；
4. 订单号没有数据库唯一约束，必须保留类型上下文；
5. 三个模型没有统一父类或公共接口，TDD 不得假设存在统一 Warehouse Order 抽象；
6. `state = cancel` 是既有订单的取消/无效状态，但不能复用为 VAS 状态；
7. 三个模型都有 warehouse，但没有显式 company 字段；
8. 当前没有可直接复用的三模型统一条码字段或扫码解析器。

### TDD Constraints

- 使用 Warehouse Order 模型作为业务引用，不替换成库存执行层模型；
- 关联入口必须保留对象类型上下文；
- 使用 `billno` 作为订单显示和业务识别依据；
- 不使用 `reference` 作为跨模型唯一主键；
- 不基于三个模型的相似性创建统一父类或修改既有模型；
- 不能复用既有订单的 `state` 作为 VAS 状态；
- 入库、出库、调拨的字段差异必须在 TDD 中显式处理；
- 如果 TDD 要求“仅输入订单号、不先选对象类型”，必须补充消歧验证或回到业务确认；
- “其他订单”是否需要绑定调拨实体，当前 SRS 没有明确规定，TDD 不得擅自加入第四种业务类型。

## 4. TV-02 PDA Feasibility

### Findings

#### 4.1 标准 Odoo 18 Web Form 已有小屏适配路径

CODE VERIFIED：

- File: `odoo/addons/web/static/src/views/form/form_controller.js`
- `loadSubViews()` 第 54-73 行接收 `isSmall`；
- 当 x2many 视图同时声明多种视图模式时，小屏自动选择 `kanban`，非小屏选择 `list`。

CODE VERIFIED：

- File: `odoo/addons/web/static/src/views/form/form_controller.scss`
- 第 15-53 行提供移动尺寸下的单列布局和字段宽度适配；
- 第 55 行以后包含标准表单的编辑和 x2many 样式；
- Odoo Web 使用 `env.isSmall` 判定小屏环境。

这说明标准 Form 并不是仅针对桌面布局，已有移动尺寸处理机制。

#### 4.2 SRS 最小流程的标准能力映射

| SRS 场景 | Odoo 18 事实 | Evidence Level |
|----------|--------------|----------------|
| 新建、保存草稿、提交、反提交 | 标准 Form 可调用模型 Business Action | INFERRED，具体 VAS 模型尚未实现 |
| 选择订单类型 | 标准 Selection/Many2one 字段能力 | CODE VERIFIED（框架能力） |
| 扫描/输入订单号 | 标准文本输入可接收键盘式扫描器输入 | INFERRED，实际设备未运行 |
| 选择操作员 | 标准 Many2one/用户字段能力 | CODE VERIFIED（框架能力） |
| 新增/删除 one2many 明细 | 标准 x2many CRUD 能力 | CODE VERIFIED |
| 小屏显示 one2many | 小屏自动选择 Kanban 子视图 | CODE VERIFIED |
| 选择操作类型和自动显示单位 | 标准字段依赖/业务方法可承载 | INFERRED，具体 VAS 模型尚未实现 |
| 输入数量和备注 | 标准数值/文本字段 | CODE VERIFIED（框架能力） |
| 上传图片/视频 | 原生文件输入支持多文件 | CODE VERIFIED |

#### 4.3 没有发现必须开发独立 PDA UI 的技术证据

当前 Odoo 18 源码已经提供：

- 标准小屏 Form 渲染；
- x2many 小屏 Kanban 回退；
- 标准 Many2one、Selection、数值和文本字段；
- 原生文件输入和多文件上传；
- `stock_barcode` 依赖及 Odoo Web Barcode 相关能力。

未发现要求必须使用独立前端、独立 PDA App 或独立移动端路由的技术阻塞。

### Blocking UX Issues

本次 TV 没有运行真实 PDA 硬件和浏览器 UI，因此以下内容不是 RUNTIME VERIFIED：

- 具体扫码枪/浏览器组合是否会自动将回车正确提交给目标订单号字段；
- 现场设备的屏幕尺寸、横竖屏和输入法行为；
- 多条明细在具体设备上需要的点击次数；
- 设备是否将文件选择器直接呈现为相机入口；
- 真实网络条件下的上传等待体验。

这些是 TDD/UI 验证事项，不构成必须开发独立 PDA UI 的证据。

### Conclusion

**TV-02: STANDARD WEB SUFFICIENT / PASS**

以 SRS 定义的业务能力为准，Odoo 18 标准 Web Form 已提供足够的能力承载 PDA 极简录单：

- 标准表单具备小屏适配；
- x2many 在小屏有 Kanban 视图路径；
- 文本输入可承接键盘式扫码器输入；
- 文件输入支持图片/视频多文件；
- 保存、提交、反提交等动作可由同一份业务模型提供。

本结论不表示任何具体设备的现场 UX 已完成验收；它表示没有技术事实证明必须开发独立 PDA App。

### TDD Constraints

- 优先采用同一套 Odoo Web 业务表单，不建立独立 PDA 数据模型或独立业务记录；
- PDA 和 Web 必须操作同一份 VAS Order 数据；
- PDA 小屏应提供适用的 x2many 子视图，不能只复制桌面表格；
- 扫码应首先按键盘输入路径验证，不得因为“PDA”名称直接引入专用前端；
- 若真实设备验证发现输入法、扫码或明细交互存在阻塞，再以最小范围 Web 定制处理；
- 不得把未运行的真实设备行为写成已验证事实。

## 5. TV-03 Attachment & Audit

### 5.1 Attachment

#### Findings

Odoo 18 原生附件模型 `ir.attachment` 已支持将文件关联到任意业务模型记录：

```text
res_model = 业务模型名称
res_id    = 业务记录 ID
```

项目现有代码也已经使用标准附件和二进制字段：

- `addons/worlddepot/views/inbound_order.xml` 使用 `widget="binary"`；
- `addons/worlddepot/views/outbound_order.xml` 使用 `widget="binary"`；
- 入库、出库、调拨表单都使用标准 `<chatter/>`；
- 出库模型中的 `pod_file` 使用 `attachment=True`。

Odoo 18 Web 原生 `FileInput`：

- File: `odoo/addons/web/static/src/core/file_input/file_input.js`
- 第 22-43 行定义标准文件输入组件；
- 默认上传路由为 `/web/binary/upload_attachment`；
- 第 60-72 行将 `resModel` 和 `resId` 作为业务关联信息；
- 第 86-99 行执行上传并清理 input；
- 支持 `multiUpload` 属性。

Odoo 18 Web 原生 `Many2ManyBinaryField`：

- File: `odoo/addons/web/static/src/views/fields/many2many_binary/many2many_binary_field.js`
- 第 10-26 行将文件记录作为 x2many 数据管理；
- 第 48-58 行逐个保存上传文件；
- 第 60-65 行支持删除单个文件；
- 第 68-95 行注册 `many2many_binary` 字段并支持多个文件。

#### Evidence

RUNTIME VERIFIED：

通过 Odoo ORM 检查：

- `env['ir.attachment']` 真实存在；
- `ir.attachment.res_model` 类型为 `char`；
- `ir.attachment.res_id` 类型为 `many2one_reference`；
- `name` 为必填；
- `datas` 为 binary；
- `mimetype` 可记录文件 MIME 类型；
- 当前数据库有 161 条附件记录；
- 未创建、修改或删除任何业务记录。

CODE VERIFIED：

- 原生附件上传支持多文件；
- 原生附件能够绑定指定 `res_model + res_id`；
- 原生附件能力不要求自建文件存储；
- 二进制字段和附件字段在当前项目已有使用先例。

INFERRED：

- 图片和视频均可作为 Odoo 附件上传；
- Web 端可以通过标准附件下载/查看路径访问文件；
- 具体视频内嵌播放行为取决于浏览器和 MIME 类型，不是 SRS 的独立播放器要求。

### Conclusion

**TV-03A: NATIVE SUFFICIENT / PASS**

Odoo 18 原生 `ir.attachment`、标准文件输入和多文件字段足以满足：

- 图片；
- 视频；
- 多附件；
- Web 上传；
- PDA 浏览器上传；
- 与单张 VAS Order 关联；
- 详情页查看或下载。

### TDD Constraints

- 使用 Odoo 原生 `ir.attachment`；
- 通过 `res_model + res_id` 关联 VAS Order；
- 使用标准文件上传/附件字段能力；
- 不设计自定义文件存储系统；
- 不在 SRS 未定义的情况下增加附件大小、格式或数量配置子系统；
- 若需要相机快捷入口，应作为最小 Web 交互增强验证，不得改变附件存储方式。

### 5.2 Audit

#### Findings

#### Odoo 自动元数据

RUNTIME VERIFIED：

三个既有 Warehouse Order 均自动包含并维护：

- `create_uid`
- `create_date`
- `write_uid`
- `write_date`

这些字段来自 Odoo ORM，不需要业务模型手工实现。

#### Chatter 和字段 tracking

CODE VERIFIED + RUNTIME VERIFIED：

- 三个既有订单模型源码显式继承 `mail.thread` 和 `mail.activity.mixin`；
- Runtime 的 `ir.model.is_mail_thread`、`is_mail_activity` 均为 `True`；
- 模型包含 `message_ids`、`message_follower_ids`、`message_attachment_count`；
- 既有模型有多个 `tracking=True` 字段，包括 `state`；
- 对应表单视图包含 `<chatter/>`；
- Odoo `mail.thread` 可记录字段变更消息和跟踪值。

#### 对 SRS 审计要求的覆盖判断

| SRS 审计事实 | 原生能力 | TV 判断 |
|--------------|----------|----------|
| 创建人/创建时间 | `create_uid` / `create_date` | NATIVE |
| 最后修改人/修改时间 | `write_uid` / `write_date` | NATIVE |
| 状态变化 | `mail.thread` + `tracking=True` | NATIVE |
| 提交人/提交时间 | 需要 VAS 业务字段及提交动作赋值 | SMALL EXTENSION |
| 反提交操作人/时间 | 需要 VAS 业务动作和追踪记录 | SMALL EXTENSION |
| 作废操作人/时间 | 需要 VAS 业务动作和追踪记录 | SMALL EXTENSION |
| 详情页查看审计 | chatter 原生能力可承载 | NATIVE + VIEW CONFIGURATION |

#### Evidence

CODE VERIFIED：

- File: `addons/worlddepot/models/inbound_order.py`
  - 第 10-14 行继承 `mail.thread` / `mail.activity.mixin`；
  - 第 75-83 行 `state` 定义；
  - 第 255-262 行确认动作写入状态和确认人/时间；
- File: `addons/worlddepot/models/outbound_order.py`
  - 第 19-23 行继承 mail mixins；
  - 第 110-118 行 `state` 定义；
  - 第 260-267 行确认动作写入状态和确认人/时间；
- File: `addons/worlddepot/models/transfer_order.py`
  - 第 10-14 行继承 mail mixins；
  - 第 61-69 行 `state` 定义；
  - 第 91-102 行确认动作写入状态和确认人/时间；
- File: `addons/worlddepot/views/transfer_order_views.xml`
  - 第 134-141 行显示确认审计字段和 `<chatter/>`。

RUNTIME VERIFIED：

- 三个模型均被识别为 mail thread/activity model；
- 三个模型均拥有标准 chatter 和 ORM 审计字段；
- 通过 `model._track_get_fields()` 可读取现有 tracking 字段集合；
- 未创建或修改任何业务记录。

### Conclusion

**TV-03B: NATIVE + SMALL EXTENSION / PASS**

Odoo 原生能力足以提供基础审计能力，但 SRS 要求的 VAS 业务动作仍需要在 VAS 自身模型中显式记录：

- `Creator` / 创建时间；
- `Submitter` / 提交时间；
- 反提交操作人/时间；
- 作废操作人/时间；
- 状态变化和 chatter 追踪。

这属于 VAS 模型字段、Business Action 和 View 配置的最小扩展，不需要自定义 Audit Framework。

### TDD Constraints

- VAS 模型应使用 Odoo 自动元数据字段；
- VAS 的 `state` 必须使用自己的状态机；
- 提交、反提交、作废必须是显式 Business Action；
- 关键状态字段应使用 `mail.thread` tracking；
- 需要的提交人、提交时间和动作审计字段应在 VAS 自身模型中定义；
- 不得通过直接写状态字段伪造提交、反提交或作废；
- 不新建独立审计基础设施，除非后续有明确技术事实证明原生能力不足。

## 6. Open Technical Questions

| ID | Question | Why Unresolved | Required Action | Blocks TDD |
|----|----------|----------------|-----------------|------------|
| OQ-01 | SRS 中“其他订单”是否业务上包含调拨订单实体？ | SRS 将对象限定为入库/出库/其他，但未把调拨单列为第四种对象；源码存在独立 Transfer Order。 | TDD 默认将 `other` 作为非实体线索；若需实体绑定，先补充业务确认或更新后续 SRS。 | No（除非要求把调拨作为显式第四类） |
| OQ-02 | 现场扫码设备、浏览器和输入法组合是否能稳定把订单号输入到字段？ | 本次未接入真实 PDA/扫码硬件。 | 在 TDD 后的最小 UI/设备验证中实测；不改变当前标准 Web 结论。 | No |
| OQ-03 | 业务是否要求视频在浏览器内嵌播放，而非详情页下载/标准查看？ | SRS 只要求 Web 查看附件，没有定义播放器行为。 | 以标准附件查看/下载为基线；若要求内嵌播放，另行形成明确需求。 | No |
| OQ-04 | 业务是否要求跨模型对 `billno` 建立全局唯一约束？ | 当前三个模型没有 SQL 唯一约束，且当前数据库无订单数据。 | TDD 使用“对象类型 + billno”消歧；若要求裸订单号全局唯一，应回到业务确认。 | No |

## 7. Technical Facts for TDD

### FACT-01

三个 Warehouse Order 模型真实存在于 `worlddepot` 模块：

```text
world.depot.inbound.order
world.depot.outbound.order
world.depot.transfer.order
```

Evidence: CODE VERIFIED + RUNTIME VERIFIED；见 TV-01 Evidence。

### FACT-02

三个 Warehouse Order 的业务显示名和订单号字段均为 `billno`，而不是 `reference` 或 `stock.picking.name`。

Evidence: CODE VERIFIED（各模型 `_rec_name = 'billno'`）+ RUNTIME VERIFIED。

### FACT-03

三个 Warehouse Order 均有 `project`、`owner`、`warehouse` 字段；均没有显式 `company_id` 字段。

Evidence: CODE VERIFIED + RUNTIME VERIFIED。

### FACT-04

三个 Warehouse Order 的 `state` 值均为 `new / confirm / cancel`，但三者的状态不是 VAS 状态。

Evidence: CODE VERIFIED + RUNTIME VERIFIED。

### FACT-05

三个 Warehouse Order 没有 `_sql_constraints`，当前代码中没有可证明的跨模型 `billno` 全局唯一约束。

Evidence: RUNTIME VERIFIED（`_sql_constraints = []`）+ CODE VERIFIED（各自 sequence 生成）。

### FACT-06

当前没有发现三个 Warehouse Order 共享的统一父类、Mixin 或公共查询接口。

Evidence: CODE VERIFIED + RUNTIME VERIFIED（`_inherits = {}`）。

### FACT-07

当前源码没有发现这三个 Warehouse Order 上可直接复用的 `barcode` 或 `qr_code` 字段，也没有三模型统一扫码解析器。

Evidence: CODE VERIFIED。

### FACT-08

Odoo 18 标准 Form 在小屏环境支持布局适配，并可为 x2many 选择 Kanban 子视图。

Evidence: CODE VERIFIED；`odoo/addons/web/static/src/views/form/form_controller.js` 第 54-73 行，`form_controller.scss` 第 15-53 行。

### FACT-09

Odoo 18 标准附件能力通过 `ir.attachment` 的 `res_model + res_id` 关联业务记录，并支持多文件上传。

Evidence: CODE VERIFIED + RUNTIME VERIFIED。

### FACT-10

Odoo ORM 自动提供 `create_uid`、`create_date`、`write_uid`、`write_date`；`mail.thread` 和 `tracking=True` 可提供 chatter/字段变更追踪。

Evidence: CODE VERIFIED + RUNTIME VERIFIED。

### FACT-11

现有 `worlddepot` 模块依赖 `base`、`mail`、`stock`、`stock_barcode`、`project` 等 Odoo 原生模块；没有发现为本 TV 必须引入新的第三方技术栈的证据。

Evidence: CODE VERIFIED；`addons/worlddepot/__manifest__.py` 第 20-21 行。

## 8. TV Gate

- TV-01: PASS
- TV-02: PASS
- TV-03A: PASS
- TV-03B: PASS

### Overall

**READY FOR TDD**

### Gate rationale

1. 三个 Warehouse Order 的真实模型、模块、订单号字段、状态和关联上下文已通过源码和 Runtime 确认；
2. 已确认 VAS 的业务对象应保持为 Warehouse Order，不能替换为 `stock.picking`；
3. 已确认三个模型没有统一父类或全局订单号唯一约束，TDD 可以据此避免错误抽象；
4. Odoo 18 标准 Web 已提供 PDA 所需的核心表单、x2many、小屏和文件上传能力；
5. 原生附件和审计能力足以承载 SRS，剩余工作是 VAS 自身动作和字段的正常 TDD 设计；
6. 未验证的问题均不会迫使项目改变 Frozen SRS 的业务含义，也不会迫使 TDD 转向错误的关联对象；
7. 没有发现必须引入独立 PDA App、自定义文件存储或自定义 Audit Framework 的技术证据。

