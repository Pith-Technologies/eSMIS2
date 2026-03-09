# Data Privacy and PII Principles

Authoritative reference for PII handling and data privacy compliance in eSMIS, a Philippine
university Student Management Information System subject to Republic Act 10173 (Data Privacy
Act of 2012).

**Legal context:** eSMIS processes Sensitive Personal Information (SPI) as defined under RA
10173. Violations involving SPI carry criminal penalties (3–6 years imprisonment) increased by
50% when minors are affected (Section 36). Administrative fines can reach PHP 5,000,000 per
act. See [`docs/research/data-privacy-act-deep-dive.md`](../research/data-privacy-act-deep-dive.md)
for the full legislative analysis.

---

## 1. Data Classification Tiers

All student data fields must be assigned to one of four tiers. The tier governs encryption,
masking, access control, audit, and export behavior. See
[ADR-011](../architecture/decisions/ADR-011-data-classification-system.md) for the
architectural decision.

| Tier | Label | Encryption | Masking | Access Control | Audit on Read | Export |
|------|-------|------------|---------|----------------|---------------|--------|
| 0 | **Public** | None | None | Authenticated user | No | Unrestricted |
| 1 | **Internal** | None | None | Campus staff | No | Excluded from public exports |
| 2 | **Confidential** | None (TDE at DB level) | Partial (list views) | Role-based | Write only | Role-controlled; Tier 2+ fields redacted for unauthorized exporters |
| 3 | **Restricted / SPI** | Application-level AES-256-GCM + TDE | Full redaction or last-4 only | Specific named groups | Every read | Never in list endpoints; only in detail endpoints with access check |

**Student data examples by tier:**

| Data Element | Tier |
|---|---|
| Student number, campus, program name, year level, graduation year | 0 — Public |
| Full legal name, sex, date of birth, civil status, enrollment status, course schedule | 1 — Internal |
| Home address, mobile number, email, grades, GWA, parent/guardian name, scholarship details, tuition balance | 2 — Confidential |
| PhilSys/PSN, LRN, SSS/GSIS, TIN, passport number, PWD ID, Solo Parent ID, health records, counseling notes, disciplinary records, biometric photo, bank account number | 3 — Restricted |

> Note: Under RA 10173 Section 3(l)(2), "education" is explicitly classified as Sensitive
> Personal Information. The NPC has confirmed that grades, test scores, section assignments,
> and enrollment status are all SPI. Grades sit at Tier 2 in the access matrix because
> application-level encryption would break ORM sorting, GWA computation, and CHED reporting
> queries — protection is achieved through access control and mandatory audit logging instead.

---

## 2. PII Field Inventory

Complete classification of PII fields collected by eSMIS, organized by category.

### Student Personal Data

| Field | Model | RA 10173 Basis | Tier |
|---|---|---|---|
| Full legal name | `res.partner` | Sec. 3(g) — personal information | 1 |
| Date of birth | `res.partner` | Sec. 3(l)(1) — age | 1 |
| Sex / gender | `res.partner` | Sec. 3(l)(1) — conservative treatment | 1 |
| Home address | `res.partner` | Sec. 3(g) | 2 |
| Mobile number | `res.partner` | Sec. 3(g) | 2 |
| Email address | `res.partner` | Sec. 3(g) | 2 |
| Photograph (non-biometric) | `ir.attachment` | Sec. 3(g) | 2 |
| Photograph (biometric use) | `ir.attachment` | Sec. 3(l)(3) — biometric | 3 |
| Nationality / citizenship | `res.partner` | Sec. 3(l)(1) — ethnic origin | 1 |
| Religion | `esmis.student` | Sec. 3(l)(1) — religious affiliation | 1 |
| Ethnicity / IP membership | `esmis.student` | Sec. 3(l)(1) — race, ethnic origin | 1 |
| Civil status | `res.partner` | Sec. 3(l)(1) — marital status | 1 |

### Government Identifiers

All government-issued IDs are SPI under Sec. 3(l)(4). All are Tier 3.

| Field | Model | Masking Pattern | Permitted Roles |
|---|---|---|---|
| PhilSys Number (PSN) | `esmis.identifier` | `****-****-####` | Registrar Manager |
| Learner Reference Number (LRN) | `esmis.identifier` | `********####` | Registrar |
| SSS / GSIS Number | `esmis.identifier` | `**-*******-#` | Finance Manager |
| TIN | `esmis.identifier` | `***-***-####` | Finance Manager |
| PWD ID Number | `esmis.identifier` | `****####` | Registrar, Financial Aid |
| Solo Parent ID Number | `esmis.identifier` | `****####` | Registrar, Financial Aid |
| Passport Number | `esmis.identifier` | `**####` | Registrar Manager |

### Academic Data

| Field | Model | Tier | Notes |
|---|---|---|---|
| Individual grades | `esmis.grade` | 2 | SPI per NPC advisory; access-controlled not encrypted |
| GWA | `esmis.student` | 2 | Aggregate of grades; same SPI classification |
| Academic standing | `esmis.student` | 2 | Dean's list, probation, dismissal — SPI |
| Enrollment status | `esmis.enrollment` | 1 | SPI per RA 10173 Sec. 3(l)(2) |
| Enrollment history | `esmis.enrollment` | 2 | Per-term records |
| Disciplinary records | `esmis.disciplinary.record` | 3 | SPI under Sec. 3(l)(2) and Sec. 3(l)(3) |

### Financial Data

| Field | Model | Tier |
|---|---|---|
| Tuition balance / ledger | `esmis.financial.assessment` | 2 |
| Financial aid award details | `esmis.financial.aid.award` | 2 |
| Family income bracket | `esmis.financial.aid.application` | 2 |
| Scholarship amounts | `esmis.financial.aid.award` | 2 |
| Bank account number | `esmis.payment` | 3 |

### Health Data

| Field | Model | Tier |
|---|---|---|
| Disability status / PWD classification | `esmis.health.record` | 3 |
| Medical records, certificates, immunization | `esmis.health.record` | 3 |
| Counseling / psychological records | `esmis.counseling.note` | 3 |

### Family Data

| Field | Model | Tier |
|---|---|---|
| Parent / guardian name | `esmis.applicant` | 2 |
| Parent / guardian contact information | `esmis.applicant` | 2 |
| Family income | `esmis.financial.aid.application` | 2 |

---

## 3. Encryption Strategy

See [ADR-012](../architecture/decisions/ADR-012-pii-encryption-strategy.md) for the
architectural decision. The hybrid approach: PostgreSQL Transparent Data Encryption (TDE)
as the baseline for all data at rest, with application-level encryption (ALE) layered on
top for Tier 3 fields only.

### Application-Level Encryption (Tier 3 Fields)

Tier 3 fields use Fernet (AES-128-CBC with HMAC-SHA256 authentication) via the
`cryptography` library. The encrypted value is stored in a `_ciphertext` column; the
human-readable value is a computed field with `store=False`.

```python
from cryptography.fernet import Fernet
from odoo import fields, models

class EsmisIdentifier(models.Model):
    _name = "esmis.identifier"
    _inherit = ["esmis.pii.aware"]

    # The ciphertext column — never expose directly in views
    philsys_psn_ciphertext = fields.Binary(string="PSN Ciphertext", attachment=False)

    # The human-readable computed field — access-controlled at the group level
    philsys_psn = fields.Char(
        string="PhilSys Number",
        compute="_compute_philsys_psn",
        inverse="_inverse_philsys_psn",
        search="_search_philsys_psn",
        store=False,
        groups="esmis_security.group_esmis_registrar_manager",
    )

    # Blind index for exact-match search without decrypting
    philsys_psn_blind_index = fields.Char(index=True)
```

### Blind Indexes for Searchable Encrypted Fields

Encrypted fields cannot be searched with `LIKE` or sorted. For exact-match lookups, a blind
index is stored alongside the ciphertext: `HMAC-SHA256(index_key, normalize(plaintext))`.

- The HMAC key is separate from the encryption key.
- The plaintext is normalized before hashing (strip whitespace and hyphens, uppercase).
- Only exact-match search (`operator == '='`) is supported on encrypted fields.
- The blind index column must have a PostgreSQL B-tree index (`index=True`) for query
  performance; without it, lookups degrade to full table scans.

```python
def _search_philsys_psn(self, operator, value):
    if operator == "=":
        blind = self._compute_blind_index(value, "philsys_psn", "exact")
        return [("philsys_psn_blind_index", "=", blind)]
    raise UserError(_("Only exact match search is supported for encrypted fields."))
```

### Key Management

| Environment | Key Location |
|---|---|
| Development | `odoo.conf` (no real PII present) |
| Staging | Docker secrets or environment variables (synthetic data only) |
| Production (minimum) | `odoo.conf` with file permissions `0600` |
| Production (standard) | Database-stored key with master key in environment variable (envelope encryption) |
| Production (enterprise) | HashiCorp Vault or cloud KMS |

**Key rotation procedure:** Generate a new key version, mark it current, re-encrypt all
records in batches of 1000 via the `esmis.pii.encryption.migration` background job, then
archive the old key. Rotate at minimum annually or immediately after suspected compromise.
Keys are backed up separately from database backups and must never be stored in the same
location as the backup files they protect.

### PostgreSQL TDE

TDE covers all data at rest across all tiers and protects against physical media theft or
backup exfiltration. TDE alone is insufficient for Tier 3 because a compromised DBA with
direct SQL access can query decrypted values. Application-level encryption ensures that
the database server never holds plaintext Tier 3 values, only ciphertext.

### Fields That Are Masked, Not Encrypted

Grades are protected at Tier 2 through access control and audit logging, not
application-level encryption. Encrypting grades would make ORM sorting, GWA computation,
and CHED HEMIS reporting queries impossible without decrypting every row. The trade-off is
documented in ADR-012.

---

## 4. Consent Management

For the full technical specification, see
[`docs/principles/consent-management.md`](consent-management.md).

**Summary of requirements:**

- One `esmis.consent` record per student per processing purpose. Purposes include:
  `enrollment`, `ched_reporting`, `financial_aid`, `health_services`, `counseling`,
  `marketing`, `research`, `alumni_services`, `third_party_sharing`.
- Each record carries a `lawful_basis` field distinguishing between `consent`, `contract`,
  `legal_obligation`, `vital_interest`, `public_authority`, and `legitimate_interest`.
- Processing under `contract` (enrollment operations) or `legal_obligation` (CHED HEMIS
  reporting) does not require a separate consent record and cannot be withdrawn by the
  student.
- **Minor consent:** Students under 18 cannot provide valid consent independently under
  RA 10173 and NPC Circular 2023-04. The `esmis.consent.minor_guardian_id` field must
  reference the consenting parent or legal guardian. Determine age at enrollment; track the
  student's 18th birthday for consent transition.
- **Withdrawal:** Withdrawal must be as easy to perform as giving consent
  (NPC Circular 2023-04 requirement). The system sets `is_withdrawn = True` and stops
  processing for that purpose. Data retained under other lawful bases (e.g., academic
  records under CHED legal obligation) is unaffected by withdrawal.
- **Re-consent:** When the consent form changes materially, existing consents remain valid
  under the version they were signed. Affected students must be notified and re-consent
  requested.

---

## 5. Data Subject Rights

Eight rights under RA 10173 Section 16. All requests must be fulfilled within 30 working
days of receipt. Students are verified before any data is released.

| Right | Implementation Approach |
|---|---|
| **Right to be informed** | Privacy notice presented at enrollment (physical and digital). Accessible from student portal. Updated when processing purposes change. Content must include: identity of the institution as PIC, DPO contact, purpose and legal basis, retention period, and description of all eight rights. |
| **Right of access** | Self-service data export from student portal. Formal request triggers a comprehensive export (CSV, JSON, or XML) of all personal data held. Includes personal info, enrollment history, grades, and financial records. Excludes privileged information. |
| **Right to rectification** | Correction request workflow with supporting documentation. Approval chain: Registrar for academic data. Audit trail preserves original and corrected values. Downstream systems and parties that received incorrect data must be notified. |
| **Right to erasure** | Available for non-essential data (marketing preferences, optional profile fields, research data). Academic records — grades, TOR, enrollment history, graduation records — cannot be erased. CHED legal obligation overrides under RA 10173 Sec. 13(b). Erasure of PII in permanent records uses anonymization: name replaced with `Student #[hash]`, contact details with `[ANONYMIZED]`, encrypted national IDs crypto-shredded (destroy the encryption key). |
| **Right to data portability** | Export personal data in CSV, JSON, or XML on request. Format must be structured and commonly used per Section 18. |
| **Right to object** | Students may object to processing based on consent or legitimate interest (marketing, analytics). Cannot object to processing required by law (CHED reporting) or the enrollment contract (grade recording). |
| **Right not to be subject to automated decision-making** | Any automated decision affecting a student (e.g., academic standing computed by algorithm, early warning flags) must be disclosed in the privacy notice. Student has the right to request human review of any automated decision. Relevant when AI/ML features are introduced (see NPC Advisory 2024-04). |
| **Right to damages** | Institutional liability for inaccurate, unlawfully obtained, or unauthorized use of personal data. Implement preventively through correct access controls and audit logging; do not wait for a claim to enforce compliance. |

---

## 6. Access Control for PII

See [`docs/principles/access-rights.md`](access-rights.md) for the group hierarchy.

### Field-Level Access via `groups=`

Every Tier 2+ field in views and every Tier 3 field on models must carry a `groups=`
attribute. When a user without the required group calls `read()`, the ORM silently omits
that field from the result — the user sees the record but not the restricted field.

```python
# Grades: visible to registrar officers/managers, faculty (own sections), student (own record)
grade_value = fields.Float(
    string="Grade",
    digits=(4, 2),
    groups="esmis_security.group_esmis_registrar_officer,"
           "esmis_security.group_esmis_faculty,"
           "esmis_security.group_esmis_student_self",
)
```

### Role-Based PII Visibility Matrix

| Field Category | Student (Self) | Faculty | Registrar Officer | Registrar Manager | Finance | Financial Aid | Counselor | Clinic | DPO |
|---|---|---|---|---|---|---|---|---|---|
| Name, student number | Own only | Own sections | All | All | All | All | Assigned | Assigned | Audit only |
| Grades | Own only | Own sections (entry) | All (read) | All (read/write) | No | No | Assigned | No | Audit only |
| Contact info | Own | No | All | All | All | All | Assigned | Assigned | Audit only |
| National IDs | No | No | No | Masked | No | No | No | No | Audit only |
| TIN | No | No | No | No | Masked | No | No | No | Audit only |
| Financial records | Own | No | No | No | All | All | No | No | Audit only |
| Health records | Own | No | No | No | No | No | No | All | Audit only |
| Counseling notes | Own | No | No | No | No | No | Own assigned | No | Audit only |
| Disciplinary records | Own (limited) | No | All | All | No | No | No | No | Audit only |

The DPO can view audit logs of who accessed which PII fields — not the PII values themselves.
This prevents the DPO from becoming a single point of compromise.

### MFA Required for SPI Access

NPC Circular 2023-06 mandates multi-factor authentication for online access to SPI and
privileged data. This applies to any session that accesses Tier 3 fields. See Section 11.

### Masking Patterns

Masked fields show partial data in list views. An explicit "Reveal" action in the form view
decrypts and displays the value for authorized users. The reveal event is logged.

| Pattern | Fields | Display |
|---|---|---|
| Last 4 digits | PhilSys, TIN, SSS, phone | `****-****-1234` |
| First char + domain | Email | `e***@university.edu.ph` |
| City only | Home address | `Quezon City` |
| Full redaction | Health, counseling, disciplinary | `[Restricted]` |
| Placeholder image | Biometric photo | Generic avatar icon |

---

## 7. Audit Requirements

See [`docs/principles/audit-compliance.md`](audit-compliance.md) for the full audit
logging specification.

All access to Confidential (Tier 2) and Restricted (Tier 3) fields must be logged in
`esmis.pii.access.log`. Standard Odoo `mail.thread` tracking logs writes only; PII audit
logging additionally covers reads.

### What Is Logged

| Event | Fields Captured | Value Logged? |
|---|---|---|
| Tier 3 field read | user, timestamp, model, record_id, field_name, IP, session_id | No |
| Masked field reveal | user, timestamp, model, record_id, field_name, IP | No |
| Tier 2+ field write | user, timestamp, model, record_id, field_name, hash(old), hash(new) | Hash only |
| Bulk export | user, timestamp, model, record_ids, field_names, export_format | No |
| Blind index search | user, timestamp, model, field_name, search_type | No (not the search term) |
| Consent event | user, timestamp, student_id, purpose, event_type | Consent metadata only |
| Break-the-glass access | requester, approver, model, fields, justification | Justification text only |

**Never log actual PII values.** Log the record ID and field name, never the field's
content. Logging PII values in audit logs creates a second PII store that must itself be
encrypted and access-controlled, defeating the purpose of the audit log.

### Immutable Audit Log

The `esmis.pii.access.log` model must be append-only:

```python
class EsmisPiiAccessLog(models.Model):
    _name = "esmis.pii.access.log"
    _log_access = False  # Prevent Odoo's write_date from being a modification vector

    def unlink(self):
        raise UserError(_("Audit log entries cannot be deleted."))

    def write(self, vals):
        # Only post_review_notes (for BTG review documentation) is writable
        immutable = {"user_id", "create_date", "model", "res_id", "field_name", "access_type"}
        if immutable & set(vals):
            raise UserError(_("Audit log entries cannot be modified."))
        return super().write(vals)
```

In addition to ORM-level protection, the audit log table must have `REVOKE DELETE` and
`REVOKE UPDATE` at the PostgreSQL level for all database roles except the audit log writer
role.

### Suspicious Access Detection

A `ir.cron` job runs every 15 minutes and checks for these patterns. High-severity alerts
are emailed immediately; medium-severity alerts create a `mail.activity` for the DPO.

| Pattern | Threshold | Severity |
|---|---|---|
| Bulk Tier 3 reads | >50 by a single user in 1 hour | High |
| Bulk export | >100 records with Tier 2+ fields | High |
| After-hours Tier 3 access | Outside configured business hours | Medium |
| Cross-campus access | User accessing records outside assigned campus | High |
| Repeated denied access | >5 failed PII access attempts in 10 minutes | High |
| BTG request spike | >3 break-the-glass requests from same user in 24 hours | Medium |

### Audit Log Retention

| Log Type | Retention | Disposal |
|---|---|---|
| PII access logs (Tier 3 reads) | 5 years | Archive encrypted, then delete |
| PII write logs | 7 years | Archive encrypted, then delete |
| Consent event logs | Permanent | Never delete |
| Break-the-glass logs | 7 years | Archive encrypted, then delete |
| Breach event logs | Permanent | Never delete |

Five years covers the NPC minimum and aligns with CHED academic record retention standards.

---

## 8. PII in Logs and Error Messages

See [`docs/principles/error-handling.md`](error-handling.md) for the full error-handling
specification.

**The rule is absolute: no PII values in log output.**

```python
import logging
_logger = logging.getLogger(__name__)

# WRONG — exposes PII in server logs
_logger.error("Failed to process student %s (PhilSys: %s)", student.name, student.philsys_psn)

# CORRECT — log only the record ID
_logger.error("Failed to process student record id=%d", student.id)
```

Fields that must never appear in log messages or error traces:

- All Tier 3 fields (national IDs, health, counseling, disciplinary, bank accounts)
- Phone numbers, email addresses, home addresses
- Parent/guardian names and contact information
- Any field value from a model inheriting `esmis.pii.aware`

**User-facing error messages** must also be sanitized. If a validation failure involves a
PII field, report the field name and the rule that failed — never the field's value.

```python
# WRONG — shows PII value in the user-facing error message
raise ValidationError(_("PhilSys number '%s' is already registered.") % psn_value)

# CORRECT — reports the rule without the value
raise ValidationError(_("A student record with this PhilSys number already exists."))
```

**Structured logging:** Log statements involving PII-adjacent models should carry a
`pii=True` marker in structured logging contexts to enable automated scrubbing pipelines.

---

## 9. PII in Backups

Backups are subject to the same confidentiality obligations as live data.

- **Backup encryption:** All database backups must be encrypted before leaving the server.
  Application-level encrypted fields (Tier 3) remain encrypted inside the backup; the backup
  encryption adds a second layer covering all tiers.
- **Key separation:** Backup encryption keys are stored separately from both the application
  encryption keys and the database itself. A stolen backup without the backup key is
  unreadable.
- **Retention alignment:** Backup retention must not exceed the data retention period of
  the longest-lived data in the backup. See
  [`docs/principles/data-retention-and-disposal.md`](data-retention-and-disposal.md).
- **Backup disposal:** When a backup is superseded or its retention period expires, dispose
  using cryptographic erasure — destroy the backup encryption key. Document the disposal in
  the disposal log per RA 10173 IRR Section 19(d).
- **Access controls:** Access to backup files is restricted to system administrators. Access
  events are logged. Production backup data must never be restored to a development or
  staging environment; use synthetic data instead.

---

## 10. Test Data and PII

For the full specification, see [`docs/principles/test-data-pii.md`](test-data-pii.md).

**No production PII in test or development environments.** This is non-negotiable.

Generate synthetic data using the `esmis_test_data` module (loaded only in test or demo
mode; excluded from production deployments via `auto_install = False` and no dependency
from production modules):

```python
import random

def fake_philsys_psn():
    """Return a structurally valid but entirely synthetic PhilSys number."""
    parts = [f"{random.randint(0, 9999):04d}" for _ in range(4)]
    return "-".join(parts)
```

Demo data must use obviously fake identifiers: `example.edu.ph` email domain, clearly
fictional names (e.g., "Juan Halimbawa"), placeholder national ID values. Any demo data
that could be mistaken for a real individual's PII must be replaced before the module ships.

---

## 11. MFA for Sensitive Data Access

NPC Circular 2023-06 mandates multi-factor authentication for online access to SPI and
privileged data. The compliance deadline was March 30, 2025.

**Operations that require MFA in eSMIS:**

| Operation | MFA Requirement |
|---|---|
| Viewing any Tier 3 field (national IDs, health records, counseling, disciplinary) | Session must have completed MFA within the last 4 hours |
| Bulk export of Tier 2+ fields (>50 records) | MFA required at time of export |
| Approving a break-the-glass access request | MFA required at point of approval |
| Modifying user group membership (security administration) | MFA required |

**Implementation:** Odoo's built-in `auth_totp` module provides the TOTP infrastructure.
The `esmis_security` module adds a check on Tier 3 field reads that inspects the session's
`mfa_verified_at` timestamp. If absent or older than 4 hours, the read is blocked and the
user is redirected to the MFA verification screen.

```python
def _check_mfa_for_spi_access(self):
    """Raise AccessError if the current session has not completed MFA recently."""
    from odoo.http import request
    mfa_verified_at = request.session.get("mfa_verified_at")
    if not mfa_verified_at:
        raise AccessError(_("Multi-factor authentication is required to access this data."))
    age = fields.Datetime.now() - mfa_verified_at
    if age.total_seconds() > 4 * 3600:
        raise AccessError(_("MFA session expired. Please re-authenticate to continue."))
```

---

## 12. Cross-Border Data Transfer

RA 10173 Section 21 holds the institution accountable for personal data transferred
internationally. Cross-border transfer is treated as processing; all lawful processing
requirements apply.

**Scenarios where student data may leave the Philippines:**

- Cloud hosting providers (AWS, GCP, Azure) with data centers outside the Philippines
- International partner universities (exchange programs, articulation agreements)
- Third-party SaaS platforms (LMS, email, analytics tools)
- CHED international reporting obligations

**Requirements before any cross-border transfer:**

1. **Inventory the flow.** Document: destination country, recipient organization, categories
   of data transferred, processing purpose, and lawful basis.
2. **Adequacy assessment.** The NPC has not published formal adequacy determinations.
   Assess the destination country's data protection regime and document the findings.
3. **Contractual safeguards.** Use Model Contractual Clauses (MCC) per NPC Advisory
   2024-01, or equivalent clauses, with cloud providers and international partners. Clauses
   must cover data protection obligations, data subject rights, security measures, breach
   notification procedures, sub-processing restrictions, and audit rights.
4. **Inform data subjects.** The enrollment privacy notice must disclose all international
   transfers, including the cloud hosting jurisdiction.
5. **Data residency preference.** Where technically and commercially feasible, configure
   cloud providers to use Philippine or ASEAN-region data centers. Document the justification
   when this is not achievable.

---

## 13. Breach Response

For the full operational procedure, see
[`docs/guides/breach-response-guide.md`](../guides/breach-response-guide.md).

**Key statutory obligations (NPC Circular 16-03):**

- Notify the NPC **within 72 hours** of discovering or reasonably believing a breach has
  occurred. Submit through the NPC's Data Breach Notification Management System (DBNMS).
- Notify affected data subjects **individually** (not by general announcement) within the
  same 72-hour window when the breach involves SPI or 100 or more data subjects.
- Submit a full breach report to the NPC within **5 days** of the initial notification.

**Concealment is a separate criminal offense** under Section 30: 1.5–5 years imprisonment
and PHP 500K–1M fine. Delay in reporting is legally prohibited when SPI or 100+ data
subjects are involved.

**Internal response:** The Data Breach Response Team must be formed as an organizational
measure under NPC Circular 2023-06. When a breach is detected or reported, the primary
source for identifying affected records and data subjects is `esmis.pii.access.log`. The
system generates a pre-filled notification report (PDF) for the DPO to review and submit
to the DBNMS.

---

## 14. Developer Checklist

Run this checklist for every feature that touches personal data:

- [ ] Classified all new fields per the four-tier model (Section 1)
- [ ] Applied application-level encryption (`esmis.pii.aware` mixin + ciphertext column) to all new Tier 3 fields
- [ ] Added a blind index for any Tier 3 field that must support search
- [ ] Set `groups=` on Tier 2+ fields in both model definitions and view XML
- [ ] Added read audit logging to any new Tier 3 field access path
- [ ] Verified that no PII values appear in `_logger` calls or user-facing error messages (Section 8)
- [ ] Created synthetic test data using `esmis_test_data` generators — no real PII in tests or demo data
- [ ] Checked consent requirements: does this new processing purpose require a new consent record type?
- [ ] Verified data retention rules apply to newly collected data (see [`data-retention-and-disposal.md`](data-retention-and-disposal.md))
- [ ] Confirmed MFA enforcement applies if the new feature accesses Tier 3 fields (Section 11)
- [ ] Updated the PII field inventory in this document if new fields are added

---

## Related Documents

| Document | Purpose |
|---|---|
| [ADR-025](../architecture/decisions/ADR-025-student-data-privacy-ra10173.md) | Architectural decisions for RA 10173 compliance |
| [ADR-011](../architecture/decisions/ADR-011-data-classification-system.md) | Data classification system design |
| [ADR-012](../architecture/decisions/ADR-012-pii-encryption-strategy.md) | PII encryption strategy and key management |
| [`consent-management.md`](consent-management.md) | Full consent data model and enforcement patterns |
| [`data-retention-and-disposal.md`](data-retention-and-disposal.md) | Retention schedules and disposal procedures |
| [`test-data-pii.md`](test-data-pii.md) | Synthetic data generation and test environment rules |
| [`access-rights.md`](access-rights.md) | Group hierarchy and three-tier access architecture |
| [`audit-compliance.md`](audit-compliance.md) | Full audit logging specification |
| [`error-handling.md`](error-handling.md) | Error handling and log sanitization patterns |
| [`guides/breach-response-guide.md`](../guides/breach-response-guide.md) | Operational breach response procedures |
| [`research/data-privacy-act-deep-dive.md`](../research/data-privacy-act-deep-dive.md) | Full RA 10173 legislative analysis |
| [`research/pii-handling-best-practices.md`](../research/pii-handling-best-practices.md) | Technical implementation patterns |
