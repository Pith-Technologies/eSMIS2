# Tutorial: Building Your First eSMIS Module

A step-by-step walkthrough of building `esmis_academic_term`, a foundation-layer module that
manages academic years and terms/semesters. This is a **teaching example** — the real module
will be built later using the full TDD workflow with `/implement`.

By the end you will understand:

- The standard eSMIS module directory structure
- How TDD works in an Odoo 19 project
- How vocabulary-backed fields replace static selections
- How campus-aware models use `company_id`
- How security groups and ACLs are structured
- How seed data ships with a module

**Prerequisites:** A working local eSMIS development environment. See the project README for
setup instructions.

---

## Step 1: Create the Module Skeleton

Every eSMIS module follows a standard directory layout. Create the full tree first, then fill
in the files.

```
esmis_academic_term/
├── __init__.py
├── __manifest__.py
├── pyproject.toml
├── models/
│   ├── __init__.py
│   └── academic_term.py
├── views/
│   ├── academic_year_views.xml
│   ├── academic_term_views.xml
│   └── menus.xml
├── security/
│   ├── security_groups.xml
│   └── ir.model.access.csv
├── data/
│   └── academic_term_data.xml
├── tests/
│   ├── __init__.py
│   ├── test_academic_year.py
│   ├── test_academic_term.py
│   └── test_security.py
└── readme/
    └── DESCRIPTION.md
```

### `__init__.py` (root)

```python
from . import models
```

**Why:** Odoo discovers Python code through `__init__.py` imports. The root init imports
the `models` package, which in turn imports individual model files.

### `__manifest__.py`

```python
{
    "name": "Academic Term",
    "version": "19.0.1.0.0",
    "category": "eSMIS/Core",
    "summary": "Academic year and term/semester definitions for scheduling and enrollment",
    "author": "Pith Technologies",
    "website": "",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": [],
    "depends": [
        "esmis_vocabulary",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/academic_year_views.xml",
        "views/academic_term_views.xml",
        "views/menus.xml",
        "data/academic_term_data.xml",
    ],
    "demo": [],
    "auto_install": False,
    "application": False,
    "installable": True,
}
```

**Why each setting:**

| Setting | Value | Reason |
|---------|-------|--------|
| `category` | `"eSMIS/Core"` | Foundation-layer module; groups under the eSMIS/Core category in the apps list |
| `depends` | `["esmis_vocabulary"]` | We use `esmis.vocabulary.code` for term types; `esmis_vocabulary` already depends on `base` |
| `application` | `False` | Only starter modules (`esmis_starter_*`) are applications |
| `auto_install` | `False` | Must be explicitly installed or pulled in by a starter module |
| `data` order | security groups first, then ACL, then views, then data | Groups must exist before ACLs reference them; views before menus; data last because it may reference views |

### `pyproject.toml`

```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

### `models/__init__.py`

```python
from . import academic_term
```

---

## Step 2: Define the Models (TDD)

We practice TDD: write tests first, watch them fail, then implement just enough code to
make them pass.

### 2a. Write the Tests First

#### `tests/__init__.py`

```python
from . import test_academic_year
from . import test_academic_term
from . import test_security
```

#### `tests/test_academic_year.py`

```python
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAcademicYear(TransactionCase):
    """Tests for the esmis.academic.year model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AcademicYear = cls.env["esmis.academic.year"]

    def test_create_academic_year(self):
        """An academic year can be created with required fields."""
        year = self.AcademicYear.create(
            {
                "name": "AY 2025-2026",
                "date_start": "2025-06-01",
                "date_end": "2026-05-31",
            }
        )
        self.assertEqual(year.name, "AY 2025-2026")
        self.assertTrue(year.active)
        self.assertFalse(year.is_current)

    def test_date_validation(self):
        """End date must be after start date."""
        with self.assertRaises(ValidationError):
            self.AcademicYear.create(
                {
                    "name": "Invalid Year",
                    "date_start": "2026-06-01",
                    "date_end": "2025-05-31",
                }
            )

    def test_term_ids_relationship(self):
        """Academic year has a One2many relationship to terms."""
        year = self.AcademicYear.create(
            {
                "name": "AY 2025-2026",
                "date_start": "2025-06-01",
                "date_end": "2026-05-31",
            }
        )
        term_type = self.env["esmis.vocabulary.code"].get_code(
            "urn:esmis:vocabulary:academic-period-type", "semester"
        )
        self.env["esmis.academic.term"].create(
            {
                "name": "1st Semester 2025-2026",
                "academic_year_id": year.id,
                "type_id": term_type.id,
                "date_start": "2025-08-01",
                "date_end": "2025-12-15",
            }
        )
        year.invalidate_recordset()
        self.assertEqual(len(year.term_ids), 1)
```

**Why these tests:**

- `test_create_academic_year` — verifies the happy path and default values
- `test_date_validation` — business rule: end must follow start
- `test_term_ids_relationship` — confirms the One2many link to terms works

#### `tests/test_academic_term.py`

```python
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAcademicTerm(TransactionCase):
    """Tests for the esmis.academic.term model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AcademicTerm = cls.env["esmis.academic.term"]
        cls.AcademicYear = cls.env["esmis.academic.year"]
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

        cls.year = cls.AcademicYear.create(
            {
                "name": "AY 2025-2026",
                "date_start": "2025-06-01",
                "date_end": "2026-05-31",
            }
        )
        cls.semester_type = cls.VocabCode.get_code(
            "urn:esmis:vocabulary:academic-period-type", "semester"
        )

    def test_create_academic_term(self):
        """A term can be created with required fields."""
        term = self.AcademicTerm.create(
            {
                "name": "1st Semester 2025-2026",
                "academic_year_id": self.year.id,
                "type_id": self.semester_type.id,
                "date_start": "2025-08-01",
                "date_end": "2025-12-15",
            }
        )
        self.assertEqual(term.name, "1st Semester 2025-2026")
        self.assertFalse(term.is_current)
        self.assertEqual(term.company_id, self.env.company)

    def test_date_validation(self):
        """Term end date must be after start date."""
        with self.assertRaises(ValidationError):
            self.AcademicTerm.create(
                {
                    "name": "Invalid Term",
                    "academic_year_id": self.year.id,
                    "type_id": self.semester_type.id,
                    "date_start": "2025-12-15",
                    "date_end": "2025-08-01",
                }
            )

    def test_enrollment_date_validation(self):
        """Enrollment end must be after enrollment start when both are set."""
        with self.assertRaises(ValidationError):
            self.AcademicTerm.create(
                {
                    "name": "Bad Enrollment Dates",
                    "academic_year_id": self.year.id,
                    "type_id": self.semester_type.id,
                    "date_start": "2025-08-01",
                    "date_end": "2025-12-15",
                    "enrollment_start": "2025-08-15 08:00:00",
                    "enrollment_end": "2025-08-01 08:00:00",
                }
            )

    def test_type_id_uses_vocabulary(self):
        """type_id links to esmis.vocabulary.code, not a static selection."""
        term = self.AcademicTerm.create(
            {
                "name": "1st Semester 2025-2026",
                "academic_year_id": self.year.id,
                "type_id": self.semester_type.id,
                "date_start": "2025-08-01",
                "date_end": "2025-12-15",
            }
        )
        self.assertEqual(term.type_id.code, "semester")
        self.assertEqual(
            term.type_id._name,
            "esmis.vocabulary.code",
        )

    def test_company_id_defaults_to_current(self):
        """company_id defaults to the current user's company (campus)."""
        term = self.AcademicTerm.create(
            {
                "name": "1st Semester 2025-2026",
                "academic_year_id": self.year.id,
                "type_id": self.semester_type.id,
                "date_start": "2025-08-01",
                "date_end": "2025-12-15",
            }
        )
        self.assertEqual(term.company_id, self.env.company)
```

**Why these tests:**

- `test_type_id_uses_vocabulary` — enforces the eSMIS convention: vocabulary codes over
  static selections. The term type (semester, trimester, quarter, summer) comes from
  `esmis.vocabulary.code` filtered by the `academic-period-type` vocabulary.
- `test_company_id_defaults_to_current` — validates campus awareness. Every campus-scoped
  model must default `company_id` to the current company.
- Date validations — core business rules that prevent data entry errors.

### 2b. Run the Tests — Confirm They Fail

```bash
./esmis test esmis_academic_term
```

The tests must fail at this point because the models do not exist yet. If they somehow pass,
the tests are not testing what you think they are.

### 2c. Implement the Models

#### `models/academic_term.py`

```python
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AcademicYear(models.Model):
    """An academic year spanning a full institutional calendar.

    Academic years are institution-wide (no company_id) because all campuses
    share the same academic calendar as defined by CHED.
    """

    _name = "esmis.academic.year"
    _description = "Academic Year"
    _order = "date_start desc"

    name = fields.Char(
        required=True,
        help="e.g., 'AY 2025-2026'",
    )
    date_start = fields.Date(
        required=True,
        help="First day of the academic year",
    )
    date_end = fields.Date(
        required=True,
        help="Last day of the academic year",
    )
    term_ids = fields.One2many(
        comodel_name="esmis.academic.term",
        inverse_name="academic_year_id",
        string="Terms",
        help="Terms (semesters, trimesters, etc.) within this academic year",
    )
    is_current = fields.Boolean(
        default=False,
        help="Whether this is the active academic year",
    )
    active = fields.Boolean(
        default=True,
        help="Set to inactive to hide without deleting",
    )

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        """End date must be after start date."""
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end <= rec.date_start:
                raise ValidationError(
                    _("End date must be after start date.")
                )


class AcademicTerm(models.Model):
    """A term or semester within an academic year.

    Terms are campus-scoped (company_id) because different campuses may have
    different enrollment windows even within the same academic year.
    """

    _name = "esmis.academic.term"
    _description = "Academic Term"
    _order = "date_start desc"

    name = fields.Char(
        required=True,
        help="e.g., '1st Semester 2025-2026'",
    )
    academic_year_id = fields.Many2one(
        comodel_name="esmis.academic.year",
        string="Academic Year",
        required=True,
        ondelete="restrict",
        index=True,
        help="The academic year this term belongs to",
    )
    type_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Term Type",
        required=True,
        ondelete="restrict",
        domain="[('namespace_uri', '=', 'urn:esmis:vocabulary:academic-period-type')]",
        help="Type of academic period (Semester, Trimester, Quarter, etc.) "
        "from the Academic Period Type vocabulary",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Campus",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Campus this term belongs to. Each campus may have "
        "different enrollment windows for the same term.",
    )
    date_start = fields.Date(
        required=True,
        help="First day of the term",
    )
    date_end = fields.Date(
        required=True,
        help="Last day of the term",
    )
    enrollment_start = fields.Datetime(
        help="When online enrollment opens for this term",
    )
    enrollment_end = fields.Datetime(
        help="When online enrollment closes for this term",
    )
    is_current = fields.Boolean(
        default=False,
        help="Whether this is the active term for the campus",
    )
    active = fields.Boolean(
        default=True,
        help="Set to inactive to hide without deleting",
    )

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        """End date must be after start date."""
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end <= rec.date_start:
                raise ValidationError(
                    _("End date must be after start date.")
                )

    @api.constrains("enrollment_start", "enrollment_end")
    def _check_enrollment_dates(self):
        """Enrollment end must be after enrollment start when both are set."""
        for rec in self:
            if (
                rec.enrollment_start
                and rec.enrollment_end
                and rec.enrollment_end <= rec.enrollment_start
            ):
                raise ValidationError(
                    _("Enrollment end date must be after enrollment start date.")
                )
```

**Key design decisions explained:**

1. **Two models in one file** — `esmis.academic.year` and `esmis.academic.term` are tightly
   coupled (parent/child). Keeping them in one file reduces cross-file navigation. For larger
   models, split them.

2. **`type_id` uses `esmis.vocabulary.code`** — instead of `fields.Selection([('semester',
   'Semester'), ...])`, we use a Many2one to vocabulary codes. This means:
   - New term types can be added via data files without code changes
   - Different deployments can have different term types
   - The `domain` filter limits the dropdown to codes from the correct vocabulary

3. **`company_id` on term but not on year** — academic years are shared across all campuses
   (institution-wide), but terms are campus-scoped because different campuses may have
   different enrollment windows. This follows the data model registry specification.

4. **`ondelete="restrict"`** — prevents deleting an academic year that still has terms, or
   deleting a vocabulary code that is in use. Data integrity over convenience.

5. **`_order = "date_start desc"`** — most recent items appear first, which is what users
   expect when browsing academic periods.

---

## Step 3: Add Security

### Security Groups (`security/security_groups.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="category_esmis_academic_term" model="ir.module.category">
        <field name="name">eSMIS Academic Term</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_academic_term_officer" model="res.groups.privilege">
        <field name="name">Academic Term Officer</field>
        <field name="category_id" ref="category_esmis_academic_term"/>
    </record>

    <!-- Viewer: read-only access. Extension point for downstream modules
         to attach record rules (e.g., campus-scoped visibility). -->
    <record id="group_academic_term_viewer" model="res.groups">
        <field name="name">Academic Term: Viewer</field>
        <field name="comment">Read-only access to academic years and terms.
Serves as an extension point for campus-scoped record rules.</field>
        <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
    </record>

    <!-- Officer: create and edit academic years and terms -->
    <record id="group_academic_term_officer" model="res.groups">
        <field name="name">Academic Term: Officer</field>
        <field name="comment">Create and edit academic years and terms.
Implies Viewer permissions.</field>
        <field name="privilege_id" ref="privilege_academic_term_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_academic_term_viewer'))]"/>
    </record>

    <!-- Manager: full access including deletion -->
    <record id="group_academic_term_manager" model="res.groups">
        <field name="name">Academic Term: Manager</field>
        <field name="comment">Full access including deletion of academic years and terms.
Implies Officer permissions.</field>
        <field name="privilege_id" ref="privilege_academic_term_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_academic_term_officer'))]"/>
    </record>
</odoo>
```

**Key patterns from `esmis_vocabulary`:**

- **`Command.link()`** — Odoo 19 syntax. Never use tuple syntax `(4, id, 0)`.
- **Three-tier groups** — Viewer (read) -> Officer (create/edit) -> Manager (full). Each
  implies the one below it.
- **`privilege_id`** — Odoo 19 uses `res.groups.privilege` to group officer/manager under a
  single privilege toggle in Settings. The viewer group does not get a privilege because it
  is implied by `base.group_user`.
- **`comment` field** — documents what each group provides. Shows in the Odoo admin UI.

### ACL File (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_academic_year_system,esmis.academic.year / System,model_esmis_academic_year,base.group_system,1,1,1,1
access_esmis_academic_year_user,esmis.academic.year / User,model_esmis_academic_year,base.group_user,1,0,0,0
access_esmis_academic_year_officer,esmis.academic.year / Officer,model_esmis_academic_year,group_academic_term_officer,1,1,1,0
access_esmis_academic_year_manager,esmis.academic.year / Manager,model_esmis_academic_year,group_academic_term_manager,1,1,1,1
access_esmis_academic_term_system,esmis.academic.term / System,model_esmis_academic_term,base.group_system,1,1,1,1
access_esmis_academic_term_user,esmis.academic.term / User,model_esmis_academic_term,base.group_user,1,0,0,0
access_esmis_academic_term_officer,esmis.academic.term / Officer,model_esmis_academic_term,group_academic_term_officer,1,1,1,0
access_esmis_academic_term_manager,esmis.academic.term / Manager,model_esmis_academic_term,group_academic_term_manager,1,1,1,1
```

**Key rules:**

- **`base.group_system` first** — every `esmis.*` model must have a `base.group_system` row
  with full CRUD. This ensures admin/superuser always has access.
- **`base.group_user` read-only** — all internal users can read academic years and terms.
  They need this for Many2one dropdowns in forms (e.g., selecting a term on an enrollment
  record).
- **Officers can create but not delete** — deletion is a manager-only action. This prevents
  accidental removal of academic terms that other records depend on.
- **Both models covered** — every model in the module needs ACL entries. A common mistake is
  to add ACLs for the parent model and forget the child.

---

## Step 4: Create Views

### Academic Year Views (`views/academic_year_views.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_esmis_academic_year_form" model="ir.ui.view">
        <field name="name">esmis.academic.year.form</field>
        <field name="model">esmis.academic.year</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="e.g. AY 2025-2026"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="date_start"/>
                            <field name="date_end"/>
                        </group>
                        <group>
                            <field name="is_current"/>
                            <field name="active" invisible="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Terms" name="terms">
                            <field name="term_ids">
                                <list>
                                    <field name="name"/>
                                    <field name="type_id"/>
                                    <field name="company_id" groups="base.group_multi_company"/>
                                    <field name="date_start"/>
                                    <field name="date_end"/>
                                    <field name="is_current"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <record id="view_esmis_academic_year_list" model="ir.ui.view">
        <field name="name">esmis.academic.year.list</field>
        <field name="model">esmis.academic.year</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="date_start"/>
                <field name="date_end"/>
                <field name="is_current"/>
            </list>
        </field>
    </record>

    <record id="view_esmis_academic_year_search" model="ir.ui.view">
        <field name="name">esmis.academic.year.search</field>
        <field name="model">esmis.academic.year</field>
        <field name="arch" type="xml">
            <search string="Search Academic Years">
                <field name="name"/>
                <separator/>
                <filter name="current" string="Current"
                        domain="[('is_current', '=', True)]"/>
                <filter name="archived" string="Archived"
                        domain="[('active', '=', False)]"/>
            </search>
        </field>
    </record>

    <record id="action_esmis_academic_year" model="ir.actions.act_window">
        <field name="name">Academic Years</field>
        <field name="res_model">esmis.academic.year</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

### Academic Term Views (`views/academic_term_views.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_esmis_academic_term_form" model="ir.ui.view">
        <field name="name">esmis.academic.term.form</field>
        <field name="model">esmis.academic.term</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name"
                                   placeholder="e.g. 1st Semester 2025-2026"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="academic_year_id"/>
                            <field name="type_id"
                                   options="{'no_create': True, 'no_open': True}"/>
                            <field name="company_id"
                                   groups="base.group_multi_company"/>
                        </group>
                        <group>
                            <field name="date_start"/>
                            <field name="date_end"/>
                            <field name="is_current"/>
                            <field name="active" invisible="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Enrollment" name="enrollment">
                            <group>
                                <group>
                                    <field name="enrollment_start"/>
                                    <field name="enrollment_end"/>
                                </group>
                                <!-- Extension point for downstream modules -->
                                <group name="enrollment_extra" invisible="1"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <record id="view_esmis_academic_term_list" model="ir.ui.view">
        <field name="name">esmis.academic.term.list</field>
        <field name="model">esmis.academic.term</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="academic_year_id"/>
                <field name="type_id"/>
                <field name="company_id" groups="base.group_multi_company"
                       optional="show"/>
                <field name="date_start"/>
                <field name="date_end"/>
                <field name="is_current"/>
            </list>
        </field>
    </record>

    <record id="view_esmis_academic_term_search" model="ir.ui.view">
        <field name="name">esmis.academic.term.search</field>
        <field name="model">esmis.academic.term</field>
        <field name="arch" type="xml">
            <search string="Search Academic Terms">
                <field name="name"/>
                <field name="academic_year_id"/>
                <separator/>
                <filter name="current" string="Current"
                        domain="[('is_current', '=', True)]"/>
                <filter name="archived" string="Archived"
                        domain="[('active', '=', False)]"/>
                <separator/>
                <group name="group_by">
                    <filter name="group_academic_year" string="Academic Year"
                            context="{'group_by': 'academic_year_id'}"/>
                    <filter name="group_type" string="Term Type"
                            context="{'group_by': 'type_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <record id="action_esmis_academic_term" model="ir.actions.act_window">
        <field name="name">Academic Terms</field>
        <field name="res_model">esmis.academic.term</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

**Key view patterns:**

- **`options="{'no_create': True, 'no_open': True}"`** on `type_id` — prevents users from
  creating or editing vocabulary codes inline. Codes should be managed through the
  Vocabularies configuration UI.
- **`groups="base.group_multi_company"`** on `company_id` — only shows the campus field when
  multi-company mode is enabled. Single-campus deployments do not see it.
- **`optional="show"`** on list columns — lets users hide columns they do not need.
- **Extension point** — `<group name="enrollment_extra" invisible="1"/>` gives downstream
  modules a place to inject fields (e.g., `esmis_enrollment` could add enrollment stats).
- **`active` is `invisible="1"`** — the archive toggle is available via the Action menu;
  showing it as a visible field adds clutter.

### Menu Structure (`views/menus.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Configuration items under the shared eSMIS Configuration menu -->
    <menuitem
        id="menu_esmis_configuration_academic_term"
        name="Academic Terms"
        parent="esmis_vocabulary.menu_esmis_configuration"
        sequence="20"
    />
    <menuitem
        id="menu_academic_year_list"
        name="Academic Years"
        parent="menu_esmis_configuration_academic_term"
        action="action_esmis_academic_year"
        sequence="10"
    />
    <menuitem
        id="menu_academic_term_list"
        name="Terms"
        parent="menu_esmis_configuration_academic_term"
        action="action_esmis_academic_term"
        sequence="20"
    />
</odoo>
```

**Why this menu structure:**

- Configuration items go under the shared `esmis_vocabulary.menu_esmis_configuration` menu,
  not under a separate top-level menu. The project has one Configuration menu for all modules.
- The parent Configuration menu already gates on `base.group_system`, so admin-only access
  is inherited.
- Vocabulary uses sequence 10, so we use sequence 20 to appear after it.

---

## Step 5: Add Seed Data

### `data/academic_term_data.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Current academic year for initial setup.
         noupdate="1" so admin customizations survive module upgrades. -->
    <record id="academic_year_2025_2026" model="esmis.academic.year">
        <field name="name">AY 2025-2026</field>
        <field name="date_start">2025-06-01</field>
        <field name="date_end">2026-05-31</field>
        <field name="is_current" eval="True"/>
    </record>

    <record id="term_1st_semester_2025" model="esmis.academic.term">
        <field name="name">1st Semester 2025-2026</field>
        <field name="academic_year_id" ref="academic_year_2025_2026"/>
        <field name="type_id"
               ref="esmis_vocabulary.code_academic_period_type_semester"/>
        <field name="date_start">2025-08-01</field>
        <field name="date_end">2025-12-15</field>
    </record>

    <record id="term_2nd_semester_2025" model="esmis.academic.term">
        <field name="name">2nd Semester 2025-2026</field>
        <field name="academic_year_id" ref="academic_year_2025_2026"/>
        <field name="type_id"
               ref="esmis_vocabulary.code_academic_period_type_semester"/>
        <field name="date_start">2026-01-06</field>
        <field name="date_end">2026-05-15</field>
    </record>

    <record id="term_summer_2026" model="esmis.academic.term">
        <field name="name">Summer 2026</field>
        <field name="academic_year_id" ref="academic_year_2025_2026"/>
        <field name="type_id"
               ref="esmis_vocabulary.code_academic_period_type_summer"/>
        <field name="date_start">2026-05-20</field>
        <field name="date_end">2026-07-15</field>
    </record>
</odoo>
```

**Key patterns:**

- **`noupdate="1"`** — this data loads once at install. If an admin edits the dates, a
  module upgrade will not overwrite their changes.
- **`ref="esmis_vocabulary.code_academic_period_type_semester"`** — references the vocabulary
  code by its XML ID. This is why seed data files are listed after security and views in the
  manifest: the vocabulary codes must already be installed.
- **No `company_id` explicitly set** — it defaults to the current company via the field's
  `default` lambda, which is the main campus during installation.
- **Complete records** — every seed record includes all required fields. Incomplete seed data
  is a known pitfall that causes install failures.

---

## Step 6: Add the DESCRIPTION.md

### `readme/DESCRIPTION.md`

```markdown
Academic year and term definitions for eSMIS modules.

## Key Capabilities

- Define academic years with start and end dates
- Create terms (semesters, trimesters, quarters, summer) within academic years
- Mark the current academic year and term
- Configure enrollment windows per term per campus
- Campus-scoped terms allow different enrollment dates per campus

## Key Models

- `esmis.academic.year` — an academic year (e.g., AY 2025-2026), shared institution-wide
- `esmis.academic.term` — a term within a year, campus-scoped via `company_id`

## Configuration

Term types are defined in the Academic Period Type vocabulary
(`urn:esmis:vocabulary:academic-period-type`), shipped by `esmis_vocabulary`.

## UI Location

Settings > Configuration > Academic Terms

## Security

- `group_academic_term_viewer` — read-only access
- `group_academic_term_officer` — create and edit
- `group_academic_term_manager` — full access including delete

## Dependencies

- `esmis_vocabulary` — provides term type vocabulary codes
```

---

## Step 7: Write Security Tests

The security tests file was declared in `tests/__init__.py` already. Here is the content:

### `tests/test_security.py`

```python
from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestAcademicTermSecurity(TransactionCase):
    """Tests for academic term access control."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AcademicYear = cls.env["esmis.academic.year"]
        cls.AcademicTerm = cls.env["esmis.academic.term"]
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

        cls.semester_type = cls.VocabCode.get_code(
            "urn:esmis:vocabulary:academic-period-type", "semester"
        )

        cls.user_basic = cls.env["res.users"].create(
            {
                "name": "Basic User",
                "login": "academic_basic",
                "group_ids": [
                    Command.set([cls.env.ref("base.group_user").id]),
                ],
            }
        )
        cls.user_officer = cls.env["res.users"].create(
            {
                "name": "Academic Officer",
                "login": "academic_officer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref(
                                "esmis_academic_term.group_academic_term_officer"
                            ).id
                        ]
                    ),
                ],
            }
        )
        cls.user_manager = cls.env["res.users"].create(
            {
                "name": "Academic Manager",
                "login": "academic_manager",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref(
                                "esmis_academic_term.group_academic_term_manager"
                            ).id
                        ]
                    ),
                ],
            }
        )

    def test_basic_user_can_read_years(self):
        """Basic users can read academic years (needed for M2O dropdowns)."""
        years = self.AcademicYear.with_user(self.user_basic).search([])
        self.assertTrue(years)

    def test_basic_user_cannot_create_year(self):
        """Basic users cannot create academic years."""
        with self.assertRaises(AccessError):
            self.AcademicYear.with_user(self.user_basic).create(
                {
                    "name": "Unauthorized Year",
                    "date_start": "2025-06-01",
                    "date_end": "2026-05-31",
                }
            )

    def test_officer_can_create_year(self):
        """Officers can create academic years."""
        year = self.AcademicYear.with_user(self.user_officer).create(
            {
                "name": "Officer Year",
                "date_start": "2027-06-01",
                "date_end": "2028-05-31",
            }
        )
        self.assertTrue(year)

    def test_officer_cannot_delete_year(self):
        """Officers cannot delete academic years."""
        year = self.AcademicYear.with_user(self.user_officer).create(
            {
                "name": "No Delete Year",
                "date_start": "2027-06-01",
                "date_end": "2028-05-31",
            }
        )
        with self.assertRaises(AccessError):
            year.with_user(self.user_officer).unlink()

    def test_manager_can_delete_year(self):
        """Managers can delete academic years."""
        year = self.AcademicYear.with_user(self.user_manager).create(
            {
                "name": "Delete Me Year",
                "date_start": "2027-06-01",
                "date_end": "2028-05-31",
            }
        )
        year.with_user(self.user_manager).unlink()

    def test_officer_can_create_term(self):
        """Officers can create academic terms."""
        year = self.AcademicYear.with_user(self.user_officer).create(
            {
                "name": "Officer Term Year",
                "date_start": "2027-06-01",
                "date_end": "2028-05-31",
            }
        )
        term = self.AcademicTerm.with_user(self.user_officer).create(
            {
                "name": "1st Semester 2027-2028",
                "academic_year_id": year.id,
                "type_id": self.semester_type.id,
                "date_start": "2027-08-01",
                "date_end": "2027-12-15",
            }
        )
        self.assertTrue(term)
```

**Key testing patterns:**

- **`Command.set()`** — Odoo 19 syntax for setting group_ids. Replaces the old tuple
  `(6, 0, [ids])`.
- **Tests run as specific users** — `with_user(self.user_basic)` ensures we test the actual
  ACL rules, not admin bypass. A test that only runs as admin does not prove security works.
- **Test all three tiers** — basic user (read-only), officer (create/edit), manager
  (full including delete).
- **Both models tested** — year and term ACLs are separate; test them separately.

---

## Step 8: Run Tests and Linters

### Run the tests

```bash
./esmis test esmis_academic_term
```

All tests should pass. If any fail, read the error carefully — the most common issues are:

| Error | Likely cause |
|-------|-------------|
| `KeyError: 'esmis.academic.year'` | Model not imported in `models/__init__.py` |
| `AccessError` | Missing ACL row for the model/group combination |
| `ValueError: External ID not found` | XML ID typo in `ref=` attribute |
| `ParseError` | XML syntax error in a view or data file |

### Run the linters

```bash
pre-commit run ruff --files esmis_academic_term/models/*.py esmis_academic_term/tests/*.py
pre-commit run ruff-format --files esmis_academic_term/models/*.py esmis_academic_term/tests/*.py
pre-commit run prettier --files esmis_academic_term/views/*.xml esmis_academic_term/security/*.xml esmis_academic_term/data/*.xml
```

Fix any issues the linters flag before moving on.

---

## Step 9: Review Checklist

Before considering the module complete, verify every item:

### General

- [ ] Module name follows `esmis_{domain}` convention
- [ ] All models use `esmis.*` prefix (`esmis.academic.year`, `esmis.academic.term`)
- [ ] `_description` set on every model
- [ ] `application = False` and `auto_install = False`
- [ ] No `print()` — only `_logger`
- [ ] No bare `except:` — specific exceptions only
- [ ] No PII in log messages
- [ ] `readme/DESCRIPTION.md` exists (25-60 lines, no marketing language)

### Fields

- [ ] Boolean fields use `is_*` prefix (`is_current`)
- [ ] Many2one fields use `{model}_id` pattern (`academic_year_id`, `type_id`, `company_id`)
- [ ] One2many fields use `{model}_ids` pattern (`term_ids`)
- [ ] No static `Selection` for values that should be vocabulary-backed (`type_id` uses vocabulary)
- [ ] `help=` on fields where the label is ambiguous

### Security

- [ ] `ir.model.access.csv` exists with entries for **every** model
- [ ] `base.group_system` full CRUD row present for every model
- [ ] `base.group_user` read-only row present (needed for M2O dropdowns)
- [ ] ACL entry IDs follow `access_{model}_{group}` pattern
- [ ] Security groups use `Command.link()` in `implied_ids`

### SIS-Specific

- [ ] `company_id` field on campus-scoped models (`esmis.academic.term`)
- [ ] Campus field uses `groups="base.group_multi_company"` in views
- [ ] Vocabulary codes referenced with `domain` filter on the namespace URI

### Tests

- [ ] Tests exist for all models
- [ ] Tests run with appropriate user context, not just admin
- [ ] Date validation tests cover edge cases
- [ ] Security tests cover all three tiers (basic, officer, manager)
- [ ] All tests pass: `./esmis test esmis_academic_term`
- [ ] Linters pass: `pre-commit run --files <changed_files>`

---

## What Comes Next

This tutorial covered the mechanics of building a module by hand. In practice, you would use
the `/implement` command, which orchestrates the full TDD workflow with subagents:

1. `/implement` generates tests from the spec
2. A developer subagent implements the code to make tests pass
3. A code reviewer subagent checks security, naming, and Odoo 19 compliance
4. `/verify-tests` confirms no tests were removed or weakened

The real `esmis_academic_term` module will be built this way. This tutorial exists so you
understand what those tools are doing under the hood.

## Further Reading

- [Module Development Guide](module-development.md) — scaffold templates and full conventions
- [Data Model Registry](../architecture/data-model-registry.md) — all planned models and their fields
- [Naming Conventions](../principles/naming-conventions.md) — field, model, and XML ID naming rules
- [Access Rights](../principles/access-rights.md) — three-tier security architecture
