# Project Architecture Vision

The architectural vision for this Odoo 19-based modular project.

## Mission

Build a well-structured, standards-compliant Odoo 19 project using custom modules. Leverage Odoo 19's ERP capabilities (HR,
accounting, inventory) while adding domain-specific modules for business operations.

## Architecture Principles

- Odoo-native models — use Odoo ORM, not a separate database
- API facade — translate to/from external API formats at system boundaries, not internally
- Compliance-aware — design modules to support regulatory requirements from the start
- Progressive deployment — start with core operations, expand to advanced features incrementally

## Module Map

| Layer              | Modules                                                          | Purpose                                      |
| ------------------ | ---------------------------------------------------------------- | -------------------------------------------- |
| **Domain Core**    | `tpl_project`, `tpl_task`, `tpl_note`            | Core business records and workflows          |
| **Operations**     | `tpl_warehouse`, `tpl_service`, `tpl_reporting`  | Operational workflows and reporting          |
| **Integration**    | `tpl_api`, `tpl_import`                               | External API facade, data import             |
| **Foundation**     | `tpl_security`, `tpl_vocabulary`                      | Security, terminology, shared infrastructure |
| **Odoo Core**      | `hr`, `stock`, `account`                                        | Staff, inventory, accounting                 |

## Implementation Phases

| Phase | Focus                  | Key Modules                                                                        |
| ----- | ---------------------- | ---------------------------------------------------------------------------------- |
| 1     | **Core Operations**    | Base setup, core records, workflows, security, reporting                           |
| 2     | **Extended Operations**| Advanced workflows, batch processing, approvals                                    |
| 3     | **Integrations**       | External API, data import/export, third-party connectors                           |
| 4     | **Advanced**           | Analytics, automation, dashboards                                                  |

## Odoo 19 Strategy

- Extend `res.partner` for domain-specific entities (no parallel entity)
- Use Odoo's workflow engine for business state machines
- Leverage stock module for inventory/supply chain
- Use accounting module for billing and invoicing
- Maintain upgrade-safe patterns: `_inherit` extensions, no core patches

## Related Documents

- [Odoo Module Integration](integration-patterns.md)
- [Module Architecture](../principles/module-architecture.md)
