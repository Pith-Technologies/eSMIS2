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

These have no Odoo base equivalent and are purely `tpl.*`:

| Model                       | Purpose                                      |
| --------------------------- | -------------------------------------------- |
| `tpl.project`          | Core project/record tracking, workflows      |
| `tpl.task`             | Task management with assignments             |
| `tpl.note`             | Documentation with signing/approval          |
| `tpl.observation`      | Measurements, readings, data points          |
| `tpl.request`          | Requests and order management                |
| `tpl.review`           | Review and approval records                  |

## Odoo Module Dependencies

```
tpl_vocabulary → base (res.partner)
tpl_project → tpl_vocabulary
tpl_note → tpl_project
tpl_warehouse → tpl_project, stock
tpl_service → tpl_project
tpl_billing → tpl_project, account
tpl_api → tpl_vocabulary, tpl_project (+ all domain modules)
```

## Security Integration

Custom access control layers on top of Odoo's group-based security:

- `group_tpl_viewer` — read records
- `group_tpl_officer` — create/edit records (operators, staff)
- `group_tpl_manager` — full access including configuration
- `group_tpl_admin` — manage system configuration
- Emergency override with audit trail (when applicable)

Record rules ensure users only see records in their assigned scope (company, department, team).

## Upgrade Safety

Principles for maintaining Odoo upgrade compatibility:

- Never modify Odoo core files — only extend via `_inherit`
- Use `hook` methods for customization points
- Store custom fields in `tpl_*` modules, not in Odoo module data
- Test against Odoo nightlies periodically

## Related Documents

- [Project Architecture Vision](vision.md)
- [Module Architecture](../principles/module-architecture.md) (principle)
- [Access Rights](../principles/access-rights.md) (principle)
