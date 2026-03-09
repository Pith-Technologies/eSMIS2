# Student Data Lifecycle

How student data flows through eSMIS from first contact at admissions to alumni status and
post-graduation credential services. This document is a reference for implementers — it
describes the full picture so that any phase can be built with the others in mind.

> **Scope:** This document describes the intended target architecture. Not all phases are
> fully implemented. Check the relevant module's `readme/DESCRIPTION.md` for current status.

---

## Table of Contents

1. [Lifecycle Overview (Diagram)](#1-lifecycle-overview-diagram)
2. [Phase 1 — Pre-Enrollment (Admissions)](#2-phase-1--pre-enrollment-admissions)
3. [Phase 2 — Enrollment](#3-phase-2--enrollment)
4. [Phase 3 — Active Academic Term](#4-phase-3--active-academic-term)
5. [Phase 4 — Grading](#5-phase-4--grading)
6. [Phase 5 — Term Transition](#6-phase-5--term-transition)
7. [Phase 6 — Graduation](#7-phase-6--graduation)
8. [Phase 7 — Post-Graduation (Alumni)](#8-phase-7--post-graduation-alumni)
9. [Cross-Cutting Concerns](#9-cross-cutting-concerns)
10. [Data Model Summary](#10-data-model-summary)

---

## 1. Lifecycle Overview (Diagram)

The diagram below shows the primary states and transitions across the full student lifecycle.
Horizontal arrows are forward transitions; upward arrows indicate reversible paths (e.g.,
re-enrollment after leave of absence).

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               STUDENT DATA LIFECYCLE                                     │
└──────────────────────────────────────────────────────────────────────────────────────────┘

 ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 │  APPLICANT  │────▶│  ADMITTED   │────▶│  ENROLLED   │────▶│   ACTIVE    │
 │             │     │ (or waitlisted│    │             │     │  (in-term)  │
 │ application │     │  or denied) │     │  validated  │     │             │
 │ submitted   │     │             │     │  assessed   │     │ attendance  │
 │             │     │ conditional │     │  paid       │     │ add/drop    │
 └─────────────┘     │  admission  │     └─────────────┘     │ midterm     │
        │            └─────────────┘            │            └─────────────┘
        │                   │                   │                   │
        │ denied            │ admitted          │ dropped           │ term ends
        ▼                   │                   ▼                   ▼
 ┌─────────────┐            │            ┌─────────────┐     ┌─────────────┐
 │   DENIED    │            │            │   DROPPED   │     │   GRADING   │
 │             │            │            │             │     │             │
 │ (terminal)  │            │            │ (per term)  │     │ draft       │
 └─────────────┘            │            └─────────────┘     │ submitted   │
                            │                                │ approved    │
                            ▼                                │ locked      │
                     ┌─────────────┐                        └─────────────┘
                     │ re-enroll   │◀──────────────────────────────│
                     │ next term   │       (retention check,        │
                     └─────────────┘        financial clearance)    │
                                                                     │
                            ┌────────────────────────────────────────┘
                            │  (after all curriculum requirements met)
                            ▼
                     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                     │  CLEARANCE  │────▶│  GRADUATED  │────▶│   ALUMNI    │
                     │             │     │             │     │             │
                     │ library     │     │ TOR issued  │     │ tracer study│
                     │ finance     │     │ diploma     │     │ directory   │
                     │ registrar   │     │ eCAV export │     │ credentials │
                     └─────────────┘     └─────────────┘     └─────────────┘

 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
 Reversible paths:
   ENROLLED ─── leave of absence ──▶ LOA ──▶ re-enroll (back to ENROLLED)
   ACTIVE ─────── stop filing ──────▶ AWOL ──▶ dismissed or re-enroll
   ADMITTED ────── declined ─────────▶ DECLINED (applicant chose not to enroll)
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
```

---

## 2. Phase 1 — Pre-Enrollment (Admissions)

**Primary module:** `esmis_admissions`
**Primary model:** `esmis.applicant`

### Sub-phases

#### Application

The applicant submits personal information and supporting credentials online or at the admissions
office. The system creates an `esmis.applicant` record at this point.

Key data captured:

| Data | Notes |
|------|-------|
| Personal information | Name, date of birth, sex, civil status, address |
| K-12 credentials | Senior High School strand, school name, GWA, track |
| Learner Reference Number (LRN) | DepEd-issued, 12 digits; validated against DepEd format |
| Entrance exam scores | Per sub-test; stored as JSON components on `esmis.applicant` |
| Contact information | Email, mobile number — used for notifications throughout the process |
| Parent/guardian info | Required for minors; triggers minor-specific consent forms |

#### PhilSys Verification

Identity is validated using PhilSys before the application advances to evaluation. Two modes
are supported (see [Government Integrations](government-integrations.md)):

| Mode | When Used |
|------|-----------|
| PhilSys Check (QR scan) | Walk-in applicants at the admissions office |
| National ID eVerify | Online applicants; live selfie submitted to PSA API |

Verification outcome is stored on `esmis.applicant`:

```python
philsys_verified = fields.Boolean(string="PhilSys Verified", default=False)
philsys_verification_date = fields.Datetime(readonly=True)
philsys_verification_mode = fields.Selection(
    [("qr", "QR Scan"), ("everify", "eVerify")],
    readonly=True,
)
# PSN is the persistent person identifier — not the card number.
# Store only with explicit consent; classify as Restricted PII.
philsys_psn = fields.Char(string="PhilSys Number (PSN)", groups="esmis_security.group_esmis_registrar_manager")
```

#### Evaluation

Admissions officers score the application against the institution's criteria:

- Entrance exam score (component-weighted)
- Academic credentials (K-12 GWA, strand alignment)
- Interview result (if required by the program)
- Credential review (authenticated documents)

The aggregate score determines ranking for admission slot allocation.

#### Decision

The admissions committee records a decision on the applicant record. The approval chain
follows the standard `esmis.approval.mixin` pattern (see [Approval Workflows](approval-workflows.md)).

| Decision | `esmis.applicant` state | Next step |
|----------|------------------------|-----------|
| `admitted` | `admitted` | Applicant proceeds to enrollment |
| `waitlisted` | `waitlisted` | Notified when a slot opens |
| `denied` | `denied` | Terminal; appeal window documented |
| `conditional` | `conditional` | Conditions recorded; re-evaluated when met |

**Conditional admission** is common for applicants awaiting final K-12 grades or missing
authenticated documents. The system stores the conditions and a resolution deadline on the
applicant record. Enrollment is blocked until all conditions are cleared. A scheduled job
monitors unresolved conditions and sends reminders at configurable intervals before the deadline.

#### Consent Capture (RA 10173)

Consent is collected at application submission, before any personal data is processed:

| Applicant type | Consent form |
|----------------|-------------|
| 18 years old and above | Standard RA 10173 consent form; signed by applicant |
| Below 18 (minor) | Parent/guardian countersign required; both signatures captured |

Consent records are stored on `esmis.applicant` and carry forward to `esmis.student` on
admission. Consent must be re-obtained if the purpose or data category changes (e.g., when
data is shared with a government agency for a new scholarship program).

```python
# Consent fields on esmis.applicant and esmis.student
consent_given = fields.Boolean(string="Privacy Consent Given", default=False)
consent_date = fields.Datetime(readonly=True)
consent_given_by = fields.Char(
    string="Consent Given By",
    help="Name of signatory. For minors, this is the parent/guardian name.",
)
is_consent_for_minor = fields.Boolean(
    string="Minor Consent",
    help="True when the consent was signed by a parent or guardian on behalf of a minor.",
)
```

---

## 3. Phase 2 — Enrollment

**Primary module:** `esmis_enrollment`
**Primary models:** `esmis.enrollment`, `esmis.enrollment.line`

### Student Record Creation

On admission, an `esmis.student` record is created from `esmis.applicant`. The applicant
record is not deleted — it is linked to the student and preserved for audit and CHED reporting.

```python
# On esmis.applicant
def action_create_student(self):
    """Convert admitted applicant to active student."""
    self.ensure_one()
    if self.state != "admitted":
        raise UserError(_("Only admitted applicants can be converted to students."))
    student = self.env["esmis.student"].create(self._prepare_student_vals())
    self.write({"student_id": student.id, "state": "enrolled"})
    return student
```

### Curriculum Binding

Each enrolled student is bound to a specific curriculum version — the exact set of required
and elective courses that must be completed for graduation. Curriculum binding happens at
first enrollment and is recorded on `esmis.student`:

```python
curriculum_id = fields.Many2one(
    "esmis.curriculum",
    string="Curriculum",
    required=True,
    help="The curriculum version the student is evaluated against for graduation.",
)
```

A student who shifts programs or takes a leave of absence longer than one year may have their
curriculum binding updated by the registrar, with the change logged in the audit trail.

### Course and Section Selection

The student (or a registrar on their behalf) builds a course cart. Each item in the cart
becomes an `esmis.enrollment.line`.

Validations run at the cart stage:

| Check | Action on failure |
|-------|------------------|
| Prerequisite courses passed | Block the line; display failed prerequisite |
| Schedule conflicts (overlapping timeslots) | Block the conflicting line |
| Section capacity | Block if section is full; offer waitlist option |
| Registration hold (academic, financial, disciplinary) | Block all additions; display hold reason |
| Maximum unit load | Warn if over regular load; block if over institutional maximum |
| Co-requisite requirements | Warn if co-requisite not also in cart |

### Financial Assessment

Once the cart is validated and submitted, the financial assessment runs:

1. Base tuition computed from credit units × rate per unit (from `esmis.fee.schedule` for the
   student's campus and classification)
2. Miscellaneous fees added per applicable fee codes
3. Financial aid discounts applied (see below)
4. Net amount due computed

Assessment results are stored on `esmis.enrollment`. The assessment is locked once payment
begins. Changes after locking (add/drop) trigger a reassessment workflow.

### Financial Aid Eligibility

Eligibility checks run automatically after assessment. Each aid program has an eligibility
rule evaluated against the student's profile:

| Program | Basis |
|---------|-------|
| Free Higher Education (RA 10931) | Citizenship, admission to public HEI, income threshold |
| PWD discount | Confirmed PWD classification on student record |
| Solo Parent discount | Solo parent ID on file, as defined by RA 8972 / RA 11861 |
| UniFAST / TES voucher | Application approved by CHED; voucher code linked to enrollment |
| Institutional scholarship | Satisfies program-specific GWA and unit load requirements |
| External scholarship (DOST-SEI, etc.) | Manually awarded by financial aid office; approval required |

Multiple aid types can be stacked where regulations permit. The system enforces stacking rules
per aid program configuration.

### Payment Processing

Payment is collected through one of the supported channels (see
[Government Integrations](government-integrations.md)): over-the-counter cashier, PayMongo
card, Maya e-wallet, or Dragonpay online banking. Payment confirmations are received via webhook
and matched to the enrollment's outstanding balance.

### Enrollment State Machine

```
 [cart] ──submit──▶ [validated] ──assess──▶ [assessed] ──payment confirmed──▶ [paid] ──▶ [enrolled]
    ▲                    │                       │
    │                    │ failed validation      │ hold placed
    └────────────────────┘                       │
                                                 ▼
                                             [on hold]
```

| State | Meaning |
|-------|---------|
| `cart` | Student is selecting courses; not yet submitted |
| `validated` | Section/prerequisite checks passed; pending assessment |
| `assessed` | Financial assessment computed; awaiting payment |
| `paid` | Full payment confirmed (or granted zero balance by financial aid) |
| `enrolled` | Official enrollment; COE can be issued |
| `on_hold` | Payment or academic hold applied after assessment |

---

## 4. Phase 3 — Active Academic Term

**Primary module:** `esmis_enrollment`, `esmis_attendance` (if enabled)

### Class Attendance

If the institution integrates an LMS or biometric attendance system, attendance records are
created per class session on `esmis.attendance.log`. Attendance data feeds into:

- Instructor grade sheets (as a component weight where configured)
- Early warning reports for at-risk students
- Automatic dropping at the absence threshold defined by institutional policy

### Add/Drop Period

During the add/drop window (dates defined on `esmis.academic.term`), students may:

- Add a new section (subject to cart validations above)
- Drop a section (subject to refund policy and minimum unit load)

Both operations create an `esmis.enrollment.change` record for audit. A dropped section
triggers financial reassessment; the refund amount depends on the timing within the refund
schedule.

### Midterm Grade Entry

Midterm grades are optional per institution. When enabled, faculty enter midterm marks on
`esmis.grade` (as a component with `is_midterm = True`). These are advisory — they do not
affect the official academic record but are visible to students and used in at-risk alerts.

### Data State at End of Phase

At the close of the add/drop period:

- `esmis.enrollment.line` records are finalized (no further additions or drops without
  a petition)
- Section enrolled counts are locked in for CHED reporting (census date)
- Student classification (regular/irregular) is computed from the finalized unit load

---

## 5. Phase 4 — Grading

**Primary module:** `esmis_grades`
**Primary models:** `esmis.grade`, `esmis.grade.component`

### Grade Entry

Faculty enter grades per section after the term's final examination period. The grade sheet
is pre-populated with all enrolled students from `esmis.enrollment.line` records for that
section.

### Component-Based Grading

Each section may use a grading template that defines weighted components:

```python
class EsmisGradeComponent(models.Model):
    _name = "esmis.grade.component"
    _description = "Grade Component"

    grade_id = fields.Many2one("esmis.grade", required=True, ondelete="cascade")
    component_type = fields.Selection([
        ("midterm", "Midterm Exam"),
        ("final", "Final Exam"),
        ("project", "Project / Output"),
        ("recitation", "Recitation / Quiz"),
        ("attendance", "Attendance"),
        ("other", "Other"),
    ], required=True)
    weight = fields.Float(string="Weight (%)", required=True)
    raw_score = fields.Float(string="Raw Score")
    weighted_score = fields.Float(
        string="Weighted Score",
        compute="_compute_weighted_score",
        store=True,
    )
```

The final grade is the sum of weighted component scores, converted to the institution's grading
scale (numerical or letter, configured on `esmis.grading.scale`).

### INC Grade Handling

An `INC` (Incomplete) grade is given when a student fails to complete a requirement due to an
excused reason. The INC resolution flow:

1. Faculty assigns `INC` with a resolution deadline (institutional policy defines maximum
   duration — typically one academic year).
2. System creates a monitoring task (`mail.activity`) on the grade record.
3. Student completes the missing requirement; faculty submits the replacement grade.
4. Registrar approves the INC resolution.
5. If the deadline passes without resolution, the INC automatically converts to the failing
   grade defined in policy (e.g., `5.0` or `F`), subject to dean approval.

### Grade Change Request Workflow

After grades are submitted, changes require an approval chain:

```
Faculty submits change request
        │
        ▼
    Dean reviews
        │
        ├──▶ Dean approves ──▶ Registrar approves ──▶ Grade updated + audit log entry
        │
        └──▶ Dean rejects ──▶ Faculty notified (reason recorded)
```

The old and new values, the reason, and every approver with timestamp are stored in the audit
log. The grade record itself is immutable once locked — a grade change creates a superseding
record that references the original.

### GWA Recomputation

After grades are locked, the student's GWA is recomputed:

```python
def _compute_gwa(self):
    """Recompute cumulative GWA from all locked grade records."""
    for student in self:
        grades = self.env["esmis.grade"].search([
            ("student_id", "=", student.id),
            ("state", "=", "locked"),
            ("is_included_in_gwa", "=", True),
        ])
        total_weighted = sum(g.final_grade * g.units for g in grades)
        total_units = sum(g.units for g in grades)
        student.gwa = total_weighted / total_units if total_units else 0.0
```

### Academic Standing Update

After GWA recomputation, the student's academic standing is updated:

| Standing | Trigger |
|----------|---------|
| `good` | GWA meets the retention threshold and no failing grades in required subjects |
| `warning` | GWA within the warning band (configurable per program) |
| `probation` | GWA below retention threshold for the first time |
| `dismissed` | GWA below threshold on probation OR specific dismissal conditions met |

The retention policy is defined on `esmis.retention.policy` per program and is evaluated by
a scheduled job at term close (Phase 5).

### Grade State Machine

```
 [draft] ──faculty submits──▶ [submitted] ──dean approves──▶ [approved] ──registrar locks──▶ [locked]
    ▲                               │
    └── returned for revision ──────┘
```

| State | Who Can Edit |
|-------|-------------|
| `draft` | Faculty |
| `submitted` | No one (under review) |
| `approved` | No one (registrar processing) |
| `locked` | No one (grade change request required) |

---

## 6. Phase 5 — Term Transition

**Primary module:** `esmis_enrollment`

Term transition runs after all grade sheets are locked. It is partially automated via
scheduled jobs and partially manual (for exception handling).

### Term Close Sequence

1. **Grades locked** — Registrar confirms all grade sheets are in `locked` state. Any
   outstanding `draft` or `submitted` sheets are escalated.
2. **GWA and standing finalized** — Standing update job runs for all students with grades in
   the closed term.
3. **Retention policy check** — Students on probation or newly below threshold are evaluated.
   Dismissed students are notified; their enrollment for the next term is blocked pending
   appeal resolution.
4. **Financial clearance check** — Outstanding balances are flagged. Students with unpaid
   balances may be blocked from next-term enrollment (configurable per institutional policy).
5. **Next-term enrollment opens** — `esmis.academic.term` for the next term is set to
   `enrollment_open`. Students with no holds and satisfactory standing can begin enrollment.
6. **Scholarship renewal evaluation** — Scholarship records with `renewable = True` are
   evaluated against renewal criteria (GWA threshold, unit load completed). Renewals are
   confirmed or lapsed automatically, with manual override available to the financial aid
   office.

---

## 7. Phase 6 — Graduation

**Primary module:** `esmis_graduation`
**Primary models:** `esmis.graduation`, `esmis.clearance`

### Curriculum Checklist Verification

The registrar runs a curriculum completion check for candidates. The system compares:

- All locked grade records for the student against the courses required by their bound
  curriculum version (`curriculum_id` on `esmis.student`)
- Elective units completed vs. required elective units
- Residency requirements (minimum units taken at the institution)
- GWA meets the minimum for graduation (and Latin honors threshold, if applicable)

Deficiencies are listed per course so the registrar can advise on remaining requirements.

### Latin Honors Computation

Latin honors are computed from the cumulative GWA at graduation:

| Honors | GWA range (numerical, 1.0 = highest) |
|--------|--------------------------------------|
| Summa Cum Laude | 1.00 – 1.20 |
| Magna Cum Laude | 1.21 – 1.45 |
| Cum Laude | 1.46 – 1.75 |

> **Note:** GWA thresholds are institution-specific and configurable on `esmis.graduation.policy`.
> The values above are illustrative. Some institutions also apply unit residency and no failing
> grade conditions for honors eligibility.

### Clearance Processing

A student must secure clearance from all offices before graduation is finalized. An
`esmis.clearance` record is created per student with clearance lines for each office:

| Office | Typical requirement |
|--------|---------------------|
| Library | All borrowed materials returned; no fines |
| Finance / Cashier | Zero outstanding balance |
| Registrar | All required documents submitted; INC grades resolved |
| Department / College | Lab equipment returned; thesis requirements met |
| Student Affairs | No unresolved disciplinary cases |

Each clearance line is approved by an officer from the responsible office. The graduation
record does not advance until all lines are cleared.

### CHED SOAIS (Special Order) Processing

For public HEIs, the graduation must be reported to CHED and a Special Order number issued
before diplomas are awarded. The SOAIS submission:

1. Registrar generates the SOAIS batch file from graduation candidates.
2. File is submitted to CHED through the HEMIS portal.
3. CHED issues a Special Order number per graduate.
4. SO numbers are recorded on the graduation record.

> **Implementation note:** CHED does not currently expose a public API for SOAIS. Generate
> the prescribed Excel file format for manual portal upload (see
> [Government Integrations](government-integrations.md)).

### TOR Generation

The Transcript of Records is generated as a PDF from a QWeb report template:

- All locked grade records, ordered by term
- GWA per term and cumulative
- Curriculum completion status
- Latin honors notation
- Graduation date and degree awarded
- Digital signature of the University Registrar (via `esmis.digital.signature`)
- QR code linking to the eSMIS public verification endpoint

TOR authenticity verification follows the eCAV (Electronic Copy Authenticated Voucher)
standard. The QR code encodes a signed token; external parties scan it to confirm the TOR
is genuine without contacting the institution directly.

### Diploma Generation

The diploma is generated as a separate document (QWeb PDF or external template) and records:

- Full legal name as it appears in the PhilSys-verified record
- Degree and program name as CHED-recognized
- Date of graduation
- Latin honors (if applicable)
- Special Order number
- Signatures of the President and University Registrar

### eCAV Credential Export

CHED's eCAV system allows institutions to submit graduate credential data for cross-institution
and employer verification. The export file is generated from the graduation records of the
applicable batch and uploaded to the CHED eCAV portal.

### Student Status Transition

```
active ──clearance complete──▶ for_graduation ──SO issued──▶ graduated
```

The `graduated` state is terminal on the student record. An archived flag is set; the record
remains fully searchable by the registrar.

---

## 8. Phase 7 — Post-Graduation (Alumni)

**Primary module:** `esmis_alumni`

### Alumni Status Transition

Transition from `graduated` to `alumni` is automatic. A scheduled job runs nightly and
converts any `graduated` student record where the graduation date is in the past and the
diploma has been released:

```python
def _cron_transition_to_alumni(self):
    students = self.env["esmis.student"].search([
        ("state", "=", "graduated"),
        ("diploma_released_date", "<=", fields.Date.today()),
    ])
    students.write({"state": "alumni"})
```

### Graduate Tracer Study

CHED requires HEIs to conduct a graduate tracer study to track employment outcomes. The system
sends a tracer survey invitation to alumni at configurable intervals after graduation (e.g.,
6 months, 2 years). Responses are stored on `esmis.tracer.response` and aggregated for the
CHED HEMIS graduate tracer report.

Alumni may opt out of tracer surveys; the opt-out is recorded and respected for all future
invitations.

### Alumni Directory

An alumni directory is available for registered alumni. Privacy controls govern what is visible:

| Field | Default visibility |
|-------|--------------------|
| Name | Visible to all authenticated alumni |
| Degree and graduation year | Visible to all authenticated alumni |
| Contact information | Hidden by default; alumni opt-in to share |
| Employer and position | Optional; alumni-controlled |
| Home address | Never shown in directory |

### Credential Verification Services

Alumni and third parties (employers, foreign institutions) can verify credentials through the
public verification endpoint. The verification service:

- Accepts the TOR QR code token or a manual reference number
- Returns the degree awarded, graduation date, and honors — no transcript details
- Logs every verification request (who, when, what) for audit

Institutions may enable paid verification for additional certified copy services.

### Document Request Workflow

Alumni may request additional certified copies of their TOR, diploma, or other credentials
through the alumni portal:

1. Alumni submits a request through the portal with document type and purpose.
2. Request is routed to the registrar office queue.
3. Registrar processes the request; payment collected if applicable.
4. Document generated and released (digital or physical).

All document releases are logged: document type, generated by, generated for, timestamp.

---

## 9. Cross-Cutting Concerns

These concerns apply at every phase of the lifecycle without exception.

### Consent Management

Every phase has at least one consent checkpoint. Consent must be:

- Freely given (not bundled with enrollment acceptance)
- Specific to purpose (a separate consent per processing purpose)
- Informed (plain-language summary of what is collected and why)
- Documented (timestamp, signatory, version of the consent form)

When a new processing purpose arises (e.g., data sharing with a new government agency),
a new consent must be obtained before data is shared. The system must not share data with
a new recipient without a matching consent record.

### Audit Trail

All changes to student data are logged with: who made the change, when, what was changed,
the old value, and the new value. Critical events require an additional reason field:

| Event | Reason required |
|-------|----------------|
| Grade change | Yes |
| Enrollment status change | Yes |
| Clearance override | Yes |
| Financial aid modification | Yes |
| Academic standing override | Yes |
| Any change to Restricted PII fields | Yes |

See [Audit & Compliance](audit-compliance.md) for the full list of required audit points.

### Data Classification

PII fields are classified into three tiers:

| Tier | Examples | Controls |
|------|----------|----------|
| Public | Name, degree, graduation year | No special access control |
| Confidential | Grades, enrollment status, contact info | Campus staff only; logged on access |
| Restricted | National ID / PSN, health records, counseling notes, financial standing details | Named role access only; every read logged |

Restricted fields are encrypted at rest (ADR-012). Access to Restricted fields is logged
even for read operations — not just writes.

### Multi-Campus Scoping

Every campus-specific record carries `company_id`. The student's core `res.partner` record
is not campus-scoped (a student transferring campuses does not get a new person record).
Campus-specific profiles (`esmis.student`) are campus-scoped and linked to the shared partner.

Refer to [Multi-Campus Architecture](multi-campus-architecture.md) for record rules and
cross-campus query patterns.

### Government Reporting

The following lifecycle events trigger data extraction for CHED HEMIS or other government
systems:

| Phase | Reporting event | System |
|-------|----------------|--------|
| Enrollment | Census date headcount | CHED HEMIS |
| Enrollment | Financial aid recipients count | UniFAST / CHED |
| Graduation | Graduate batch submission | CHED SOAIS, eCAV |
| Alumni | Graduate tracer results | CHED HEMIS |
| Annual | Faculty-to-student ratio, research outputs | CHED HEMIS |

Government reports are generated as prescribed file formats for manual portal upload. No
live API push to CHED systems is currently supported. See
[Government Integrations](government-integrations.md) for file format specifications.

---

## 10. Data Model Summary

The table below maps each lifecycle phase to the models it creates or primarily modifies.

| Phase | Models Created | Models Modified |
|-------|---------------|-----------------|
| Admissions | `esmis.applicant` | — |
| PhilSys verification | `esmis.philsys.verification` | `esmis.applicant` |
| Admission decision | `esmis.admission.decision` | `esmis.applicant` |
| Student creation | `esmis.student` | `esmis.applicant` |
| Enrollment | `esmis.enrollment`, `esmis.enrollment.line` | `esmis.student` |
| Financial assessment | `esmis.financial.assessment` | `esmis.enrollment` |
| Financial aid | `esmis.financial.aid.award` | `esmis.financial.assessment` |
| Add/drop | `esmis.enrollment.change` | `esmis.enrollment.line`, `esmis.section` |
| Grade entry | `esmis.grade`, `esmis.grade.component` | — |
| Grade change | `esmis.grade.change.request` | `esmis.grade` |
| Graduation clearance | `esmis.clearance`, `esmis.clearance.line` | — |
| Graduation | `esmis.graduation` | `esmis.student` |
| TOR | `esmis.document` (type=tor) | `esmis.graduation` |
| Diploma | `esmis.document` (type=diploma) | `esmis.graduation` |
| Alumni | — | `esmis.student` (state → alumni) |
| Tracer study | `esmis.tracer.response` | — |
| Document request | `esmis.document.request` | — |

---

## Implementation Checklist

Use this checklist when building any new feature that touches student data:

- [ ] Identify which lifecycle phase the feature belongs to
- [ ] Confirm the correct primary model and its `company_id` scoping
- [ ] Add a consent checkpoint if new personal data is collected or a new purpose arises
- [ ] Ensure all state transitions are logged in the audit trail
- [ ] Classify any new PII fields and apply appropriate access group restrictions
- [ ] Add government reporting hooks if the feature affects CHED-reportable data
- [ ] Write tests covering the state machine transitions (not just the happy path)
- [ ] Verify that a campus officer cannot access another campus's records for this feature

---

**See also:** [Audit & Compliance](audit-compliance.md), [Regulatory Compliance](regulatory-compliance.md), [Approval Workflows](approval-workflows.md), [Multi-Campus Architecture](multi-campus-architecture.md), [Government Integrations](government-integrations.md)
