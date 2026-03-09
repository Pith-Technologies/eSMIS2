Security infrastructure for eSMIS — security groups and cross-cutting
abstract mixins required by all domain modules.

### Abstract Mixins

- **esmis.pii.aware** — Field-level PII classification and masking.
- **esmis.campus.aware** — Campus isolation via `company_id`.
- **esmis.audit.mixin** — Soft delete, legal hold, and archival tracking.
- **esmis.retention.aware** — Lightweight legal hold for retention-managed records.

### Security Groups

- **Security** — Viewer / Officer / Manager hierarchy
- **Data Protection Officer** — Breach, DSAR, legal hold, disposal reviews
- **Audit** — Viewer / Officer hierarchy
- **System-wide roles** — VP Academic, President, CHED Reporter

### Extension Points

- Override `_pii_fields` on `esmis.pii.aware` to classify fields
- Each campus-aware model defines its own record rule for isolation

### Dependencies

- `base` — Odoo core
- `mail` — Chatter integration
- `esmis_vocabulary` — Controlled vocabularies
