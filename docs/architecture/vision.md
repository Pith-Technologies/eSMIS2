# Project Architecture Vision

eSMIS is a Student Management Information System (SMIS) for Philippine Higher Education Institutions (HEIs), built on
Odoo 19. It is designed to comply with CHED regulations, the Data Privacy Act (RA 10173), and the evidence requirements
of accreditation bodies (AACCUP, PACUCOA, PAASCU).

## Mission

Build a standards-compliant, modular Student Information System on Odoo 19 that supports the full student lifecycle —
from application and enrollment through graduation and alumni tracking — while meeting Philippine regulatory reporting
requirements (CHED HEMIS, UniFAST, eCAV) and enabling multi-campus HEI deployments.

## Architecture Principles

- Odoo-native models — use Odoo ORM, not a separate database
- API facade — translate to/from external API formats at system boundaries, not internally
- Compliance-aware — design modules to support CHED, Data Privacy Act, and accreditation requirements from the start
- Progressive deployment — start with core operations, expand to advanced features incrementally
- PQF-aligned — academic programs are mapped to Philippine Qualifications Framework (PQF) levels
- Privacy by design — PII handling follows RA 10173; consent, breach notification, and DPO workflows built in

## Module Map

| Layer              | Modules                                                                                                                       | Purpose                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Integrations**   | `esmis_api`, `esmis_lms_bridge`, `esmis_philsys`, `esmis_payment`                                                            | External API facade, LMS (LTI/OneRoster), PhilSys, payments |
| **Extensions**     | `esmis_reports`, `esmis_documents`, `esmis_alumni`, `esmis_student_services`                                                  | Reporting dashboards, TOR/documents, alumni, student services |
| **Domain Core**    | `esmis_enrollment`, `esmis_curriculum`, `esmis_grading`, `esmis_scheduling`, `esmis_billing`, `esmis_financial_aid`, `esmis_faculty` | Core academic and financial operations               |
| **Foundation**     | `esmis_security`, `esmis_vocabulary`, `esmis_student`, `esmis_academic_term`                                                  | Security, terminology, student records, academic periods   |
| **Odoo Core**      | `hr`, `account`, `calendar`                                                                                                   | Staff/faculty, billing/accounting, scheduling base         |

## Implementation Phases

| Phase | Focus                  | Key Modules                                                                                          |
| ----- | ---------------------- | ---------------------------------------------------------------------------------------------------- |
| 1     | **Foundation**         | `esmis_security`, `esmis_vocabulary`, `esmis_student`, `esmis_academic_term`, `esmis_curriculum`     |
| 2     | **Core Operations**    | `esmis_scheduling`, `esmis_enrollment`, `esmis_grading`                                              |
| 3     | **Financial**          | `esmis_billing`, `esmis_financial_aid`, `esmis_faculty` (workload and payroll inputs)                |
| 4     | **Extended**           | `esmis_documents` (TOR, credentials), `esmis_student_services`, `esmis_alumni`                       |
| 5     | **Portals**            | Student portal, parent portal, reporting dashboards, accreditation evidence exports                  |
| 6     | **Integrations**       | `esmis_api`, `esmis_lms_bridge`, `esmis_philsys`, `esmis_payment`                                   |

## Odoo 19 Strategy

- Extend `res.partner` for domain-specific entities (no parallel entity)
- Use Odoo's workflow engine for business state machines
- Use accounting module for student billing, fees, and financial aid disbursement
- Maintain upgrade-safe patterns: `_inherit` extensions, no core patches

## Multi-Campus Support

eSMIS uses Odoo's native multi-company feature to support multi-campus HEIs. Each campus is modeled as a `res.company`
record. This gives each campus isolated financial records, user access scoping, and configurable academic calendars,
while allowing central administration to view consolidated data across all campuses.

- Campus-specific academic terms, fee schedules, and enrollment quotas are scoped per `res.company`
- Cross-campus course sharing and student transfers are handled via inter-campus records
- Country-specific modules follow the `esmis_*_ph` naming pattern for Philippine-only logic

## Government Integrations

Philippine HEIs must report to multiple government agencies. eSMIS integrates with these systems as follows:

| System        | Type              | Approach                                                         |
| ------------- | ----------------- | ---------------------------------------------------------------- |
| CHED HEMIS    | Portal/file-based | Annual Excel export via `esmis_reports`                         |
| eCAV          | Portal-based      | Document export for credential authentication requests          |
| UniFAST / TES | Portal/file-based | File export for Free Tuition Law (RA 10931) compliance          |
| PhilSys       | Real API          | QR + biometric identity verification via `esmis_philsys`        |
| PayMongo / Maya / Dragonpay | Real API | Online payment collection via `esmis_payment`      |
| LMS (Moodle, Canvas) | LTI 1.3 / OneRoster | Course and grade sync via `esmis_lms_bridge`      |

File-based government integrations are built as export wizards; real-API integrations are dedicated modules.

## PQF Alignment

Academic programs are mapped to Philippine Qualifications Framework (PQF) levels within `esmis_curriculum`. Each
program record carries a `pqf_level` field (levels 1–8), enabling CHED CMO compliance checks and accreditation
reports that require qualification level data.

## Accreditation Support

`esmis_reports` generates evidence packages for AACCUP, PACUCOA, and PAASCU accreditation visits, including:

- Grade distribution and retention rate trend reports
- Faculty qualification summaries (aligned to CHED minimum standards)
- Enrollment and graduation rate data across academic years
- Program outcome achievement summaries (linked to PQF levels)

## Related Documents

- [Odoo Module Integration](integration-patterns.md)
- [Module Architecture](../principles/module-architecture.md)
