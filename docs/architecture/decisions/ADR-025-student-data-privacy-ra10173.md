# ADR-025: Student Data Privacy — RA 10173 Compliance

## Status

**Accepted** - Implementation pending

**Date:** 2026-03-09
**Decision Owners:** Core Team, Data Protection Officer

## Context

Republic Act 10173 (Data Privacy Act of 2012) and its Implementing Rules and Regulations (IRR) impose binding obligations on Higher Education Institutions as Personal Information Controllers (PICs). HEIs collect, process, and store large volumes of student personal data, including sensitive personal information (SPI) as defined under the Act.

### Data Categories in eSMIS

| Category | Classification | Examples |
|----------|---------------|---------|
| Directory information | Internal | Name, student number, course, year level |
| Contact information | Confidential | Home address, mobile number, email |
| Academic records | Confidential | Grades, academic standing, enrollment history |
| Financial records | Confidential | Tuition ledger, scholarship details, payment history |
| National identifiers | Restricted | PhilSys RN, TIN, SSS/GSIS number |
| Health information | Restricted | Medical certificate, PWD status, health history |
| Disciplinary records | Restricted | Violation records, sanctions, clearance holds |
| Biometric data | Restricted | Photo ID, fingerprint (where collected) |

### Regulatory Requirements

1. **Consent**: Explicit, informed, freely given consent required per processing purpose (Section 12, RA 10173)
2. **Purpose limitation**: Data collected for enrollment must not be used for unrelated purposes without fresh consent
3. **Data subject rights**: Right to be informed, access, rectification, erasure, portability, and object (Section 16)
4. **Minor protection**: Students under 18 require parental or guardian consent
5. **Breach notification**: NPC must be notified within 72 hours of discovery of a personal data breach (NPC Circular 16-03)
6. **Data Protection Officer**: HEI must appoint a DPO registered with the NPC
7. **Privacy Impact Assessment (PIA)**: Required before deploying new systems processing SPI
8. **Retention and disposal**: Records retained per CHED-prescribed schedules; disposal must be documented

### Gaps Without This ADR

Without a deliberate privacy architecture, the system would have no mechanism to track consent, no way to enforce purpose limitation programmatically, no structured breach notification workflow, and no data subject rights implementation. Each of these gaps is a regulatory violation.

## Decision

**Implement privacy as a cross-cutting architectural concern, not as a feature bolt-on.**

The implementation is built on five pillars, each corresponding to an existing ADR or new component:

### Pillar 1: Consent Management

A dedicated `esmis.consent` model tracks explicit consent per student per processing purpose:

```
esmis.consent
├── student_id         (Many2one esmis.student)
├── purpose            (Selection: enrollment, ched_reporting, financial_aid, emergency_contact, marketing, research)
├── consent_date       (Datetime)
├── expiry_date        (Datetime, optional)
├── is_withdrawn       (Boolean)
├── withdrawal_date    (Datetime)
├── granted_by         (Many2one res.partner — student or guardian)
├── minor_guardian_id  (Many2one res.partner — required when student age < 18 at consent_date)
└── evidence_file_id   (Many2one ir.attachment — signed form scan, optional)
```

Before any processing of SPI for a given purpose, the calling code must verify active consent using `esmis.consent.has_active_consent(student_id, purpose)`. This check is enforced in service-layer methods, not in `read()` overrides, to avoid breaking internal system operations that process data under a lawful basis other than consent (e.g., CHED reporting under a legal obligation basis).

### Pillar 2: Data Classification

All SPI fields are classified according to ADR-011's four-tier taxonomy (Public, Internal, Confidential, Restricted). Field-level classification is declared in model metadata and drives masking in list views and exports. No changes to ADR-011 are required; this ADR extends its application to student data specifically.

### Pillar 3: PII Encryption

National identifiers (PhilSys RN, TIN), health information fields, and disciplinary record summaries are encrypted at the application layer per ADR-012's strategy (Fernet encryption + blind index for searchable fields). Grades and financial ledgers are stored plaintext but access-controlled; they do not require encryption because they are not in the "Restricted" classification under the ADR-011 taxonomy.

### Pillar 4: Audit Trail

All read and write access to Confidential and Restricted fields is logged in the unified audit trail per ADR-020. Audit log entries include: user ID, timestamp, operation type, model, record ID, and field names accessed. No field values are logged (logging PII values would compound a breach). Audit logs are retained for 3 years per NPC recommendation.

### Pillar 5: Data Subject Rights

| Right | Implementation |
|-------|---------------|
| Right to be informed | Privacy notice presented and acknowledged during enrollment; stored as a consent record |
| Right of access | "Export my data" wizard in the student self-service portal generates a structured JSON/PDF export |
| Right to rectification | "Request correction" workflow creates a `mail.activity` assigned to the Registrar; changes are audit-logged |
| Right to erasure | Anonymization wizard replaces PII with pseudonymous tokens; referential integrity is preserved by retaining record shells with anonymized fields |
| Right to data portability | Same export wizard as right of access; output is machine-readable JSON following a published schema |
| Right to object | Consent withdrawal form sets `esmis.consent.is_withdrawn = True`; downstream processing checks are blocked at next execution |

### Minor Protection

The `esmis.consent` model enforces parental/guardian consent when the student's birthdate indicates age < 18 at the time of consent collection. The system calculates age dynamically and raises a `ValidationError` if a consent record is created for a minor without `minor_guardian_id`. Enrollment workflows check this condition before allowing a student to self-consent.

### Breach Notification Workflow

A `esmis.data.breach` model tracks detected breaches:

```
esmis.data.breach
├── name               (Char — internal reference)
├── discovery_date     (Datetime)
├── npc_deadline       (Datetime — computed: discovery_date + 72 hours)
├── description        (Text — non-PII description of the breach)
├── affected_count     (Integer — number of data subjects affected)
├── npc_notified       (Boolean)
├── npc_notification_date (Datetime)
├── dpo_id             (Many2one res.users — assigned DPO)
└── activity_ids       (One2many mail.activity)
```

On creation, a `mail.activity` is automatically created assigned to the DPO with a deadline of `npc_deadline`. The activity type is "NPC Breach Notification" with a 72-hour SLA. If the deadline passes without `npc_notified = True`, the system escalates via email to the system administrator group.

## Consequences

### Positive

- Full RA 10173 compliance at the architectural level, not as an afterthought
- Builds entirely on ADR-011 (data classification), ADR-012 (encryption), and ADR-020 (audit trail) — no new infrastructure required
- Consent records provide an auditable paper trail for NPC investigations
- Data subject rights are self-service where possible, reducing Registrar workload
- Minor protection is enforced by the system rather than depending on staff awareness
- The breach notification workflow ensures the 72-hour NPC deadline is tracked even during weekends or holidays

### Negative

- Consent checks in service-layer methods add a database query per SPI-processing operation; this must be benchmarked and cached where the consent status is stable within a transaction
- Anonymization for erasure requests is complex: financial records, grade transcripts, and disciplinary records have legal retention requirements that may override an erasure request; staff must evaluate each request individually
- The `esmis.consent` model must be populated retroactively for existing students on system migration; a data migration script and a bulk consent import wizard are required
- The `esmis_consent` mixin adds model complexity; developers must understand when to inherit it and when not to

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Consent check bypassed with `sudo()` | MEDIUM | HIGH | Code review rule: no `sudo()` in consent-check paths; enforced via pre-commit hook pattern scan |
| Breach not logged within 72 hours | LOW | HIGH | Automated activity creation + escalation email if deadline missed |
| Retroactive consent migration incomplete | HIGH | MEDIUM | Migration script includes coverage report; DPO reviews before go-live |
| Erasure request conflicts with legal retention | HIGH | MEDIUM | Anonymization wizard checks retention schedule before proceeding; legal hold flag blocks anonymization |
| Minor age check bypassed at consent creation | LOW | HIGH | `@api.constrains` on `esmis.consent` validates age; cannot be bypassed in normal ORM usage |

## Implementation Notes

1. **`esmis_consent` module**: The consent model, minor protection logic, and data subject rights wizards are implemented in a dedicated `esmis_consent` module that depends on `esmis_security`. Domain modules that process SPI add `esmis_consent` as a dependency.

2. **Consent check pattern**: Service-layer methods that process SPI for a specific purpose call:
   ```python
   self.env['esmis.consent'].check_active_consent(student_id, purpose)
   # Raises UserError if no active consent exists for the given purpose
   ```

3. **Mixin for PII models**: Models that store student PII inherit `esmis.consent.mixin`, which provides the `_check_consent_for_export()` hook called by export wizards.

4. **Audit trail integration**: The ADR-020 audit log hooks are extended to log access to fields tagged with `pii_classification` in `_fields` metadata. No changes to ADR-020's core model are needed.

5. **Breach notification escalation**: A scheduled action (`ir.cron`) runs hourly and checks for `esmis.data.breach` records where `npc_deadline < now()` and `npc_notified = False`. Matching records trigger an email to the `esmis_security.group_system_admin` group.

6. **No PII in logs**: The breach model's `description` field must describe the nature of the breach (e.g., "unauthorized access to grade records") without naming affected students. Affected students are tracked in a separate `esmis.data.breach.subject` relation.

7. **Retention schedule integration**: The anonymization wizard queries a configurable retention schedule (`esmis.retention.schedule`) before anonymizing any record. Records under a legal hold or within the mandatory retention period cannot be anonymized; the wizard informs the operator and skips those records.

## References

- [RA 10173 — Data Privacy Act of 2012](https://www.officialgazette.gov.ph/2012/08/15/republic-act-no-10173/)
- [NPC Circular 16-03 — Security Incident Notification](https://www.privacy.gov.ph/circular-16-03/)
- [NPC Advisory 2020-02 — Guidelines on Personal Data Breach Management](https://www.privacy.gov.ph/advisory-2020-02/)
- ADR-011: Data Classification System
- ADR-012: PII Encryption Strategy
- ADR-020: Unified API Audit Log
- ADR-022: API V2 Application-Level Authorization

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09 **Next Review:** Upon NPC issuance of HEI-specific advisory or amendment to RA 10173 IRR
