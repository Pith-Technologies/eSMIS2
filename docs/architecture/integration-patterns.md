# Odoo Module Integration Patterns

How eSMIS modules map to and extend Odoo 19's built-in capabilities for a Philippine Higher Education SIS.

## Integration Strategy

Extend Odoo modules rather than replacing them. Custom modules add domain-specific fields, workflows, and
validations on top of Odoo's proven foundation. External system integrations follow a dual strategy: real
API calls for systems that support them (PhilSys, payment gateways, LMS), and file export wizards for
portal-based government systems (CHED HEMIS, UniFAST). See ADR-024 for the rationale.

## Module Mapping

| Domain                   | Odoo Module        | Extension Approach                                                                    |
| ------------------------ | ------------------ | ------------------------------------------------------------------------------------- |
| **Students/Contacts**    | `res.partner` (base) | `_inherit` — add `is_student`, `is_faculty`, `is_parent` flags, `student_number`, `program_id` |
| **Faculty/Staff**        | `hr`               | `_inherit` — add `academic_rank`, `specialization`, `teaching_load_units`            |
| **Billing/Fees**         | `account`          | `_inherit` — tuition assessments as invoices, fee payments as journal entries         |
| **Scheduling**           | `calendar`         | `_inherit` — add class session types, room slots, examination schedules               |
| **Documents**            | `documents`        | `_inherit` — add TOR types, credentials, clearance forms, scanned student records     |

## res.partner Extension (Student Profile)

`esmis_student` inherits `res.partner` to represent students, parents, and faculty contacts without
creating a parallel entity:

```python
class ResPartner(models.Model):
    _inherit = "res.partner"

    is_student = fields.Boolean(string="Is Student", default=False)
    is_faculty = fields.Boolean(string="Is Faculty", default=False)
    is_parent = fields.Boolean(string="Is Parent/Guardian", default=False)
    student_number = fields.Char(string="Student Number", index=True)
    program_id = fields.Many2one("esmis.program", string="Program")
```

## hr Extension (Faculty Profile)

`esmis_faculty` inherits `hr.employee` to add academic-specific attributes:

```python
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    academic_rank = fields.Selection(
        selection=[
            ("instructor", "Instructor"),
            ("assistant_professor", "Assistant Professor"),
            ("associate_professor", "Associate Professor"),
            ("full_professor", "Full Professor"),
        ],
        string="Academic Rank",
    )
    specialization = fields.Char(string="Specialization/Field")
    teaching_load_units = fields.Float(string="Teaching Load (Units)")
```

## Custom Models

These have no Odoo base equivalent and are purely `esmis.*`:

| Model                        | Purpose                                               |
| ---------------------------- | ----------------------------------------------------- |
| `esmis.student`              | Student academic record, linked to `res.partner`      |
| `esmis.program`              | Degree program with PQF level, CHED program code      |
| `esmis.curriculum`           | Program curriculum version with subject requirements  |
| `esmis.academic.term`        | Semester/trimester definition per campus              |
| `esmis.enrollment`           | Student enrollment record per term                    |
| `esmis.section`              | Class section with `learning_modality` field          |
| `esmis.grade`                | Grade record with draft → approved → locked workflow  |
| `esmis.financial.aid`        | Scholarship/grant/TES awards linked to `account.*`    |

## Odoo Module Dependencies

```
esmis_vocabulary → base (res.partner)
esmis_student → esmis_vocabulary
esmis_academic_term → esmis_vocabulary
esmis_curriculum → esmis_vocabulary, esmis_academic_term
esmis_enrollment → esmis_student, esmis_curriculum
esmis_grading → esmis_enrollment
esmis_billing → esmis_enrollment, account
esmis_faculty → esmis_vocabulary, hr
esmis_financial_aid → esmis_billing
esmis_api → esmis_vocabulary, esmis_enrollment (+ all domain modules)
esmis_lms_bridge → esmis_enrollment, esmis_grading
esmis_philsys → esmis_student
esmis_payment → esmis_billing
```

## Security Integration

Custom access control layers on top of Odoo's group-based security:

- `group_esmis_viewer` — read records (e.g., student self-service portal)
- `group_esmis_officer` — create/edit records (registrar staff, cashiers)
- `group_esmis_manager` — full access including configuration (registrar head, dean)
- `group_esmis_admin` — manage system configuration

Record rules ensure users only see records in their assigned campus (`res.company`), department, or
advising load. Faculty can only see the grades and enrollments of their own sections.

## Government System Integrations

Philippine HEIs must report to multiple government agencies. eSMIS uses two integration strategies:
**real API** for systems that support it, and **file export wizards** for portal-based systems. See
ADR-024 for the full rationale and consequences.

### PhilSys (PSA — Philippine Identification System)

Module: `esmis_philsys`

| Method | Description |
| ------ | ----------- |
| **PhilSys Check** | QR code scan + EdDSA signature verification against PSA public key. Works offline once the key is distributed. Returns name, date of birth, PCN. |
| **eVerify API** | Live biometric comparison (selfie vs. reference). REST API call returning pass/fail. Requires prior onboarding with PSA and an executed NDA. |

API calls are dispatched via `queue_job` (channel `root.government_api`, max 5 retries with exponential
backoff). PhilSys verification is advisory — enrollment is not hard-blocked if the API is unavailable.
API credentials are stored in `ir.config_parameter` under keys namespaced `esmis_philsys.*`.

### CHED HEMIS

Module: `esmis_ched_hemis_export`

- Integration method: **Excel file export** (no public REST API)
- Annual data collection submitted via CHED Regional Office portal
- Export wizard generates prescribed forms (Form A, Form B/BC, Form E1/E5, Graduate List)
- Wizard validates data completeness before allowing download
- File format version is displayed in the wizard UI so operators can identify stale formats

### UniFAST / TES (Free Tuition — RA 10931)

Module: `esmis_unifast_export`

- Integration method: **Spreadsheet file upload** to TES Portal
- HEI uploads certified list of enrolled student-applicants and applicable fees
- Export wizard pulls from `esmis.enrollment` and `esmis.financial.aid` records
- MOA with CHED-UniFAST is a prerequisite for portal access

### Payment Gateways

Module: `esmis_payment`

- Tuition and fee payments collected via **REST API** (PayMongo, Maya, or Dragonpay)
- Recommended: PayMongo as primary aggregator (single API covers cards, GCash, Maya, bank transfer, OTC)
- Integration model: Payment Intent + **webhooks** for async payment confirmation (`payment.paid`, `payment.failed`)
- Webhook events trigger `account.payment` creation and reconciliation against the student's tuition invoice
- All gateway API calls are asynchronous via `queue_job`; credentials stored in `ir.config_parameter`

## LMS Integration

Module: `esmis_lms_bridge`

Positioned at Layer 4 (Integrations). Nothing depends on it — the core SIS operates normally without it
installed. See ADR-027 for the full decision record.

| Standard | Version | Purpose |
| -------- | ------- | ------- |
| **LTI** | 1.3 | Authenticated tool launch from LMS into SIS-hosted tools; grade passback via Assignment and Grade Services (AGS) |
| **OneRoster** | 1.2 | Enrollment roster synchronization — courses, sections, student/teacher enrollments, add/drop changes |

**Grade passback flow:** LTI AGS writes incoming grades to `esmis.grade` with `state = 'draft'` and
`source = 'lms'`. Faculty review and submit; a registrar approves before the grade is locked. LMS data
cannot directly mutate official grade records.

**OneRoster endpoint:** `/api/oneroster/v1p2/` — authenticated with API key + HMAC-SHA256 per
OneRoster 1.2 security spec. Delta sync uses a `last_modified` cursor per LMS platform record.

**Google Classroom** does not implement LTI 1.3. Integration falls back to OneRoster for roster sync;
grade passback requires manual entry.

**Learning modality** is tracked on `esmis.section` via a `learning_modality` selection field
(`face_to_face`, `online`, `blended`, `asynchronous`) to support CHED CMO No. 4 compliance reporting.

## Library Integration

The dominant ILS in Philippine universities is **Koha** (open-source).

Integration module: `esmis_koha_bridge` (planned)

| Integration Point | Method | Notes |
| ----------------- | ------ | ----- |
| **Patron sync** | Koha REST API | Student enrollment status synced to Koha patron records on enrollment/withdrawal |
| **Clearance verification** | Koha REST API | SIS checks for outstanding library holds/fines before allowing enrollment or TOR release |
| **SSO** | Odoo OAuth | Unified student login for both SIS and OPAC |
| **Self-checkout / RFID gates** | SIP2 | Koha-native; no SIS involvement required |

Koha REST API credentials are stored in `ir.config_parameter` under keys namespaced `esmis_koha.*`.

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
- [ADR-024: Government Integration Architecture](decisions/ADR-024-government-integration-architecture.md)
- [ADR-027: LMS Integration Standards](decisions/ADR-027-lms-integration-standards.md)
- [External System Integrations Research](../research/external-system-integrations.md)
