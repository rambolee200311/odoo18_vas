# Odoo Engineering Rules
## Odoo 开发强制工程规则
## Status: Frozen
## Version Policy: Odoo 版本无关

本文件定义所有 Odoo 开发任务必须遵守的强制工程边界。

所有规则均为 MUST / MUST NOT。

Agent 无权自行偏离、降级或批准例外。

如果任务必须违反任一规则：

**Stop → Escalate → Human Decision**

---

## RULE-01 — 严格使用目标 Odoo 版本技术

必须使用项目目标 Odoo 版本实际支持的技术。

禁止：

- 使用目标版本已经废弃的技术；
- 使用旧版本遗留实现；
- 使用高于目标版本才提供的技术；
- 混用不同 Odoo 大版本的 API 和实现方式。

无法确认兼容性时，必须先验证，不得猜测。

---

## RULE-02 — 严格使用项目 Python Runtime

项目必须在项目目录维护独立 `.venv`。

必须严格使用项目规定的 Python 版本。

开发、测试、Shell、升级及工具执行必须使用该项目的 Python Environment。

禁止使用系统 Python、其他项目 venv 或未经确认的 Python Runtime 替代。

---

## RULE-03 — 严禁直接访问 PostgreSQL 业务数据库

禁止绕过 Odoo Runtime 直接访问 PostgreSQL 查询、修改、删除或修复 Odoo 业务数据。

禁止使用：

- psql；
- pgAdmin；
- DBeaver；
- 独立 psycopg；
- 独立 SQL Script；

直接操作 Odoo 业务数据。

模块内部确有 SQL 技术需求时，只允许通过 Odoo 管理的 Cursor，并必须经过项目技术设计明确批准。

---

## RULE-04 — 数据调查必须通过 Odoo Runtime

开发、排错、数据核查必须使用：

odoo-bin shell
→ Odoo Environment
→ ORM

不得为了方便绕过 Odoo Runtime 直接查询数据库。

---

## RULE-05 — 严禁修改 Odoo 官方源码

禁止修改 Odoo Community、Enterprise 及官方 Addon 的 Python、XML、JavaScript、QWeb 等源码。

所有定制必须通过 Odoo 正式扩展机制或独立 Custom Addon 实现。

**Custom code extends Odoo; it does not rewrite Odoo.**

---

## RULE-06 — 模块升级必须验证真实常驻升级路径

需要 Upgrade Verification 的模块，最终升级验证必须针对已经正常常驻运行的 Odoo Server 执行。

必须通过目标版本正式支持的 RPC / 管理入口触发模块升级。

目标版本支持 XML-RPC 时，应使用 XML-RPC 模拟真实模块升级。

一次性 `odoo-bin -u ... --stop-after-init` 可以用于开发辅助，但不得作为最终 Upgrade Verification Evidence。

---

## RULE-07 — 不得绕过正式业务入口伪造业务结果

存在正式 Business Action 时，不得通过直接修改内部状态或结果字段伪造业务动作已经完成。

正式 Action 是业务转换入口时，必须通过正式 Action 执行。

---

## RULE-08 — Agent 不得自行突破 Frozen 工程边界

Agent 不得为了让代码运行、测试通过或简化实现而自行：

- 修改业务语义；
- 修改官方源码；
- 修改目标 Odoo / Python 版本；
- 绕过数据库访问规则；
- 引入未经批准的核心基础设施；
- 突破 Frozen TDD；
- 突破 Coding Contract。

需要突破时：

**Stop → Escalate → Human Decision**

---

## Governing Rule

> **Agent may execute inside the boundary, but may not redefine the boundary.**
>
> **Agent 可以在边界内自主执行，但无权修改边界本身。**