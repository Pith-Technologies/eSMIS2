# eSMIS Development Principles

This directory contains the core principles and standards that guide eSMIS development. These principles ensure consistency, maintainability, and quality across all modules.

## Principle Documents

| Document | Description |
|----------|-------------|
| [Naming Conventions](naming-conventions.md) | Standards for naming modules, models, fields, XML IDs, and security groups |
| [Access Rights](access-rights.md) | Security architecture, permission levels, and group hierarchy |
| [Module Architecture](module-architecture.md) | Module organization, consolidation decisions, and extension patterns |
| [Module Visibility](module-visibility.md) | `application`, `auto_install`, and category settings |
| [API Design](api-design.md) | External identifiers, API standards, and integration patterns |
| [Performance & Scalability](performance-scalability.md) | Database optimization, batch processing, and async patterns |
| [Testing](testing.md) | Coverage targets, test types, and quality requirements |
| [Approval Workflows](approval-workflows.md) | Standardized approval patterns and state machines |
| [Error Handling & Logging](error-handling.md) | Exception patterns, logging standards, and PII protection |
| [Audit & Compliance](audit-compliance.md) | Audit trails, data integrity, and regulatory compliance |
| [UI Design](ui-design.md) | Form layouts, tab structure, extension points, and CSS patterns |
| [UI Entity Classification](ui-entity-classification.md) | Choose UI patterns based on entity type and record volume |
| [UI Performance](ui-performance.md) | Scalability patterns for list views, search panels, and large datasets |
| [Pretty URLs](pretty-urls.md) | User-friendly URL paths for actions |
| [Odoo 19 Compatibility](odoo19-compatibility.md) | Odoo 19 gotchas (constraints, views, Command API) |
| [Module Descriptions](module-descriptions.md) | Writing readme/DESCRIPTION.md files for modules |
| [Multi-Campus Architecture](multi-campus-architecture.md) | Multi-campus deployment, campus isolation, consolidated reporting |
| [Government Integrations](government-integrations.md) | Philippine government systems, LMS, payment gateways, and campus subsystems |
| [Regulatory Compliance](regulatory-compliance.md) | Philippine regulations (RA 10173, MORPHE, RA 10931, RA 10687, PWD, Solo Parent, PQF, Flexible Learning, Microcredentials, RA 9470, Accreditation) |
| [Financial Aid Patterns](financial-aid-patterns.md) | Program types (government, institutional, external, statutory discounts), eligibility rules, discount stacking order, award workflow, and audit/reporting requirements |
| [Enrollment Workflows](enrollment-workflows.md) | Admission pipeline, pre-enrollment gates, enrollment state machine, validation hooks, add/drop, cross-enrollment, and staggered enrollment |
| [Grading and Academic Standing](grading-and-academic-standing.md) | Philippine grading systems, GWA computation, academic standing, INC resolution, grade change workflow, Latin honors |
| [Student Data Lifecycle](student-data-lifecycle.md) | Full student data flow from admissions through alumni status; state machines, models, and cross-cutting concerns per phase |
| [Test Data and PII](test-data-pii.md) | Rules for synthetic test data, demo data, staging masking, CI safeguards, and developer access to PII |
| [Consent Management](consent-management.md) | Consent model, processing purposes, minor consent, withdrawal rules, enforcement patterns, and testing requirements under RA 10173 |
| [Data Retention and Disposal](data-retention-and-disposal.md) | Retention schedule matrix, anonymization rules, disposal procedures, legal hold, and conflict resolution between CHED and RA 10173 |
| [Data Privacy and PII](data-privacy-and-pii.md) | **AUTHORITATIVE** — PII classification tiers, field inventory, encryption strategy, consent management, data subject rights, audit logging, breach response, and developer checklist for RA 10173 compliance |

## How to Use These Principles

1. **New Development**: Review relevant principles before starting new features
2. **Code Reviews**: Reference principles when reviewing pull requests
3. **Onboarding**: New team members should read all principle documents
4. **Decision Making**: Use principles to guide architectural decisions

## Relationship to Other Documentation

These principles are extracted from and complement:

- [Architecture Decisions](../architecture/decisions/) - Architectural Decision Records (ADRs)

## Contributing

When proposing changes to principles:

1. Create an ADR in `docs/architecture/decisions/` for significant changes
2. Update the relevant principle document
3. Ensure consistency across all principle documents
4. Get team review before merging
