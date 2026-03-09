RA 10173 consent management for eSMIS — tracks per-partner, per-purpose
consent with lawful basis, evidence, and withdrawal audit trail.

### Key Models

- **esmis.consent** — Per-partner, per-purpose consent record. Tracks lawful
  basis, evidence, and withdrawal. Records are never deleted.
- **esmis.consent.scope** — Fine-grained scope definitions within a consent
  record (data categories, third parties, expiry dates).
- **esmis.consent.mixin** — Abstract mixin for models that need to check
  consent status before processing PII.

### Key Capabilities

- One active consent per partner per purpose (unique constraint)
- Consent withdrawal with full audit trail
- Evidence type enforcement for explicit consent
- Parent/guardian consent tracking for minors
- Export consent validation via `_check_consent_for_export()`

### Dependencies

- `base` — Odoo core
- `mail` — Chatter integration
- `esmis_security` — Security groups for ACLs
