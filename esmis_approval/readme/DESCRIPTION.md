Standardized approval workflows for eSMIS — provides a reusable state
machine mixin and configurable approval definitions.

### Key Models

- **esmis.approval.mixin** — Abstract mixin providing a complete approval
  state machine (draft → pending → approved/rejected/revision) with
  four-eyes enforcement.
- **esmis.approval.definition** — Configurable approval workflow definition
  per model. Phase 1 captures definitions; full multi-stage routing is
  implemented in Phase 2.

### Key Capabilities

- Four-eyes principle enforcement (submitter cannot self-approve)
- Full audit trail of submissions, approvals, and rejections
- Hook methods (`_on_submit()`, `_on_approve()`) for custom logic
- Revision request workflow

### Dependencies

- `base` — Odoo core
- `esmis_security` — Security groups for ACLs
