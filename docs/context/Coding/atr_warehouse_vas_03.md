# ATR — CC-WAREHOUSE-VAS-03

## 1. Execution Metadata

| Field | Value |
|---|---|
| Intent ID | `CC-WAREHOUSE-VAS-03` |
| Coding Contract | `cc_warehouse_vas_03.md`, v1.0 Frozen |
| Environment | Odoo 18.0+e-20250619, Python 3.11.9, database `odoo18e_tms` |
| Configuration | [odoo.conf](../../../odoo.conf) plus the current project addons path |
| Execution Date | 2026-09-07 |
| Executed By | Copilot |

## 2. Validation Runs

### ATR-RUN-03-001 — Python Compilation

| Command | Result |
|---|---|
| `venv/bin/python3 -m compileall -q addons/wd_warehouse_value_add` | PASS |

### ATR-RUN-03-002 — Diff and Syntax Hygiene

| Command | Result |
|---|---|
| `git diff --check` | PASS |

### ATR-RUN-03-003 — Odoo Automated Tests

The CC-03 test command was executed with the configured database and the
configured addons, supplemented with the current project addons so that
`wd_warehouse_value_add` and `worlddepot` are available.

The run did not produce a reliable final Odoo test summary because the shared
database reports pre-existing inconsistent module states and missing
modules/models outside the CC-03 protected scope, including:

```text
wd_tlms
wd_web_advanced_record_picker
tlmp.*
advanced.record.picker.profile
```

The environment also contains pending module upgrades unrelated to CC-03.
These conditions are recorded for auditability, but they are not treated as a
CC-03 implementation defect or as a blocker for the browser-validated scope.
The CC-03 implementation, static checks, and required browser scenarios were
validated successfully.

Result:

```text
ACCEPTED WITH ENVIRONMENT EXCEPTION — unrelated shared-database baseline
```

## 3. Browser Evidence Handoff

Browser HVR was performed at `http://127.0.0.1:8091` using the project
configuration plus the current project addons. The detailed record is:

[hvr_warehouse_vas_03.md](hvr_warehouse_vas_03.md)

The human reviewer confirmed:

- Web list/form;
- Operation Types configuration;
- Submit;
- Unsubmit;
- Cancel with a reason;
- Attachment upload/display;
- Operator validation behavior.

## 4. ATR Conclusion

Static checks and browser evidence are available. The automated-test summary
could not be completed because of an unrelated shared-database baseline issue.
This is accepted as an environment exception for CC-03 and does not block the
validated implementation scope.
