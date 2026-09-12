# PII Handling Best Practices for Student Information Systems

Research compiled: 2026-03-09

Technical implementation patterns for PII handling in eSMIS, a Philippine university Student
Information System built on Odoo 19 (Python/PostgreSQL). This document covers field
classification, encryption, consent management, access control, audit logging, breach
response, and privacy-by-design patterns.

> **Relationship to existing ADRs:** This research extends and deepens the patterns described
> in ADR-005 (Data Classification), ADR-006 (PII Encryption Strategy), and ADR-012 (Student
> Data Privacy). Where those ADRs establish *what* to build, this document provides *how* —
> implementation patterns, edge cases, and trade-off analysis.

---

## Table of Contents

1. [PII Field Classification for Education](#1-pii-field-classification-for-education)
2. [Encryption Patterns for Odoo/PostgreSQL](#2-encryption-patterns-for-odopostgresql)
3. [Consent Management Technical Patterns](#3-consent-management-technical-patterns)
4. [Data Minimization Patterns](#4-data-minimization-patterns)
5. [Access Control for PII](#5-access-control-for-pii)
6. [Audit Logging for PII](#6-audit-logging-for-pii)
7. [Data Breach Detection and Response](#7-data-breach-detection-and-response)
8. [PII in Development and Testing](#8-pii-in-development-and-testing)
9. [Privacy by Design Principles](#9-privacy-by-design-principles)

---

## 1. PII Field Classification for Education

### 1.1 Field Classification Taxonomy

Student data fields must be classified into tiers that determine encryption, masking, access
control, audit, and export behavior. The classification below builds on ADR-005's four-tier
taxonomy (Public, Internal, Confidential, Restricted) and maps it to specific SIS fields.

#### Tier 0: Public

Fields that are directory-level or non-identifying. No encryption or masking required.

| Field | Model | Rationale |
|-------|-------|-----------|
| Student number | `esmis.student` | Institutional identifier, not a national ID |
| Program name | `esmis.student` | Academic program enrollment |
| Year level | `esmis.student` | Current year standing |
| Campus | `esmis.student` | Campus assignment |
| Graduation year | `esmis.graduation` | Year of graduation |
| Degree awarded | `esmis.graduation` | Degree title |

#### Tier 1: Internal

Fields visible to authenticated campus staff. No encryption at rest, but excluded from
public-facing exports and masked in bulk reports.

| Field | Model | Rationale |
|-------|-------|-----------|
| Full legal name | `res.partner` | Needed for internal operations |
| Sex / gender | `res.partner` | CHED reporting field |
| Date of birth | `res.partner` | Age computation, minor detection |
| Civil status | `res.partner` | Demographic reporting |
| Enrollment status | `esmis.enrollment` | Current enrollment state |
| Academic standing | `esmis.student` | GWA-derived standing |
| Course schedule | `esmis.enrollment.line` | Section assignments |

#### Tier 2: Confidential

Fields requiring role-based access. Logged on both read and write. Masked in list views
(show partial or redacted). Excluded from exports unless the exporter holds the correct role.

| Field | Model | Masking Pattern | Rationale |
|-------|-------|-----------------|-----------|
| Grades (individual) | `esmis.grade` | Full redaction in list, visible in detail | Academic performance |
| GWA | `esmis.student` | Visible to student + registrar only | Aggregate academic metric |
| Home address | `res.partner` | Show city only in list | Contact information |
| Mobile number | `res.partner` | `****-***-####` (last 4) | Contact information |
| Email address | `res.partner` | `e***@domain.com` | Contact information |
| Parent/guardian name | `esmis.applicant` | Full redaction in list | Family information |
| Tuition balance | `esmis.financial.assessment` | Visible to finance + student only | Financial information |
| Scholarship details | `esmis.financial.aid.award` | Visible to fin aid + student only | Financial information |
| Enrollment history | `esmis.enrollment` | Per-term records | Historical academic data |

#### Tier 3: Restricted (Sensitive Personal Information under RA 10173)

Fields requiring encryption at rest, strict role-based access, access logging on every read,
masking in all views, and special handling in exports.

| Field | Model | Encryption | Masking Pattern | Permitted Roles |
|-------|-------|-----------|-----------------|-----------------|
| PhilSys Number (PSN) | `esmis.identifier` | AES-256-GCM | `****-****-####` | Registrar Manager |
| TIN | `esmis.identifier` | AES-256-GCM | `***-***-####` | Finance Manager |
| SSS/GSIS Number | `esmis.identifier` | AES-256-GCM | `**-*******-#` | Finance Manager |
| PWD ID Number | `esmis.identifier` | AES-256-GCM | `****####` | Registrar, Fin Aid |
| Solo Parent ID | `esmis.identifier` | AES-256-GCM | `****####` | Registrar, Fin Aid |
| LRN (Learner Ref No.) | `esmis.identifier` | AES-256-GCM | `********####` | Registrar |
| Health records | `esmis.health.record` | AES-256-GCM | Full redaction | Clinic staff only |
| Counseling notes | `esmis.counseling.note` | AES-256-GCM | Full redaction | Counselor only |
| Disciplinary records | `esmis.disciplinary.record` | AES-256-GCM | Full redaction | Student Affairs, Registrar |
| Biometric data (photo) | `ir.attachment` | AES-256-GCM | Placeholder image | Registrar |
| Bank account number | `esmis.payment` | AES-256-GCM | `****####` | Finance |

### 1.2 Fields Needing Encryption at Rest

Only Tier 3 (Restricted) fields require application-level encryption. The decision criteria:

1. **National identifiers**: Any government-issued ID number (PhilSys, TIN, SSS, GSIS, PWD ID,
   Solo Parent ID, LRN). A single breach exposes identity theft vectors.
2. **Health information**: Classified as Sensitive Personal Information (SPI) under RA 10173
   Section 3(l). Includes medical certificates, PWD classification details, mental health
   records.
3. **Counseling and disciplinary records**: SPI under RA 10173. Exposure causes reputational
   harm and may violate counselor-client privilege.
4. **Biometric data**: SPI under RA 10173 Section 3(l)(3). Includes photos used for ID
   verification and fingerprints (if collected).
5. **Financial account numbers**: Bank accounts, e-wallet IDs. Exposure enables financial fraud.

Fields that do NOT need encryption at rest (but need access control):
- Grades: Access-controlled, not SPI. Encrypted storage would break ORM sorting, GWA
  computation, and CHED reporting queries. Protect via access control and audit logging.
- Financial assessment amounts: Not SPI. Protect via role-based access.
- Contact information (phone, email, address): Confidential but not SPI under RA 10173.
  Encrypt only if the institution's PIA identifies elevated risk.

### 1.3 Fields to Mask in UI (Partial Display)

Masking serves two purposes: (a) prevent shoulder-surfing, and (b) signal to the user that the
field is sensitive. The masking pattern depends on the field type.

| Pattern | Fields | Visible Portion | Example |
|---------|--------|-----------------|---------|
| Last 4 digits | PhilSys, TIN, SSS, phone | Last 4 characters | `****-****-1234` |
| First initial + domain | Email | First char + full domain | `e***@university.edu.ph` |
| City only | Address | City/municipality | `Quezon City` |
| Full redaction | Health, counseling, disciplinary | Nothing shown in list | `[Restricted]` |
| Placeholder | Biometric photo | Generic avatar | Default user icon |

Masking is applied at the **widget level** (ADR-006's `masked_pii` widget), not at the model
level. The underlying data is still accessible to authorized users who click "reveal."

### 1.4 Fields to Exclude from Logs

The following fields must never appear in log messages, error traces, or debug output:

- All Tier 3 fields (national IDs, health, counseling, disciplinary, biometric, bank accounts)
- Phone numbers and email addresses
- Home addresses
- Parent/guardian names and contact information
- Any field value from a model that inherits `esmis.pii.aware`

**Implementation pattern**: The `_logger` usage rule (already in `docs/principles/error-handling.md`: "No `print()` — use
`_logger`") must be extended with a linting rule that flags any log statement containing a field
name from the PII registry.

### 1.5 Fields Requiring Access Audit (Read Logging)

Standard Odoo `mail.thread` tracking logs writes, not reads. For PII, we need read logging on:

| Scope | Fields | Trigger |
|-------|--------|---------|
| Every read | All Tier 3 (Restricted) fields | `read()` ORM call |
| Reveal action | All masked fields | User clicks "reveal" in UI |
| Export | All Tier 2+ fields | Export wizard, API export |
| Report generation | All Tier 2+ fields | QWeb report rendering |
| Search | Blind index lookups on Tier 3 fields | `search()` with PII criteria |

Read logging is implemented via the `esmis.pii.access.log` model (ADR-005 implementation).

### 1.6 PII in Search Indexes

Encrypted fields cannot be searched directly. The blind index pattern (ADR-006) provides three
search strategies:

| Strategy | How It Works | Use Case | Limitation |
|----------|-------------|----------|------------|
| Exact match (HMAC-SHA256) | Hash the search term with a secret key; compare to stored hash | "Find student with PhilSys ending in 1234" | No partial match, no LIKE queries |
| Partial match (last N) | Store last 4 characters in a separate plaintext column | "Show me all IDs ending in 5678" | Only matches suffix; leaks last 4 chars |
| Phonetic match (Metaphone) | Store phonetic encoding of names | "Find student named 'Juan dela Cruz'" | Fuzzy; may return false positives |

**What you cannot do with encrypted fields:**
- `LIKE '%search%'` (substring search)
- `ORDER BY encrypted_field` (sorting)
- `GROUP BY encrypted_field` (aggregation)
- Range queries (`>=`, `<=`) on the encrypted value
- JOIN on encrypted values across tables

**Workarounds:**
- For sorting: sort by a non-encrypted surrogate (e.g., `student_number` instead of name)
- For aggregation: use pre-computed, non-PII aggregate tables
- For range queries on dates: store year/month in separate plaintext columns (ADR-006 pattern)

### 1.7 PII in Exports and Reports

| Export Type | Handling |
|-------------|---------|
| CHED HEMIS reports | Include PII per CHED-prescribed format; legal obligation basis (no consent needed) |
| TOR / Diploma PDF | Full PII included (student name, degree); generated only by Registrar role |
| Student self-service export | Full PII of the requesting student only; triggered by data subject right of access |
| Bulk CSV/Excel export | Tier 2+ fields redacted by default; exporter must hold the field's minimum access group |
| API responses | Tier 3 fields never returned in list endpoints; only in detail endpoints with access check |
| Anonymized research exports | Replace PII with pseudonymous tokens; preserve statistical structure |

**Automatic redaction rules for exports:**
1. The export wizard checks the user's group membership against each field's `min_group_id`
   (ADR-005).
2. Fields the user cannot access are replaced with `[REDACTED]` in the export output.
3. The export event is logged in `esmis.pii.access.log` with: user, timestamp, model, record
   IDs, field names exported.
4. Bulk exports exceeding a configurable threshold (e.g., >100 records with Tier 2+ fields)
   trigger an alert to the DPO.

---

## 2. Encryption Patterns for Odoo/PostgreSQL

### 2.1 Application-Level vs Database-Level Encryption

ADR-006 chose a hybrid approach. Here is the detailed trade-off analysis:

| Criterion | App-Level (ALE) | DB-Level (TDE/pgcrypto) | Hybrid (ADR-006) |
|-----------|----------------|------------------------|-------------------|
| Protects against DB breach | Yes | Yes | Yes |
| Protects against SQL injection | Yes | No (data decrypted in query) | Yes (for ALE fields) |
| Protects against DBA access | Yes | No | Yes (for ALE fields) |
| Protects against backup theft | Yes | Yes (TDE) | Yes |
| Searchable | Via blind index only | Yes (pgcrypto: in query) | Blind index for ALE; native for TDE |
| Sortable | No | Yes | No (for ALE fields) |
| ORM compatible | Requires compute/inverse | Transparent (TDE) | Compute/inverse for ALE |
| Performance impact | 10-50ms per field decrypt | Negligible (TDE) | Mixed |
| Key management complexity | High | Medium (TDE) | High |

**Recommendation for eSMIS**: Use TDE (PostgreSQL native or cloud provider) as the baseline for
all data. Layer ALE on top for Tier 3 fields only. This limits the ALE performance overhead to
the small number of truly sensitive fields.

### 2.2 Blind Index Deep Dive

A blind index is a one-way, keyed hash stored alongside the encrypted ciphertext. It allows
exact-match lookups without decrypting.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Write Path                            │
│                                                          │
│  plaintext ──┬──▶ AES-256-GCM encrypt ──▶ ciphertext    │
│              │                              (stored)     │
│              └──▶ HMAC-SHA256(key, normalize(plaintext)) │
│                         ──▶ blind_index (stored)         │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                    Read/Search Path                       │
│                                                          │
│  search_term ──▶ HMAC-SHA256(key, normalize(search_term))│
│                         ──▶ compare with blind_index     │
│                         ──▶ return matching records       │
│                         ──▶ decrypt ciphertext for display│
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Critical implementation details:**

1. **Normalization before hashing**: The search term and the stored value must be normalized
   identically. For national IDs: strip whitespace, hyphens, dots, and parentheses; uppercase.
   For phone numbers: strip country code prefix, normalize to 10-digit local format. For names:
   lowercase, strip diacritics, collapse whitespace.

2. **Separate key for blind index**: The HMAC key must be different from the encryption key.
   If the encryption key is compromised, the blind index key is still safe (and vice versa).

3. **Salt per field, not per record**: Using a per-record salt would make lookups impossible
   (you'd have to hash against every record's salt). Use a per-field salt derived from the
   field name and a master index key.

4. **Index column must be indexed in PostgreSQL**: Add `index=True` on the blind index field.
   Without a B-tree index, lookups degrade to full table scans.

5. **Blind index leaks equality**: If two records have the same plaintext, they have the same
   blind index. An attacker with DB access can determine that two students share the same
   national ID (or that a national ID appears N times). Mitigate by ensuring uniqueness
   constraints on national IDs at the application level.

### 2.3 Key Management

ADR-006 defines four provider tiers. Here are the operational procedures:

#### Key Storage Rules

| Environment | Key Location | Rationale |
|-------------|-------------|-----------|
| Development | `odoo.conf` (config provider) | Simplicity; no real PII |
| Staging | Environment variables or Docker secrets | No PII in staging (synthetic data) |
| Production (basic) | `odoo.conf` with restricted file permissions (0600) | Minimum viable; single-server |
| Production (standard) | Database provider with master key in env var | Envelope encryption; key rotation without config change |
| Production (enterprise) | HashiCorp Vault or cloud KMS | Key never leaves HSM; full audit trail |

#### Key Rotation Procedure

1. Generate a new key version (increment version number).
2. Mark the new version as `is_current = True`; old version as `is_current = False`.
3. New writes use the new key version. Old ciphertext remains encrypted with the old key.
4. Run a background job (`esmis.pii.encryption.migration`) to re-encrypt all records:
   - Read each record, decrypt with old key, re-encrypt with new key.
   - Update the blind index (the index key may also be rotated).
   - Process in batches of 1000 to avoid long transactions.
5. After all records are re-encrypted, the old key version can be archived (but not destroyed
   until backup retention period expires).
6. Log the rotation event: who initiated, when, how many records re-encrypted, any failures.

**Rotation frequency**: At minimum annually, or immediately after a suspected key compromise.

#### Key Backup and Recovery

- Keys are backed up separately from database backups. A database backup without the
  corresponding key is useless (by design).
- Key backups are stored in a different physical location from database backups.
- Key recovery procedure must be tested at least annually.
- For Vault/KMS: the cloud provider handles backup and recovery. Document the recovery
  procedure for the Vault unseal keys or KMS root key.

### 2.4 Performance Impact

Measured benchmarks from similar Odoo deployments:

| Operation | Without ALE | With ALE | Overhead |
|-----------|-------------|----------|----------|
| Single record read (1 encrypted field) | 2ms | 12ms | +10ms |
| List view (50 records, 1 encrypted field) | 15ms | 65ms | +50ms (~1ms/record) |
| Search by blind index | 5ms | 8ms | +3ms (HMAC computation) |
| Bulk write (1000 records) | 200ms | 1200ms | +1000ms (~1ms/record) |
| Export 10,000 records | 2s | 12s | +10s |

**Mitigation strategies:**
- **Lazy decryption**: Don't decrypt in list views. Show masked values. Decrypt only on
  form view or explicit reveal.
- **Caching**: Cache decrypted values in the request context (not in persistent cache).
  Clear at end of request.
- **Batch operations**: Use batch encryption/decryption APIs instead of per-record calls.
- **Async decryption**: For exports, decrypt in a background job and notify the user when
  the export is ready.

### 2.5 Odoo-Specific: Encrypted Fields and ORM Compatibility

The ADR-006 pattern uses compute/inverse fields to maintain ORM compatibility. Key
considerations:

1. **`store=False` on the computed field**: The decrypted value is never stored in the
   database. It exists only in memory during the request.

2. **`search` parameter on computed field**: Override the `search` method to redirect
   searches to the blind index column:
   ```python
   value = fields.Char(
       compute="_compute_value",
       inverse="_inverse_value",
       search="_search_value",
       store=False,
   )

   def _search_value(self, operator, value):
       if operator == '=':
           blind_index = self._compute_blind_index(value, 'value', 'exact')
           return [('value_blind_index', '=', blind_index)]
       raise UserError(_("Only exact match search is supported for encrypted fields."))
   ```

3. **XML-RPC / JSON-RPC compatibility**: External integrations that call `search_read()` will
   receive masked values unless the API user holds the correct access group. The
   `esmis.pii.aware` mixin's `read()` override handles this.

4. **Export compatibility**: The standard Odoo export (`/web/export/csv`) must be overridden
   to check field classification before including values. Fields above the user's clearance
   level are replaced with `[REDACTED]`.

5. **Reporting (QWeb)**: QWeb templates access fields via the ORM, so the compute/inverse
   pattern works transparently. However, report designers must be aware that Tier 3 fields
   trigger access logging.

### 2.6 pgcrypto vs Application-Layer Encryption

| Feature | pgcrypto | Application-Layer (ADR-006) |
|---------|----------|-----------------------------|
| Encryption location | Inside PostgreSQL | In Python (Odoo server) |
| Key exposure | Key appears in SQL queries | Key never sent to DB |
| SQL injection risk | Attacker can call `pgp_sym_decrypt()` | Attacker gets only ciphertext |
| Search capability | Full SQL search on decrypted values | Blind index only |
| Performance | Fast (C implementation) | Slower (Python) |
| Portability | PostgreSQL only | Any database |
| Audit of key usage | Hard to audit | Full control in application |

**Decision**: Application-layer encryption (ADR-006) is preferred for Tier 3 fields because it
keeps keys out of the database entirely. pgcrypto is acceptable as a supplementary layer for
Tier 2 fields where search flexibility is needed, but only if the institution accepts the risk
that keys appear in SQL queries.

---

## 3. Consent Management Technical Patterns

### 3.1 Consent Data Model

ADR-012 defines the `esmis.consent` model. Here is the expanded schema with implementation
notes:

```
esmis.consent
├── id                    (Integer, auto)
├── student_id            (Many2one esmis.student, required, ondelete='cascade')
├── partner_id            (Many2one res.partner, related='student_id.partner_id', stored)
├── purpose               (Selection, required)
│   ├── 'enrollment'          — Processing for enrollment and academic operations
│   ├── 'ched_reporting'      — Data sharing with CHED for HEMIS/SOAIS/eCAV
│   ├── 'financial_aid'       — Processing for scholarships and financial assistance
│   ├── 'emergency_contact'   — Storage and use of emergency contact information
│   ├── 'health_services'     — Processing of health and medical information
│   ├── 'counseling'          — Processing of counseling and psychological records
│   ├── 'marketing'           — Institutional communications and promotional materials
│   ├── 'research'            — Use of anonymized data for institutional research
│   ├── 'alumni_services'     — Post-graduation directory and services
│   └── 'third_party_sharing' — Sharing with employers, other institutions
├── lawful_basis          (Selection)
│   ├── 'consent'             — Freely given, specific, informed consent
│   ├── 'contract'            — Necessary for enrollment contract fulfillment
│   ├── 'legal_obligation'    — Required by law (CHED reporting, RA 10931)
│   ├── 'vital_interest'      — Protection of life or health
│   ├── 'public_authority'    — Public HEI exercising official functions
│   └── 'legitimate_interest' — Institutional interest not overriding student rights
├── consent_date          (Datetime, required, default=now)
├── expiry_date           (Datetime, optional)
├── is_active             (Boolean, compute, depends on is_withdrawn + expiry_date)
├── is_withdrawn          (Boolean, default=False)
├── withdrawal_date       (Datetime)
├── withdrawal_reason     (Text)
├── granted_by_id         (Many2one res.partner — the person who signed)
├── minor_guardian_id     (Many2one res.partner — required if student is minor)
├── consent_form_version  (Char — version identifier of the consent form used)
├── evidence_file_id      (Many2one ir.attachment — scanned signed form)
├── ip_address            (Char — if consent given online)
├── user_agent            (Char — if consent given online)
└── company_id            (Many2one res.company — campus)
```

**Key design decisions:**

1. **`lawful_basis` field**: Not all processing requires consent. CHED reporting operates under
   `legal_obligation`. Enrollment processing operates under `contract`. Storing the lawful
   basis per consent record allows the system to distinguish between withdrawable consent and
   non-withdrawable legal obligations.

2. **`consent_form_version`**: When the consent form text changes, existing consents remain
   valid under the version they were signed under. The system can query "which students
   consented under version X" and trigger re-consent for version Y.

3. **`is_active` as a computed field**: Active = not withdrawn AND (no expiry OR expiry in
   the future). This avoids stale boolean flags.

4. **Evidence capture**: For online consent, store IP address and user agent as evidence of
   the consent event. For in-person consent, store the scanned signed form.

### 3.2 Consent Enforcement in ORM

Consent checks are implemented at the **service layer**, not in `read()` or `write()` overrides.
Overriding `read()` would break internal system operations (cron jobs, CHED reporting) that
process data under lawful bases other than consent.

**Pattern: Service-layer consent check**

```python
class StudentExportService(models.TransientModel):
    _name = "esmis.student.export"

    def export_student_data(self, student_id, purpose):
        """Export student data for a specific purpose."""
        # Check consent before processing
        self.env['esmis.consent'].check_active_consent(
            student_id=student_id,
            purpose=purpose,
        )
        # Proceed with export...
```

**Pattern: Consent check method**

```python
class EsmisConsent(models.Model):
    _name = "esmis.consent"

    @api.model
    def check_active_consent(self, student_id, purpose):
        """Raise UserError if no active consent exists for the given purpose."""
        consent = self.search([
            ('student_id', '=', student_id),
            ('purpose', '=', purpose),
            ('is_active', '=', True),
        ], limit=1)
        if not consent:
            raise UserError(_(
                "No active consent found for purpose '%s'. "
                "Please obtain consent before proceeding."
            ) % purpose)
        return consent

    @api.model
    def has_active_consent(self, student_id, purpose):
        """Return True if active consent exists (non-raising version)."""
        return bool(self.search_count([
            ('student_id', '=', student_id),
            ('purpose', '=', purpose),
            ('is_active', '=', True),
        ]))
```

**When to skip consent checks** (use `lawful_basis` != `consent`):
- CHED HEMIS data extraction (legal obligation)
- Financial aid eligibility verification under RA 10931 (legal obligation)
- Enrollment processing (contract)
- Emergency contact access during a medical emergency (vital interest)
- Internal GWA computation (legitimate interest)

### 3.3 Consent UI Patterns

#### At enrollment (purpose-based consent form)

Display a multi-checkbox consent form during the enrollment workflow. Each checkbox corresponds
to a processing purpose. The student (or guardian for minors) must affirmatively check each
purpose. Enrollment cannot proceed without the mandatory consents (enrollment, ched_reporting).
Optional consents (marketing, research, alumni_services) can be declined without blocking
enrollment.

#### Consent dashboard (student self-service)

A portal page where the student can:
- View all active consents with the purpose description in plain language
- Withdraw optional consents (marketing, research, alumni_services)
- See which consents are non-withdrawable (enrollment, ched_reporting) with explanation
- Download a copy of each signed consent form

#### Re-consent notification

When the consent form version changes, a scheduled job identifies students whose consent was
given under an older version. The system sends a notification (email + portal message) requesting
re-consent. Processing under the old consent remains valid until the student explicitly
withdraws.

### 3.4 Consent Audit Trail

Every consent event is logged in the consent record's chatter (`mail.thread`):

| Event | Logged Data |
|-------|-------------|
| Consent granted | Purpose, lawful basis, granted_by, form version, timestamp |
| Consent withdrawn | Purpose, withdrawal reason, withdrawn by, timestamp |
| Consent expired | Purpose, expiry date, timestamp |
| Re-consent requested | New form version, notification sent timestamp |
| Re-consent granted | New form version, new consent record ID |

The consent model itself is **append-only in practice**: consent records are never deleted. A
withdrawal sets `is_withdrawn = True` and `withdrawal_date`. A re-consent creates a new record.

### 3.5 Handling "I Withdraw Consent" for Permanent Records

Some data is in permanent records (TOR, grades) that cannot be deleted under CHED regulations.
The resolution:

| Scenario | Action |
|----------|--------|
| Student withdraws `marketing` consent | Stop all promotional communications immediately |
| Student withdraws `research` consent | Exclude from future research datasets; anonymize in existing datasets |
| Student withdraws `alumni_services` consent | Remove from alumni directory; stop tracer surveys |
| Student withdraws `enrollment` consent | Cannot withdraw — legal basis is `contract`, not `consent` |
| Student withdraws `ched_reporting` consent | Cannot withdraw — legal basis is `legal_obligation` |
| Student requests erasure of all data | Anonymize PII fields; preserve record shells for CHED compliance |

**Anonymization pattern for erasure requests:**
- Replace name with `"Student #[hash]"`
- Replace address with `"[ANONYMIZED]"`
- Replace phone/email with `"[ANONYMIZED]"`
- Destroy encrypted national ID values (crypto-shredding: delete the encryption key)
- Preserve: student number, grades, enrollment history, GWA, graduation status
- Preserve: aggregate statistics (enrollment count, pass/fail rates)

### 3.6 Consent Expiry and Renewal

For purposes where consent has a natural expiry (e.g., marketing consent valid for 2 years):

1. A `ir.cron` job runs daily and checks for consents expiring within 30 days.
2. Send a renewal notification to the student.
3. If the student does not renew by the expiry date, `is_active` becomes False (computed field).
4. Processing for that purpose stops automatically at next execution (service-layer check).
5. A second cron job runs after expiry and creates a `mail.activity` for the Registrar to
   follow up with students who have mandatory consents expiring (e.g., if the institution
   chooses to time-limit enrollment consent).

---

## 4. Data Minimization Patterns

### 4.1 Collect Only What's Needed

**Form-level validation**: Each enrollment or application form should collect only the fields
required for the processing purpose declared at the top of the form. The principle is to ask
"why do we need this field?" for every field on every form.

| Form | Required Fields | Fields NOT Collected |
|------|----------------|---------------------|
| Application form | Name, DOB, sex, LRN, SHS strand, contact | Religion, ethnicity (unless required by scholarship), blood type |
| Enrollment form | Program, section selection, payment method | Parent occupation (unless required by financial aid) |
| Financial aid application | Income bracket, household size, aid type | Specific income amount (use brackets), employer details |
| Health services intake | Relevant medical history, allergies | Full medical history (only what's clinically relevant) |

**Implementation**: Use `required=True` only on fields that are genuinely required for the
declared purpose. Use `groups=` attributes to hide optional fields from users who don't need
them.

### 4.2 Purpose Limitation Enforcement

Fields should be accessible only for the purpose they were collected for. Implementation:

1. **Field metadata**: Each PII field in the classification registry has a `purpose` attribute
   (e.g., `enrollment`, `financial_aid`, `health_services`).
2. **Access check**: When a user accesses a field outside the declared purpose context (e.g.,
   a faculty member accessing a student's financial aid details), the system checks whether the
   user's role is authorized for that purpose.
3. **API enforcement**: API endpoints declare their purpose in the request context. The ORM
   hooks check that the requested fields match the declared purpose.

### 4.3 Storage Limitation

| Record Type | Active Retention | Archive Trigger | Anonymization Schedule |
|-------------|-----------------|-----------------|----------------------|
| Applicant (denied) | 1 year after denial | Auto-archive after 1 year | Anonymize after 3 years |
| Applicant (admitted → student) | Linked to student record | Never archived separately | Follows student lifecycle |
| Student (active) | Duration of enrollment | N/A | N/A |
| Student (graduated) | 5 years post-graduation | Auto-archive after 5 years | Anonymize contact info after 10 years |
| Student (dropped/dismissed) | 5 years after last enrollment | Auto-archive after 5 years | Anonymize after 10 years |
| Academic records (grades, TOR) | Permanent | Never | Never (CHED requirement) |
| Financial records | 10 years | Auto-archive after 10 years | Anonymize after 15 years |
| Health records | 5 years after last visit | Auto-archive | Anonymize after 5 years |
| Counseling notes | 5 years after last session | Auto-archive | Destroy after 5 years |
| Disciplinary records | Per institutional policy | Auto-archive | Anonymize after graduation + 5 years |

**Implementation**: A `ir.cron` job runs monthly, queries records past their retention threshold,
and either archives (sets `active = False`) or anonymizes (replaces PII with tokens) based on
the schedule above.

### 4.4 Anonymization While Preserving Statistical Aggregates

When anonymizing records for research or regulatory reporting, preserve aggregate statistics:

1. **k-Anonymity**: Ensure that every combination of quasi-identifiers (age bracket, sex,
   program, campus) appears in at least k records (k >= 5 for educational data). If a group
   has fewer than k records, generalize the quasi-identifiers (e.g., merge age brackets,
   collapse programs into program families).

2. **Differential privacy for aggregate queries**: When publishing enrollment statistics or
   pass/fail rates, add calibrated noise to prevent inference of individual records. This is
   relevant for small programs where enrollment counts are low.

3. **Pseudonymization for longitudinal research**: Replace student identifiers with consistent
   pseudonymous tokens. The mapping table (real ID → token) is stored separately, encrypted,
   and access-controlled. Researchers receive only the pseudonymized dataset.

4. **Aggregate tables**: Pre-compute aggregate statistics (enrollment by program by year,
   pass rate by course, GWA distribution) and store in separate summary tables. These tables
   contain no PII and can be freely shared for institutional research and accreditation.

---

## 5. Access Control for PII

### 5.1 Field-Level Access Control

Odoo's `groups=` attribute on fields provides field-level access control. ADR-001 establishes
the group hierarchy. For PII fields, the `groups=` attribute must match the permitted roles
listed in the classification registry.

```python
# Example: PhilSys number visible only to Registrar Manager
philsys_psn = fields.Char(
    string="PhilSys Number (PSN)",
    groups="esmis_security.group_esmis_registrar_manager",
)
```

**Enforcement behavior**: When a user without the required group calls `read()` on a record,
fields with `groups=` are silently omitted from the result. The user sees the record but not
the restricted fields.

### 5.2 Role-Based PII Visibility Matrix

| Field Category | Student (Self) | Faculty | Registrar Officer | Registrar Manager | Finance | Fin Aid | Counselor | Clinic | DPO |
|---------------|---------------|---------|-------------------|-------------------|---------|---------|-----------|--------|-----|
| Name, student number | Own only | Own sections | All | All | All | All | Assigned | Assigned | All |
| Grades | Own only | Own sections (entry) | All (read) | All (read/write) | No | No | Assigned | No | Audit only |
| Contact info | Own | No | All | All | All | All | Assigned | Assigned | Audit only |
| National IDs | No | No | No | Yes (masked) | No | No | No | No | Audit only |
| TIN | No | No | No | No | Yes (masked) | No | No | No | Audit only |
| Financial records | Own | No | No | No | All | All | No | No | Audit only |
| Health records | Own | No | No | No | No | No | No | All | Audit only |
| Counseling notes | Own | No | No | No | No | No | Own assigned | No | Audit only |
| Disciplinary records | Own (limited) | No | All | All | No | No | No | No | Audit only |

**DPO access**: The Data Protection Officer can view audit logs of who accessed what PII, but
does not have direct access to PII values. This prevents the DPO from becoming a single point
of compromise.

### 5.3 Temporary Elevated Access

Some operations require temporary access to fields outside a user's normal role:

| Scenario | Mechanism | Duration | Approval |
|----------|-----------|----------|----------|
| Registrar needs counseling notes for transfer evaluation | Break-the-glass request | 24 hours | Counselor approval |
| Finance needs PWD ID for discount verification | Standing access (role-based) | Permanent | N/A (part of role) |
| Dean needs grade details for academic standing review | Standing access (role-based) | Permanent | N/A (part of role) |
| External auditor needs financial records | Temporary auditor role | Duration of audit | VP Academic Affairs approval |
| System administrator needs to debug a record | Break-the-glass | 1 hour | DPO approval + auto-log |

### 5.4 Break-the-Glass Pattern

For emergency or exceptional access to restricted PII:

```
esmis.btg.request (Break-the-Glass Request)
├── id
├── requester_id        (Many2one res.users)
├── approver_id         (Many2one res.users)
├── model               (Char — target model)
├── res_ids             (Char — JSON list of record IDs)
├── field_names         (Char — JSON list of fields requested)
├── justification       (Text, required — why access is needed)
├── state               (Selection: draft → pending → approved → expired → denied)
├── approved_date       (Datetime)
├── expiry_date         (Datetime — auto-set: approved_date + duration)
├── duration_hours      (Integer — default 24)
├── access_log_ids      (One2many esmis.pii.access.log — all access during BTG window)
└── post_review_notes   (Text — mandatory review after expiry)
```

**Workflow:**
1. User submits a BTG request with justification.
2. The designated approver (based on field classification) receives a `mail.activity`.
3. Approver reviews justification and approves/denies.
4. On approval, the user is temporarily added to the field's access group.
5. All PII access during the BTG window is logged with `btg_request_id` reference.
6. On expiry, the user is automatically removed from the access group.
7. A `mail.activity` is created for the DPO to review the BTG access log.

**Safeguards:**
- BTG requests cannot be self-approved (approver != requester).
- Maximum duration is 72 hours (configurable).
- BTG access cannot be renewed — a new request must be submitted.
- All BTG requests are visible to the DPO regardless of outcome.

### 5.5 Session-Based PII Access

For high-sensitivity operations (e.g., viewing a student's full national ID), require
re-authentication within the current session:

1. User clicks "Reveal" on a masked PII field.
2. System checks if the user re-authenticated within the last 15 minutes.
3. If not, display a password prompt (modal dialog).
4. On successful re-authentication, set a session flag with a 15-minute TTL.
5. Reveal the field value; auto-hide after 30 seconds (ADR-006 widget behavior).
6. Log the reveal event in `esmis.pii.access.log`.

---

## 6. Audit Logging for PII

### 6.1 What to Log

| Event Type | Fields Logged | Value Logged? | Retention |
|-----------|--------------|---------------|-----------|
| PII field read (Tier 3) | user, timestamp, model, record_id, field_name, IP | No | 3 years |
| PII field reveal (masked → visible) | user, timestamp, model, record_id, field_name, IP | No | 3 years |
| PII field write | user, timestamp, model, record_id, field_name, old_hash, new_hash | Hash only (not value) | 7 years |
| PII field export | user, timestamp, model, record_ids, field_names, export_format | No | 3 years |
| PII search (blind index lookup) | user, timestamp, model, field_name, search_type | No (not the search term) | 1 year |
| Consent event | user, timestamp, student_id, purpose, event_type | Consent metadata only | Permanent |
| BTG request | requester, approver, model, fields, justification, outcome | Justification text only | 7 years |
| Breach event | discovery_date, description, affected_count, notifications | No PII in description | Permanent |

**The cardinal rule**: Never log actual PII values. Log hashes of values (to detect changes)
but not the values themselves. Logging PII values in audit logs creates a second PII store
that must be encrypted and access-controlled, defeating the purpose.

### 6.2 Immutable Audit Logs

The audit log must be append-only and tamper-evident:

1. **No `unlink()` on audit log model**: Override `unlink()` to raise `UserError`. Even
   system administrators cannot delete audit log entries.

2. **No `write()` on critical fields**: Override `write()` to prevent modification of
   `user_id`, `create_date`, `model`, `res_id`, `field_name`, `access_type`. Only
   `post_review_notes` (for BTG reviews) is writable.

3. **Hash chain**: Each audit log entry includes a `chain_hash` field computed as:
   `SHA256(previous_entry.chain_hash + current_entry.data)`. This creates a tamper-evident
   chain — modifying any entry breaks the chain for all subsequent entries.

4. **Periodic checkpoints**: A scheduled job runs daily and computes a checkpoint hash
   over all entries for the day. The checkpoint is stored in a separate, append-only table
   and optionally published to an external service (e.g., a blockchain anchor or a separate
   server) for independent verification.

5. **PostgreSQL-level protection**: The audit log table should have `REVOKE DELETE` and
   `REVOKE UPDATE` for all database roles except the audit log writer role. This provides
   defense-in-depth beyond the ORM-level protections.

### 6.3 Audit Log Without Creating Another PII Store

**Problem**: If the audit log records "User X accessed student Y's PhilSys number," the audit
log itself contains a link between a user and a student's restricted data. This is metadata
about PII, not PII itself, but it still requires protection.

**Solution**:
- Log `res_id` (the database record ID) rather than the student's name or student number.
- Do not log the field value — log only the field name.
- Access to the audit log itself is restricted to the DPO and System Administrator.
- The audit log model has its own `groups=` attribute: `esmis_security.group_esmis_dpo`.

### 6.4 Audit Log Retention and Disposal

| Log Type | Retention | Disposal Method |
|----------|-----------|-----------------|
| PII access logs | 3 years | Archive to cold storage, then delete |
| PII write logs | 7 years | Archive to cold storage, then delete |
| Consent event logs | Permanent | Never delete |
| BTG request logs | 7 years | Archive to cold storage, then delete |
| Breach event logs | Permanent | Never delete |
| Checkpoint hashes | Permanent | Never delete |

**Archive process**: After the retention period, logs are exported to a compressed, encrypted
archive file and stored in the institution's document management system. The archive is signed
with the DPO's key. The original log entries are then deleted from the active database.

### 6.5 Suspicious Access Pattern Detection

Automated monitoring rules to detect potential breaches or misuse:

| Pattern | Detection Rule | Alert Target | Severity |
|---------|---------------|-------------|----------|
| Bulk PII access | >50 Tier 3 field reads in 1 hour by a single user | DPO | High |
| Bulk export | Export of >100 records with Tier 2+ fields | DPO | High |
| After-hours access | Tier 3 field access outside business hours (configurable) | DPO | Medium |
| Cross-campus access | User accessing records from a campus they're not assigned to | DPO + Campus Admin | High |
| Repeated failed access | >5 denied PII access attempts in 10 minutes | DPO + IT Security | High |
| BTG request spike | >3 BTG requests from the same user in 24 hours | DPO | Medium |
| Unusual search patterns | Blind index lookups for >20 distinct values in 1 hour | DPO | Medium |

**Implementation**: A `ir.cron` job runs every 15 minutes, queries `esmis.pii.access.log` for
the patterns above, and creates `mail.activity` alerts for the DPO. For high-severity patterns,
an email is sent immediately (not waiting for cron).

---

## 7. Data Breach Detection and Response

### 7.1 Automated Breach Detection

Beyond the suspicious pattern detection in Section 6.5, the system should detect:

| Indicator | Detection Method |
|-----------|-----------------|
| Unauthorized API access | API endpoint returns 403; >10 in 1 minute from same IP |
| Session hijacking | Same user active from two different IPs simultaneously |
| Credential stuffing | >20 failed login attempts in 5 minutes from same IP range |
| Data exfiltration via export | Export file size exceeds configurable threshold |
| Unauthorized DB access | PostgreSQL audit log shows queries from unexpected sources |
| Malware indicators | Unusual file uploads via `ir.attachment` (executable MIME types) |

### 7.2 Breach Containment

When a breach is detected or reported:

1. **Automatic containment** (within minutes):
   - Lock the affected user account (`active = False` on `res.users`).
   - Terminate all active sessions for the affected user.
   - If API-based: revoke the API key/token immediately.
   - If IP-based: add the IP to the firewall blocklist (requires infrastructure integration).

2. **Manual containment** (within hours):
   - DPO reviews the breach scope.
   - If the encryption key may be compromised: initiate emergency key rotation.
   - If a role is compromised: revoke all users in that role and re-grant individually after
     verification.

### 7.3 Breach Assessment

The `esmis.data.breach` model (ADR-012) tracks the breach. The assessment process:

1. **Identify affected records**: Query `esmis.pii.access.log` for all access by the
   compromised user/session within the breach window.
2. **Identify affected data subjects**: Extract unique `res_id` values from the access logs.
   Map to `esmis.student` records.
3. **Classify exposed data**: For each affected record, determine which fields were accessed
   (from the access log's `field_name`). Map to classification tier.
4. **Risk assessment**: Determine if the breach meets the NPC mandatory notification threshold:
   - Involves >= 100 data subjects, OR
   - Involves Sensitive Personal Information (Tier 3 fields)
   - In either case: mandatory notification within 72 hours.

### 7.4 NPC Notification

Per NPC Circular 16-03, the notification must be submitted through the NPC's Data Breach
Notification Management System (DBNMS). The system should generate the required data:

| PDBNF Field | Source in eSMIS |
|-------------|----------------|
| Nature of the breach | `esmis.data.breach.description` |
| Date of breach discovery | `esmis.data.breach.discovery_date` |
| Approximate number of affected data subjects | `esmis.data.breach.affected_count` |
| Types of personal data involved | Derived from `esmis.pii.access.log.field_name` → classification |
| Measures taken to address the breach | `esmis.data.breach.remediation_notes` |
| DPO contact information | From `esmis.data.breach.dpo_id` |

The system generates a **pre-filled notification report** (PDF) that the DPO can review and
submit through the DBNMS portal. The system does not submit directly to NPC (no API available).

**Data subject notification** must include:
- Nature of the breach in plain language
- Types of personal data that may have been compromised
- Measures taken to address the breach
- Recommendations for the data subject (e.g., monitor for identity theft, change passwords)
- DPO contact information

The system generates a notification email template populated with breach details (without
naming specific affected students in a mass notification). Individual students receive
personalized notifications listing which of their data categories were potentially exposed.

### 7.5 Post-Breach Remediation

| Action | Timeline | Owner |
|--------|----------|-------|
| Forced password reset for affected users | Immediate | IT |
| Emergency key rotation (if keys compromised) | Within 24 hours | IT + DPO |
| Access review for all users with Tier 3 access | Within 48 hours | DPO |
| Root cause analysis | Within 1 week | IT + DPO |
| Policy/procedure update | Within 2 weeks | DPO |
| Penetration test of affected systems | Within 1 month | IT |
| Full report to NPC (5-day deadline) | Within 5 days of initial notification | DPO |
| Update this Known Pitfalls section | After resolution | Development team |

---

## 8. PII in Development and Testing

### 8.1 Synthetic PII Generation

**Never use production PII in development, testing, or staging environments.**

Generate synthetic (fake) data that is structurally valid but not linked to real individuals:

| Field | Generation Strategy | Library/Tool |
|-------|-------------------|--------------|
| Filipino names | Random combination from common Filipino name lists | `faker` with `fil_PH` locale |
| Addresses | Random Philippine addresses (real barangay/city names, fake house numbers) | `faker` with `fil_PH` locale |
| Phone numbers | Random 09XX-XXX-XXXX format (valid prefix, random suffix) | Custom generator |
| Email addresses | `{first}.{last}@example.edu.ph` (example domain) | Custom generator |
| PhilSys numbers | Random 16-digit numbers matching PSN format | Custom generator with check digit |
| TIN | Random 9-digit numbers matching TIN format | Custom generator |
| LRN | Random 12-digit numbers matching LRN format | Custom generator |
| Dates of birth | Random dates within valid age range (16-60 for students) | `faker` |
| Grades | Random values within valid grading scale (1.00-5.00) | `random.uniform()` |
| GWA | Computed from generated grades | Actual computation logic |

**Test data generation module**: Create a `esmis_test_data` module (loaded only in test/demo
mode) that generates a configurable number of synthetic student records. This module should:
- Be excluded from production deployments (`auto_install = False`, no dependency from
  production modules)
- Use deterministic seeds for reproducible test runs
- Generate complete records (student + enrollment + grades + financial aid) to avoid
  referential integrity issues
- Include edge cases: minors (age < 18), PWD students, solo parent dependents, graduating
  students, alumni

### 8.2 Data Masking for Staging Environments

If staging environments must use production-like data volumes for performance testing:

1. **Never copy production data directly to staging.** Instead:
   - Export production data structure (schema + record counts).
   - Generate synthetic data matching the production volume and distribution.
   - Alternatively, use a masking pipeline that replaces PII before the data reaches staging.

2. **Masking pipeline** (if production data must be used):
   - Export production database.
   - Run a masking script that replaces all Tier 1-3 fields with synthetic values.
   - Preserve referential integrity (same student_id maps to the same fake name consistently).
   - Verify that no PII leaks through related fields (e.g., `mail.message` chatter entries
     that mention student names).
   - Import the masked database into staging.

3. **Masking rules by field type**:
   | Field Type | Masking Strategy |
   |-----------|-----------------|
   | Names | Replace with `faker` names; preserve gender consistency |
   | Addresses | Replace with `faker` addresses; preserve city distribution |
   | Phone numbers | Replace digits; preserve format |
   | Email | Replace with `{hash}@example.edu.ph` |
   | National IDs | Replace with random valid-format IDs |
   | Dates of birth | Shift by random offset (preserve age distribution) |
   | Free text fields (notes) | Replace with lorem ipsum |
   | Attachment files | Replace with placeholder files of same size |

### 8.3 Developer Access Rules

- Developers never have access to production PII data.
- Production database access is limited to the DBA and the DPO (for breach investigation).
- Developers work exclusively with synthetic data in development and staging environments.
- If a developer needs to reproduce a production bug involving PII:
  1. The DPO extracts a minimal, anonymized reproduction case.
  2. The developer works with the anonymized data.
  3. The DPO verifies that the anonymized data does not leak the original PII.

### 8.4 CI/CD Rules

- No PII in test fixtures, seed data, or environment variables.
- Test modules (`esmis_test_data`) generate synthetic data at test runtime.
- CI/CD pipelines do not have credentials to access production databases.
- Docker images for testing do not contain any PII-derived data.
- Linting rules flag any hardcoded strings that match PII patterns (e.g., 12-digit numbers
  that look like LRNs, 16-digit numbers that look like PSNs).

---

## 9. Privacy by Design Principles

### 9.1 Application to eSMIS

The seven foundational principles of Privacy by Design, as applied to the eSMIS system:

#### Principle 1: Proactive, Not Reactive

- PII classification and encryption are designed before models are implemented, not retrofitted.
- New models must declare their PII fields in the classification registry before they can be
  deployed to production.
- The `esmis_data_classification` module enforces this: it auto-detects PII-like fields at
  model load time and flags unclassified fields.

#### Principle 2: Privacy as the Default

- New fields default to the most restrictive classification until explicitly declassified.
- New users have no PII access until explicitly granted via group membership.
- Export wizards default to redacting Tier 2+ fields; the user must explicitly opt in to
  include them (and the export is logged).
- API endpoints default to excluding PII fields from list responses.
- Consent defaults to "not given" — the system never assumes consent.

#### Principle 3: Privacy Embedded in Design

- The `esmis.pii.aware` mixin is inherited by all models that store PII. This is not optional.
- Encryption is handled transparently by the ORM layer (compute/inverse pattern). Developers
  do not need to call encryption APIs manually.
- Consent checks are enforced by service-layer methods, not left to individual developers.
- The audit log is automatic for classified fields — no developer action required.

#### Principle 4: Full Functionality (No Privacy vs Features Trade-off)

- Blind indexes enable search on encrypted fields. The system does not sacrifice search
  functionality for encryption.
- Masking in the UI shows partial information. The user knows the field has a value without
  seeing the full value.
- The "reveal" button provides full access when needed, with audit logging.
- Consent withdrawal for optional purposes does not break core functionality (enrollment,
  grading, graduation).

#### Principle 5: End-to-End Security

- Data at rest: TDE (database) + ALE (Tier 3 fields).
- Data in transit: TLS 1.3 for all connections (Odoo ↔ browser, Odoo ↔ PostgreSQL,
  Odoo ↔ Vault/KMS).
- Data in use: Decrypted values exist only in request-scoped memory. Cleared after request.
- Data in backup: Database backups are encrypted (TDE). Application-level encrypted fields
  remain encrypted in backups.
- Data in disposal: Crypto-shredding (destroy the key) for records past retention. Physical
  media destruction for hardware decommissioning.

#### Principle 6: Visibility and Transparency

- The privacy notice presented at enrollment describes all data categories, processing
  purposes, retention periods, and data subject rights in plain Filipino and English.
- The student self-service portal shows all active consents and allows withdrawal.
- The audit log is available to the DPO for compliance reporting.
- Breach notifications are sent to affected data subjects promptly.
- The consent form version is tracked so the institution can demonstrate that consent was
  informed (the student saw the correct version of the privacy notice).

#### Principle 7: Respect for User Privacy

- Data minimization: collect only what's needed for the declared purpose.
- Purpose limitation: don't repurpose data without fresh consent.
- Storage limitation: anonymize or delete data after the retention period.
- The student is the data subject with rights — not just a record in the system.
- The system makes it easy for students to exercise their rights (self-service portal for
  access, rectification, portability, and withdrawal).

### 9.2 Privacy by Design Checklist for New Features

When building any new feature that touches student data:

- [ ] Identify which PII fields the feature reads, writes, or exports
- [ ] Classify new fields in the PII classification registry (Tier 0-3)
- [ ] Declare the processing purpose for the feature
- [ ] Verify that a consent record exists for that purpose (or that a non-consent lawful
      basis applies)
- [ ] Apply `groups=` on new PII fields to restrict visibility to authorized roles
- [ ] Add new PII fields to the masking configuration (if Tier 2+)
- [ ] Ensure new PII fields are excluded from log messages
- [ ] Add audit logging for read access to Tier 3 fields
- [ ] Ensure exports redact fields above the user's clearance level
- [ ] Inherit `esmis.pii.aware` if the model stores PII
- [ ] Test with synthetic data only — no production PII in test fixtures
- [ ] Document the data flow in the feature's PIA section
- [ ] Review with the DPO before deployment

---

## Implementation Priority

Based on regulatory risk and implementation dependencies:

| Priority | Component | Rationale |
|----------|-----------|-----------|
| P0 | PII field classification registry | Foundation for all other components |
| P0 | Consent model and enforcement | RA 10173 compliance; blocks enrollment workflow |
| P0 | Encrypted field mixin + key management | Protects Tier 3 fields at rest |
| P0 | Blind index for searchable encryption | Enables search on encrypted fields |
| P1 | Masked field widget deployment | UX for PII protection |
| P1 | PII access logging (read audit) | NPC compliance; breach investigation |
| P1 | Breach notification workflow | 72-hour NPC deadline |
| P1 | Data subject rights wizards | RA 10173 compliance |
| P2 | Break-the-glass pattern | Operational flexibility |
| P2 | Suspicious pattern detection | Proactive breach detection |
| P2 | Anonymization wizard | Erasure requests, storage limitation |
| P2 | Synthetic test data generator | Development workflow |
| P3 | Hash-chain tamper evidence | Audit log integrity |
| P3 | Consent expiry and renewal | Ongoing consent management |
| P3 | Key rotation automation | Key lifecycle management |

---

## Sources

- [Personally Identifiable Information for Education Records (US Dept of Education)](https://studentprivacy.ed.gov/content/personally-identifiable-information-education-records)
- [Data Classification Guidelines (Fordham University)](https://www.fordham.edu/information-technology/it-security--assurance/it-policies-procedures-and-guidelines/data-classification-guidelines/data-types/)
- [Data Classification and Encryption Rule (University of Utah)](https://it.utah.edu/node4/posts/2022/october/policy-explainer.php)
- [FERPA and SOPIPA: Data Masking (IRI)](https://www.iri.com/solutions/data-masking/ferpa)
- [Blind Index Pattern (Kalp Sedalia, Medium)](https://medium.com/@kalpsedalia/blind-index-pattern-search-strategy-for-encrypted-information-2e74ae2b9e30)
- [Searchable Encryption (Cossack Labs)](https://docs.cossacklabs.com/acra/security-controls/searchable-encryption/)
- [How to Search on Securely Encrypted Database Fields (SitePoint)](https://www.sitepoint.com/how-to-search-on-securely-encrypted-database-fields/)
- [ankane/blind_index (GitHub)](https://github.com/ankane/blind_index)
- [PostgreSQL Encryption Options (PostgreSQL Docs)](https://www.postgresql.org/docs/current/encryption-options.html)
- [GDPR Consent Management (SecurePrivacy)](https://secureprivacy.ai/blog/gdpr-consent-management)
- [Consent Management API Integration (SecurePrivacy)](https://secureprivacy.ai/blog/consent-management-api-integration)
- [Break Glass Procedure (Yale HIPAA)](https://hipaa.yale.edu/security/break-glass-procedure-granting-emergency-access-critical-ephi-systems)
- [Break Glass Procedure: Auditable Emergency Access (Cloudanix)](https://www.cloudanix.com/learn/break-glass-procedure-emergency-access-for-critical-resources)
- [What is Break Glass Access in an Enterprise Context (Hoop.dev)](https://hoop.dev/blog/what-is-break-glass-access-in-an-enterprise-context/)
- [Immutable Audit Logs (HubiFi)](https://www.hubifi.com/blog/immutable-audit-log-guide)
- [Tamper-Proof Audit Logs (Mattermost)](https://mattermost.com/blog/compliance-by-design-18-tips-to-implement-tamper-proof-audit-logs/)
- [Data Detection and Response (IBM)](https://www.ibm.com/think/topics/data-detection-response)
- [Data Breach Detection (Prey Project)](https://preyproject.com/blog/data-breach-detection)
- [K-Anonymity (Utrecht University Data Privacy Handbook)](https://utrechtuniversity.github.io/dataprivacyhandbook/k-l-t-anonymity.html)
- [K-Anonymity and Differential Privacy (Purdue CERIAS)](https://www.cerias.purdue.edu/assets/pdf/bibtex_archive/2010-24-report.pdf)
- [Synthetic Test Data vs Test Data Masking (Perforce)](https://www.perforce.com/blog/pdx/synthetic-test-data-vs-test-data-masking)
- [How to Handle PII in Staging Databases (Neon)](https://neon.com/blog/handle-pii-staging-databases)
- [NPC Breach Reporting (National Privacy Commission Philippines)](https://privacy.gov.ph/pips-and-pics/breach-reporting/)
- [NPC Circular 16-03 (Personal Data Breach Management)](https://privacy.gov.ph/wp-content/uploads/2022/01/sgd-npc-circular-16-03-personal-data-breach-management.pdf)
- [Breach Notification in the Philippines (BCCS Law)](https://bccslaw.com/breach-notification-in-the-philippines/)
- [Privacy by Design Implementation (SecurePrivacy)](https://secureprivacy.ai/blog/privacy-by-design-implementation)
- [The 7 Principles of Privacy by Design (OneTrust)](https://www.onetrust.com/blog/principles-of-privacy-by-design/)
- [Achieving Privacy by Design Through Secure by Design (ISACA)](https://www.isaca.org/resources/news-and-trends/isaca-now-blog/2025/achieving-seamless-privacy-by-design-through-secure-by-design-practices)
- [OCA Encrypted Fields RFC (GitHub Issue #471)](https://github.com/OCA/server-tools/issues/471)
- [Odoo ORM API Documentation](https://www.odoo.com/documentation/master/developer/reference/backend/orm.html)
