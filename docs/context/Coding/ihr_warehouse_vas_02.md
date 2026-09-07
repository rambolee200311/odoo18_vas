# IHR — CC-WAREHOUSE-VAS-02

## 1. Execution Metadata

| Field | Value |
|---|---|
| IHR Document | `ihr_warehouse_vas_02.md` |
| Intent ID | `CC-WAREHOUSE-VAS-02` |
| Coding Contract | `cc_warehouse_vas_02.md`, v1.0 Frozen |
| Module | `wd_warehouse_value_add` |
| Implementer | Copilot |
| Start / Last Updated | 2026-09-07 |
| Branch | `main` |
| Base Commit | `75d7cc5ccd2d293bf9503358e1a8f4f398d6fbce` |
| Current Status | Implementation Complete |

## 2. Scope and Baseline

Implementation was performed only against the CC-02 allowlist:

- `models/vas_order.py`
- `models/vas_order_line.py`
- `tests/test_vas_order.py`
- `tests/test_vas_concurrency.py`
- `tests/__init__.py`

No protected Warehouse Order model, Odoo official source, SRS, verification record, or workflow document was modified.

## 3. Implementation History

### IHR-02-001 — Lifecycle and Submit Integrity

Implemented `action_submit`, `action_unsubmit`, and `action_cancel` with Draft/Submitted/Cancelled state guards, active Operator validation, line completeness checks, cancellation reason validation, and Submit-time Warehouse Order resolution.

Contract references: `CC-CHANGE-001` through `CC-CHANGE-006`; TDD `TD-002`, `TD-003`, `TD-007`.

### IHR-02-002 — Snapshot, Audit, and Server-Side Protection

Submit now binds exactly one Warehouse Order and writes the relation, bill number, warehouse snapshot, submitter, and timestamp. Unsubmit and Cancel write their corresponding audit fields. Submitted and Cancelled orders, and their lines, reject protected writes through ORM entry points.

Contract references: `CC-CHANGE-005` through `CC-CHANGE-007`; TDD §§5, 8, 9, 10.

### IHR-02-003 — Locking and Concurrency Test

Added parameterized `FOR UPDATE` helpers for VAS Orders and the resolved Warehouse Order. VAS actions lock the VAS row first, invalidate caches, and then resolve/lock the Warehouse Order. Added an independent-cursor test proving the VAS row lock blocks a second cursor until the first cursor releases it.

Contract references: `CC-CHANGE-008`, `CC-CHANGE-009`; TDD `TD-008`, `TEST-CONC-001`.

### IHR-02-004 — Test Fixture Correction

The first CC-02 test run exposed that database user 1 is inactive in this environment. Lifecycle fixtures were corrected to use an active `res.users` record as the Operator; this preserves the Frozen TDD rule that submission requires an active Operator and does not implement CC-03 security semantics.

Contract references: `CC-TEST-003`, `TD-010` boundary.

## 4. Actual Change Inventory

| File | Change |
|---|---|
| `models/vas_order.py` | Lifecycle actions, Submit binding, snapshots, audit fields, protected writes, parameterized row locks |
| `models/vas_order_line.py` | Submitted/Cancelled parent protection for create/write/unlink |
| `tests/test_vas_order.py` | Submit, failure path, lifecycle, audit, snapshots, and locked-write coverage |
| `tests/test_vas_concurrency.py` | Independent-cursor row-lock serialization coverage |
| `tests/__init__.py` | Registered concurrency tests |

## 5. Deviations and Stop Conditions

No scope deviation was made. The three protected Warehouse Order Cancel implementations were inspected and were not modified; their existing lock behavior is not assumed to follow the VAS lock protocol. No ACL, record rule, UI, PDA, attachment UX, or CC-03 security implementation was added.

## 6. Validation Handoff

The final implementation test run passed:

```text
wd_warehouse_value_add: 15 tests
0 failed, 0 error(s) of 11 tests
```

ATR records the executable evidence. FR must determine CC-02 closure from this IHR, ATR, the Frozen CC, and the HVR applicability conclusion.
