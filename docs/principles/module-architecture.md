# Module Architecture Principles

Guidelines for organizing, consolidating, and extending eSMIS modules.

## Core Principles

1. **Extensible Core** - Clear extension points, not configuration in database
2. **Functional Cohesion** - Group by business capability, not origin
3. **Single Responsibility** - Each module has ONE clear purpose
4. **Extension Over Duplication** - Don't reinvent what exists
5. **Layered Architecture** - Foundation → Capabilities → Extensions

## Layer Structure

```
Layer 3: COUNTRY/DOMAIN EXTENSIONS
├── esmis_reporting (Reporting integration)
└── esmis_workflow (Workflow management)

Layer 2: CAPABILITIES
├── esmis_order (Order management)
├── esmis_inventory (Inventory tracking)
└── esmis_procurement (Procurement orders)

Layer 1: FOUNDATION
├── esmis_contact (Contact management)
├── esmis_vocabulary (Vocabulary & identifiers)
├── esmis_security (Access control)
└── esmis_area (Geographic management)
```

## Three-Tier Customization Model

For configurable features (like Change Request Types, Variables, Events), eSMIS supports three levels of customization:

| Tier | User | Tools | Use Case |
|------|------|-------|----------|
| **Admin** | Government staff | Studio UI | Field-based customization, no coding |
| **Implementer** | SI partners | XML data files | Pre-built strategy selection, configuration |
| **Developer** | Core team | Python code | Custom business logic, new strategies |

### When to Support Each Tier

**Tier 1 (Studio UI):**
- Simple field mappings (copy field A to field B)
- Configuration selection (pick from existing options)
- Basic validation rules (required, regex)

**Tier 2 (XML Configuration):**
- Reference pre-built strategies
- Complex configuration not suited for UI
- Deployment-specific settings

**Tier 3 (Python Code):**
- Custom business logic
- Complex calculations
- External system integration
- Operations affecting multiple records

### Editability Flags

Use boolean flags to indicate which records can be modified at each tier:

| Flag | Purpose |
|------|---------|
| `studio_editable` | Can be modified via Studio UI |
| `studio_cloneable` | Can be copied via Studio |
| `is_system_type` | Defined by module data (vs user-created) |

Python-only features should set `studio_editable=False` with a clear `locked_reason` explaining why and pointing to documentation.

## Module Consolidation Decision

### Consolidate When ✅

- Same team maintains all modules
- Modules always installed together
- Mostly Python code, minimal DB schema
- Reduces duplicate code >50%

### Keep Separate When ❌

- Different teams maintain the modules
- Lots of stored data (complex migration)
- High fan-out (many dependents)
- Different deployment patterns

## Country-Specific Module Pattern

Fields and logic specific to a single country belong in a country-suffixed module, never in the base module.

| Base module | Country module | Contains |
|-------------|----------------|----------|
| `esmis_contact` | `esmis_contact_us` | Country-specific fields, validation rules |
| `esmis_order` | `esmis_order_us` | Country-specific order types, regulatory codes |
| `esmis_integration` | `esmis_integration_us` | Country-specific API profiles, identifier mappings |

**Rule:** If a field, constraint, or method only applies to one country's regulations, it goes in the `_us` (or `_ke`, `_ng`, etc.) module. The base module must remain country-agnostic.

### Country Module Exclusion

Country-specific modules **must declare exclusions** against all other country variants of the same base module. This prevents conflicting country implementations from being installed simultaneously.

Odoo's `excludes` manifest key enforces this at install time — attempting to install an excluded module raises a `UserError`.

```python
# esmis_contact_us/__manifest__.py
{
    "name": "eSMIS Contact - United States",
    "depends": ["esmis_contact", "esmis_vocabulary"],
    "excludes": ["esmis_contact_ke", "esmis_contact_ng"],
    "auto_install": False,  # installed via esmis_starter_us
    ...
}
```

**Convention:** Every `esmis_{domain}_{country}` module must list all other `esmis_{domain}_{other_country}` modules in its `excludes`. When adding a new country, update all existing country modules to exclude the new one.

Country modules never use `auto_install`. They are installed exclusively through a country starter module (`esmis_starter_{country}`), which is the only `application=True` entry point in the Apps menu. This prevents country-specific data from leaking into non-country deployments.

### Starter Module Localization

Beyond aggregating country module dependencies, each starter module configures the Odoo database for the target country's locale via `data/res_company_data.xml` (`noupdate="1"`). This includes activating the country's currency, setting the main company's country and currency, and configuring the default timezone. See [Module Visibility — Localization Defaults](module-visibility.md#localization-defaults) for the full checklist.

This applies to all layers:
- `esmis_contact_us` excludes `esmis_contact_ke`, `esmis_contact_ng`, etc.
- `esmis_order_us` excludes `esmis_order_ke`, etc.

Country modules use `_inherit` to extend the base model:

```python
# esmis_contact_us/models/res_partner.py
class ResPartner(models.Model):
    _inherit = "res.partner"

    tax_id_number = fields.Char(string="Tax ID Number")
    membership_type_id = fields.Many2one(
        "esmis.vocabulary.code",
        domain="[('namespace_uri', '=', 'urn:gov:us:irs:membership-type')]",
    )
```

## Identifier Pattern

External identifiers (tax IDs, national IDs, passport numbers, etc.) are stored in a **separate identifier model** linked to `res.partner` via One2many — never as direct fields on the partner.

```
res.partner
    └── identifier_ids (One2many → esmis.identifier)
            ├── type_id → esmis.vocabulary.code (display, uri)
            ├── system_uri → (related from type_id.uri, stored, indexed)
            └── value → "123-45-6789"
```

**Why not direct fields?** A contact can have many identifiers, and different deployments need different ID types. A relational model allows:
- Adding new ID types via data files (no code changes)
- Enforcing uniqueness per type+value via SQL constraints
- Validating format per type via regex patterns
- Standardized mapping to external identifier formats

The identifier type definitions are seeded as data in the appropriate country module (e.g., `esmis_contact_us`).

**Exception: High-frequency convenience fields.** A country module may add a direct `Char` field (e.g., `tax_id_number`) for an identifier that appears on most forms and is entered frequently. The field must sync bidirectionally with `esmis.identifier` via overridden `create()` and `write()`. This is a UX shortcut, not a replacement — the identifier model remains the canonical store.

## Vocabulary Pattern

Avoid hardcoding selection values for fields like status, category, type, or any classification that could vary by deployment. Instead, use a vocabulary model (`esmis_vocabulary`) that stores code lists as configurable records.

**Instead of this:**
```python
priority = fields.Selection([("low", "Low"), ("medium", "Medium"), ("high", "High")])
```

**Do this:**
```python
priority_id = fields.Many2one(
    "esmis.vocabulary.code",
    domain="[('namespace_uri', '=', 'urn:example:priority')]",
)
```

The `esmis_vocabulary` module provides:

| Model | Purpose |
|-------|---------|
| `esmis.vocabulary` | A named code list with a namespace URI (e.g., `urn:example:priority` for priority levels) |
| `esmis.vocabulary.code` | Individual code within a vocabulary (code, display label, sequence, URI) |

**When to use vocabulary vs. static selection:**
- **Use vocabulary** for values that follow external standards, vary by deployment, or need to be extended without code changes.
- **Use static selection** only for internal workflow states (`draft`, `confirmed`, `cancelled`) or boolean-like choices that are truly fixed.

## Extension Patterns

### Pattern 1: Inherit and Extend

```python
# In country module
class ResPartner(models.Model):
    _inherit = "res.partner"

    def validate_registration(self):
        # Override with country-specific rules
        super().validate_registration()
        self._validate_country_requirements()
```

### Pattern 2: Plugin Architecture

```python
# Core defines interface
class ProcessPlugin(models.AbstractModel):
    _name = "esmis.process.plugin"

    def apply_changes(self, record):
        raise NotImplementedError

# Extensions implement
class ApprovalPlugin(models.AbstractModel):
    _inherit = "esmis.process.plugin"

    def apply_changes(self, record):
        # Implementation
```

### Pattern 3: Hook Methods

```python
# Core module
class Order(models.Model):
    def register_contact(self, partner):
        self._pre_registration_hook(partner)
        # ... registration logic ...
        self._post_registration_hook(partner)

    def _pre_registration_hook(self, partner):
        """Override in extensions for custom validation"""
        pass
```

## Dependency Guidelines

- Minimize dependencies between peer modules
- Dependencies should flow downward (Layer 3 → 2 → 1)
- Avoid circular dependencies
- Use soft dependencies when possible

## Partner Abstraction

Build on Odoo's `res.partner`, not custom models:

```
res.partner (Odoo)
    └── is_contact (esmis_contact)
        ├── identifier_ids → esmis.identifier (domain module)
        ├── category_id → esmis.vocabulary.code (esmis_vocabulary)
        └── status_id → esmis.vocabulary.code (esmis_vocabulary)
```

**Benefits:** Leverage Odoo's contact management, deduplication, relationships.

---

**See also:** [Naming Conventions](naming-conventions.md), [API Design](api-design.md)
