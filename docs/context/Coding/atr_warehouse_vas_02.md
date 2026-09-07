# ATR — CC-WAREHOUSE-VAS-02

## 1. Execution Metadata

| Field | Value |
|---|---|
| Intent ID | `CC-WAREHOUSE-VAS-02` |
| IHR | `ihr_warehouse_vas_02.md` |
| CC Version | v1.0 Frozen |
| Environment | Odoo 18.0+e-20250619, Python 3.11.9, database `odoo18e_tms` |
| Test Framework | Odoo `--test-enable` / `TransactionCase` |
| Execution Date | 2026-09-07 |
| Executed By | Copilot |

## 2. Validation Runs

### ATR-RUN-02-001 — Compilation

| Command | Result |
|---|---|
| `venv/bin/python3 -m compileall -q addons/wd_warehouse_value_add` | PASS |

### ATR-RUN-02-002 — CC-02 Module Suite

| Field | Value |
|---|---|
| Invocation | `venv/bin/python3 odoo-bin -c odoo.conf --logfile=/dev/stdout --addons-path=/Users/lijianqiang/Documents/odoo18e_vas/odoo/addons,/Users/lijianqiang/Documents/odoo18e_vas/addons -d odoo18e_tms -u wd_warehouse_value_add --test-enable --test-tags=/wd_warehouse_value_add --stop-after-init` |
| Executed | 15 Odoo test cases |
| PASS / FAIL / ERROR | 15 / 0 / 0 |
| Runner summary | `0 failed, 0 error(s) of 11 tests` |
| Result | PASS |

The runner's module count and loaded-test count use different Odoo statistics; both report zero failures and zero errors.

## 3. Contract Coverage

| Contract Area | Automated Evidence | Result |
|---|---|---|
| Submit binding and snapshots | `test_submit_binds_order_and_writes_audit_and_snapshots` | PASS |
| Submit failure paths | `test_submit_rejects_cancelled_order_and_zero_lines` | PASS |
| State actions and audit | `test_lifecycle_actions_and_locked_writes`; `test_draft_cancel_requires_reason` | PASS |
| Submitted/Cancelled write protection | lifecycle and line protection assertions | PASS |
| Active Operator and line validation | lifecycle and Submit tests | PASS |
| Independent-cursor VAS row locking | `TestVasConcurrency.test_vas_row_lock_blocks_second_cursor_until_release` | PASS |
| Python compilation | ATR-RUN-02-001 | PASS |

## 4. Preservation and Environment Notes

- No protected Warehouse Order or Odoo official source file was modified.
- No SQL business-data write or SQL unique constraint was added.
- The expected lock-timeout log emitted by the concurrency test is evidence that the second cursor was blocked; the test catches it and the suite remains green.
- Existing environment warnings about missing `queue_job` and legacy field parameters are unrelated baseline warnings and did not cause test failures.
- CC-03 security, UI, PDA, attachment UX, and real-device verification were not run because they are outside CC-02.

## 5. ATR Conclusion

All CC-02 automated verification items were executed with no failed or errored tests. ATR does not itself close the contract; FR must assess closure.
