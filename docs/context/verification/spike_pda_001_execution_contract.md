# SPIKE-PDA-001 — Warehouse VAS OWL/JS Frontend Feasibility

> 文档版本：v1.0 Draft  
> 状态：SPIKE CONTRACT — PENDING HUMAN REVIEW  
> 模块：`wd_warehouse_value_add`  
> 技术基线：Odoo 18 Enterprise `18.0+e-20250619`  
> 上游：Frozen SRS v1.0.0、TDD v1.0.0 Frozen、TDD v1.1 Draft  
> 相关历史基线：CC-01、CC-02、CC-03 已完成并集成  
> 后续：TDD v1.1 Freeze；CC-04（本 Spike 不创建）

本文是 SPIKE-PDA-001 的执行契约草案。本文只授权最小技术可行性验证，
不授权完整 PDA 功能开发，不授权 CC-04，不修改既有业务实现。

---

## 1. Human Review Decision

Human Review 已确认：

1. TDD v1.1 的技术架构方向批准；
2. PDA 必须采用专用 OWL/JS 表现层，不再重新评估该方向；
3. Dashboard 是模块默认首页，提供 PDA 作业录入和 Web 作业单管理两个入口；
4. CC-01/02/03 保持 Frozen Historical Baseline；
5. 授权执行 SPIKE-PDA-001；
6. TDD v1.1 的具体技术实现细节等待 Spike 证据；
7. 本次不启动 CC-04，不进行完整 PDA 功能开发。

---

## 2. Spike Goal

验证专用 OWL/JS PDA Frontend 在当前 Odoo 18 Enterprise 环境中的最小
落地路径，为 TDD v1.1 Freeze 提供技术证据。

Spike 只回答：

```text
Odoo 18 中如何安全地落地既定的 OWL/JS PDA Frontend 架构？
```

Spike 不回答：

```text
完整 PDA 产品是否已经开发完成；
CC-04 的全部实现是否已经完成；
真实仓库业务流程是否已经完成最终验收。
```

---

## 3. Non-Negotiable Boundaries

### 3.1 Must Preserve

Spike 必须保留：

- `wd.vas.order`；
- `wd.vas.order.line`；
- `wd.vas.operation.type`；
- Submit / Unsubmit / Cancel；
- Warehouse Order association；
- billno 和 warehouse snapshot；
- locking；
- ACL / record rules；
- 服务端 action permission；
- Desktop Web；
- attachment relation；
- chatter / audit；
- CC-01/02/03 历史实现和证据。

### 3.2 Must Not Introduce

Spike 不得引入：

- 第二套业务模型；
- 第二套状态机；
- 第二套权限模型；
- 第二套附件关系；
- 独立 PDA Backend；
- 独立业务 API；
- queue、Redis、事件总线或离线同步；
- 客户快照；
- Warehouse Order 模型修改；
- CC-04 生产实现；
- 新的业务语义。

### 3.3 Temporary Experiment Rule

如需临时验证代码，必须满足：

1. 与正式模块代码隔离；
2. 文件路径在本契约允许的临时范围内；
3. 文件明确标记为 `SPIKE-PDA-001`；
4. 不修改生产模块的业务模型、视图、安全或测试；
5. 不被模块 manifest 或正式 assets 永久引用；
6. 验证完成后清理；
7. 清理后通过文件清单、工作区状态和 diff 检查证明没有遗留；
8. 不得直接将 Spike 文件作为 CC-04 生产代码合入。

### 3.4 Isolated Environment and Test Data

Spike 必须使用隔离测试数据库及临时实验环境，不得在现有业务数据库中
验证 Save Draft、Submit 或附件上传。

允许在隔离环境中：

- 创建、修改、提交和删除测试 VAS 记录；
- 创建、上传、读取和删除测试附件；
- 安装或加载仅用于 Spike 的临时实验代码；
- 使用临时配置、临时 assets 和临时服务。

禁止：

- 修改现有业务数据库中的业务记录或附件；
- 将临时 OWL/JS 代码合入正式模块；
- 将临时实验环境作为生产环境或 CC-04 实现；
- 用隔离环境中的测试结果替代真实目标 PDA HVR。

实验结束后必须删除临时环境和测试数据，并保留可复核的环境、
数据清理和结果证据。

---

## 4. Verification Questions

### VQ-001 — OWL Client Action

在当前 Odoo 18 环境中，如何注册并加载最小 OWL/JS client action，
使 PDA Frontend 可以在现有 Odoo 会话中启动？

必须确认：

- 注册位置；
- action 类型；
- 入口参数；
- 会话和用户上下文；
- 失败时的可观察错误。

### VQ-002 — Dashboard Navigation

如何实现：

```text
模块根菜单 → Dashboard
Dashboard → PDA Action
Dashboard → Web List Action
```

Dashboard 只作为入口选择器，不承载业务逻辑。

### VQ-003 — PDA Direct Entry

确认 PDA Action 是否可以：

- 由菜单直接进入；
- 被用户收藏后直接打开；
- 不经过 Dashboard；
- 复用同一 Odoo session、用户、权限和上下文。

### VQ-004 — Frontend Assets

确认专用 OWL/JS PDA Frontend 所需的：

- JavaScript；
- XML template；
- SCSS；
- asset bundle；
- module loading；

在当前 Odoo 18 环境中的最小声明和加载方式。

具体目录、bundle 名称和 API 在 Spike 前不得假定。

### VQ-005 — ORM/RPC Read

确认 PDA Frontend 可以通过标准 Odoo 技术路径读取现有：

```text
wd.vas.order
```

必须确认：

- 使用当前用户上下文；
- 遵守 ACL 和 record rules；
- 不引入独立业务 API；
- 读取失败可被前端识别。

### VQ-006 — One-Line Interaction

验证最小明细交互：

1. 读取一张 Draft；
2. 添加一条明细；
3. 选择 Operation Type；
4. 显示自动带出的 Unit；
5. 编辑 Quantity / Time；
6. 将结果交给现有保存路径。

不要求完成全部多行编辑、复杂删除或生产级卡片系统。

### VQ-007 — Existing Save Draft / Submit

确认 PDA Frontend 可以：

- 保存 Draft；
- 调用现有 Submit 服务端能力；
- 接收服务端成功结果；
- 接收服务端 ValidationError / AccessError；
- 在成功或失败后刷新服务端状态。

不得在前端复制 Submit 校验、状态机、锁或快照逻辑。

### VQ-008 — Billno Input

验证：

- billno 手工输入；
- 目标 PDA 键盘式扫码输入；
- 扫码结果写入 billno 输入；
- 输入失败或解析失败的可观察反馈。

摄像头扫码能力如无法在目标设备上确认，必须记录为设备能力限制，
不得伪装为已实现。

### VQ-009 — Camera / File Selection

验证目标 Android PDA 浏览器是否能完成最小的：

- 相机调用或拍照入口；
- 文件选择；
- 图片选择；
- 多文件选择的能力边界。

Spike 不要求完成完整相册管理、视频采集或生产级媒体处理。

### VQ-010 — One Attachment Upload

验证至少一条路径：

```text
PDA 选择一个图片或文件
    → 使用现有 attachment relation
    → 上传
    → 当前 VAS Order 可读取附件
```

不得创建第二套附件模型或附件存储系统。

### VQ-011 — Sticky Bottom Action Bar

验证最小底部固定操作栏：

- Draft 显示 Save Draft / Submit；
- Submitted 不显示 PDA Unsubmit；
- Cancelled 只读；
- 软键盘弹出时按钮不被严重遮挡；
- 小屏触摸可操作。

### VQ-012 — Customer Readonly Path

验证 PDA 在订单解析成功后能读取并只读展示：

```text
Warehouse Order.owner → res.partner
```

三类 Warehouse Order 的既有字段事实为：

| Warehouse Order | Field | Source |
|---|---|---|
| `world.depot.inbound.order` | `owner` | `related='project.owner'` |
| `world.depot.outbound.order` | `owner` | `related='project.owner'`，stored |
| `world.depot.transfer.order` | `owner` | `related='project.owner'` |

Spike 不新增 VAS 客户字段，不新增客户快照。

必须记录：

- 解析成功后客户读取路径；
- `owner` 为空时的观察结果；
- 客户展示值使用的现有 display value；
- Draft 预览读取是否需要额外的标准 ORM/RPC 调用。

### VQ-013 — Android PDA Compatibility

在目标 Android PDA 浏览器上验证最小路径：

- Dashboard 或 PDA 入口加载；
- 触摸输入；
- billno 手工或键盘式扫码输入；
- 一条明细交互；
- Save Draft；
- 一个附件选择或上传；
- 底部固定操作栏可见；
- RPC 失败能够被感知。

目标设备、浏览器名称和版本必须写入 Spike 证据。

---

## 5. Minimal Experiments

### EXP-001 — Dashboard / Action Entry

目标：证明 Dashboard、PDA Action、Web List Action 的最小导航关系。

最小结果：

```text
模块根菜单 → Dashboard
Dashboard → PDA
Dashboard → Web List
PDA 可直接入口
```

### EXP-002 — OWL/JS Asset Loading

目标：证明一个最小 OWL/JS 组件可以在当前 Odoo Web 会话中加载。

最小结果：

- 组件渲染；
- 资产加载；
- 失败时有可观察错误；
- 明确真实目录、bundle 和注册方式。

### EXP-003 — Read Existing VAS Record

目标：通过标准 ORM/RPC 路径读取现有 `wd.vas.order`。

最小结果：

- 读取一张 Draft；
- 显示单号、状态、Operator；
- 当前用户权限生效；
- 不新增 API。

### EXP-004 — One Line and Save/Submit

目标：验证一条明细与现有服务端能力的连接。

最小结果：

- 添加一条明细；
- Operation Type 带出 Unit；
- 保存 Draft；
- 调用 Submit；
- 正确显示服务端成功或错误。

### EXP-005 — Input and Media

目标：验证目标设备的 billno 输入和最小媒体能力。

最小结果：

- 手工 billno；
- 键盘式扫码或明确记录不支持；
- 相机或文件选择；
- 一个附件上传。

### EXP-006 — Bottom Action and Device

目标：验证固定操作栏和目标 Android PDA 浏览器的最小兼容性。

最小结果：

- Draft 操作栏；
- Submitted 只读；
- 软键盘不遮挡关键操作；
- 目标设备最小录入路径可完成。

---

## 6. Allowed Files

### 6.1 Production Files

默认不允许修改任何生产文件。

只有在 Human Review 另行批准，并且确实无法在隔离环境验证时，才可对
生产文件执行最小、可逆、临时验证修改；该修改必须在同一 Spike 内清理，
不得提交。

### 6.2 Temporary Experiment Files

允许使用以下隔离位置：

```text
/tmp/warehouse_vas_spike_pda_001/
```

或当前仓库明确标记的临时目录：

```text
.spike/pda_001/
```

临时文件必须：

- 只包含 Spike 代码和配置；
- 不被正式 manifest 永久引用；
- 不修改既有生产模型；
- 不修改既有安全；
- 不修改既有 Web 视图；
- 不修改既有测试；
- 不作为 CC-04 代码直接使用。

### 6.3 Evidence Files

Spike 完成后允许新增：

```text
docs/context/verification/spike_pda_001_execution_evidence.md
```

证据文件必须记录真实命令、真实设备、真实结果、失败项和清理结果。

本契约本身不是执行证据，也不代表 Spike 已通过。

---

## 7. Forbidden Files and Changes

禁止修改：

- `docs/context/Designing/SRS.md`；
- `docs/context/Designing/tdd_warehouse_vas_v1.0.0.md`；
- `docs/context/Designing/tdd_warehouse_vas_v1.1_draft.md`，除非 Human Review
  明确批准证据回写；
- `docs/context/Coding/cc_warehouse_vas_01.md`；
- `docs/context/Coding/cc_warehouse_vas_02.md`；
- `docs/context/Coding/cc_warehouse_vas_03.md`；
- `addons/wd_warehouse_value_add/models/vas_order.py`；
- `addons/wd_warehouse_value_add/models/vas_order_line.py`；
- `addons/wd_warehouse_value_add/models/vas_operation_type.py`；
- 现有 `security/`；
- 现有 `views/`；
- 现有 `tests/`；
- `addons/worlddepot/`；
- Odoo 官方源码；
- 现有业务数据库及其中的业务数据；
- 生产 manifest；
- 生产 assets。

禁止行为：

- 启动 CC-04；
- 提交 Spike 代码；
- 修改 CC-01/02/03；
- 改变状态机；
- 改变锁顺序；
- 改变快照；
- 改变 ACL / record rules；
- 创建客户快照；
- 创建独立 PDA API；
- 将临时组件当作生产功能验收。

---

## 8. Evidence Requirements

Spike 必须形成可复核证据：

### 8.1 Environment

- Odoo 版本；
- Python 版本；
- 数据库名称；
- 配置文件路径；
- addons path；
- 目标 Android PDA 型号；
- 浏览器名称和版本；
- 执行日期；
- 执行人。

### 8.2 Per-Experiment Evidence

每个实验至少记录：

- 实验 ID；
- 验证问题；
- 使用的临时文件；
- 执行命令或操作步骤；
- 预期结果；
- 实际结果；
- PASS / FAIL；
- 截图或日志引用；
- 清理状态；
- 对 TDD v1.1 的影响。

### 8.3 Safety Evidence

必须证明：

- 生产模块文件没有未授权修改；
- Frozen SRS/TDD/CC 没有修改；
- CC-01/02/03 没有修改；
- 临时文件已删除；
- 工作区没有遗留 Spike 代码；
- 没有创建新业务模型或 API；
- 没有修改现有业务数据库及其中的业务数据；
- 隔离测试数据库中的测试记录和附件已按契约清理；
- 隔离数据库、临时配置和临时服务已停止或删除。

---

## 9. Result Standards

### 9.1 PASS

以下条件全部满足：

- OWL/JS 最小加载路径已验证；
- Dashboard、PDA、Web List 导航已验证；
- PDA 直接入口已验证；
- assets 加载方式已确定；
- ORM/RPC 读取现有 VAS 已验证；
- 一条明细添加/编辑已验证；
- Save Draft / Submit 调用路径已验证；
- billno 手工和至少一种扫码输入路径已验证；
- 相机或文件选择能力已验证；
- 一个附件上传已验证；
- 底部固定操作栏已验证；
- Android PDA 浏览器最小路径已验证；
- `Warehouse Order.owner` 只读展示路径已验证；
- 关键失败项和降级策略已记录；
- 临时文件已清理；
- 未修改受保护生产范围。

### 9.2 CONDITIONAL PASS

核心技术路径可行，但存在明确设备或浏览器限制，例如：

- 摄像头扫码不可用，但键盘式扫码可用；
- 相机调用受权限限制，但文件选择可用；
- 多媒体能力在目标设备上部分可用；
- Dashboard 使用标准低复杂度入口，PDA 使用 OWL/JS。

Conditional Pass 必须明确：

- 已验证能力；
- 未验证能力；
- 可接受降级；
- 目标设备限制；
- TDD v1.1 需要补充的约束；
- 不得把缺失能力描述为已完成。

### 9.3 FAIL

出现任一情况：

- 无法加载 OWL/JS PDA Frontend；
- 无法安全复用现有 Odoo session；
- 无法通过标准 ORM/RPC 读取 VAS；
- 必须创建第二套业务模型；
- 必须绕过现有权限或服务端动作；
- 无法保持 Web/PDA 数据一致；
- 目标设备无法完成最小保存/提交路径；
- 关键能力只能依赖未经验证的假设；
- Spike 修改污染生产范围；
- 临时文件无法清理。

---

## 10. Cleanup and Rollback

### 10.1 Cleanup

Spike 完成或中止时必须：

1. 停止临时服务；
2. 删除 `/tmp/warehouse_vas_spike_pda_001/` 或 `.spike/pda_001/`；
3. 删除临时数据库记录或恢复临时数据库；
4. 清除临时 assets 引用；
5. 检查 `git status --short`；
6. 检查 `git diff --check`；
7. 确认生产模块没有新增或修改文件；
8. 确认 Frozen 文档和 CC 没有变化；
9. 将清理结果写入证据文件。

### 10.2 Rollback

如需回滚：

- 优先删除隔离临时目录；
- 停止临时 Odoo 服务；
- 删除临时数据库或临时模块安装；
- 不使用 `git reset --hard`；
- 不使用 `git checkout --` 丢弃用户变更；
- 不回滚 CC-01/02/03；
- 不回滚现有生产数据库业务记录。

如果临时验证不得不触碰生产文件，必须逐项恢复并由
`git diff --check`、`git status` 和文件清单确认；未完成清理前不得判定
Spike 完成。

---

## 11. TDD v1.1 Write-back

Spike 完成后，只有真实证据可以回写 TDD v1.1：

### 11.1 Architecture

- OWL/JS PDA Frontend 的实际入口方式；
- Dashboard 的最低复杂度实现方式；
- PDA Action 和 Web List Action 的关系；
- PDA 直接入口；
- 前端资源目录和 bundle；
- component / registry 注册方式。

### 11.2 Data Access

- ORM/RPC service 的实际调用方式；
- 当前用户权限上下文；
- Draft 读取和保存；
- Submit 调用和错误处理；
- `Warehouse Order.owner` 展示路径。

### 11.3 Device Capability

- 目标 Android PDA 浏览器；
- billno 手工输入；
- 键盘式扫码；
- 摄像头扫码；
- camera capture；
- gallery/file selection；
- attachment upload；
- 失败和降级边界。

### 11.4 UI and Testing

- PDA Header；
- line card；
- bottom action bar；
- Submitted 只读；
- PDA 不提供 Unsubmit 的第一版边界；
- JS/OWL 测试技术；
- Browser Test 技术；
- PDA HVR 设备矩阵；
- CC-04 的实现和验收范围。

### 11.5 Write-back Rule

Spike 只能提出证据支持的修订。不得因为实验方便而：

- 改写 Backend 业务语义；
- 修改 Frozen SRS；
- 修改 CC-01/02/03；
- 把临时代码直接写成生产实现；
- 在没有证据的情况下冻结具体 Odoo 18 API。

---

## 12. Next Gate

当前状态：

```text
SPIKE-PDA-001 CONTRACT = DRAFT
SPIKE EXECUTION = NOT STARTED
CC-04 = NOT STARTED
TDD v1.1 = NOT FROZEN
```

下一步必须先获得 Human Review 对本契约的批准。

批准后执行：

```text
SPIKE-PDA-001
    ↓
Evidence Review
    ↓
TDD v1.1 Revision / Freeze
    ↓
Implementation Plan v1.1
    ↓
CC-04
```

在本契约获得批准前，不执行 Spike，不创建实验代码，不启动 CC-04。
