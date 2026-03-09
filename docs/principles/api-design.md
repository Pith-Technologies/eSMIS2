# API Design Principles

Standards for building APIs in {Project}.

## Core Principles

1. **External Identifiers Only** - Never expose internal database IDs
2. **Standards-Based** - Use well-known standards for interoperability
3. **Field Filtering** - Control which fields are returned per endpoint
4. **Versioned** - Explicit versioning with deprecation periods

## External Identifier Rule (Critical)

**NEVER expose internal database IDs for cross-system integration.**

```python
# WRONG - exposes internal ID
{
    "id": 12345,
    "name": "Jane Smith"
}

# CORRECT - uses external identifiers
{
    "identifier": [
        {"name": "National ID", "identifier": "US-123456789"},
        {"name": "Tax ID", "identifier": "12-3456789"}
    ],
    "name": "Jane Smith"
}
```

**Why:** Integrated systems require stable, external IDs for cross-system references.

## Use `tpl.identifier` for All Identifiers

```python
# Single system for flexible + external IDs
tpl.vocabulary.code  # Configuration: identifier types (National ID, Tax ID, etc.)
tpl.identifier       # Storage: partner_id, type_id, system_uri, value
res.partner.identifier_ids → Many tpl.identifier records
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
@route('/api/v2/tpl/contacts/<id>')
```

## Namespace Convention

All APIs use the `tpl.*` namespace:

- Models: `tpl.{domain}` or `tpl.{domain}.{entity}`
- REST mixins: `tpl.process.individual.rest.mixin`, `tpl.process.group.rest.mixin`

## Field Filtering

Use `tpl.api.path` model for configuration:

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
- Audit logging via `tpl_api.log`

---

**Authoritative Sources:**
- Architecture documentation for API-First design philosophy

**See also:** [Module Architecture](module-architecture.md), [Access Rights](access-rights.md)
