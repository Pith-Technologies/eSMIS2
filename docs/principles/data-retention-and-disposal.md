# Data Retention and Disposal

This document defines how long eSMIS retains each category of student data, what happens when
that period expires, and the procedures required for lawful disposal. It is the authoritative
reference for retention schedules, anonymization rules, legal holds, and conflict resolution
between competing regulatory requirements.

## Table of Contents

1. [Retention Schedule Matrix](#1-retention-schedule-matrix)
2. [Anonymization Rules](#2-anonymization-rules)
3. [Disposal Procedures](#3-disposal-procedures)
4. [Legal Hold](#4-legal-hold)
5. [Conflict Resolution](#5-conflict-resolution)

---

## 1. Retention Schedule Matrix

The table below governs all student data held by eSMIS. "Expiry" is measured from the event
in the "Retention" column. "Action at Expiry" is what the system does after the DPO review
step described in section 3.

| Data Type | Retention Period | Action at Expiry | Legal Basis |
|-----------|-----------------|-----------------|-------------|
| TOR / academic transcript | Permanent | Archive (never delete) | CHED MORPHE |
| Diploma records | Permanent | Archive (never delete) | CHED MORPHE |
| Enrollment forms | 5 years after graduation | Anonymize non-academic PII | CHED En Banc Resolution 170-2018 |
| Transfer credentials | 10 years | Archive | CHED MORPHE |
| Financial records (tuition) | 10 years | Anonymize | BIR, COA |
| Scholarship / financial aid records | 10 years | Anonymize | UniFAST, COA |
| Disciplinary records | Per institutional policy | Anonymize | Institutional policy |
| Counseling records | 5 years after last session | Delete | RA 10173 |
| Health / medical records | 5 years after graduation | Delete | RA 10173 |
| Consent records | Duration of consent + 3 years after withdrawal or expiry | Archive | RA 10173 |
| Audit logs | 7 years | Archive | NPC guidelines |
| Session / login logs | 1 year | Delete | Institutional policy |
| Application data (denied applicants) | 2 years from application decision | Delete | RA 10173 |

### Notes on "Archive" vs. "Delete" vs. "Anonymize"

- **Archive**: move to a read-only store with restricted access. The record still contains
  identifiable data but is no longer in the operational database. Required for records that
  may be needed to verify credentials long-term.
- **Anonymize**: strip identifying fields per the rules in section 2. The structural record
  remains for aggregate reporting but cannot be linked back to an individual.
- **Delete**: permanently remove from the database and backups within the backup rotation
  window. For public HEIs, National Archives approval is required first (see section 3).

---

## 2. Anonymization Rules

Anonymization is irreversible. Once applied, no process in eSMIS can recover the original
identifiers. Before running anonymization, the DPO must confirm that no legal hold applies
(see section 4).

### Fields to Replace

| Original Field | Replacement Value |
|----------------|------------------|
| `name` | `SHA256(name + institution_salt)[:8]` — first 8 hex characters of a salted hash |
| `email` | `anonymized_XXXX@invalid` where XXXX is a random 4-digit number |
| `phone` | Empty string |
| `mobile` | Empty string |
| `street`, `street2`, `city`, `zip` | Empty string |
| `emergency_contact_name` | Empty string |
| `emergency_contact_phone` | Empty string |
| `philsys_number` | Empty string |
| `birthdate` | Replaced with birth year only (e.g., `1998-01-01`) |

### Fields to Retain

The following fields are kept intact because they are needed for aggregate reporting, academic
verification, and regulatory audits:

- `student_number` — required for record linkage and transcript verification
- `program_id` — needed for CHED enrolment statistics
- `graduation_year` — needed for cohort analysis
- Aggregate grades (GWA, academic standing category) — not individually identifying
- Enrollment status history — needed for accreditation reporting

### Implementation Requirements

- Anonymization must run inside a database transaction. If any field update fails, the entire
  batch for that record rolls back.
- A disposal log entry (see section 3) must be written within the same transaction.
- Do not log original PII values anywhere during the anonymization process — not in `_logger`,
  not in job output, not in the disposal log.
- The `institution_salt` used in name hashing must be stored in the system parameter
  `esmis.anonymization_salt` and must never be exported or logged.

---

## 3. Disposal Procedures

Disposal is a three-step process: automated identification, DPO review, and execution.

### Step 1 — Automated Identification

An `ir.cron` job runs on the first working day of each month. It queries each data category
against its retention schedule and builds a candidate list: records whose retention period has
expired and that do not carry a `legal_hold` flag.

The job does not modify any records. It creates a draft `esmis.disposal.review` record
listing all candidates, grouped by data type, with counts and the proposed action.

### Step 2 — DPO Review

The DPO receives a notification and reviews the draft disposal record. The review must include:

- Confirming that no records in the candidate list are subject to an active legal hold that
  the system has not yet captured.
- For public HEIs: obtaining National Archives of the Philippines (NAP) approval before
  proceeding with deletion of any records that qualify as government records under RA 9470.
  This approval must be attached to the disposal review record before execution is allowed.
- Confirming the proposed action (anonymize vs. delete) is correct for each data type.

The DPO approves the disposal review record to unlock execution.

### Step 3 — Execution

Once approved, the system executes disposal in batches using `queue_job`. Each job handles
one data type. On completion:

- A disposal log record is written with: data type, record count, disposal method
  (anonymize/delete/archive), execution datetime, and `authorized_by` (the DPO's user ID).
- The disposal review record is marked complete.
- Affected records are updated or removed per the approved action.

The disposal log is itself subject to audit log retention (7 years) and must never be deleted.

### Public HEI Requirement (RA 9470)

Public higher education institutions are subject to the National Archives of the Philippines
Act. Before disposing of any record that constitutes a government record, the institution must
obtain written NAP approval. The `esmis.disposal.review` record must store the NAP approval
reference before the system will allow execution of a delete action.

Private HEIs are not subject to RA 9470 but must still document disposal per NPC requirements.

---

## 4. Legal Hold

A legal hold prevents automated disposal for records that are involved in ongoing legal cases,
regulatory investigations, or external audits.

### Setting a Legal Hold

Only the DPO or a user with the `esmis_security.group_dpo` security group may set or remove
a legal hold. The `legal_hold` boolean field exists on all models subject to the retention
schedule.

When `legal_hold = True`:

- The monthly cron job excludes the record from all candidate lists.
- No anonymization or deletion may be executed for that record, even via manual action.
- The hold reason and the user who set it are recorded in `legal_hold_reason` and
  `legal_hold_set_by`.

### Removing a Legal Hold

When the legal matter is resolved, the DPO sets `legal_hold = False` and documents the
resolution in `legal_hold_reason`. The record then becomes eligible for the next monthly
disposal review cycle.

### Notification

When a legal hold is set, the system notifies the records officer and the DPO. When a legal
hold is removed, the same parties are notified so that the disposal cycle can proceed.

---

## 5. Conflict Resolution

Two regulatory frameworks create genuine tension in this domain: CHED permanent record
requirements and the RA 10173 data minimization principle. The rules below resolve each
conflict.

### Academic Records vs. Data Minimization

**CHED wins for academic records.**

CHED MORPHE and CMO requirements mandate permanent retention of TORs, diplomas, and transfer
credentials. RA 10173 Section 13(b) explicitly exempts processing required by existing law.
These records must be archived permanently and may not be anonymized or deleted.

However, "academic record" is narrowly defined. The grade and program data in the TOR are
permanent; the contact details and emergency contacts attached to the same enrollment
record are not. Non-academic PII on enrollment forms is anonymized 5 years after graduation
even though the academic portion is archived permanently.

### Financial Records vs. Data Minimization

**BIR and COA win for financial records.**

Tuition and scholarship financial records must be retained for 10 years per BIR regulations
and Commission on Audit rules. At the 10-year mark, the financial amounts and program codes
are retained for audit purposes, but direct identifiers (name, address, contact details) are
anonymized.

### Counseling and Health Records

**RA 10173 wins.**

CHED has no retention mandate for counseling or health records. These contain sensitive
personal information (SPI) and must be deleted — not archived or anonymized — at the end of
their retention period. Deletion must be complete including removal from backup rotation
within the backup window.

### Summary Decision Table

| Data Category | Governing Rule | Resolution |
|---|---|---|
| TOR, diploma, transfer credentials | CHED MORPHE (existing law) | Permanent archive — RA 10173 Section 13(b) applies |
| Non-academic PII on enrollment forms | RA 10173 | Anonymize 5 years after graduation |
| Financial records | BIR / COA | Retain 10 years, then anonymize identifiers |
| Counseling and health records | RA 10173 | Delete at schedule; no CHED mandate applies |
| Consent records | RA 10173 | Archive for duration + 3 years |

---

## Related Documents

- [Consent Management](consent-management.md) — retention rules for consent records specifically
- [Regulatory Compliance](regulatory-compliance.md) — full list of applicable Philippine regulations
- [Audit and Compliance](audit-compliance.md) — audit trail requirements for disposal events
- [Error Handling and Logging](error-handling.md) — no PII in logs, including disposal logs
- [Performance and Scalability](performance-scalability.md) — batch disposal via `queue_job`
