# Module Visibility

Guidelines for `application`, `auto_install`, and `category` in module manifests.

## Core Principles

1. **Starter Module Entry Point** - Only `esmis_starter_{country}` modules are `application=True`
2. **Domain Modules are Hidden** - All `esmis_*` domain modules are `application=False`
3. **Auto-Install Bridges** - Non-country modules connecting two features should auto-install
4. **Consistent Categories** - Use hierarchy: `eSMIS/{Domain}`
5. **Clean Apps Menu** - Users see one starter module per country, not 50+ modules

## Starter Module Pattern

The **only** modules with `application=True` are country-specific starter modules:

```python
# esmis_starter_us/__manifest__.py
{
    "name": "eSMIS United States",
    "application": True,  # appears in Apps menu
    "depends": ["esmis_contact_us", "esmis_integration_us"],
}
```

Starter modules are the single entry point for installing eSMIS in a specific country. They pull in the appropriate foundation, capability, and country-specific modules via their dependency chain.

### Localization Defaults

In addition to aggregating dependencies, starter modules configure the Odoo database for the target country's locale via a `data/res_company_data.xml` file (with `noupdate="1"`):

- **Currency** — activate the country's currency (many are inactive by default) and set it on the main campus (`res.company`)
- **Country** — set the main campus partner's country
- **Timezone** — set the admin user's timezone to the country's primary zone
- **Language** — only needed if the country's primary language is not English (`en_US`)

These are applied once on install and will not overwrite admin customizations on upgrade.

All `esmis_*` domain modules (foundation, capabilities, extensions) set `application=False`.

### Country Module Installation

Country-specific modules (`esmis_{domain}_{country}`) are **never** installed via `auto_install`. They are only installed as dependencies of a country starter module. This ensures a fresh Odoo database has zero `esmis_*` modules until an administrator explicitly installs a starter from the Apps menu.

## Application Flag

| Set `application=True` | Set `application=False` |
|------------------------|-------------------------|
| Starter modules (`esmis_starter_{country}`) | All `esmis_*` domain modules |
| | Base module (`esmis_base`) |
| | Foundation modules (esmis_vocabulary, esmis_contact) |
| | Capability modules (esmis_order, esmis_inventory) |
| | Bridge/glue modules |
| | Extensions, API modules, technical infra |

## Auto-Install Pattern

Use `auto_install` for modules that **only make sense when dependencies coexist**:

```python
# Bridge module - installs when BOTH dependencies present
# Use list syntax to specify which deps trigger auto-install
"depends": ["esmis_order", "esmis_procurement"],
"auto_install": ["esmis_order", "esmis_procurement"],
"application": False,

# Extension module - installs when ANY dependency present
# Use True only for single-dependency extensions
"depends": ["esmis_vocabulary"],
"auto_install": True,
"application": False,
```

> **Important:** For multi-dependency bridges, use `auto_install: ["dep1", "dep2"]` (list)
> instead of `auto_install: True`. This ensures the module only installs when ALL
> listed dependencies are present, not just one.

> **Country modules:** `esmis_{domain}_{country}` modules must always set `auto_install=False`.
> They are installed exclusively through country starter modules (`esmis_starter_{country}`).

## Categories

| Category | Use For |
|----------|---------|
| `eSMIS/Core` | base, contact, area |
| `eSMIS/Operations` | order, inventory, procurement |
| `eSMIS/Identity` | identifiers, authentication |
| `eSMIS/Billing` | invoicing, payments |
| `eSMIS/Integration` | api, import_*, connectors |
| `eSMIS/Configuration` | studio, custom_field |
| `eSMIS/Reporting` | reports, dashboards |

> **Note:** Some modules still use the top-level `eSMIS` category without hierarchy.
> New modules should always use the hierarchical categories above.
> Starter modules use the top-level `eSMIS` category (no sub-hierarchy).

## Country Module Exclusions

Country-specific modules must use Odoo's `excludes` manifest key to prevent conflicting country implementations from coexisting:

```python
# esmis_contact_us/__manifest__.py
{
    "excludes": ["esmis_contact_ke", "esmis_contact_ng"],
    ...
}
```

When Odoo encounters an `excludes` conflict at install time, it raises a `UserError`: *"Modules 'A' and 'B' are incompatible."*

**Rule:** Every `esmis_{domain}_{country}` module must exclude all other `esmis_{domain}_{other_country}` modules. When adding a new country, update all existing country modules to exclude it.

## Decision Checklist

When creating a module:

- [ ] Is this a **country starter module** (`esmis_starter_{country}`)? → `application=True`
- [ ] Is this any other `esmis_*` module? → `application=False`
- [ ] Does this **connect two existing non-country features**? → `auto_install=["dep1", "dep2"]`
- [ ] Does this **extend a single non-country feature**? → `auto_install=True`
- [ ] Is this a **country-specific module** (`esmis_{domain}_{country}`)? → `auto_install=False`, add `excludes` for other countries

---

**See also:** [Module Architecture](module-architecture.md), [Naming Conventions](naming-conventions.md)
