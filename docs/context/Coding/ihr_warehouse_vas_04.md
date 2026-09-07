# IHR — CC-WAREHOUSE-VAS-04

## 1. Execution Metadata

| Field | Value |
|---|---|
| Intent ID | `CC-WAREHOUSE-VAS-04` |
| Coding Contract | `cc_warehouse_vas_04.md` |
| Module | `wd_warehouse_value_add` |
| Implementer | Copilot |
| Start / Last Updated | 2026-09-07 |
| Branch | `main` |
| Current Status | CC-04 Closed by Human Review |

## 2. Implemented Scope to Date

The current implementation covers the first CC-04 increment:

- Dashboard client action with PDA and Web List entry cards.
- Direct PDA client action and menu entry.
- Dedicated OWL/JS PDA action using the standard `orm` service.
- Prototype-aligned PDA form sections:
  - read-only base information;
  - Warehouse Order type and bill number;
  - customer and current operator display;
  - work line cards;
  - add-line modal;
  - attachment actions and attachment list;
  - Save Draft and Submit bottom bar.
  - Draft creation without a Warehouse Order association; association remains
    mandatory before Submit.
- Existing `wd.vas.order`, `wd.vas.order.line`, lifecycle actions,
  security, locks, snapshots, and attachment relation were reused.
- Existing server-side `action_submit()` remains the only submit path.

## 3. Prototype Alignment Work

The PDA form was revised against:

- `docs/context/Designing/pda_form.drawio`
- `docs/context/Designing/pda_form_detail.drawio`

The first implementation had only a flat input form. The revised structure now
adds the prototype's information hierarchy and detail modal rather than treating
the difference as a CSS-only issue.

## 4. Actual Change Inventory

| File / Area | Change |
|---|---|
| `static/src/js/vas_pda_action.js` | PDA state, ORM/RPC, line modal, line note, attachments, navigation |
| `static/src/xml/vas_pda_action.xml` | Prototype-aligned PDA form and add-line modal |
| `static/src/scss/vas_pda_action.scss` | Dashboard/PDA layout, cards, modal, attachment area, bottom bar |
| Earlier CC-04 allowlisted files | Dashboard, actions, manifest, menus, integration test |

## 5. Preservation and Boundary

- No VAS business model was redesigned.
- No ACL, record rule, state machine, lock, snapshot, or attachment relation was
  replaced.
- No independent PDA backend or second business model was introduced.
- No Odoo official source or `addons/worlddepot/**` file was modified.
- No production database business record was used for Spike or test data.

## 5.1 Approved Behavior Adjustment

The implementation now follows the selected behavior:

```text
Draft:
  warehouse_order_billno = optional
  warehouse_id = optional

Submit:
  a valid Warehouse Order must be resolved and bound
  bill number and warehouse snapshot are written by the existing action_submit
```

This is a server-side semantic change from the original required-field
baseline. The Frozen TDD/Implementation Plan require a corresponding revision
record before final CC-04 Closure.

## 6. Human Verification Handoff

Human browser verification passed for the current reviewed PDA scope:

- PDA form structure and prototype-aligned information hierarchy;
- current document number and status in the Header;
- new Draft entry;
- operation line add flow and add-line modal;
- quantity/time, unit, and note display;
- New, Save Draft, Submit, and Cancel controls;
- Cancel reason dialog;
- attachment entry points;
- Android PDA barcode scanning;
- Android PDA photo capture;
- Android PDA gallery/file multi-select;
- weak-network behavior;
- timeout handling;
- duplicate-click handling;
- concurrent modification handling;
- Draft/Submitted/Cancelled status presentation boundaries.
- Android PDA manual verification.

The detailed record is:

[hvr_warehouse_vas_04.md](hvr_warehouse_vas_04.md)

## 7. Current Handoff

The reviewed browser and Android PDA scope is complete. Human Review on
2026-09-07 authorized CC-04 Closure with the following follow-up evidence
items explicitly accepted rather than misrepresented as PASS:

- complete Browser Test/web tour;
- expand and isolate OWL/Hoot frontend coverage;
- complete Submitted/Cancelled read-only verification;
- complete Android PDA browser-version evidence;
- attachment failure/safe-retry and remaining lifecycle evidence;
- final evidence refinement, if required.

The Android PDA result is recorded as passed based on the human review. The
device identity and Android version are now recorded as 东集 Cruise GE2 and
Android 11. The exact Firefox version and scanner mode were not provided and
remain explicitly marked in the HVR record. These limitations do not block the
human-authorized CC-04 Closure.

```text
CC-04 Closure: CLOSED BY HUMAN REVIEW
Closure date: 2026-09-07
```
