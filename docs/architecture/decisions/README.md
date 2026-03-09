# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records documenting significant architectural decisions for the project.

## ADR Index

| # | Title | Status | Date | Summary |
|---|-------|--------|------|---------|
| [001](ADR-001-access-rights-management.md) | Access Rights Management | **Implemented** | 2025-11-26 | Three-tier security with Odoo 19 privileges |
| [002](ADR-002-namespace-uris-for-identifiers.md) | Namespace URIs for Identifiers | **Implemented** | 2025-11-28 | Globally unique URIs for ID types |
| [003](ADR-003-terminology-system.md) | Vocabulary System | **Implemented** | 2025-11-28 | Standard + extensible code vocabularies |
| [004](ADR-004-api-v2-architecture.md) | API V2 Architecture | **Implemented** | 2024-11-28 | REST-first, consent-based |
| [005](ADR-005-data-classification-system.md) | Data Classification System | **Implemented** | 2025-11-28 | PII taxonomy, masking, GDPR compliance |
| [006](ADR-006-pii-encryption-strategy.md) | PII Encryption Strategy | Accepted | 2025-11-28 | Application-level encryption + blind indexes |
| [007](ADR-007-dms-security-and-storage-enhancements.md) | DMS Security & Storage Enhancements | **Implemented** | 2025-12-14 | AV scanning, pluggable storage, audit |
| [008](ADR-008-unified-api-audit-log.md) | Unified API Audit Log | Accepted | 2025-12-14 | Single audit model for all API operations |
| [009](ADR-009-api-v2-application-level-authorization.md) | API V2 Application-Level Authorization | Accepted | 2025-12-14 | Scope + consent-based API auth |
| [010](ADR-010-multi-campus-architecture.md) | Multi-Campus Architecture | Accepted | 2026-03-09 | One `res.company` per campus; shared master data, campus-scoped transactional data |
| [011](ADR-011-government-integration-architecture.md) | Government Integration Architecture | Accepted | 2026-03-09 | Dual strategy: API for PhilSys/payments, file export for portal-based systems |
| [012](ADR-012-student-data-privacy-ra10173.md) | Student Data Privacy — RA 10173 | Accepted | 2026-03-09 | Consent management, data subject rights, breach notification (72-hour NPC) |
| [013](ADR-013-financial-aid-modeling.md) | Financial Aid Modeling | Accepted | 2026-03-09 | Rule-based eligibility, stacking order, audit trail for UniFAST/COA |
| [014](ADR-014-lms-integration-standards.md) | LMS Integration Standards | Accepted | 2026-03-09 | LTI 1.3 + OneRoster 1.2, modality tracking, grade passback |
| [015](ADR-015-grading-system-flexibility.md) | Grading System Flexibility | Accepted | 2026-03-09 | Configurable scales, GWA rules, INC resolution, Latin honors |
| [016](ADR-016-foundation-module-strategy.md) | Foundation Module Strategy | Accepted | 2026-03-09 | Keep four separate foundation modules; no esmis_base consolidation |
| [017](ADR-017-internationalization-strategy.md) | Internationalization Strategy | Accepted | 2026-03-09 | Layered localization: country-neutral base modules + `esmis_*_{country}` extensions |

## Status Legend

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet approved |
| **Accepted** | Approved, implementation pending or in progress |
| **Implemented** | Fully implemented and in production |
| **Partial** | Partially implemented |
| **Deprecated** | No longer recommended |
| **Superseded** | Replaced by another ADR |

## Context

ADRs 001–009 cover cross-cutting concerns (security, identifiers, terminology, data classification, encryption, document management, API audit/auth) that apply to any Odoo 19 project using the `esmis_*` module convention.

## Creating New ADRs

1. Use the next available number (currently 018)
2. Follow the template: `ADR-NNN-short-title.md`
3. Include: Status, Date, Context, Decision, Consequences
4. Update this index after creating
