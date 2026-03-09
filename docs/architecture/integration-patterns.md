# Odoo Module Integration Patterns

How custom project modules map to and extend Odoo 19's built-in capabilities.

## Integration Strategy

Extend Odoo modules rather than replacing them. Custom modules add domain-specific fields, workflows, and
validations on top of Odoo's proven ERP foundation.

## Module Mapping

| Domain                   | Odoo Module        | Extension Approach                                                               |
| ------------------------ | ------------------ | -------------------------------------------------------------------------------- |
| **Contacts/Entities**    | `res.partner` (base) | `_inherit` — add domain-specific fields (registration codes, categories, tags) |
| **Inventory**            | `stock`            | `_inherit` — add custom lot tracking, expiry management, specialized workflows   |
| **Billing**              | `account`          | `_inherit` — add custom charge capture, rate tables, statement generation        |
| **Staff**                | `hr`               | `_inherit` — add license numbers, specialties, roles, scheduling                 |
| **Scheduling**           | `calendar`         | `_inherit` — add custom event types, resource slots, queue management            |
| **Documents**            | `documents`        | `_inherit` — add custom document types, approval forms, scanned records          |

## Custom Models

These have no Odoo base equivalent and are purely `esmis.*`:

| Model                       | Purpose                                      |
| --------------------------- | -------------------------------------------- |
| `esmis.project`          | Core project/record tracking, workflows      |
| `esmis.task`             | Task management with assignments             |
| `esmis.note`             | Documentation with signing/approval          |
| `esmis.observation`      | Measurements, readings, data points          |
| `esmis.request`          | Requests and order management                |
| `esmis.review`           | Review and approval records                  |

## Odoo Module Dependencies

```
esmis_vocabulary → base (res.partner)
esmis_project → esmis_vocabulary
esmis_note → esmis_project
esmis_warehouse → esmis_project, stock
esmis_service → esmis_project
esmis_billing → esmis_project, account
esmis_api → esmis_vocabulary, esmis_project (+ all domain modules)
```

## Security Integration

Custom access control layers on top of Odoo's group-based security:

- `group_esmis_viewer` — read records
- `group_esmis_officer` — create/edit records (operators, staff)
- `group_esmis_manager` — full access including configuration
- `group_esmis_admin` — manage system configuration
- Emergency override with audit trail (when applicable)

Record rules ensure users only see records in their assigned scope (company, department, team).

## Upgrade Safety

Principles for maintaining Odoo upgrade compatibility:

- Never modify Odoo core files — only extend via `_inherit`
- Use `hook` methods for customization points
- Store custom fields in `esmis_*` modules, not in Odoo module data
- Test against Odoo nightlies periodically

## Related Documents

- [Project Architecture Vision](vision.md)
- [Module Architecture](../principles/module-architecture.md) (principle)
- [Access Rights](../principles/access-rights.md) (principle)
