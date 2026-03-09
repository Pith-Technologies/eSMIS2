# ADR-002: Namespace URIs for Identifier Types

**Status:** **IMPLEMENTED** - Production ready
**Date:** 2025-11-28
**Implementation Date:** 2025-12-04
**Deciders:** Architecture Team

> **Post-refactor:** Code examples updated to current model names. `esmis.identifier` (was `esmis.registry.id`),
> `esmis.vocabulary.code` (was `esmis.id.type`), `type_id` (was `id_type_id`), `system_uri` (was `namespace_uri`).
> The identifier model is defined in the domain module that implements identifiers.

### Implementation Summary

| Component | Status | Notes |
|-----------|--------|-------|
| `namespace_uri` on identifier type | ✅ Complete | Now on `esmis.vocabulary.code` via vocabulary |
| Denormalized on `esmis.identifier` | ✅ Complete | `system_uri` related from `type_id.uri`, stored, indexed |
| URN format validation | ✅ Complete | Via `id_validation` regex on vocabulary code (added by identifier domain module via `_inherit`) |
| Seed data | ✅ Complete | national-id, passport, tax-id, birth-certificate |
| API v2 integration | ✅ Complete | Namespace-based lookups |

**Code Location:** The domain module implementing identifiers (e.g., `models/identifier.py`), `esmis_vocabulary/models/vocabulary_code.py`

## Context

The system supports multiple identifier types per entity via `esmis.vocabulary.code` (identifier types) and `esmis.identifier`. Current implementation uses human-readable names (e.g., "National ID", "Tax ID") but lacks globally unique identifiers for interoperability.

**Problems with current approach:**
1. Name collisions across deployments ("National ID" means different things in different countries)
2. No standard way for external systems to reference ID types
3. API integrations require custom mapping per deployment
4. Federation between instances requires manual coordination

**Industry alignment:** This pattern is used by FHIR for identifier systems.

## Decision

Add a `namespace_uri` field to `esmis.vocabulary.code` (the vocabulary code model used for identifier types) that provides a globally unique identifier for each ID type.

## Implementation

### 1. Schema Changes

**File:** `esmis_vocabulary/models/vocabulary_code.py`

> Simplified — see actual implementation in `esmis_vocabulary/models/vocabulary_code.py`.

```python
class VocabularyCode(models.Model):
    _name = "esmis.vocabulary.code"

    # namespace_uri is a related field from the parent vocabulary's URI,
    # combined with the code value to produce a globally unique URI per code.
    namespace_uri = fields.Char(
        related="vocabulary_id.namespace_uri",
        store=True,
        index=True,
        string="Namespace URI",
    )

    # Uniqueness enforced at the database level using Odoo 19 Constraint API.
    _unique_uri = models.Constraint(
        "UNIQUE(uri)",
        "URI must be globally unique",
    )
```

### 2. Denormalized Field on Registry ID (for query performance)

**File:** The domain module implementing `esmis.identifier` (e.g., `models/identifier.py`)

```python
class Identifier(models.Model):
    _inherit = "esmis.identifier"

    system_uri = fields.Char(
        related="type_id.uri",
        store=True,
        index=True,
        string="Namespace",
    )
```

This enables fast lookups without joining to `esmis_vocabulary_code`:
```python
identifier = self.env["esmis.identifier"].search([
    ("system_uri", "=", "urn:gov:us:ssa:ssn"),
    ("value", "=", "123456789"),
], limit=1)
```

### 3. Namespace URI Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| `urn:gov:{cc}:{agency}:{type}` | Government IDs | `urn:gov:us:ssa:ssn`, `urn:gov:ke:nssf:member-id` |
| `urn:org:{org}:{type}` | Organization IDs | `urn:org:unhcr:refugee-id` |
| `urn:iso:std:iso:{num}` | ISO standards | `urn:iso:std:iso:7812` |
| `urn:tpl:id:{type}` | Project-specific generic IDs | `urn:tpl:id:passport` |

> **Note:** The `urn:gov:{cc}:{agency}:{type}` pattern is used for all government-issued identifiers. The `{agency}` component differentiates the issuing authority.

### 4. Seed Data

**File:** Domain module data (e.g., `data/vocabulary_identifier_type.xml`)

> The `id_validation` and `target_type` fields are added to `esmis.vocabulary.code` by the domain module implementing identifiers (via `_inherit`), not by the base `esmis_vocabulary` module.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Generic identifier types within the identifier-type vocabulary -->
    <record id="code_id_national_id" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_identifier_type"/>
        <field name="code">national-id</field>
        <field name="display">National ID</field>
        <field name="id_validation">^[A-Za-z0-9-]+$</field>
        <field name="target_type">both</field>
    </record>

    <record id="code_id_passport" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_identifier_type"/>
        <field name="code">passport</field>
        <field name="display">Passport</field>
        <field name="target_type">individual</field>
    </record>

    <record id="code_id_tax_id" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_identifier_type"/>
        <field name="code">tax-id</field>
        <field name="display">Tax ID</field>
        <field name="target_type">both</field>
    </record>

    <record id="code_id_birth_certificate" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_identifier_type"/>
        <field name="code">birth-certificate</field>
        <field name="display">Birth Certificate</field>
        <field name="target_type">individual</field>
    </record>
</odoo>
```

**File:** `esmis_contact_{cc}/data/identifier_types.xml` (country override example)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Override generic national ID with country-specific version -->
    <record id="esmis_vocabulary.code_id_national_id" model="esmis.vocabulary.code">
        <field name="display">National ID Card</field>
        <field name="namespace_uri">urn:gov:{cc}:{agency}:national-id</field>
        <field name="id_validation">^[0-9]{9}$</field>
    </record>

    <!-- Country-specific ID types -->
    <record id="id_type_social_security" model="esmis.vocabulary.code">
        <field name="display">Social Security Number</field>
        <field name="namespace_uri">urn:gov:{cc}:{agency}:ssn</field>
        <field name="id_validation">^[0-9]{3}-[0-9]{2}-[0-9]{4}$</field>
        <field name="target_type">individual</field>
    </record>

    <record id="id_type_drivers_license" model="esmis.vocabulary.code">
        <field name="display">Driver's License</field>
        <field name="namespace_uri">urn:gov:{cc}:{agency}:license</field>
        <field name="id_validation">^[A-Z0-9-]+$</field>
        <field name="target_type">individual</field>
    </record>
</odoo>
```

### 5. View Updates

**File:** `esmis_vocabulary/views/vocabulary_code_views.xml`

```xml
<!-- Vocabulary code form already includes URI field -->
<record id="view_vocabulary_code_form" model="ir.ui.view">
    <field name="name">esmis.vocabulary.code.form</field>
    <field name="model">esmis.vocabulary.code</field>
    <field name="arch" type="xml">
        <form>
            <group>
                <field name="code"/>
                <field name="display"/>
                <field name="vocabulary_id"/>
                <!-- URI computed from namespace_uri#code -->
            </group>
        </form>
    </field>
</record>
```

### 6. Migration Script

**File:** The domain module implementing identifiers (e.g., `migrations/X.X.X/post-migrate.py`)

```python
def migrate(cr, version):
    """Populate system_uri on identifiers from vocabulary code URIs"""
    cr.execute("""
        UPDATE esmis_identifier ident
        SET system_uri = vc.uri
        FROM esmis_vocabulary_code vc
        WHERE ident.type_id = vc.id
          AND (ident.system_uri IS NULL OR ident.system_uri = '')
    """)
```

### FHIR NamingSystem Mapping

Namespace URIs can be mapped to FHIR NamingSystem URLs for interoperability:

| Namespace URI | FHIR Identifier Type | Notes |
|-----------------------|---------------------|-------|
| `urn:gov:{cc}:{agency}:national-id` | `NI` (National ID) | Country-specific national ID |
| `urn:gov:{cc}:{agency}:tax-id` | `TAX` | Tax identification number |
| `urn:gov:{cc}:{agency}:license` | `DL` (Driver's License) | Driver's license |
| `urn:tpl:id:passport` | `PPN` (Passport) | Passport number |

The FHIR module performs this mapping when translating `esmis.identifier` records to FHIR `Identifier` elements.

## Consequences

### Positive
- Globally unique identification of ID types
- Standard pattern for federation between instances
- API integrations use stable URIs, not display names
- Aligns with FHIR patterns
- Fast lookups via denormalized `system_uri` on identifier

### Negative
- Existing deployments need data migration
- Administrators must understand namespace conventions

## Usage Guide

### For Administrators

**Adding a new ID type via UI:**
1. Navigate to **Settings > Vocabularies**
2. Click **Create**
3. Enter:
   - **Name**: Human-readable name (e.g., "Social Security Number")
   - **Namespace URI**: Globally unique URN (e.g., `urn:gov:us:ssa:ssn`)
   - **ID Type Validation**: Optional regex pattern (e.g., `^[0-9]{3}-[0-9]{2}-[0-9]{4}$`)

**Namespace URI format rules:**
- Must start with `urn:`
- Use lowercase letters, numbers, hyphens, dots, and underscores
- Follow pattern: `urn:{authority}:{type}` with optional additional segments
- Examples: `urn:gov:ke:nssf:member-id`, `urn:org:unhcr:refugee-id`

**Country-specific deployments:**
Override the generic ID types by creating XML data files that reference the base record IDs:
```xml
<record id="esmis_vocabulary.code_id_national_id" model="esmis.vocabulary.code">
    <field name="display">Kenya National ID</field>
    <field name="namespace_uri">urn:gov:ke:iprs:national-id</field>
</record>
```

### For Developers

**Looking up records by system URI:**
```python
# Fast lookup using indexed system_uri field
identifier = self.env["esmis.identifier"].search([
    ("system_uri", "=", "urn:gov:us:ssa:ssn"),
    ("value", "=", "123-45-6789"),
], limit=1)

if identifier:
    partner = identifier.partner_id
```

**Creating identifier types programmatically** (requires the identifier domain module that adds `id_validation` via `_inherit`):
```python
vocab = self.env.ref("esmis_vocabulary.vocab_identifier_type")
id_type = self.env["esmis.vocabulary.code"].create({
    "vocabulary_id": vocab.id,
    "code": "social-security",
    "display": "Social Security",
    "id_validation": r"^[0-9]{9}$",  # field added by identifier domain module
})
```

**Pre-defined ID types (from seed data):**
| XML ID | Name | Namespace URI |
|--------|------|---------------|
| `esmis_vocabulary.code_id_national_id` | National ID | `urn:tpl:id:national-id` |
| `esmis_vocabulary.code_id_passport` | Passport | `urn:tpl:id:passport` |
| `esmis_vocabulary.code_id_tax_id` | Tax ID | `urn:tpl:id:tax-id` |
| `esmis_vocabulary.code_id_birth_certificate` | Birth Certificate | `urn:tpl:id:birth-certificate` |

## Implementation Checklist

- [x] Add `uri` field to `esmis.vocabulary.code` (identifier types)
- [x] Add constraint for URI format validation
- [x] Add denormalized `system_uri` to `esmis.identifier`
- [x] Update form/tree views for `esmis.vocabulary.code`
- [x] Create seed data with standard ID types
- [x] Write migration script for existing data
- [ ] Update API to support namespace-based lookups
- [x] Add tests for namespace validation and lookups

## References

- [FHIR Identifier Registry](https://www.hl7.org/fhir/identifier-registry.html)
- [URN Syntax (RFC 8141)](https://datatracker.ietf.org/doc/html/rfc8141)
- [FHIR Naming Systems](https://www.hl7.org/fhir/namingsystem.html)
