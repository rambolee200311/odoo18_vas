# Project Closure Workflow Extension

## 组织级标准 — v1.0.1

**状态：Frozen**  
**上游基线：SRS v1.0.0 | DDD v1.0.0 | TDD v1.0.0 | CC v1.0.0 | IHR v1.0.0 | ATR v1.0.0 | HVR v1.0.0 | FR v1.0.0 | PVR v1.0.0 | PCR v1.0.0**  
**更新日期：2026-09-07**

---

## 0. 文档治理

### 0.1 定位

本文件定义 **Agent-Assisted Software Engineering Management / Agent 辅助开发的软件工程管理** 中的 Project Closure Workflow，并明确它与 Implementation Plan、Coding Contract 及单轮 Coding Closure 的关系。

它解决两个层级的问题：

1. Frozen TDD 如何经过 Implementation Plan 被拆分为若干可独立验证的 Coding Slice；
2. 多轮 Coding Contract 全部关闭后，如何证明最终项目基线真正满足最终 Authority Baseline。

本文件不把 Implementation Plan 提升为新的 Authority，也不新增 Project-IHR / Project-ATR / Project-HVR。

### 0.2 顶层工程管理对象

整个体系管理的不是“Agent 写代码”本身，而是：

```text
Authority
→ Context
→ Planning
→ Boundary
→ Agent Execution
→ Evidence
→ Closure
→ Human Decision
```

最高层原则：

> **Bounded Autonomy, Human Authority.**  
> **边界内自治，边界外人决。**

### 0.3 文档与控制域

| 控制域 | 主要文档 / 机制 | 职责 |
|---|---|---|
| Authority | Business Ready Gate / Frozen SRS / Frozen DDD（如有）/ Frozen TDD / Release Decision | 决定进入、业务事实、技术设计与最终发布权 |
| Context | SRS / DDD / TDD | 定义 WHAT / Domain / HOW |
| Planning | Implementation Plan | 决定分几轮、按什么顺序实施；不是 Frozen Authority |
| Boundary | Engineering Rules / Coding Contract | 定义不可突破红线与单轮授权范围 |
| Execution | Implementation | Agent 编码、测试、修复 |
| Evidence | IHR / ATR / HVR | 记录实际执行与验证事实 |
| Closure | FR / PVR / PCR | 单轮 Closure 与项目级 Closure |
| Human Decision | Human Review / Project Final Review | Merge / Integration 与 Release Decision |

### 0.4 涉及母版与项目级产物

| 层级 | 目录 | 文件 / 产物 | 状态 |
|---|---|---|---|
| Designing | `docs/template/Designing/` | SRS模板.md | Frozen v1.0.0 |
|  |  | DDD模板.md | Frozen v1.0.0 |
|  |  | TDD模板.md | Frozen v1.0.0 |
| Planning | 项目目录，如 `docs/context/implementation/` | `implementation_plan_*.md` | 项目级 Current / Approved Baseline；**不设 Frozen 母版 Authority** |
| Coding | `docs/template/Coding/` | Coding_Contract模板.md | Frozen v1.0.0 |
|  |  | IHR模板.md | Frozen v1.0.0 |
|  |  | ATR模板.md | Frozen v1.0.0 |
|  |  | HVR模板.md | Frozen v1.0.0 |
|  |  | FR模板.md | Frozen v1.0.0 |
| Closure | `docs/template/Closure/` | PVR模板.md | Frozen v1.0.0 |
|  |  | PCR模板.md | Frozen v1.0.0 |
|  |  | workflow.md | Frozen v1.0.1 |

**Implementation Plan 不新增组织级 Authority 母版。** 如需统一格式，只允许形成轻量 Guide / 示例，不得把 Plan 变成第二份 TDD。

---

## 1. 完整 Engineering Workflow

### 1.1 顶层流程

```text
Business Requirements Guide
→ Business Ready Gate
→ SRS
→ DDD (optional)
→ Technical Verification (as needed)
→ TDD
→ Implementation Plan
→ [CC → Implementation → IHR → ATR → HVR (when required) → FR] × N
→ Final Project Authority Baseline
→ Final Project Code Baseline
→ PVR
→ PCR
→ Project Final Review
→ Release Decision
```

### 1.2 核心执行原则

> **Plan all, Contract next, Execute, Verify, Close, then continue.**  
> **整体规划，逐轮契约；完成一轮，验证一轮，闭环后再进入下一轮。**

### 1.3 三层职责

> **TDD 决定怎么做；Plan 决定分几轮、按什么顺序做；CC 决定这一轮 Agent 被允许做什么。**

其中：

- TDD = Technical HOW Authority；
- Implementation Plan = Execution Sequencing / Coding Slice decomposition；
- Coding Contract = Current Slice Execution Boundary；
- IHR / ATR / HVR = Evidence Records；
- FR = Current Coding Contract Closure；
- PVR = Final Project Verification Evidence；
- PCR = Project Closure Assessment；
- Project Final Review = Release Authority Gate。

---

## 2. Implementation Plan Gate

### 2.1 定位

Implementation Plan 位于 Frozen TDD 与 Coding Contract 之间，解决：

> 项目级 TDD 应如何拆成若干轮可独立授权、实施、验证、关闭的 Coding Contracts？

Plan 只负责：

- Coding Slice 列表；
- 每个 Slice 的目标；
- TDD Scope 映射；
- Slice 依赖和顺序；
- Verification 类型；
- Exit Criteria；
- 下一份 CC 的生成触发条件。

Plan 不负责：

- 新业务规则；
- 新技术设计；
- 精确代码实现；
- 正式 file allowlist；
- 一次性生成全部未来 Coding Contracts。

### 2.2 Plan 不是 Frozen Authority

Implementation Plan 是 **Current / Approved Execution Baseline**，不是 Frozen Authority。

允许在已完成 FR 后，根据已验证的实现事实：

- 调整后续 Slice 顺序；
- 合并或拆分后续 Slice；
- 调整 Expected Files；
- 调整后续 Exit Criteria；
- 决定是否触发 Optional Slice。

但 Plan 不得：

- 改变 Frozen SRS / DDD / TDD 的规范性义务；
- 删除 Frozen TDD obligation；
- 用 Re-plan 吞掉 TDD 设计错误。

如果实现事实证明 Frozen TDD assumption / decision 不成立：

```text
TDD IMPACT
→ 停止受影响后续 Slice
→ 回到 TDD Change / Review
→ 更新 Authority Baseline
→ 再重新规划
```

### 2.3 Plan Gate

Plan 只使用轻量 Gate：

```text
READY TO DRAFT CC-01
```

或：

```text
PLAN BLOCKED
```

Plan 不使用 `SATISFIED / NOT SATISFIED / BLOCKED` 作为 Closure 状态，因为 Plan 不是 Closure 文档。

---

## 3. Coding Iteration 与单轮 Closure

### 3.1 单轮链路

```text
Approved Current Plan
→ Draft Next CC
→ Human Review / Approval
→ Implementation
→ IHR
→ ATR
→ HVR (when applicable)
→ FR
```

### 3.2 只 Contract Next

原则：

- Plan 可以规划所有 Slice；
- 正式 Coding Contract 只起草**下一轮**；
- CC-02 及以后必须基于 Frozen TDD + 当前代码事实 + 前一轮 FR；
- 不得在 Plan 阶段把预测文件表升级为未来 CC 的正式 allowlist；
- 不得因为 Plan 已写出未来 Slice 就假定未来实现事实已经成立。

### 3.3 FR Gate 到下一轮

FR 严格使用三态：

```text
SATISFIED
NOT SATISFIED
BLOCKED
```

推进规则：

```text
FR-CC-N = SATISFIED
→ 默认允许根据最新代码事实起草下一份 CC

FR-CC-N = NOT SATISFIED
→ 不得机械进入下一 Slice；先修复、补证据或重新规划

FR-CC-N = BLOCKED
→ 不得假设当前 Slice 已完成；先解除 Blocker
```

不得使用：

- PARTIALLY SATISFIED；
- CONDITIONAL PASS；
- MOSTLY SATISFIED；
- HUMAN WAIVER。

### 3.4 HVR Applicability

HVR 不是每轮必需。

- 若 CC/TDD 将 HVR 标记为 Mandatory / Applicable，则 FR 必须等待相应 HVR Evidence；
- 若真实设备 / 业务验收被明确放到项目级验证，则 FR 不得宣称它已完成，PVR 在最终项目基线上收集该 Evidence；
- 不允许用自动化测试替代明确要求的人机交互、真实设备或 UAT 验证。

---

## 4. 两级 Closure 模型

| 层级 | Authority Chain | Evidence | Closure 文档 | Human Gate |
|---|---|---|---|---|
| Coding | CC | IHR + ATR + HVR（按适用性） | FR | Human Review → Merge / Integration Decision |
| Project | SRS → DDD（如有）→ TDD | 全部适用 Coding FR + PVR | PCR | Project Final Review → Release Decision |

**不变量：**

1. All Coding FRs SATISFIED does not imply Project Closure.
2. Project Closure applies only to the Final Project Authority Baseline AND the Final Project Code Baseline.
3. Implementation Plan 不进入 Final Project Authority Baseline。
4. Historical PASS does not automatically prove the Final Baseline.

---

## 5. 顶层职责链

```text
                 PROJECT AUTHORITY
                        │
          SRS → DDD(optional) → TDD
                        │
                        ▼
              IMPLEMENTATION PLANNING
                        │
               Implementation Plan
                        │
                        ▼
                 Coding Iterations
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        CC-001         CC-002         CC-N
          ↓              ↓              ↓
      IHR/ATR/HVR    IHR/ATR/HVR      ...
          ↓              ↓
        FR-001         FR-002
          └─────────────┼─────────────┘
                        ▼
         Final Project Authority Baseline
         Final Project Code Baseline
                        │
                        ▼
                       PVR
             Project Verification Evidence
                        │
                        ▼
                       PCR
              Project Closure Assessment
                        │
                        ▼
              Project Final Review
                        │
                        ▼
                 Release Decision
```

---

## 6. 权威链设计

### 6.1 两级 Authority 对照

| 层级 | Authority Chain | Planning / Boundary | Evidence | Closure |
|---|---|---|---|---|
| Coding | Frozen TDD → CC | Implementation Plan → Current CC | IHR + ATR + HVR | FR |
| Project | SRS → DDD（如有）→ TDD | Plan 不属于 Final Authority | 全部 Coding FR + PVR | PCR |

### 6.2 项目级权威分层职责与冲突处理

- **SRS**：决定“业务是否完成”——所有纳入 Project Closure 的 Normative Requirements 是否覆盖并满足；
- **DDD**（如有）：决定“领域语义是否保持一致”；
- **TDD**：决定“技术设计与技术约束是否落实”；
- **Implementation Plan**：只决定“这些技术义务如何被分轮实施”，不得解决 Authority 冲突；
- **CC**：只决定“当前 Slice 被授权修改和验证什么”。

当 SRS / DDD / TDD 之间出现矛盾时，不得由 Plan、CC、FR、PVR 或 PCR 自行调和。必须回到对应上游基线修订，再重新进入后续流程。

### 6.3 Final Project Authority Baseline（必填）

Project Closure 开始前，必须明确一组最终批准的 Authority Baseline：

| Authority | Final Version |
|---|---|
| SRS | `<final version>` |
| DDD | `<final version / N/A>` |
| TDD | `<final version>` |

规则：

- PVR / PCR 的 Coverage 与 Closure 判断均以该最终批准版本为准；
- 历史 Coding FR 可来自更早上游版本，但不得因此自动证明 Final Authority Baseline 已覆盖；
- 最终基线新增、修改或废止规范性义务时，必须重新完成 Coverage / Impact Analysis / Verification；
- Implementation Plan 的版本可记录为项目执行历史，但**不进入 Final Project Authority Baseline**。

### 6.4 两个 Final Baseline

| 概念 | 含义 |
|---|---|
| Final Project Authority Baseline | 最终验什么（SRS / DDD / TDD 最终批准版本） |
| Final Project Code Baseline | 最终验哪版代码（Commit / Build） |

---

## 7. Project Closure 反模式

| 禁止 | 原因 |
|---|---|
| 拼各轮 FR = Project Done | FR 只证明单轮 CC，不证明 SRS 全覆盖 |
| 拼各轮 ATR = Final Regression | 分散 commit 的 PASS 不能证明最终集成基线正确 |
| 把 Implementation Plan 当 Frozen Authority | Plan 是执行路线图，可在 FR 后按事实重规划 |
| 一次生成全部未来正式 CC | 未来 CC 必须基于前一轮真实代码事实和 FR |
| 用 Plan 修改 TDD | Plan 不能吞掉 Authority 设计变更 |
| 造 Project-IHR / Project-ATR / Project-HVR | 体系膨胀，用 PVR + PCR 收口 |
| FR 宣布 Project Closure | FR 的 Closure 对象是一份 CC |
| PCR 决定 Release | PCR 只做 Project Closure，Release 属于 Project Final Review |
| PCR 调和 SRS/DDD/TDD 冲突 | 冲突必须回上游修订 |
| “完整回归 / 全量回归” | 应为 Final Regression Assessment，范围由风险决定 |

---

## 8. PVR（Project Verification Record）

### 8.1 定位

**PVR = 项目级综合 Verification Evidence Record。**

PVR 聚合项目级自动化验证、人工验证、E2E/UAT 与最终基线覆盖事实。**PVR 不做 Closure 判断。**

### 8.2 核心职责

- SRS Coverage Review（事实映射）；
- Final Regression Assessment；
- End-to-End / UAT 场景验证；
- DDD/TDD applicable obligation 核对；
- Outstanding Issues 汇总。

### 8.3 Project Coverage Matrix

| Requirement | Upstream AC | Coding Contract | Coding FR | Mapping Status | Project Evidence | Verification Status |
|---|---|---|---|---|---|---|
| FR-001 | AC-001.1 | CC-001 | FR-001 | MAPPED | IHR-003, ATR-004 | VERIFIED |
| FR-002 | AC-002.1 | CC-001 | FR-001 | MAPPED | — | NOT VERIFIED |
| FR-028 | AC-028.1 | — | — | UNMAPPED | — | NOT VERIFIED |

两个状态维度不可合并：

- **Mapping Status**：`MAPPED / UNMAPPED / N/A`；
- **Verification Status**：`VERIFIED / NOT VERIFIED / EVIDENCE MISSING / N/A`。

`MAPPED ≠ VERIFIED`。

PVR 可以发现 UNMAPPED / NOT VERIFIED / EVIDENCE MISSING，但不得输出 Project Closure 结论。

追溯链：

```text
Requirement → AC → CC → FR → PVR Evidence
```

Implementation Plan 可以作为“为何如此切片”的执行历史参考，但不替代上述 Normative Traceability。

---

## 9. Project Closure 核心内容

### 9.1 Final Regression Assessment

Project Closure 必须对 Final Project Code Baseline 执行 Final Regression Assessment。

- 若存在可执行自动化回归能力且变更可能产生跨 CC 影响，必须在 Final Project Code Baseline 上执行适当范围的 Final Baseline Regression；
- 若不执行，必须记录明确理由、风险评估和替代验证方式。

原则：

> **强制回答，不强制答案。**

### 9.2 SRS Normative Requirements 覆盖

全部纳入 Project Closure 的 SRS Normative Requirements 必须完成项目级追溯，包括：

- ROLE；
- FR；
- BR；
- CFG；
- NFR；
- 对应 AC。

不得遗漏规范性 Requirement Type。

### 9.3 DDD/TDD Coverage Review

只检查项目适用、规范性、且被 Final Project Authority Baseline 承载的 DDD/TDD obligations。

- 不机械覆盖所有设计说明、决策记录或非规范性内容；
- DDD：检查关键 ENT / VO / Aggregate 边界和核心不变式；
- TDD：检查关键架构约束、接口契约和 Guardrails。

---

## 10. PVR 文档结构

1. Project Metadata（Final Project Authority Baseline + Final Project Code Baseline）
2. Project Coverage Matrix
3. DDD/TDD Coverage Summary
4. Final Regression Assessment Record
5. E2E / UAT Evidence
6. Outstanding Issues（事实列表，不做 Closure 判定）

---

## 11. PCR 文档结构

1. Project Metadata（两个 Final Baseline）
2. Authority Chain 核对（SRS → DDD → TDD）
3. 全部适用 Coding FR 状态汇总
4. PVR 状态汇总
5. Coverage Gaps 评估
6. Project Closure Determination：`SATISFIED / NOT SATISFIED / BLOCKED`
7. Handoff to Project Final Review

### 11.1 PCR 三态规则

PCR 使用严格三态：

- `SATISFIED`：全部适用 Mandatory obligations 已知且满足；
- `NOT SATISFIED`：存在已知 Mandatory failure；
- `BLOCKED`：无法可靠判断某个 Mandatory obligation。

确定性优先级：

1. 任一 Mandatory / Applicable `NOT SATISFIED` → Overall `NOT SATISFIED`；
2. 否则任一 `BLOCKED` → Overall `BLOCKED`；
3. 否则全部适用项 SATISFIED → Overall `SATISFIED`；
4. N/A 不参与 Closure。

已知失败不得因为同时存在未知项而降级为 BLOCKED。

PCR 不得制造新 Evidence，也不得决定 Release。

---

## 12. 对现有体系的影响

- **SRS / DDD / TDD**：仍是项目 Authority；
- **Implementation Plan**：正式加入 TDD 与 CC 之间，作为项目级 Current / Approved Execution Baseline；不成为 Frozen Authority；
- **Coding Contract**：仍是单轮执行授权边界；
- **IHR / ATR / HVR**：职责不变，仍是 Evidence Records；
- **FR**：Closure 对象是一份 Coding Contract，不等同于 Project Closure；
- **PVR**：项目级 Verification Evidence；
- **PCR**：项目级 Closure Report；
- **Project Final Review**：保留最终 Release Authority。

---

## 13. 单轮项目处理

单轮项目仍应完成 Project Closure 判断，但允许：

- PVR / PCR 极简化；
- 或在组织规则允许时采用合并式 Project Closure Record。

不得因为只有一轮 Coding Contract 就省略：

- SRS 全局 Coverage；
- Final Project Code Baseline 验证；
- 最终项目级 Closure 判断。

---

## 14. 目录约定

### 14.1 组织级模板

```text
docs/template/
├── Designing/
│   ├── SRS模板.md
│   ├── DDD模板.md
│   └── TDD模板.md
├── Coding/
│   ├── Coding_Contract模板.md
│   ├── IHR模板.md
│   ├── ATR模板.md
│   ├── HVR模板.md
│   └── FR模板.md
└── Closure/
    ├── workflow.md
    ├── PVR模板.md
    └── PCR模板.md
```

### 14.2 项目级 Planning 产物

推荐：

```text
docs/context/implementation/
└── implementation_plan_<project>_vX.Y.md
```

Implementation Plan 是项目级产物，不要求新增 `docs/template/Planning/Implementation_Plan模板.md`。如后续多个真实项目证明需要统一格式，再考虑轻量 Guide；不得提前制造模板体系。

---

## 15. 术语表

| 缩写 / 术语 | 全称 / 含义 | 层级 |
|---|---|---|
| SRS | Software Requirements Specification | Authority / Designing |
| DDD | Domain-Driven Design document（Optional） | Authority / Designing |
| TDD | Technical Detailed Design | Authority / Designing |
| Implementation Plan | Coding Slice sequencing plan | Planning |
| CC | Coding Contract | Coding Boundary |
| IHR | Implementation History Record | Coding Evidence |
| ATR | Automated Test Record | Coding Evidence |
| HVR | Human Verification Record | Coding Evidence |
| FR | Final Report | Coding Closure |
| PVR | Project Verification Record | Project Evidence |
| PCR | Project Closure Report | Project Closure |

Human Gate：

- Coding 层：`Human Review` → Merge / Integration Decision；
- Project 层：`Project Final Review` → Release Decision。

二者是不同层级的 Human Authority Gate，不另设重复 Gate。

---

## 16. 版本历史

| 版本 | 日期 | 状态 | 关键变更 |
|---|---|---|---|
| v0.1 | 2026-09-04 | Draft | 初稿：两级 Closure、PVR + PCR、防体系膨胀 |
| v0.2 | 2026-09-04 | RC | Authority Chain、PVR Evidence-only、Final Regression Assessment、Normative Coverage、单轮退化 |
| v1.0.0 | 2026-09-04 | Frozen | Final Project Authority Baseline、双状态 Coverage、Human Gate 术语冻结 |
| **v1.0.1** | **2026-09-07** | **Frozen** | **正式加入 Implementation Plan；明确 Plan 非 Frozen Authority；增加 Plan Gate、Re-plan Rule、Contract-next、FR→下一 Slice Gate；完善完整 Agent-Assisted Software Engineering Management Workflow** |

### v1.0.1 变更摘要

1. 在 `TDD → CC` 之间正式加入 `Implementation Plan`；
2. 明确 `TDD = HOW Authority / Plan = Sequencing / CC = Current Slice Boundary`；
3. 明确 Plan 是 Current / Approved Execution Baseline，不是 Frozen Authority；
4. 增加 Re-planning Rule 与 `TDD IMPACT` 回退规则；
5. 增加 `Plan all, Contract next, Execute, Verify, Close, then continue`；
6. 增加 FR 三态到下一 Coding Slice 的 Gate 规则；
7. 明确 HVR applicability 与 Coding Closure / Project Verification 的边界；
8. 明确 Implementation Plan 不进入 Final Project Authority Baseline；
9. 不新增 Implementation Plan 母版，避免体系膨胀。

**冻结规则：** v1.0.1 后仅在真实项目验证发现明确制度缺陷时修订；不得为格式偏好持续增加小版本。
