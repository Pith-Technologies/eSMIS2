# API Design Principles

Standards for building APIs in eSMIS.

## Core Principles

1. **Stable Identifiers Only** - Never expose internal database IDs; use `esmis.identifier` records or XML IDs
2. **Standards-Based** - Use well-known standards for interoperability
3. **Field Filtering** - Control which fields are returned per endpoint
4. **Versioned** - Explicit versioning with deprecation periods

## Stable Identifier Rule (Critical)

**NEVER expose internal database IDs in API responses.**

Use `esmis.identifier` records (government IDs like PhilSys, TIN, LRN) as stable, cross-system identifiers. Do not confuse these with Odoo's "external identifiers" (`ir.model.data` XML IDs), which are a separate concept used internally for data records.

```python
# WRONG - exposes internal DB ID
{
    "id": 12345,
    "name": "Jane Smith"
}

# CORRECT - uses esmis.identifier records (government/institutional IDs)
{
    "identifier": [
        {"name": "National ID", "identifier": "US-123456789"},
        {"name": "Tax ID", "identifier": "12-3456789"}
    ],
    "name": "Jane Smith"
}
```

**Why:** Integrated systems require stable identifiers for cross-system references. Database IDs are internal and may change across environments.

## Use `esmis.identifier` for All Identifiers

```python
# Single system for flexible government/institutional IDs
esmis.vocabulary.code  # Configuration: identifier types (National ID, Tax ID, etc.)
esmis.identifier       # Storage: partner_id, type_id, system_uri, value
res.partner.identifier_ids → Many esmis.identifier records
```

## API Response Pattern

```json
{
    "identifier": [...],
    "givenName": "Jane",
    "familyName": "Smith",
    "birthDate": "1990-01-15"
}
```

## Versioning

- Path-based: `/api/v1/`, `/api/v2/`
- 6-month compatibility period for deprecated endpoints
- Deprecation warnings in response headers

```python
@route('/api/v2/esmis/contacts/<id>')
```

## Namespace Convention

All APIs use the `esmis.*` namespace:

- Models: `esmis.{domain}` or `esmis.{domain}.{entity}`
- REST mixins: `esmis.process.individual.rest.mixin`, `esmis.process.group.rest.mixin`

## Field Filtering

Use `esmis.api.path` model for configuration:

```
API Path → field_ids → Only these fields returned
        → filter_domain → Which records accessible
        → limit → Max records per request
```

## Supported Standards

| Standard | Purpose |
|----------|---------|
| REST/JSON | Standard API format |
| OpenID VCI | Verifiable credentials |

## Authentication

- OAuth 2.0 for external APIs
- API keys with scoped permissions
- Audit logging via `esmis_api.log`

## Government System API Patterns

### PhilSys (Philippine Identification System)

Two integration modes:

- **Offline QR**: Validate EdDSA signature on scanned QR using the PSA public key. No network call required.
- **Online eVerify**: REST API call to PSA for biometric verification. Requires approved MOA and PSA-issued credentials.

Store PSN (PhilSys Number) as an `esmis.identifier` record (not as a raw field). Credentials (API keys, PSA public key) go in `ir.config_parameter`, never in source code.

### CHED (Commission on Higher Education)

No public API. Integration is export-only:

- **HEMIS forms**: Export to Excel in the prescribed layout. Build `esmis.export.wizard` models, not API clients.
- **eCAV (web portal)**: Manual upload. Provide a downloadable file with validation before export.

### UniFAST / TES (Tertiary Education Subsidy)

Portal-based file upload only. Export eligible student lists in the prescribed format. Integration requires a signed MOA before access is granted.

### General Pattern for Portal-Based Systems

Create `esmis.export.wizard` models that:

1. Validate data before generating the file (report errors to the user, not silently)
2. Generate a downloadable file in the required format (Excel, CSV, fixed-width)
3. Log the export event (timestamp, user, record count) for audit purposes

## LMS Integration Standards

eSMIS acts as the **Tool Platform**; the LMS acts as the **Tool**.

| Standard | Purpose |
|----------|---------|
| LTI 1.3 | Tool launch and grade passback (OAuth2 / OIDC / JWT) |
| OneRoster 1.2 | Roster sync — students, teachers, sections, enrollments |
| AGS (Assignment and Grade Services) | Grade passback from LMS to eSMIS |

Implement roster sync as a scheduled action, not a real-time webhook, to avoid tight coupling.

## Payment Gateway Integration

Supported gateways: PayMongo, Maya, Dragonpay.

- **Authentication**: REST API with API key (stored in `ir.config_parameter`)
- **Payment confirmation**: Webhook-based async flow — never rely on redirect-only confirmation
- **Idempotency**: Pass idempotency keys when creating payment intents to prevent duplicate charges
- **Testing**: Sandbox environment required and must pass before any production credential is provisioned

## SIS-Specific API Resources

| Resource | Description |
|----------|-------------|
| `/students` | Student profiles, filterable by program, campus, and academic standing |
| `/enrollments` | Per-term enrollment records |
| `/sections` | Class sections with schedule and seat availability |
| `/grades` | Grade records — faculty submit, registrar approves |
| `/curricula` | Program curriculum with prerequisite graph |
| `/financial-aid` | Scholarship awards and eligibility status |

All resources follow the Stable Identifier Rule — no internal database IDs in responses.

---

**Authoritative Sources:**
- Architecture documentation for API-First design philosophy

**See also:** [Module Architecture](module-architecture.md), [Access Rights](access-rights.md)
