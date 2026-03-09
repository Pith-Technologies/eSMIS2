# Consent Management

This document defines how eSMIS captures, enforces, and manages consent under the Philippine
Data Privacy Act (RA 10173) and NPC implementing rules. It is the authoritative reference for
all consent-related implementation decisions.

## Table of Contents

1. [Consent Model](#1-consent-model)
2. [Processing Purposes](#2-processing-purposes)
3. [When Consent Is Required vs. Not Required](#3-when-consent-is-required-vs-not-required)
4. [Minor Consent](#4-minor-consent)
5. [Consent Withdrawal](#5-consent-withdrawal)
6. [Consent Enforcement in Code](#6-consent-enforcement-in-code)
7. [Testing Consent](#7-testing-consent)

---

## 1. Consent Model

The `esmis.consent` model is the single source of truth for all consent records in the system.
One record exists per student per purpose. Records are never deleted — only marked as withdrawn.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | The student whose data is being processed |
| `purpose` | Selection | Processing purpose code (see section 2) |
| `lawful_basis` | Selection | Legal basis for processing (see values below) |
| `date_given` | Datetime | When consent or acknowledgment was recorded |
| `date_withdrawn` | Datetime | Set when consent is withdrawn; `False` if still active |
| `evidence_type` | Selection | How evidence was captured: `electronic`, `written`, `verbal` |
| `evidence_ref` | Many2one (`ir.attachment`) | Supporting document or attachment, if any |
| `captured_by` | Many2one (`res.users`) | Staff member or system that recorded the consent |
| `ip_address` | Char | IP address at time of electronic consent capture |
| `form_version` | Char | Version identifier of the consent form shown to the student |
| `is_active` | Boolean (computed) | `True` when `date_withdrawn` is not set |
| `parent_consent` | Boolean | `True` when this record represents parent/guardian consent for a minor |

### Lawful Basis Values

| Value | Label |
|-------|-------|
| `consent` | Consent |
| `contract` | Contract |
| `legal_obligation` | Legal Obligation |
| `vital_interest` | Vital Interest |
| `legitimate_interest` | Legitimate Interest |

### Key Constraints

- The combination of `student_id` and `purpose` must be unique among active records
  (`date_withdrawn` is `False`).
- `evidence_type` is required when `lawful_basis` is `consent`.
- `parent_consent` may only be `True` when the student is a minor at `date_given`.

---

## 2. Processing Purposes

Purposes are defined as vocabulary codes. Each maps to a default lawful basis, though the
actual basis recorded on the consent record governs.

| Purpose Code | Description | Default Lawful Basis |
|---|---|---|
| `consent_enrollment` | Enrollment data processing | `contract` |
| `consent_ched_reporting` | CHED HEMIS/eCAV data submission | `legal_obligation` |
| `consent_financial_aid` | Scholarship/subsidy eligibility evaluation, including government cross-referencing | `consent` |
| `consent_emergency_contact` | Sharing data with emergency services | `vital_interest` |
| `consent_alumni_tracking` | Post-graduation contact and surveys | `consent` |
| `consent_research` | Use of anonymized data for institutional research | `legitimate_interest` |
| `consent_lms_sync` | Sharing roster and grade data with the LMS | `contract` |
| `consent_payment` | Sharing data with payment processors | `contract` |
| `consent_philsys` | Identity verification via PhilSys | `consent` |

These codes are stored as vocabulary entries and must not be renamed or deleted once data
exists against them. Adding new codes requires a corresponding ADR.

---

## 3. When Consent Is Required vs. Not Required

Determining whether explicit consent must be collected before processing is the most important
decision in this domain. Misclassification either creates unnecessary friction for students or
exposes the institution to NPC penalties.

### Consent IS Required

The following purposes require an active `esmis.consent` record with `lawful_basis = 'consent'`
before any processing occurs:

- **PhilSys verification** (`consent_philsys`) — voluntary identity verification; student must
  affirmatively agree before the institution queries the PhilSys API.
- **Alumni tracking** (`consent_alumni_tracking`) — post-graduation contact is not part of the
  enrollment contract; requires standalone consent that can be withdrawn at any time.
- **Research analytics** (`consent_research`) — even when data is anonymized, institutional
  research use requires consent or a legitimate interest assessment on file.
- **Financial aid cross-referencing** (`consent_financial_aid`) — when eligibility evaluation
  involves sharing data with a third-party government agency (e.g., DSWD, GSIS), consent is
  required because the disclosure extends beyond the enrollment contract.

### Consent Is NOT Required

The following purposes are covered by another lawful basis and must NOT gate processing on a
consent record:

| Purpose | Lawful Basis | Rationale |
|---------|-------------|-----------|
| CHED HEMIS / eCAV reporting (`consent_ched_reporting`) | `legal_obligation` | CHED MORPHE and CMO mandate submission; RA 10173 Section 13(b) exempts processing required by law |
| Free tuition eligibility (UniFAST) | `legal_obligation` | RA 10931 requires institutions to verify and report eligibility |
| Tax reporting (BIR) | `legal_obligation` | NIRC and BIR regulations require disclosure |
| Enrollment processing (`consent_enrollment`) | `contract` | Processing is necessary to fulfill the enrollment contract the student entered into |
| Grade recording and transcript generation | `contract` | Same contract basis as enrollment |
| LMS sync (`consent_lms_sync`) | `contract` | LMS access is a service the student contracted for |
| Payment processing (`consent_payment`) | `contract` | Payment is part of the enrollment contract |
| Emergency medical situations (`consent_emergency_contact`) | `vital_interest` | Protecting life takes priority; consent cannot be required when the student is incapacitated |

Attempting to obtain "consent" for a legal obligation purpose is a compliance risk: it implies
the student can refuse, which is false, and may invalidate the lawful basis claim.

---

## 4. Minor Consent

Students under 18 at the time of enrollment are minors under Philippine law. The DPA IRR and
NPC Advisory 2024-03 require additional safeguards.

### At Enrollment

The system checks the student's birthdate at enrollment creation. If the student is under 18:

1. A `parent_consent` record must exist for any purpose requiring consent before processing
   may begin.
2. The parent or guardian is linked via the student's `res.partner` relationship
   (`guardian_id` on `esmis.student`).
3. The enrollment officer is prompted to record the guardian's consent, including
   `evidence_type` and `evidence_ref`.

### When the Student Turns 18

- The system generates a task for the records office to collect direct consent from the student
  for all purposes previously covered by parent consent.
- Parent consent records remain valid and `is_active = True` until a student consent record
  for the same purpose is created.
- There is no automatic expiry of parent consent; the student must take an affirmative action.

### Age-Appropriate Privacy Notices

Per NPC Advisory 2024-03, privacy notices shown to students in the 13–17 age band must use
plain, age-appropriate language. The `form_version` field on the consent record must reference
the specific notice version shown (e.g., `enrollment_v3_minor_en`), so that the institution
can demonstrate compliance if challenged.

---

## 5. Consent Withdrawal

### What Can Be Withdrawn

Students may withdraw consent only for purposes whose lawful basis is `consent`. The following
purposes are withdrawable:

- `consent_alumni_tracking`
- `consent_research`
- `consent_philsys`
- `consent_financial_aid` (when the basis is consent, not contract)

Purposes based on `legal_obligation` or `contract` cannot be withdrawn. If a student attempts
to withdraw from CHED reporting, the system must explain that this is a legal obligation and
no action can be taken.

### Double-Notice Rule (NPC Circular 2023-04)

Before finalizing any consent withdrawal, the system must display a notice informing the
student of the consequences. For example:

> Withdrawing consent for alumni tracking means you will no longer receive information about
> career services, alumni events, or transcript attestation requests. This cannot be reversed
> without re-consenting.

The student must confirm after reading the notice. The confirmation event is logged.

### Withdrawal Mechanics

1. `date_withdrawn` is set to the current datetime on the consent record.
2. `is_active` becomes `False` (computed from `date_withdrawn`).
3. The consent record is retained permanently — it is never deleted.
4. Any active processing jobs for the withdrawn purpose must stop within 30 working days
   (RA 10173 Section 16(c)).
5. Queue jobs that check consent must re-verify `is_active` at execution time, not just at
   job creation time, to respect withdrawals that occur while a job is queued.

---

## 6. Consent Enforcement in Code

### The Mixin

All models that process PII for consent-required purposes must inherit `esmis.consent.mixin`.
The mixin provides a single helper method:

```python
def _has_active_consent(self, purpose: str) -> bool:
    """Return True if the student has an active consent record for the given purpose."""
```

The method returns `False` if no consent record exists, if the record has `date_withdrawn`
set, or if the student is a minor and only a parent consent record exists for a purpose that
requires direct student consent after the student has turned 18.

### Enforcement Pattern

Check consent at the boundary of every operation that processes PII for a consent-required
purpose. Raise `UserError` so the caller can surface the message to the user; do not silently
skip processing.

```python
def _process_alumni_survey(self, student):
    if not student._has_active_consent('consent_alumni_tracking'):
        raise UserError(_("Student has not consented to alumni tracking."))
    # proceed with processing
```

For batch jobs using `queue_job`, check consent inside the job body, not at job creation time:

```python
def _run_alumni_survey_batch(self):
    for student in self.env['esmis.student'].search([]):
        if not student._has_active_consent('consent_alumni_tracking'):
            continue
        self._process_alumni_survey(student)
```

### What Not to Do

- Do not bypass consent checks with `sudo()`. The consent requirement is a legal obligation,
  not a permissions issue.
- Do not cache consent status across request boundaries. Consent can be withdrawn between
  calls.
- Do not assume consent because a student completed enrollment. Enrollment consent covers only
  `consent_enrollment`; each purpose requires its own record.

---

## 7. Testing Consent

Every feature that touches PII for a consent-required purpose must include tests in all three
categories below.

### Unit Tests

- Consent check fails (raises `UserError`) when no consent record exists for the student.
- Consent check fails when the consent record has `date_withdrawn` set.
- Consent check passes when an active consent record exists.
- `is_active` computed field returns `False` when `date_withdrawn` is set and `True` otherwise.

### Integration Tests

- Processing succeeds without any consent record for legal obligation purposes
  (`consent_ched_reporting`, etc.) — confirm that the check is absent, not just passing.
- Minor consent flow: enrollment of an under-18 student requires a `parent_consent = True`
  record; enrollment fails without it.
- After student turns 18, the system generates the re-consent task.
- Consent withdrawal sets `date_withdrawn`, marks `is_active = False`, and retains the record.

### End-to-End Tests

- Student completes the PhilSys consent UI flow; a consent record is created with correct
  `evidence_type`, `form_version`, and `captured_by`.
- Student withdraws alumni tracking consent; double-notice dialog appears; on confirmation,
  processing stops within the required window.
- Batch alumni survey job skips students who have withdrawn consent and processes those who
  have not.

---

## Related Documents

- [Regulatory Compliance](regulatory-compliance.md) — RA 10173 obligations overview
- [Data Retention and Disposal](data-retention-and-disposal.md) — how long consent records are kept
- [Audit and Compliance](audit-compliance.md) — audit trail requirements for consent events
- [Student Data Lifecycle](student-data-lifecycle.md) — where consent fits in the enrollment pipeline
- [PhilSys Integration Guide](../guides/philsys-integration-guide.md) — consent steps for PhilSys verification
