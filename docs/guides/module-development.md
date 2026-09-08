# Module Development Guide

How to create, structure, and ship a new module from scratch using TDD and Claude Code.

## Module Naming

All project modules use the `esmis_*` prefix:

| Pattern | Example | When to use |
|---------|---------|-------------|
| `esmis_{domain}` | `esmis_warehouse` | Single-domain module |
| `esmis_{domain}_{feature}` | `esmis_warehouse_barcode` | Feature within a domain |

Models inside a module use the `esmis.*` prefix: `esmis.warehouse`, `esmis.warehouse.barcode`.

## Standard Directory Structure

```
esmis_inventory/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── esmis_stock_move.py
├── views/
│   └── stock_move_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml       # Only if defining new groups
├── data/
│   └── stock_move_data.xml       # Reference/config data
├── demo/
│   └── stock_move_demo.xml       # Demo records
├── tests/
│   ├── __init__.py
│   └── test_stock_move.py
└── readme/
    └── DESCRIPTION.md
```

Every subdirectory that contains Python files needs an `__init__.py`. Every directory listed in the manifest must exist.

## `__manifest__.py` Template

```python
{
    "name": "Inventory Extensions",
    "version": "19.0.1.0.0",
    "category": "eSMIS/{Domain}",
    "summary": "Custom stock move tracking for warehouse operations",
    "author": "Pith Technologies",
    "website": "https://example.com",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": [],
    "depends": [
        "esmis_vocabulary",
        "stock",
    ],
    "external_dependencies": {"python": ["somelib"]},  # only when needed
    "data": [
        "security/ir.model.access.csv",
        "views/stock_move_views.xml",
    ],
    "demo": [
        "demo/stock_move_demo.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
```

### `application` and `auto_install` rules

| Setting | Value | When |
|---------|-------|------|
| `application` | `True` | **Only** starter modules (`esmis_starter_{variant}`) — the single entry point users install |
| `application` | `False` | All `esmis_*` domain modules (foundation, bridges, extensions, API, infra) |
| `auto_install` | `["dep1", "dep2"]` | Non-variant bridge module that activates when both deps are installed |
| `auto_install` | `True` | Non-variant single-dependency extension that always activates with its parent |
| `auto_install` | `False` | Manual install required (most modules), **always** for variant modules (`esmis_*_{variant}`) |

> **Variant modules** (`esmis_{domain}_{variant}`) must always set `auto_install=False`. They are installed exclusively via starter modules (`esmis_starter_{variant}`).

### Starter module pattern

A starter module (`esmis_starter_{variant}`) is the single `application=True` entry point for a variant deployment. It contains:

1. **Dependencies** on all variant modules (`esmis_*_{variant}`)
2. **Configuration data** (`data/res_company_data.xml`) that configures the database for the target locale/variant

Template for `data/res_company_data.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Activate the target currency (many are inactive by default) -->
    <record id="base.EUR" model="res.currency">
        <field name="active" eval="True"/>
    </record>

    <!-- Set main campus (res.company) country -->
    <record id="base.main_partner" model="res.partner">
        <field name="country_id" ref="base.de"/>
    </record>

    <!-- Set main campus (res.company) currency -->
    <record id="base.main_company" model="res.company">
        <field name="currency_id" ref="base.EUR"/>
    </record>

    <!-- Set default timezone for admin user -->
    <record id="base.user_admin" model="res.users">
        <field name="tz">Europe/Berlin</field>
    </record>
</odoo>
```

Use `noupdate="1"` so these defaults are applied once on install and do not overwrite admin customizations on upgrade. If the variant's primary language is not English, also activate the language and set it on the admin user.

### Category hierarchy

Use `eSMIS/{Domain}` with domain names relevant to your project (e.g., `Core`, `Operations`, `Integration`, `Reporting`).

## Layer Architecture

Dependencies must flow downward. Never create circular dependencies.

```
Layer 3: EXTENSIONS           (esmis_reporting, esmis_api)
    ↓
Layer 2: DOMAIN CORE          (esmis_project, esmis_warehouse, esmis_service)
    ↓
Layer 1: FOUNDATION           (esmis_security, esmis_vocabulary)
    ↓
Layer 0: ODOO CORE            (base, hr, stock, account, calendar)
```

If your module adds a feature that only makes sense when two other modules are installed together, it belongs in Layer 3 as a bridge module, not in Layer 2.

## Key Architectural Patterns

These patterns are enforced across all project modules. See `docs/principles/module-architecture.md` for full details.

### Variant-specific modules

Fields and logic specific to a single variant (e.g., country or deployment) go in a variant-suffixed module (`esmis_{domain}_{variant}`), never in the base domain module. The domain module must remain variant-agnostic.

### Identifiers as a separate model

Government and institutional identifiers (tax numbers, registration codes, national IDs, passport numbers) are stored in the `esmis.identifier` model linked via One2many to `res.partner` — never as direct `Char` fields on the partner.

### Vocabulary over static selections

Use `esmis_vocabulary` (Many2one to `esmis.vocabulary.code`) instead of `fields.Selection` for values that may grow or vary by deployment (e.g., categories, types, statuses). Static selections are acceptable only for internal workflow states.

### Configuration menu placement

Configuration items belong under the shared app-level Configuration menu, not nested inside domain menus. To add a configuration menu item from a new module:

```xml
<!-- esmis_warehouse/views/menus.xml -->
<odoo>
    <menuitem id="menu_esmis_configuration_locations"
              name="Warehouse Locations"
              parent="esmis_vocabulary.menu_esmis_configuration"
              action="action_warehouse_location"
              sequence="20"/>
</odoo>
```

Key points:

- **Parent** — always `esmis_vocabulary.menu_esmis_configuration` (module-qualified, since `esmis_vocabulary` defines it).
- **Sequence** — pick a number that orders logically among other config items (Vocabularies is 10).
- **Groups** — the parent menu already gates on `base.group_system`. Add additional group restrictions on the child only if a narrower audience is needed.

## TDD Workflow

The required order is: write a failing test, run it (watch it fail), implement the minimum code to pass, run again.

### Step 1: Write the failing test

```python
# esmis_inventory/tests/test_stock_move.py
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestStockMove(TransactionCase):

    def setUp(self):
        super().setUp()
        self.warehouse = self.env["esmis.warehouse"].create({
            "name": "Main Warehouse",
        })

    def test_quantity_must_be_positive(self):
        """Stock move quantity must be a positive number."""
        with self.assertRaises(ValidationError):
            self.env["esmis.stock.move"].create({
                "warehouse_id": self.warehouse.id,
                "quantity": -10,
            })

    def test_stock_move_linked_to_warehouse(self):
        """Creating a stock move links it to the warehouse."""
        move = self.env["esmis.stock.move"].create({
            "warehouse_id": self.warehouse.id,
            "quantity": 50,
            "product_name": "Widget A",
        })
        self.assertIn(move, self.warehouse.stock_move_ids)
```

### Step 2: Run the test — confirm it fails

```bash
./scripts/test_single_module.sh esmis_inventory
```

The test must fail at this stage. If it passes without implementation, the test is not actually testing the right thing.

### Step 3: Implement the model

```python
# esmis_inventory/models/esmis_stock_move.py
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PrefixStockMove(models.Model):
    _name = "esmis.stock.move"
    _description = "Stock Move"

    warehouse_id = fields.Many2one(
        "esmis.warehouse",
        string="Warehouse",
        required=True,
        ondelete="cascade",
    )
    quantity = fields.Integer(string="Quantity")
    product_name = fields.Char(string="Product Name")

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity is not False and record.quantity < 0:
                raise ValidationError(_("Quantity must be a positive value."))
```

### Step 4: Add the ACL file

Every model must have an entry in `security/ir.model.access.csv`. Every custom `esmis.*` model must include a `base.group_system` row with full CRUD as the first data row — this ensures the admin/superuser always has access:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_stock_move_system,esmis.stock.move / System,model_esmis_stock_move,base.group_system,1,1,1,1
access_esmis_stock_move_officer,esmis.stock.move officer,model_esmis_stock_move,esmis_security.group_esmis_officer,1,1,1,0
access_esmis_stock_move_manager,esmis.stock.move manager,model_esmis_stock_move,esmis_security.group_esmis_manager,1,1,1,1
```

> **Note:** The `esmis_security` module provides cross-project security groups. If your project has not created this module yet, define module-specific groups (see the [Security groups template](#security-groups-securitysecurity_groupsxml) below) and reference those instead.

### Step 5: Run the test — confirm it passes

```bash
./scripts/test_single_module.sh esmis_inventory
```

All tests must pass before moving on.

## Code Documentation

Every module should include documentation at four levels: module-level (`DESCRIPTION.md`), class-level, method-level, and inline. The goal is for a developer unfamiliar with the module to understand the _why_ behind the code without needing to ask the original author.

### Python: Models and Methods

**Model classes** must always set `_description` to a human-readable name:

```python
class PrefixStockMove(models.Model):
    _name = "esmis.stock.move"
    _description = "Stock Move"
```

Add a **class-level docstring** when the model's purpose is not obvious from `_name` and `_description`:

```python
class PrefixOrderDisposition(models.Model):
    _name = "esmis.order.disposition"
    _description = "Order Disposition"
    """Tracks how an order was resolved (fulfilled, cancelled, returned, partial).
    Used by reporting modules to determine order completion metrics."""
```

**Method docstrings** are required on:

- Public methods and action methods (`action_confirm`, `action_cancel`)
- Overrides of Odoo ORM methods (`create`, `write`, `unlink`)
- Constraint methods (`_check_*`) — explain the business rule
- Complex private methods — if the logic spans more than ~10 lines or encodes a non-obvious rule

```python
@api.constrains("min_quantity", "max_quantity")
def _check_quantity_range(self):
    """Max quantity must exceed min quantity. Values above 10000 trigger
    a warning in the UI but do not block the save."""
    ...
```

One-liner docstrings are fine for simple methods. Do not add docstrings to trivial getters/setters or methods whose name already fully describes the behavior.

**Field `help=` attribute** — use on fields where the label alone is ambiguous. This renders as a tooltip in the Odoo UI:

```python
tax_id_number = fields.Char(
    string="Tax ID",
    help="Taxpayer identification number without dashes or spaces.",
)
```

### Python: Inline Comments

- Explain _why_, not _what_. Do not restate code (`# increment counter` above `counter += 1`).
- Do comment non-obvious business rules, domain logic, regulatory requirements, and Odoo-specific workarounds.
- Use `# TODO:` for known gaps with a brief explanation of what is needed.
- No PII in comments — do not use real names, IDs, or sensitive data in examples.

### XML: Views and Data

- Use `<!-- Section: Name -->` comments to separate logical groups in view files (header, tabs, chatter).
- Comment groups of records in data XML files (e.g., `<!-- Default warehouse location types -->`).
- Comment non-obvious `attrs`, `domain`, or `context` expressions that encode business rules.
- Do not comment self-evident XML — `<!-- Partner name field -->` above `<field name="name"/>` is noise.

### Module-Level: `readme/DESCRIPTION.md`

Every module must have a `readme/DESCRIPTION.md`. See the [DESCRIPTION.md Requirements](#descriptionmd-requirements) section below and `docs/principles/module-descriptions.md` for the full policy, template, and anti-patterns.

## Using Claude Code Commands

| Command | When to use |
|---------|-------------|
| `/implement` | Runs the full TDD cycle with subagents: tests first, then implementation, then review |
| `/verify-tests` | After a subagent session — checks that no tests were removed or weakened |
| `/commit` | Produces a conventional commit message (`feat:`, `fix:`, etc.) |
| `/pr` | Creates a GitHub PR with OpenProject task linking |

Start non-trivial features in Plan mode (shift+tab twice) before running `/implement`.

## Using Subagents

| Subagent | Best for |
|----------|----------|
| `@odoo-developer` | Models, views, ACL, business logic |
| `@code-reviewer` | Security, Odoo 19 naming, and compliance check before PR |
| `@ux-expert` | Form layouts and UI patterns |
| `@code-simplifier` | Reducing complexity after the implementation is working |
| `@verify-module` | Confirming the module installs and all tests pass |

When asking `@odoo-developer` to implement a model, include the test file you already wrote so the agent targets exactly what needs to pass.

## DESCRIPTION.md Requirements

Every module must have `readme/DESCRIPTION.md`. Keep it to 25–60 lines.

Required sections: overview paragraph, Key Capabilities, Key Models, Configuration, UI Location, Security, Dependencies.

```markdown
## Overview

Inventory Extensions adds custom stock move tracking for warehouse operations
and links each move to the originating warehouse record.

## Key Capabilities

- Record inbound and outbound stock moves per warehouse
- Flag out-of-range quantities for review

## Key Models

- `esmis.stock.move` — one stock move record per warehouse operation

## UI Location

eSMIS > Inventory > Warehouses > [warehouse] > Stock Moves tab

## Security

- `esmis_security.group_esmis_officer` — create and edit
- `esmis_security.group_esmis_manager` — full access including delete

## Dependencies

- `esmis_vocabulary` — vocabulary infrastructure
- `stock` — Odoo stock module
```

No marketing language ("robust", "seamless", "comprehensive"). Every claim must match the actual code.

## Verification Checklist

Before marking any task complete, confirm all items below:

- [ ] Module name follows `esmis_{domain}` or `esmis_{domain}_{feature}`
- [ ] All models use `esmis.*` prefix
- [ ] `ir.model.access.csv` exists with an entry for every model
- [ ] Every custom `esmis.*` model has a `base.group_system` full CRUD row
- [ ] ACL entry IDs follow `access_{model}_{group}` pattern
- [ ] No `print()` — use `_logger`
- [ ] No bare `except:` — catch specific exceptions
- [ ] No `cr.commit()` in loops — use `queue_job` for batch work
- [ ] No PII in log messages
- [ ] Boolean fields use `is_*` or `has_*` prefix
- [ ] Many2one fields use `{model}_id`, One2many/M2m use `{model}_ids`
- [ ] No variant-specific fields in base modules (use `esmis_*_{variant}` modules)
- [ ] No static `Selection` for values that should be vocabulary-backed
- [ ] Government/institutional IDs stored in `esmis.identifier` model, not as direct fields
- [ ] `application` and `auto_install` set correctly
- [ ] All models have `_description` set
- [ ] Public methods, overrides, and constraints have docstrings
- [ ] `help=` set on fields with ambiguous labels
- [ ] `DESCRIPTION.md` written (25–60 lines, no marketing language)
- [ ] Tests exist and pass: `./scripts/test_single_module.sh <module>`
- [ ] Linter passes: `pre-commit run --files <changed_files>`

## Module Scaffold Reference

Use these templates when creating a new module from scratch. Every file below is the minimal starting point for a `esmis_{domain}` module.

### Required Files

#### `esmis_{domain}/__manifest__.py`

```python
{
    "name": "{Domain}",
    "version": "19.0.1.0.0",
    "category": "eSMIS/{Domain}",
    "summary": "One-line description of what this module does",
    "author": "Pith Technologies",
    "website": "",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": [],
    "depends": [
        "esmis_vocabulary",  # foundation dependency
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/{domain}_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "auto_install": False,
    "application": False,
    "installable": True,
}
```

#### `esmis_{domain}/__init__.py`

```python
from . import models
```

#### `esmis_{domain}/models/__init__.py`

```python
from . import {domain}
```

#### `esmis_{domain}/models/{domain}.py`

```python
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Prefix{Domain}(models.Model):
    """Short description of what this model represents."""

    _name = "esmis.{domain}"
    _description = "{Domain}"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    @api.constrains("name")
    def _check_name(self):
        """Name must not be empty after stripping whitespace."""
        for rec in self:
            if rec.name and not rec.name.strip():
                raise ValidationError(_("Name cannot be blank."))
```

#### `esmis_{domain}/views/{domain}_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_esmis_{domain}_form" model="ir.ui.view">
        <field name="name">esmis.{domain}.form</field>
        <field name="model">esmis.{domain}</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="e.g. Example Name"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <!-- Primary fields here -->
                        </group>
                        <group>
                            <field name="active" invisible="1"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="view_esmis_{domain}_list" model="ir.ui.view">
        <field name="name">esmis.{domain}.list</field>
        <field name="model">esmis.{domain}</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_esmis_{domain}" model="ir.actions.act_window">
        <field name="name">{Domain}</field>
        <field name="res_model">esmis.{domain}</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

#### `esmis_{domain}/views/menus.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem
        id="menu_{domain}_root"
        name="{Domain}"
        parent="base.menu_custom"
        sequence="20"
    />
    <menuitem
        id="menu_{domain}_list"
        name="{Domain} Records"
        parent="menu_{domain}_root"
        action="action_esmis_{domain}"
        sequence="10"
    />
</odoo>
```

#### `esmis_{domain}/security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_{domain}_system,esmis.{domain} / System,model_esmis_{domain},base.group_system,1,1,1,1
access_esmis_{domain}_officer,esmis.{domain} / Officer,model_esmis_{domain},esmis_security.group_esmis_officer,1,1,1,0
access_esmis_{domain}_manager,esmis.{domain} / Manager,model_esmis_{domain},esmis_security.group_esmis_manager,1,1,1,1
```

> **Note:** The `esmis_security` module provides cross-project security groups. If your project has not created this module yet, define module-specific groups (see the [Security groups template](#security-groups-securitysecurity_groupsxml) below) and reference those instead.

#### `esmis_{domain}/tests/__init__.py`

```python
from . import test_{domain}
```

#### `esmis_{domain}/tests/test_{domain}.py`

```python
from odoo.tests import TransactionCase


class TestPrefix{Domain}(TransactionCase):

    def setUp(self):
        super().setUp()
        self.record = self.env["esmis.{domain}"].create({
            "name": "Test Record",
        })

    def test_create_record(self):
        """Creating a record sets the name correctly."""
        self.assertEqual(self.record.name, "Test Record")

    def test_active_default(self):
        """New records are active by default."""
        self.assertTrue(self.record.active)
```

#### `esmis_{domain}/readme/DESCRIPTION.md`

```markdown
Short overview of what esmis_{domain} provides.

## Key Capabilities

- Capability one
- Capability two

## Key Models

- `esmis.{domain}` — description of the model

## UI Location

eSMIS > {Domain} > Records

## Security

- `esmis_security.group_esmis_officer` — create and edit
- `esmis_security.group_esmis_manager` — full access including delete

## Dependencies

- `esmis_vocabulary` — vocabulary infrastructure
```

#### `esmis_{domain}/pyproject.toml`

```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

### Optional Patterns

These are not part of every module but are common additions.

#### Settings model: `models/res_config_settings.py`

When your module needs system-wide configuration options:

```python
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    {domain}_feature_enabled = fields.Boolean(
        string="Enable {Domain} Feature",
        config_parameter="esmis_{domain}.feature_enabled",
    )
```

Companion view in `views/res_config_settings_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="res_config_settings_view_form" model="ir.ui.view">
        <field name="name">res.config.settings.form.inherit.esmis_{domain}</field>
        <field name="model">res.config.settings</field>
        <field name="inherit_id" ref="base.res_config_settings_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//form" position="inside">
                <app data-string="{Domain} Settings" string="{Domain} Settings">
                    <block title="{Domain} Configuration">
                        <setting string="Enable Feature"
                                 help="Activate the {domain} feature for this database.">
                            <field name="{domain}_feature_enabled"/>
                        </setting>
                    </block>
                </app>
            </xpath>
        </field>
    </record>
</odoo>
```

Add both files to `__manifest__.py` `data` list and add `"models/res_config_settings.py"` import.

#### Security groups: `security/security_groups.xml`

When your module defines its own permission groups (instead of relying on `esmis_security`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="category_esmis_{domain}" model="ir.module.category">
        <field name="name">esmis {Domain}</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_{domain}_officer" model="res.groups.privilege">
        <field name="name">{Domain} Officer</field>
        <field name="category_id" ref="category_esmis_{domain}"/>
    </record>

    <record id="group_{domain}_viewer" model="res.groups">
        <field name="name">{Domain}: Viewer</field>
        <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
    </record>

    <record id="group_{domain}_officer" model="res.groups">
        <field name="name">{Domain}: Officer</field>
        <field name="privilege_id" ref="privilege_{domain}_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_{domain}_viewer'))]"/>
    </record>

    <record id="group_{domain}_manager" model="res.groups">
        <field name="name">{Domain}: Manager</field>
        <field name="privilege_id" ref="privilege_{domain}_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_{domain}_officer'))]"/>
    </record>
</odoo>
```

#### Seed data: `data/{domain}_data.xml`

When your module ships with reference data using vocabulary codes:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="{domain}_default_record" model="esmis.{domain}">
        <field name="name">Default Record</field>
        <field name="type_id" ref="esmis_vocabulary.code_some_type"/>
    </record>
</odoo>
```

Use `noupdate="1"` for data that should not be overwritten on module upgrade.

## `esmis_vocabulary` Foundation

The `esmis_vocabulary` module provides the foundation vocabulary infrastructure for all project modules. It should be included in `depends` for any module that uses vocabulary-backed fields.

### What It Provides

| Model | Purpose |
|-------|---------|
| `esmis.vocabulary` | Named collection of codes with a globally unique namespace URI |
| `esmis.vocabulary.code` | Individual code within a vocabulary — has a code, display label, and computed URI |

Key features:
- **Namespace URIs** for interoperability (`urn:iso:std:iso:5218`, `urn:tpl:vocab:{name}`)
- **System protection** — system vocabularies (`is_system=True`) prevent user edits
- **Cached lookups** — `get_code(namespace_uri, code)` and `resolve_by_uri(uri)` with ORM cache
- **Configuration menu** — owns the top-level `menu_esmis_configuration` used by all modules

### Seed Vocabularies

Installed with the module:

| Vocabulary | Namespace URI | Codes |
|------------|---------------|-------|
| Gender | `urn:iso:std:iso:5218` | Not Known (0), Male (1), Female (2), Not Applicable (9) |
| Civil Status | `urn:un:vocab:marital-status` | Single, Married, Widowed, Divorced, Separated |
| Blood Type | `urn:tpl:vocab:blood-type` | A+, A-, B+, B-, AB+, AB-, O+, O- |

### Adding a Vocabulary via XML Data

Create a data file (e.g., `data/vocabulary_{name}.xml`) and add it to `__manifest__.py`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="vocab_priority" model="esmis.vocabulary">
        <field name="name">Priority Level</field>
        <field name="namespace_uri">urn:tpl:vocab:priority</field>
        <field name="description">Priority classification for work items</field>
        <field name="is_system" eval="True"/>
        <field name="domain">administrative</field>
    </record>

    <record id="code_priority_low" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_priority"/>
        <field name="code">low</field>
        <field name="display">Low</field>
        <field name="sequence">10</field>
    </record>

    <record id="code_priority_medium" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_priority"/>
        <field name="code">medium</field>
        <field name="display">Medium</field>
        <field name="sequence">20</field>
    </record>

    <record id="code_priority_high" model="esmis.vocabulary.code">
        <field name="vocabulary_id" ref="vocab_priority"/>
        <field name="code">high</field>
        <field name="display">High</field>
        <field name="sequence">30</field>
    </record>
</odoo>
```

### Using Vocabulary Codes in Models

Reference a vocabulary code with a `Many2one` field:

```python
from odoo import fields, models


class PrefixWorkItem(models.Model):
    _name = "esmis.work.item"
    _description = "Work Item"

    name = fields.Char(required=True)
    priority_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Priority",
        domain="[('namespace_uri', '=', 'urn:tpl:vocab:priority')]",
        help="Priority level from the Priority vocabulary",
    )
```

The `domain` filter ensures only codes from the correct vocabulary appear in the dropdown. In the corresponding form view:

```xml
<field name="priority_id"
       options="{'no_create': True, 'no_open': True}"/>
```

Use `no_create` and `no_open` to prevent users from creating or editing vocabulary codes inline — codes should be managed through the Vocabularies configuration UI.

### Looking Up Codes in Python

```python
# By namespace + code
code = self.env["esmis.vocabulary.code"].get_code("urn:tpl:vocab:priority", "high")

# By full URI
code = self.env["esmis.vocabulary.code"].resolve_by_uri("urn:tpl:vocab:priority#high")
```

Both methods use the ORM cache for fast repeated lookups.

## SIS Module Development Patterns

These patterns apply to all eSMIS Student Information System modules.

### Government identifier integration

Use the `esmis.identifier` model with URIs (e.g., `urn:gov:ph:deped:lrn`) for all government IDs. Never store national IDs as plain text fields on the model — use the identifier system with encryption.

### Consent mixin

Models handling student PII should inherit `esmis.consent.mixin`. This adds consent tracking and enforces RA 10173 compliance. Check consent status before exposing PII in `read()` or API responses.

### Learning modality

All course/section models must support a `learning_modality` field (vocabulary code: `f2f`, `online`, `blended`) per CMO No. 4, s. 2020.

### Multi-campus

All domain models include `company_id = fields.Many2one('res.company', default=lambda self: self.env.company)`. Add a campus isolation record rule. See `docs/principles/multi-campus-architecture.md`.

### Financial aid hooks

Enrollment models should call `_compute_financial_aid_eligibility()` hook to allow `esmis_financial_aid` and `esmis_financial_aid_ph` to inject eligibility checks.

## SIS Module Checklist

In addition to the [Verification Checklist](#verification-checklist) above, confirm these SIS-specific items:

- [ ] `company_id` field added for multi-campus
- [ ] Company record rule created in `security/`
- [ ] Consent mixin inherited if model handles student PII
- [ ] Government identifier URIs used (not plain text fields)
- [ ] Learning modality vocabulary used (not hardcoded selection)
- [ ] Hook methods defined for extension points
- [ ] Philippine-specific logic isolated in `esmis_*_ph` module

## Deep Dives

- `docs/principles/module-architecture.md` — layer structure, extension patterns, consolidation decisions
- `docs/principles/naming-conventions.md` — all naming rules including field types and XML IDs
- `docs/principles/access-rights.md` — three-tier security, ACL format, record rules
- `docs/principles/module-descriptions.md` — DESCRIPTION.md anti-patterns and examples
- `.claude/rules/module-setup.md` — auto-loaded rule summary (loaded when editing `__manifest__.py`)
