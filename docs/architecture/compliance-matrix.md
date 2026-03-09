# Compliance Matrix

Cross-reference of Philippine regulations addressed by each eSMIS module. Intended for accreditation reviews,
institutional evaluations, and internal compliance audits.

> **Scope:** This matrix maps system-level compliance responsibilities. Organizational obligations (e.g., appointing a
> DPO, conducting a PIA) are listed in the audit checklist but are not module deliverables. See
> [Regulatory Compliance](../principles/regulatory-compliance.md) for the full legal analysis.

---

## Table of Contents

1. [Module x Regulation Matrix](#1-module--regulation-matrix)
2. [Per-Regulation Detail](#2-per-regulation-detail)
3. [Compliance Audit Checklist](#3-compliance-audit-checklist)
4. [Gap Analysis](#4-gap-analysis)

---

## 1. Module x Regulation Matrix

Legend:

- **X** — Primary compliance responsibility (the module directly implements requirements of this regulation)
- **(P)** — Partial / supporting compliance (the module contributes data or infrastructure used by a primary module)

### Regulations (columns)

| Abbrev  | Regulation                                       |
| ------- | ------------------------------------------------ |
| DPA     | RA 10173 — Data Privacy Act                      |
| MORPHE  | CHED MORPHE (CMO 40, s. 2008) — Academic Records |
| FTL     | RA 10931 — Free Tuition Law                      |
| UniFAST | RA 10687 — UniFAST Act                           |
| PWD     | RA 7277/9442/10754 — PWD Rights                  |
| SoloPar | RA 8972/11861 — Solo Parent Welfare              |
| PQF     | RA 10968 — Philippine Qualifications Framework   |
| MicroCr | CMO 1, s. 2025 — Microcredentials                |
| NSLA    | RA 9470 — National Archives / Records Retention  |
| Accred  | Accreditation (AACCUP/PACUCOA/PAASCU)            |

### Matrix

| Module                   | DPA   | MORPHE | FTL   | UniFAST | PWD   | SoloPar | PQF   | MicroCr | NSLA  | Accred |
| ------------------------ | ----- | ------ | ----- | ------- | ----- | ------- | ----- | ------- | ----- | ------ |
| `esmis_vocabulary`       | (P)   | (P)    |       |         | (P)   |         | (P)   |         |       |        |
| `esmis_security`         | **X** |        |       |         |       |         |       |         | **X** |        |
| `esmis_academic_term`    |       | (P)    |       |         |       |         |       |         |       | (P)    |
| `esmis_student`          | **X** | **X**  | (P)   |         | (P)   | (P)     |       |         | (P)   | (P)    |
| `esmis_curriculum`       |       | **X**  |       |         |       |         | **X** | (P)     |       | (P)    |
| `esmis_scheduling`       |       | (P)    |       |         |       |         |       |         |       | (P)    |
| `esmis_faculty`          |       | (P)    |       |         |       |         |       |         |       | (P)    |
| `esmis_enrollment`       | **X** | **X**  | **X** |         | **X** | **X**   |       |         |       | (P)    |
| `esmis_grading`          | **X** | **X**  |       |         |       |         |       |         | (P)   | (P)    |
| `esmis_billing`          |       |        | **X** |         | **X** | (P)     |       |         | (P)   |        |
| `esmis_financial_aid`    |       |        | **X** | **X**   | **X** | **X**   |       |         | (P)   | (P)    |
| `esmis_documents`        | (P)   | **X**  |       |         |       |         |       | (P)     | **X** | (P)    |
| `esmis_reports`          | (P)   | (P)    | **X** | **X**   | (P)   |         | **X** |         |       | **X**  |
| `esmis_student_services` | **X** |        |       |         | **X** |         |       |         | (P)   | (P)    |
| `esmis_alumni`           | **X** |        |       |         |       |         |       |         |       | (P)    |
| `esmis_api`              | **X** |        |       |         |       |         |       |         |       |        |
| `esmis_student_portal`   | **X** |        |       |         |       |         |       |         |       |        |
| `esmis_lms_bridge`       | (P)   | (P)    |       |         |       |         |       |         |       |        |
| `esmis_philsys`          | **X** |        | (P)   |         |       |         |       |         |       |        |
| `esmis_payment`          | (P)   |        |       |         |       |         |       |         | (P)   |        |

### Reading the Matrix

- **esmis_security** is the infrastructure backbone for RA 10173 (consent, breach notification, DSAR, PII access
  logging, audit trails) and RA 9470 (retention schedules, disposal workflows, legal holds).
- **esmis_enrollment** is the primary collection point for regulatory data: citizenship (FTL), PWD status, solo parent
  status, minor consent (DPA), and cross-enrollment/transfer records (MORPHE).
- **esmis_financial_aid** is the convergence point for all financial benefit laws: RA 10931 (Free Tuition), RA 10687
  (UniFAST/StuFAP), RA 7277/10754 (PWD discount), and RA 8972/11861 (solo parent scholarship).
- **esmis_reports** is the primary output module for government and accreditation reporting across most regulations.
- **(P)** entries indicate that a module provides data or vocabulary codes consumed by a primary module (e.g.,
  `esmis_vocabulary` supplies PWD disability type codes used by `esmis_enrollment`).

---

## 2. Per-Regulation Detail

### 2.1 RA 10173 — Data Privacy Act

**Enforcing body:** National Privacy Commission (NPC)<br> **Key articles:** Sections 3(l), 11–13 (lawful processing),
16–18 (data subject rights), 20–23 (security), 25–26 (breach notification), 36 (penalty increase for minors)<br> **NPC
Circulars:** 2023-06 (MFA), 2020-03 (ROPA), 16-03 (breach management)

| Requirement                                                          | Implementing Module(s)                                                          | Status      |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------- |
| Consent capture (adult and minor) with per-purpose granularity       | `esmis_security` (consent model), `esmis_enrollment` (collection point)         | Not Started |
| Consent versioning and re-consent on policy change                   | `esmis_security`                                                                | Not Started |
| DPO role with ROPA and consent record access                         | `esmis_security`                                                                | Not Started |
| Record of Processing Activities (ROPA)                               | `esmis_security`                                                                | Not Started |
| Breach notification workflow (72-hour NPC deadline)                  | `esmis_security`                                                                | Not Started |
| Data subject access requests (DSAR) with 30-working-day SLA          | `esmis_security`                                                                | Not Started |
| Data export per student (JSON/PDF) on access request                 | `esmis_security`, `esmis_student`                                               | Not Started |
| Rectification workflow with audit trail                              | `esmis_security` (audit mixin), all domain modules                              | Not Started |
| Erasure of non-permanent data; blocking erasure of permanent records | `esmis_security` (audit mixin), `esmis_documents`                               | Not Started |
| Data portability export (structured, machine-readable)               | `esmis_security`, `esmis_api`                                                   | Not Started |
| Role-based access control (registrar, finance, student, etc.)        | `esmis_security` (groups/ACLs), all modules                                     | Not Started |
| PII field classification (Tier 1/2/3) and field-level access         | `esmis_security` (pii.aware mixin), all PII models                              | Not Started |
| PII access logging (append-only, immutable)                          | `esmis_security`                                                                | Not Started |
| Encryption at rest for Tier 3 fields                                 | `esmis_security` (pii.aware), `esmis_student`, `esmis_philsys`, `esmis_payment` | Not Started |
| TLS in transit                                                       | Infrastructure (not a module)                                                   | Not Started |
| MFA for SPI access (NPC Circular 2023-06)                            | `esmis_security`, `esmis_student_portal`                                        | Not Started |
| Grades treated as SPI — no public posting                            | `esmis_grading`, `esmis_student_portal`                                         | Not Started |
| Cross-border transfer logging and NPC approval                       | `esmis_security`                                                                | Not Started |
| Alumni-specific consent for post-graduation tracking                 | `esmis_alumni`                                                                  | Not Started |
| API consent verification before returning PII                        | `esmis_api`                                                                     | Not Started |
| Portal PII update logging                                            | `esmis_student_portal`                                                          | Not Started |

### 2.2 CHED MORPHE (CMO 40, s. 2008)

**Scope:** All private HEIs; SUCs follow equivalent regulations<br> **Key sections:** Permanent academic records,
enrollment/registration, grading, academic standing, Latin honors

| Requirement                                                             | Implementing Module(s)                              | Status      |
| ----------------------------------------------------------------------- | --------------------------------------------------- | ----------- |
| Permanent academic record per student (TOR as official document)        | `esmis_documents`, `esmis_grading`, `esmis_student` | Not Started |
| Admission credentials capture (Form 137, SHS Diploma, LRN)              | `esmis_enrollment`                                  | Not Started |
| Enrollment forms per semester                                           | `esmis_enrollment`                                  | Not Started |
| Academic transcript (course, units, grade, semester, year)              | `esmis_grading`, `esmis_documents`                  | Not Started |
| Financial ledger (tuition/fee history)                                  | `esmis_billing`                                     | Not Started |
| Configurable grading scale (1.0-5.0, letter, percentage)                | `esmis_grading`                                     | Not Started |
| GWA/GPA computation (formula-driven, per-institution)                   | `esmis_grading`                                     | Not Started |
| Grade change workflow (request, approval, audit trail)                  | `esmis_grading`                                     | Not Started |
| INC grade resolution with deadline and auto-conversion                  | `esmis_grading`                                     | Not Started |
| Cross-enrollment tracking and credit flagging                           | `esmis_enrollment`                                  | Not Started |
| Transfer student admission (honorable dismissal, TOR, unit equivalency) | `esmis_enrollment`                                  | Not Started |
| Maximum residency tracking                                              | `esmis_enrollment`                                  | Not Started |
| Academic standing computation (probation, dismissal)                    | `esmis_grading`                                     | Not Started |
| Latin honors computation at graduation                                  | `esmis_grading`, `esmis_documents`                  | Not Started |
| TOR generation with all enrolled semesters and GWA                      | `esmis_documents`                                   | Not Started |
| Permanent records immutable once certified                              | `esmis_documents`, `esmis_security` (audit mixin)   | Not Started |
| Learning modality per section per semester                              | `esmis_scheduling`                                  | Not Started |

### 2.3 RA 10931 — Free Tuition Law

**Implementing agencies:** CHED, UniFAST<br> **Scope:** SUCs and LUCs (free tuition); private HEIs (TES subsidy)

| Requirement                                                      | Implementing Module(s)                               | Status      |
| ---------------------------------------------------------------- | ---------------------------------------------------- | ----------- |
| Filipino citizenship capture and verification                    | `esmis_enrollment`, `esmis_student`, `esmis_philsys` | Not Started |
| Prior degree status tracking (disqualifies from free tuition)    | `esmis_enrollment`, `esmis_student`                  | Not Started |
| Institutional type configuration (SUC/LUC/private)               | `esmis_enrollment` (institution-level config)        | Not Started |
| Academic standing check for retention compliance                 | `esmis_grading`, `esmis_enrollment`                  | Not Started |
| Free tuition eligibility computed automatically (4 criteria)     | `esmis_billing`, `esmis_financial_aid`               | Not Started |
| Tuition subsidy stored as named ledger line per student/semester | `esmis_billing`                                      | Not Started |
| TES beneficiary flag and amount (separate from free tuition)     | `esmis_financial_aid`                                | Not Started |
| CHED subsidy report per student per semester                     | `esmis_reports`                                      | Not Started |
| UniFAST annual report (StuFAP summary)                           | `esmis_reports`                                      | Not Started |
| Retention failure suspends next-semester eligibility             | `esmis_financial_aid`, `esmis_grading`               | Not Started |

### 2.4 RA 10687 — UniFAST Act

**Purpose:** Unify all government-funded StuFAPs under the UniFAST Board

| Requirement                                                            | Implementing Module(s)                              | Status      |
| ---------------------------------------------------------------------- | --------------------------------------------------- | ----------- |
| Per-student StuFAP grant records (program, agency, modality, amount)   | `esmis_financial_aid`                               | Not Started |
| Multiple StuFAP programs per student per semester                      | `esmis_financial_aid`                               | Not Started |
| Implementing agency as required field on each grant                    | `esmis_financial_aid`                               | Not Started |
| Configurable eligibility criteria per program                          | `esmis_financial_aid`                               | Not Started |
| UniFAST annual report grouped by agency and modality                   | `esmis_reports`                                     | Not Started |
| TES tracked as one StuFAP modality (no duplication)                    | `esmis_financial_aid`                               | Not Started |
| Historical StuFAP records retained per retention policy (10 years min) | `esmis_financial_aid`, `esmis_security` (retention) | Not Started |

### 2.5 RA 7277/9442/10754 — PWD Rights

**Enforcing body:** National Council on Disability Affairs (NCDA)

| Requirement                                                    | Implementing Module(s)                        | Status      |
| -------------------------------------------------------------- | --------------------------------------------- | ----------- |
| PWD status and PWD ID capture with expiry tracking             | `esmis_enrollment`, `esmis_student`           | Not Started |
| PWD ID classified as SPI with restricted access                | `esmis_security` (pii.aware), `esmis_student` | Not Started |
| 20% discount on qualifying educational fees                    | `esmis_billing`, `esmis_financial_aid`        | Not Started |
| Discount as named ledger line for audit                        | `esmis_billing`                               | Not Started |
| Accommodation tracking (extended time, assistive devices)      | `esmis_student_services`                      | Not Started |
| PWD scholarship eligibility auto-flagging                      | `esmis_financial_aid`                         | Not Started |
| HEMIS PWD count by program, year level, disability type        | `esmis_reports`                               | Not Started |
| Non-discrimination: disability excluded from rejection reasons | `esmis_enrollment`                            | Not Started |
| Disability type as configurable vocabulary                     | `esmis_vocabulary`                            | Not Started |

### 2.6 RA 8972/11861 — Solo Parent Welfare

**Key provision:** Full scholarship for one dependent child of a qualified solo parent

| Requirement                                                           | Implementing Module(s)                        | Status      |
| --------------------------------------------------------------------- | --------------------------------------------- | ----------- |
| Solo parent dependent status and Solo Parent ID capture               | `esmis_enrollment`, `esmis_student`           | Not Started |
| Solo Parent ID classified as SPI with restricted access               | `esmis_security` (pii.aware), `esmis_student` | Not Started |
| Dependency eligibility enforcement (age <= 22, unmarried, unemployed) | `esmis_enrollment`                            | Not Started |
| Scholarship eligibility auto-flagging                                 | `esmis_financial_aid`                         | Not Started |
| Solo Parent ID expiry tracking and renewal reminders                  | `esmis_enrollment`                            | Not Started |
| Dual-benefit support (PWD + solo parent without conflict)             | `esmis_billing`, `esmis_financial_aid`        | Not Started |
| Financial aid record linked to solo parent dependent record           | `esmis_financial_aid`                         | Not Started |
| Annual ID re-verification at enrollment                               | `esmis_enrollment`                            | Not Started |

### 2.7 RA 10968 — Philippine Qualifications Framework

**Coordinating body:** PQF-NCC<br> **eSMIS scope:** PQF Levels 5-8 (HEI programs)

| Requirement                                                   | Implementing Module(s) | Status      |
| ------------------------------------------------------------- | ---------------------- | ----------- |
| Program-to-PQF-level mapping (required field)                 | `esmis_curriculum`     | Not Started |
| Curriculum learning outcomes aligned to PQF level descriptors | `esmis_curriculum`     | Not Started |
| Credit transfer with PQF-level equivalency rationale          | `esmis_enrollment`     | Not Started |
| Qualification pathways (lateral and vertical mobility)        | `esmis_curriculum`     | Not Started |
| Microcredential PQF level mapping                             | `esmis_curriculum`     | Not Started |
| PQF-NCC registry export (programs, levels, graduate counts)   | `esmis_reports`        | Not Started |

### 2.8 CMO 1, s. 2025 — Microcredentials

**Purpose:** National guidelines for microcredential development and CHED recognition

| Requirement                                                                  | Implementing Module(s)                           | Status      |
| ---------------------------------------------------------------------------- | ------------------------------------------------ | ----------- |
| Microcredential records with PQF level, CHED approval ref, learning outcomes | `esmis_curriculum` (planned `esmis_credentials`) | Not Started |
| Credential stacking toward larger qualifications (diploma/degree)            | `esmis_curriculum` (planned `esmis_credentials`) | Not Started |
| CHED approval required before award                                          | `esmis_curriculum` (planned `esmis_credentials`) | Not Started |
| Open Badges 3.0 issuance (JSON-LD, signed)                                   | `esmis_documents` (planned `esmis_credentials`)  | Not Started |
| W3C Verifiable Credentials issuance (JWT or JSON-LD proof)                   | `esmis_documents` (planned `esmis_credentials`)  | Not Started |
| Credential revocation capability                                             | `esmis_documents` (planned `esmis_credentials`)  | Not Started |
| Unauthenticated verification endpoint                                        | `esmis_api` (planned `esmis_credentials`)        | Not Started |
| Stacking ledger auditable                                                    | `esmis_curriculum` (planned `esmis_credentials`) | Not Started |

### 2.9 RA 9470 — National Archives Act (NSLA)

**Enforcing body:** National Archives of the Philippines (NAP)<br> **Scope:** Public HEIs (NAP approval required);
private HEIs follow CHED retention guidelines

| Requirement                                                       | Implementing Module(s)                                             | Status      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ | ----------- |
| Record type classification with retention category                | `esmis_security` (retention.aware mixin, retention.schedule)       | Not Started |
| Permanent records (TOR, grade sheets, diplomas) cannot be deleted | `esmis_documents`, `esmis_grading`, `esmis_security` (audit mixin) | Not Started |
| Retention end date computation for finite-retention records       | `esmis_security` (retention.schedule)                              | Not Started |
| Monthly scheduled job for disposal review task creation           | `esmis_security` (disposal.review)                                 | Not Started |
| Disposal workflow with NAP approval step (public HEIs)            | `esmis_security` (disposal.review)                                 | Not Started |
| Legal hold flag blocks disposal                                   | `esmis_security` (audit.mixin, retention.aware)                    | Not Started |
| Disposal logs (immutable, retained 5 years)                       | `esmis_security` (audit.log)                                       | Not Started |
| Digital erasure method documented in disposal log                 | `esmis_security`                                                   | Not Started |
| 10-year minimum financial record retention (COA alignment)        | `esmis_billing`, `esmis_financial_aid`, `esmis_security`           | Not Started |
| Historical data retained for 10+ years (accreditation cycles)     | All transactional modules, `esmis_security`                        | Not Started |

### 2.10 Accreditation (AACCUP/PACUCOA/PAASCU)

**Recognized by:** CHED through FAAP<br> **Cycle:** 3-5 years; requires 10+ years of historical data

| Requirement                                                          | Implementing Module(s)                    | Status      |
| -------------------------------------------------------------------- | ----------------------------------------- | ----------- |
| Enrollment trends (program, year level, sex, modality)               | `esmis_reports`, `esmis_enrollment`       | Not Started |
| Retention rates (cohort-based, semester-to-semester)                 | `esmis_reports`, `esmis_enrollment`       | Not Started |
| Completion/graduation rates (per program, per cohort)                | `esmis_reports`, `esmis_documents`        | Not Started |
| Grade distributions (per course, per semester)                       | `esmis_reports`, `esmis_grading`          | Not Started |
| Faculty-student ratios (per program, per semester)                   | `esmis_reports`, `esmis_faculty`          | Not Started |
| Student services utilization (guidance, health, financial aid)       | `esmis_reports`, `esmis_student_services` | Not Started |
| Research output tracking (thesis/dissertation for graduate programs) | `esmis_reports`                           | Not Started |
| Scholarship and financial assistance data                            | `esmis_reports`, `esmis_financial_aid`    | Not Started |
| Disciplinary case statistics                                         | `esmis_reports`, `esmis_student_services` | Not Started |
| PWD accommodation records                                            | `esmis_student_services`                  | Not Started |
| Accreditation evidence export (packaged, date-ranged)                | `esmis_reports`                           | Not Started |
| Alumni tracer study outcomes                                         | `esmis_alumni`                            | Not Started |
| Report metadata (data source, computation method, period)            | `esmis_reports`                           | Not Started |

---

## 3. Compliance Audit Checklist

Use this checklist as a go/no-go gate before deployment. Each item is actionable and references the regulation that
requires it.

### 3.1 RA 10173 — Data Privacy Act

#### Organizational (pre-deployment)

- [ ] NPC registration completed for eSMIS as a data processing system
- [ ] Data Protection Officer (DPO) appointed and named user role exists in system
- [ ] Privacy Impact Assessment (PIA) conducted and attached to deployment record
- [ ] Record of Processing Activities (ROPA) maintained and current
- [ ] Privacy notice published and presented at enrollment

#### Technical (system verification)

- [ ] Consent model (`esmis.consent`) captures: student, purpose, date given, date withdrawn, captured by whom
- [ ] Minor vs. adult consent routing works (age < 18 at enrollment triggers parental consent)
- [ ] Consent forms are versioned; policy change triggers re-consent
- [ ] Breach notification workflow completes all steps within 72 hours (test with simulated breach)
- [ ] DSAR workflow tracks: received, acknowledged (30 working days), fulfilled or rejected with reason
- [ ] Data export per student produces complete personal data in JSON/PDF
- [ ] Rectification creates audit log entry (old value, new value, requestor, approver, date)
- [ ] Erasure of permanent academic records raises `UserError` citing legal basis
- [ ] Erasure of non-academic personal data succeeds
- [ ] Data portability export excludes other students' PII
- [ ] PII fields classified by tier; Tier 2/3 have field-level access groups
- [ ] PII access log is append-only (write/unlink blocked)
- [ ] Tier 3 fields (national IDs, grades, health data) encrypted at rest
- [ ] MFA enabled for all users accessing SPI data
- [ ] Grades not exposed in any public-facing view or list export
- [ ] Cross-border transfer logged and requires NPC approval
- [ ] No PII in `_logger` calls or exception messages (audit codebase)
- [ ] API endpoints verify consent before returning PII fields
- [ ] Portal personal info updates logged in PII access log

### 3.2 CHED MORPHE (CMO 40, s. 2008)

- [ ] Grading scale configurable per HEI and per program
- [ ] GWA computation formula documented in system configuration (not hard-coded)
- [ ] Grade change workflow: request with reason -> department head -> registrar -> audit log; original preserved
- [ ] INC grades have resolution deadline; unresolved INC auto-converts to failing grade
- [ ] Cross-enrollment records link home institution, host, course, units, grade
- [ ] Transfer students: honorable dismissal number, source TOR, credited units with equivalency
- [ ] Maximum residency computed (program length x 1.5); students approaching limit flagged
- [ ] TOR generation: complete transcript with all semesters, grades, units, GWA
- [ ] Academic standing computed automatically after each grading period
- [ ] Latin honors computed at graduation using all applicable enrolled units
- [ ] Permanent records immutable once certified; corrections go through grade change workflow
- [ ] Learning modality stored per section per semester; historical data immutable

### 3.3 RA 10931 — Free Tuition Law

- [ ] Filipino citizenship field required at enrollment; drives eligibility
- [ ] Prior degree field captured; automatically disqualifies from free tuition
- [ ] Institutional type (SUC/LUC/private) configured at HEI level
- [ ] Free tuition eligibility auto-computed using all 4 criteria at enrollment
- [ ] Tuition and school fees zeroed for eligible students; non-covered fees computed normally
- [ ] Tuition subsidy stored as named ledger line (not silently removed) for CHED audit
- [ ] TES beneficiary flag and amount stored separately from free tuition subsidy
- [ ] Retention failure flags student; next-semester eligibility suspended pending review
- [ ] CHED subsidy report: per-student, per-semester breakdown in CHED format
- [ ] UniFAST annual report: consolidated StuFAP summary per student

### 3.4 RA 10687 — UniFAST Act

- [ ] Each StuFAP grant recorded as separate record: program name, agency, modality, semester, amount
- [ ] Multiple StuFAP programs per student per semester supported
- [ ] Implementing agency is required field; reports filterable by agency
- [ ] Eligibility criteria per program configurable; verification recorded
- [ ] UniFAST annual report: per-student summary grouped by agency and modality
- [ ] TES tracked as one StuFAP modality within UniFAST framework (no duplication)
- [ ] Historical StuFAP records retained minimum 10 years

### 3.5 RA 7277/9442/10754 — PWD Rights

- [ ] `is_pwd` boolean and `pwd_id_number` on student record; PWD ID expiry tracked
- [ ] PWD ID number restricted to authorized roles (SPI)
- [ ] 20% discount auto-applied on qualifying fee lines when `is_pwd = True`
- [ ] Discount recorded as named line item ("PWD Discount -- RA 9442") for audit
- [ ] Accommodations recorded (extended exam time, accessible seating, assistive devices)
- [ ] PWD scholarship eligibility auto-flagged
- [ ] HEMIS: PWD count disaggregated by program, year level, disability type
- [ ] Disability type is a configurable vocabulary (via `esmis_vocabulary`)
- [ ] Admission system does not allow disability as rejection reason

### 3.6 RA 8972/11861 — Solo Parent Welfare

- [ ] `is_solo_parent_dependent` boolean and `solo_parent_id_number` on student record; ID expiry tracked
- [ ] Solo Parent ID restricted to authorized roles (SPI)
- [ ] Dependency criteria enforced: age <= 22, unmarried, unemployed
- [ ] Eligible students auto-flagged for solo parent scholarship programs
- [ ] Expired Solo Parent ID triggers renewal reminder (no auto-removal of benefit)
- [ ] Dual-benefit: PWD discount + solo parent scholarship coexist without conflict
- [ ] Financial aid record links to solo parent dependent record for audit
- [ ] Annual ID re-verification prompted at enrollment

### 3.7 RA 10968 — Philippine Qualifications Framework

- [ ] Every program has `pqf_level` field (5, 6, 7, 8); required before program activation
- [ ] Curriculum records link courses to PQF level descriptors (knowledge, skills, values)
- [ ] Credit transfer records include PQF-level equivalency rationale
- [ ] Qualification pathways (lateral/vertical mobility) recorded
- [ ] Microcredential records inherit PQF level field
- [ ] PQF-NCC registry export: active programs, levels, learning outcome summaries, graduate counts

### 3.8 CMO 1, s. 2025 — Microcredentials

- [ ] Microcredential model stores: title, PQF level, learning outcomes, CHED approval ref, stackable target, unit
      equivalency
- [ ] Student earned-credential record: student, microcredential, completion date, issuing HEI, credential object
- [ ] Stacking toward degree updates earned-units count; stacking ledger auditable
- [ ] CHED approval reference required before award (system blocks issuance without it)
- [ ] Open Badges 3.0 JSON-LD assertion generated and hosted; schema-valid
- [ ] W3C Verifiable Credential generated with configurable proof mechanism (JWT or JSON-LD)
- [ ] Revocation capability; revocation reflected in credential status URL/list
- [ ] Unauthenticated verification endpoint; does not expose other student data

### 3.9 RA 9470 — National Archives Act

- [ ] Every record type classified with retention category (permanent, 10-year, 5-year, institutional)
- [ ] Permanent records: `unlink()` raises `UserError` citing legal basis
- [ ] Finite-retention records have computed `retention_end_date`
- [ ] Monthly scheduled job identifies past-retention records; creates disposal review tasks
- [ ] Public HEI disposal workflow requires NAP approval reference before disposal
- [ ] Private HEI disposal workflow requires CHED-aligned retention verification
- [ ] `is_legal_hold = True` blocks disposal workflow; surfaced to legal/compliance officer
- [ ] Disposal logs: record type, identifier, date, method, authorized by, approval ref, legal hold attestation
- [ ] Disposal logs retained 5 years; immutable after creation
- [ ] Digital erasure method documented in disposal log

### 3.10 Accreditation (AACCUP/PACUCOA/PAASCU)

- [ ] Enrollment trend report: by program, year level, sex, modality; cross-semester; exportable CSV/PDF
- [ ] Retention rate report: cohort-based, semester-to-semester tracking
- [ ] Completion rate report: graduates vs. dropouts vs. still-enrolled, filterable by program/entry year
- [ ] Grade distribution report: per course/semester; aggregatable across sections; exportable
- [ ] Faculty-student ratio: per program per semester; FTE-based computation
- [ ] Student services utilization: service type, date, frequency reports
- [ ] Research output: thesis/dissertation tracking for graduate programs
- [ ] Historical data retained minimum 10 years (two full accreditation cycles)
- [ ] Accreditation evidence export: packaged report with all metrics for specified date range
- [ ] Every report includes data source, computation method, and reporting period
- [ ] Large historical reports generated asynchronously via `queue_job`
- [ ] Alumni tracer study data supports graduate outcome reporting

---

## 4. Gap Analysis

Regulatory requirements that are not yet clearly mapped to a specific planned module.

### 4.1 Identified Gaps

| #   | Regulation         | Requirement                                                                      | Gap Description                                                                                                                                                                                                                                                                                                   | Suggested Resolution                                                                                                                                                                                 |
| --- | ------------------ | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | CMO 1, s. 2025     | Microcredential program management, stacking, and verifiable credential issuance | The regulatory compliance doc references a planned `esmis_credentials` module, but this module does not appear in the 20-module implementation roadmap. Microcredential features are tentatively assigned to `esmis_curriculum` and `esmis_documents`, but neither module's spec includes microcredential models. | Add `esmis_credentials` as a Phase 4 or Phase 5 module, or explicitly add microcredential models to `esmis_curriculum` and verifiable credential issuance to `esmis_documents`.                      |
| 2   | RA 10173           | Privacy Impact Assessment (PIA) documentation and tracking                       | PIA is an organizational requirement. The system could track PIA versions and link them to deployment records, but no module currently plans this.                                                                                                                                                                | Consider adding PIA tracking to `esmis_security` as a configuration record.                                                                                                                          |
| 3   | RA 10173           | NPC registration tracking                                                        | Registration of eSMIS as a data processing system with the NPC is a pre-deployment step. No module tracks this status.                                                                                                                                                                                            | Add NPC registration reference field to `esmis_security` institution configuration.                                                                                                                  |
| 4   | CMO 4, s. 2020     | Flexible learning modality GWA computation adjustments                           | CMO 4 permits HEIs to adjust GWA computation for online modalities. The grading module supports configurable grading systems but does not explicitly model modality-aware GWA formulas.                                                                                                                           | Ensure `esmis_grading` GWA computation can reference section modality. Likely a configuration enhancement rather than a new module.                                                                  |
| 5   | CHED MORPHE        | Disciplinary records as part of permanent student file                           | MORPHE requires disciplinary records in the student file. `esmis_student_services` handles disciplinary records, but linking them to the permanent record (TOR/student file) is not explicitly specified.                                                                                                         | Ensure `esmis_documents` can include or reference disciplinary records when generating the complete student file.                                                                                    |
| 6   | RA 10173           | Cross-border data transfer approval workflow                                     | The system must log cross-border transfers and require NPC approval. No specific model or workflow is defined for this in the `esmis_security` specification.                                                                                                                                                     | Add a `esmis.cross.border.transfer` model (or equivalent) to `esmis_security` to track transfer requests, destinations, NPC approval status, and logging.                                            |
| 7   | Accreditation      | Research output tracking (thesis/dissertation)                                   | Accreditation bodies require research output metrics for graduate programs. No module currently models thesis/dissertation records.                                                                                                                                                                               | Add thesis/dissertation tracking to `esmis_documents` or create a lightweight model in `esmis_reports`. Alternatively, define a new `esmis_research` module for institutions with graduate programs. |
| 8   | RA 10173 + RA 9470 | Consent form retention                                                           | Consent forms must be retained for the duration of processing plus a reasonable period. The retention schedule model exists in `esmis_security`, but explicit retention category assignment for consent records is not specified.                                                                                 | Ensure `esmis.consent` records are classified under the retention schedule with an appropriate category.                                                                                             |
| 9   | CHED               | HEMIS form specifications (CMO 45, s. 2016)                                      | `esmis_reports` includes a HEMIS export wizard, but the exact CHED form specifications (Forms A, B/BC, E1/E2/E5, GH, Graduate List) need validation against current CHED templates.                                                                                                                               | Obtain current CHED HEMIS Excel templates and validate export format during `esmis_reports` implementation.                                                                                          |
| 10  | CHED               | eCAV (Electronic Certification, Authentication, and Verification)                | The regulatory compliance doc mentions eCAV-compatible credential formats, but no module explicitly implements eCAV integration.                                                                                                                                                                                  | Add eCAV format support to `esmis_documents` for TOR and diploma verification.                                                                                                                       |

### 4.2 Risk Assessment

| Risk Level | Count | Description                                                                                                                             |
| ---------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **High**   | 1     | Gap #1 (Microcredentials): CMO 1, s. 2025 is a new regulation. No module currently owns this. Requires architectural decision.          |
| **Medium** | 4     | Gaps #4, #5, #6, #7: Feature enhancements needed in existing planned modules. Can be addressed during implementation.                   |
| **Low**    | 5     | Gaps #2, #3, #8, #9, #10: Configuration or specification details. Addressed during module implementation without architectural changes. |

### 4.3 Recommended Actions

1. **Architectural Decision Required:** Decide whether microcredentials (CMO 1, s. 2025) become a dedicated
   `esmis_credentials` module or are absorbed into `esmis_curriculum` + `esmis_documents`. Document the decision in
   `docs/architecture/decisions/`.

2. **Specification Updates Needed:** During implementation of `esmis_grading`, `esmis_documents`, `esmis_security`, and
   `esmis_reports`, incorporate the medium-risk gaps (#4, #5, #6, #7) into acceptance criteria.

3. **Pre-Deployment Verification:** Gaps #9 (HEMIS templates) and #10 (eCAV format) require validation against current
   government portal specifications before deployment.

---

**Cross-references:**

- [Regulatory Compliance Principles](../principles/regulatory-compliance.md) — full legal analysis and implementation
  checklists
- [Implementation Roadmap](implementation-roadmap.md) — module specifications, dependencies, and phasing
- [Government Integrations](../principles/government-integrations.md) — API and export specifications for government
  systems
