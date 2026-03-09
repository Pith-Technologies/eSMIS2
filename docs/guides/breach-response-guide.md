# Data Breach Response Guide

This guide describes the step-by-step procedure for responding to a personal data breach
affecting eSMIS data. It is written for the Data Protection Officer (DPO), records officers,
and system administrators who may be involved at different stages.

All timelines below are measured from the moment the institution has sufficient certainty to
confirm that a breach has occurred — this is "time of discovery," not time of initial suspicion.

---

## Quick Reference Timeline

| Action | Deadline |
|--------|----------|
| Contain compromised accounts / keys / IPs | Within 1 hour of detection |
| Complete initial scope assessment | Within 24 hours of discovery |
| File NPC notification (PDBNF) | Within 72 hours of discovery |
| Notify affected data subjects | As soon as reasonably practicable after NPC notification |
| Complete remediation | Per remediation plan (document target date) |
| Submit post-incident report to management | Within 30 days of closure |

---

## Step 1 — Detection

A breach may be identified through any of the following channels. All staff must know to
escalate immediately to the DPO.

- Unusual access patterns detected by the audit log monitoring job (bulk exports, off-hours
  access, access from unexpected IP ranges)
- Bulk data export or download events flagged by the system
- Unauthorized API calls or API key usage outside expected patterns
- Report from a staff member who observes suspicious behavior
- External notification (NPC, partner institution, law enforcement, or a data subject
  reporting that their data has appeared elsewhere)
- Automated security alert from infrastructure monitoring

When any of these occur, the staff member who detects the event must immediately notify the
DPO and the system administrator. Do not attempt to investigate unilaterally — coordinated
response prevents evidence destruction.

---

## Step 2 — Containment

Containment must begin within one hour of detection, before the full scope is known. Speed
matters more than completeness at this stage.

Actions to take in parallel:

1. **Disable compromised user accounts.** If a specific account is suspected, deactivate it
   in Odoo immediately. Do not reset the password first — deactivation preserves the audit
   trail.
2. **Revoke compromised API keys.** Rotate any API keys or tokens that may have been exposed.
   Issue replacement keys only to confirmed-safe integrations after the scope assessment.
3. **Block suspicious IP addresses** at the network or application firewall level. Retain the
   block list and the timestamps for the breach record.
4. **Preserve audit logs.** Set a legal hold on all audit log records from the suspected
   breach window. This prevents the monthly cron job from rotating them.
5. **Do not notify data subjects yet.** Premature notification before scope is known causes
   unnecessary alarm and may interfere with the investigation.

Document every containment action with a timestamp and the name of the person who took it.
This log becomes part of the formal breach record.

---

## Step 3 — Scope Assessment

The goal of scope assessment is to answer four questions:

1. Which records were accessed or exfiltrated?
2. Which students (data subjects) are affected?
3. Which data types (PII tiers) were exposed?
4. How did the breach occur?

### Querying Audit Logs

Use the `esmis.audit.log` model to query access events in the suspected breach window:

```python
# Example: find all read events on sensitive models during the breach window
self.env['esmis.audit.log'].search([
    ('model', 'in', ['esmis.student', 'esmis.health.record', 'esmis.financial.record']),
    ('operation', '=', 'read'),
    ('timestamp', '>=', suspected_start),
    ('timestamp', '<=', suspected_end),
    ('user_id', '=', compromised_user_id),
])
```

The audit log records model, operation, user, timestamp, and (where applicable) record count.
It does not store field values — this is intentional to avoid compounding the breach.

### Data Type Classification

Once you know which models were accessed, classify the exposed data types:

| Data Type | Classification | Penalty Multiplier |
|-----------|---------------|-------------------|
| Basic PII (name, student number, program) | General Personal Information | Standard |
| Contact details (phone, address, email) | General Personal Information | Standard |
| Financial records, grades | General Personal Information | Standard |
| Health / medical records | Sensitive Personal Information (SPI) | Increased |
| Counseling records | Sensitive Personal Information (SPI) | Increased |
| PhilSys number, biometric data | Sensitive Personal Information (SPI) | Increased |
| Any SPI involving minors | Sensitive Personal Information — Minors | +50% penalty (RA 10173 Section 36) |

The data type classification determines notification requirements and potential penalties.
SPI breaches require mandatory data subject notification. SPI breaches involving minors carry
a 50% penalty increase under RA 10173 Section 36 — flag these to legal counsel immediately.

---

## Step 4 — Classification

Assign a severity level to the breach based on the scope assessment. This governs escalation
and urgency of notification.

| Severity | Criteria |
|----------|----------|
| Critical | SPI exposed; or minors affected; or more than 500 data subjects affected; or data confirmed exfiltrated externally |
| High | General PII of 100–499 data subjects; or SPI of fewer than 100 data subjects; or unauthorized access confirmed but exfiltration uncertain |
| Medium | General PII of fewer than 100 data subjects; internal access only; no evidence of exfiltration |
| Low | Near-miss or suspected breach not confirmed; no personal data confirmed accessed |

Critical and High breaches must be reported to NPC within 72 hours. Medium and Low breaches
must still be documented internally but NPC notification may not be required — the DPO makes
this determination based on likelihood of harm.

---

## Step 5 — NPC Notification

For Critical and High severity breaches (and any breach where the DPO determines notification
is required), submit the NPC Personal Data Breach Notification Form (PDBNF) within 72 hours
of discovery.

**Submission address:** complaints@privacy.gov.ph

### Required Information on the PDBNF

- Nature of the breach (unauthorized access, accidental disclosure, system compromise, etc.)
- Approximate number of data subjects affected (use the scope assessment count; note if the
  figure is still being refined)
- Categories of data involved (list the data types and their classification tier)
- Likely consequences of the breach for data subjects
- Measures already taken to address the breach (containment actions from Step 2)
- Measures planned to prevent recurrence
- Name, position, and contact details of the DPO

If the full scope is not yet known at the 72-hour mark, submit what is known and follow up
with a supplemental notification. Late or absent notification is a separate violation.

---

## Step 6 — Data Subject Notification

Notify affected students (and parents/guardians for minors) when the breach involves SPI or
when it is likely to cause harm to the data subject. Notification must occur as soon as
reasonably practicable after the NPC notification is filed.

### Notification Template

The notification must include, in plain language:

1. **What happened** — a factual description of the breach without technical jargon.
2. **What data was exposed** — specific categories (e.g., "your name, student number, and
   medical records").
3. **What we are doing** — containment and remediation steps already taken.
4. **What you can do** — practical steps the student can take (e.g., monitor for phishing,
   contact the DPO, request a copy of their data).
5. **DPO contact information** — name, email, and phone number.

Notification is delivered by email to the student's institutional email address and, where
the institution has a mobile number on file, by SMS. For minors, notification is also sent
to the guardian's contact on record.

All notification events are logged in the breach record with timestamps.

---

## Step 7 — Remediation

Remediation addresses the root cause identified in the scope assessment. It must not be
delayed while notifications are in progress — both workstreams run concurrently.

Common remediation actions:

- **Password resets** for all accounts that may have been compromised, not just the confirmed
  one. Use the system bulk password reset tool and force re-authentication.
- **Key rotation** for all API keys, even those not confirmed as compromised, if the breach
  involved credential exposure.
- **Access review** — audit all user accounts with access to the affected models and remove
  any access that is no longer appropriate. Apply least-privilege corrections.
- **Vulnerability patching** — if the breach was caused by a software vulnerability, apply
  the patch and verify it closes the vector before re-enabling affected services.
- **MFA enforcement** — if the breach involved credential theft and MFA was not enforced,
  implement MFA for all users with access to SPI models.

Document each remediation action with the person responsible and a target completion date.
Track open items in the breach record until all are closed.

---

## Step 8 — Post-Incident Review

Within 30 days of breach closure (all remediation items complete), conduct a post-incident
review and submit a written report to institutional management.

The report must cover:

1. **Root cause analysis** — what condition allowed the breach to occur.
2. **Timeline** — detection, containment, assessment, notification, and remediation with
   timestamps.
3. **Scope** — confirmed number of affected records and data subjects, data types involved.
4. **Notifications sent** — NPC filing reference, data subject notification dates.
5. **Policy or process gaps** — what existing controls failed or were absent.
6. **Recommended changes** — policy updates, technical controls, staff training topics.
7. **Staff training plan** — if the breach involved human error, specify the training to be
   delivered and the timeline.

The post-incident report is a management document, not a technical one. Write it so that
non-technical readers can understand what happened and what is being done to prevent recurrence.

---

## Step 9 — Documentation

Every breach, regardless of severity, requires a complete breach record. This is a legal
requirement under RA 10173 and NPC rules.

The `esmis.breach.record` model stores:

| Field | Description |
|-------|-------------|
| `detection_datetime` | When the breach was first detected |
| `discovery_datetime` | When the breach was confirmed |
| `severity` | Classification from Step 4 |
| `affected_record_count` | Number of data records involved |
| `affected_subject_count` | Number of unique data subjects |
| `data_types` | Categories of data exposed |
| `breach_description` | Factual description of what occurred |
| `containment_log` | Timestamped log of containment actions |
| `npc_filing_reference` | PDBNF reference number from NPC |
| `npc_filing_datetime` | When the PDBNF was submitted |
| `subject_notification_datetime` | When data subjects were notified |
| `remediation_items` | One2many of remediation actions with owner and status |
| `post_incident_report` | Attachment of the final management report |
| `closed_datetime` | When all remediation items were marked complete |
| `legal_hold` | Set to `True` for the duration of any related legal proceedings |

Breach records are subject to the 7-year audit log retention schedule and must never be
deleted or anonymized.

---

## Penalty Awareness

Understanding penalty exposure informs how urgently leadership must treat breach response.

Under RA 10173:

- Unauthorized processing of SPI: imprisonment of 3–6 years and fine of PHP 500,000–4,000,000
- Negligent failure to notify NPC within 72 hours: administrative fines per NPC guidelines
- Breach involving SPI of minors: **50% increase** on applicable penalties (Section 36)
- Each count of unauthorized disclosure is a separate offense

These are institutional penalties in addition to civil liability to affected data subjects.
Brief legal counsel as soon as a Critical or High breach is confirmed. Do not wait for the
post-incident review.

---

## Related Documents

- [Regulatory Compliance](../principles/regulatory-compliance.md) — RA 10173 obligations and NPC framework
- [Audit and Compliance](../principles/audit-compliance.md) — audit log structure and retention
- [Data Retention and Disposal](../principles/data-retention-and-disposal.md) — legal hold procedures
- [Consent Management](../principles/consent-management.md) — consent records and withdrawal
- [Error Handling and Logging](../principles/error-handling.md) — no PII in logs
- [Security Audit Guide](security-audit-guide.md) — proactive security review procedures
