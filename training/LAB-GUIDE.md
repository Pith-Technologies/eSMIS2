# Hands-On Lab Guide: Student Information System

> **Author**: Edwin Gonzales **Last Updated**: March 4, 2026 **Duration**: 2 hours **Prerequisites**: Python
> proficiency, basic Odoo familiarity, tools installed per **SETUP.md** > **Outcome**: 4 modules + web portal, all with
> tests and security

Make sure you have completed **SETUP.md** before starting. Keep **REFERENCE.md** open in a second tab for quick lookups.

---

## Phase 0: Environment Setup (15 min)

**Goal**: Unzip the template, initialize the project, set up Git, and verify everything works.

**What you'll learn**: The `init` command, `doctor` check, basic `odoo-project` CLI usage, and Git initialization.

### Step 0.1 — Unzip and Initialize

Your instructor has provided a ZIP file of the project template. Unzip it into your working directory:

```bash
unzip template-project.zip -d sis-project
cd sis-project
```

Now run the `init` command to transform the template into your Student Information System:

```bash
./odoo-project init sis "Student Information System"
```

This replaces all `tpl_` prefixes with `sis_` throughout the project:

- `tpl_vocabulary/` → `sis_vocabulary/`
- `tpl.vocabulary` → `sis.vocabulary`
- `{Project}` → `Student Information System`

### Step 0.2 — Initialize Git

The ZIP file does not include Git history, so initialize a fresh repository:

```bash
git init
git add -A
git commit -m "chore: initialize SIS project from template"
```

This gives you a clean starting point. Later, you can push this to your own GitHub account:

```bash
git remote add origin https://github.com/<your-username>/sis-project.git
git push -u origin main
```

> **Note**: The `git remote add` and `push` steps are optional during the lab. You can do this after the training.

### Step 0.3 — Check Prerequisites

```bash
./odoo-project doctor
```

You should see green checks for Docker, Docker Compose, and Git. Fix any issues before proceeding.

### Step 0.4 — Build and Start

```bash
./odoo-project build
./odoo-project start
```

Wait for the health check to pass (up to 90 seconds on first run), then open <http://localhost:8069>.

- **Login**: `admin` / `admin`
- Navigate to **Settings → Technical → Vocabularies** to confirm `sis_vocabulary` installed
- You should see three vocabularies: Gender (ISO 5218), Civil Status, Blood Type

### Step 0.5 — Tour the Template

Look at the `sis_vocabulary/` module to understand the structure:

```
sis_vocabulary/
├── __init__.py                  # Package init
├── __manifest__.py              # Module metadata
├── models/
│   ├── __init__.py
│   ├── vocabulary.py            # sis.vocabulary model
│   └── vocabulary_code.py       # sis.vocabulary.code model
├── views/
│   ├── vocabulary_views.xml
│   ├── vocabulary_code_views.xml
│   └── menus.xml
├── security/
│   ├── ir.model.access.csv      # ACLs (who can do what)
│   └── security_groups.xml      # Group hierarchy
├── data/                        # Seed data (Gender, Civil Status, Blood Type)
└── tests/                       # 35 test methods across 4 files
```

Read `CLAUDE.md` at the project root — it defines conventions, the quick checklist, and how Claude Code is configured.

**Checkpoint**: Odoo is running at port 8069, you can see Vocabularies in the UI, and you understand the module
structure.

---

## Phase 1: Student Module — `sis_student` (40 min)

**Goal**: Create a module that extends `res.partner` to manage student records.

**What you'll learn**: Inherit-and-extend pattern, vocabulary fields, three-tier security, views, testing.

### Step 1.1 — Create the Module Scaffold

Create the directory structure:

```bash
mkdir -p sis_student/{models,views,security,tests}
```

Create the package init files:

**`sis_student/__init__.py`**:

```python
from . import models
```

**`sis_student/models/__init__.py`**:

```python
from . import res_partner
```

**`sis_student/tests/__init__.py`**:

```python
from . import test_student
```

### Step 1.2 — Write the Manifest

**`sis_student/__manifest__.py`**:

```python
{
    "name": "Student",
    "version": "19.0.1.0.0",
    "category": "Student Information System/Core",
    "summary": "Student records extending contacts",
    "license": "LGPL-3",
    "depends": ["base", "sis_vocabulary"],
    "data": [
        "security/security_groups.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "development_status": "Alpha",
    "application": False,
    "auto_install": False,
    "installable": True,
    "maintainers": [],
}
```

Note: We depend on `sis_vocabulary` so we can use vocabulary fields, and `base` for `res.partner`. No
`ir.model.access.csv` is needed because we're extending `res.partner`, which already has ACLs from Odoo core.

### Step 1.3 — Write the Tests First (TDD)

**`sis_student/tests/test_student.py`**:

```python
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStudent(TransactionCase):
    """Tests for student records on res.partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)

    def test_create_student(self):
        """A student can be created with required fields."""
        student = self.Partner.create(
            {
                "name": "Alice Johnson",
                "is_student": True,
                "student_number": "STU-001",
            }
        )
        self.assertTrue(student.is_student)
        self.assertEqual(student.student_number, "STU-001")

    def test_student_number_required_when_student(self):
        """Student number is required when is_student is True."""
        with self.assertRaises(ValidationError):
            self.Partner.create(
                {
                    "name": "Bob Smith",
                    "is_student": True,
                    "student_number": False,
                }
            )

    def test_student_number_unique(self):
        """No two students can share the same student number."""
        self.Partner.create(
            {
                "name": "Alice Johnson",
                "is_student": True,
                "student_number": "STU-001",
            }
        )
        with self.assertRaises(Exception):
            self.Partner.create(
                {
                    "name": "Bob Smith",
                    "is_student": True,
                    "student_number": "STU-001",
                }
            )

    def test_non_student_no_number_required(self):
        """Non-students do not require a student number."""
        partner = self.Partner.create(
            {
                "name": "Regular Contact",
                "is_student": False,
            }
        )
        self.assertFalse(partner.is_student)

    def test_gender_vocabulary_field(self):
        """Gender can be set from the vocabulary."""
        gender_code = self.env["sis.vocabulary.code"].search(
            [("namespace_uri", "=", "urn:iso:std:iso:5218"), ("code", "=", "2")],
            limit=1,
        )
        student = self.Partner.create(
            {
                "name": "Carol Davis",
                "is_student": True,
                "student_number": "STU-002",
                "gender_id": gender_code.id,
            }
        )
        self.assertEqual(student.gender_id, gender_code)
```

Run the tests — they should fail (modules not yet implemented):

```bash
./odoo-project test sis_student
```

### Step 1.4 — Implement the Model

**`sis_student/models/res_partner.py`**:

```python
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_student = fields.Boolean(
        string="Is Student",
        default=False,
        help="Check if this contact is a student.",
    )
    student_number = fields.Char(
        string="Student Number",
        index=True,
        copy=False,
        help="Unique identifier for the student (e.g., STU-001).",
    )
    enrollment_date = fields.Date(
        string="Enrollment Date",
        help="Date the student enrolled in the institution.",
    )
    program = fields.Char(
        string="Program",
        help="Academic program the student is enrolled in.",
    )
    gender_id = fields.Many2one(
        "sis.vocabulary.code",
        string="Gender",
        domain="[('namespace_uri', '=', 'urn:iso:std:iso:5218')]",
        help="Gender identity from ISO 5218 standard.",
    )

    _student_number_unique = models.Constraint(
        "UNIQUE(student_number)",
        "Student number must be unique.",
    )

    @api.constrains("is_student", "student_number")
    def _check_student_number_required(self):
        for record in self:
            if record.is_student and not record.student_number:
                raise ValidationError(
                    _("Student number is required for students.")
                )
```

### Step 1.5 — Add Security

**`sis_student/security/security_groups.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="category_sis_student" model="ir.module.category">
        <field name="name">sis Student</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_student_officer" model="res.groups.privilege">
        <field name="name">Student Officer</field>
        <field name="category_id" ref="category_sis_student"/>
    </record>

    <record id="group_student_viewer" model="res.groups">
        <field name="name">Student: Viewer</field>
        <field name="comment">Read-only access to student records.</field>
        <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
    </record>

    <record id="group_student_officer" model="res.groups">
        <field name="name">Student: Officer</field>
        <field name="comment">Create and edit student records.</field>
        <field name="privilege_id" ref="privilege_student_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_student_viewer'))]"/>
    </record>

    <record id="group_student_manager" model="res.groups">
        <field name="name">Student: Manager</field>
        <field name="comment">Full access including deletion of student records.</field>
        <field name="privilege_id" ref="privilege_student_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_student_officer'))]"/>
    </record>
</odoo>
```

**`sis_student/security/ir.model.access.csv`**:

Since we're extending `res.partner` (not creating a new model), `res.partner` already has ACLs in Odoo core. We don't
need additional ACL rows for the partner model itself.

> **Note**: When you inherit an existing model with `_inherit` (no new `_name`), the base model's ACLs still apply. You
> only need new ACL rows when creating a standalone model (like `sis.course` in Phase 2). We still define security
> groups here so we can use them for menu visibility and future record rules.

Since we have no new model to protect, we can omit the ACL file from the manifest. Remove the
`"security/ir.model.access.csv"` line from `__manifest__.py` — you don't need to create the file at all. (Keep
`security_groups.xml` — that defines the groups we need.)

### Step 1.6 — Create Views

**`sis_student/views/res_partner_views.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Extend partner form to add student fields -->
    <record id="view_partner_student_form" model="ir.ui.view">
        <field name="name">res.partner.student.form</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <xpath expr="//page[1]" position="before">
                <page string="Student Info" name="student_info"
                      invisible="not is_student">
                    <group>
                        <group string="Academic">
                            <field name="student_number"/>
                            <field name="enrollment_date"/>
                            <field name="program"/>
                        </group>
                        <group string="Personal">
                            <field name="gender_id"/>
                        </group>
                    </group>
                </page>
            </xpath>
            <xpath expr="//field[@name='company_type']" position="after">
                <field name="is_student"/>
            </xpath>
        </field>
    </record>

    <!-- Student list view (filtered) -->
    <record id="view_student_list" model="ir.ui.view">
        <field name="name">res.partner.student.list</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <list>
                <field name="student_number"/>
                <field name="name"/>
                <field name="program"/>
                <field name="enrollment_date"/>
                <field name="gender_id"/>
            </list>
        </field>
    </record>

    <!-- Student search view -->
    <record id="view_student_search" model="ir.ui.view">
        <field name="name">res.partner.student.search</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="student_number"/>
                <field name="program"/>
            </search>
        </field>
    </record>

    <!-- Action to view students only -->
    <record id="action_sis_student" model="ir.actions.act_window">
        <field name="name">Students</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">list,form</field>
        <field name="domain">[('is_student', '=', True)]</field>
        <field name="context">{'default_is_student': True}</field>
        <field name="view_ids" eval="[
            Command.create({'view_mode': 'list', 'view_id': ref('view_student_list')}),
        ]"/>
    </record>
</odoo>
```

**`sis_student/views/menus.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Root SIS menu -->
    <menuitem id="menu_sis_root"
              name="SIS"
              sequence="50"/>

    <menuitem id="menu_sis_student"
              name="Students"
              parent="menu_sis_root"
              action="action_sis_student"
              sequence="10"/>
</odoo>
```

### Step 1.7 — Run Tests

```bash
./odoo-project test sis_student
```

All 5 tests should pass. If you get errors, check:

- `__init__.py` files import correctly
- `__manifest__.py` depends includes `sis_vocabulary`
- Field names match between model and tests

### Step 1.8 — Verify in the UI

```bash
./odoo-project stop -v -y
./odoo-project start --demo=base
```

After restart:

1. Go to **SIS → Students** in the top menu
2. Create a new student: set "Is Student" checkbox, fill in Student Number, Name, Program
3. The "Student Info" tab should appear with academic and personal fields
4. Try creating a duplicate student number — it should be rejected

**Checkpoint**: `sis_student` tests pass, students appear in the UI with vocabulary-based gender field.

---

## Phase 2: Course Module — `sis_course` (25 min)

**Goal**: Create a standalone course catalog model.

**What you'll learn**: Creating a new model (not inheriting), full ACL setup, basic CRUD views.

### Step 2.1 — Create the Module Scaffold

```bash
mkdir -p sis_course/{models,views,security,tests}
```

**`sis_course/__init__.py`**:

```python
from . import models
```

**`sis_course/models/__init__.py`**:

```python
from . import course
```

**`sis_course/tests/__init__.py`**:

```python
from . import test_course
```

### Step 2.2 — Write the Manifest

**`sis_course/__manifest__.py`**:

```python
{
    "name": "Course",
    "version": "19.0.1.0.0",
    "category": "Student Information System/Core",
    "summary": "Course catalog management",
    "license": "LGPL-3",
    "depends": ["base", "sis_student"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/course_views.xml",
        "views/menus.xml",
    ],
    "development_status": "Alpha",
    "application": False,
    "auto_install": False,
    "installable": True,
    "maintainers": [],
}
```

### Step 2.3 — Write Tests First

**`sis_course/tests/test_course.py`**:

```python
from odoo.tests.common import TransactionCase


class TestCourse(TransactionCase):
    """Tests for the sis.course model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Course = cls.env["sis.course"]

    def test_create_course(self):
        """A course can be created with required fields."""
        course = self.Course.create(
            {
                "name": "Introduction to Computer Science",
                "code": "CS101",
                "credit_hours": 3,
            }
        )
        self.assertEqual(course.name, "Introduction to Computer Science")
        self.assertEqual(course.code, "CS101")
        self.assertEqual(course.credit_hours, 3)
        self.assertTrue(course.active)

    def test_course_code_unique(self):
        """No two courses can share the same code."""
        self.Course.create(
            {
                "name": "Intro to CS",
                "code": "CS101",
            }
        )
        with self.assertRaises(Exception):
            self.Course.create(
                {
                    "name": "Another CS Course",
                    "code": "CS101",
                }
            )

    def test_course_active_default(self):
        """Courses are active by default."""
        course = self.Course.create(
            {
                "name": "Math 101",
                "code": "MATH101",
            }
        )
        self.assertTrue(course.active)

    def test_course_archive(self):
        """A course can be archived."""
        course = self.Course.create(
            {
                "name": "Retired Course",
                "code": "OLD001",
            }
        )
        course.active = False
        self.assertFalse(course.active)
```

### Step 2.4 — Implement the Model

**`sis_course/models/course.py`**:

```python
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Course(models.Model):
    _name = "sis.course"
    _description = "Course"
    _order = "code"

    name = fields.Char(
        string="Course Name",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Course Code",
        required=True,
        index=True,
        help="Unique course identifier (e.g., CS101).",
    )
    description = fields.Html(
        string="Description",
        translate=True,
        help="Detailed course description.",
    )
    credit_hours = fields.Integer(
        string="Credit Hours",
        default=0,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "Course code must be unique.",
    )
```

### Step 2.5 — Add Security

This is a standalone model, so we need the full ACL setup.

**`sis_course/security/security_groups.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="category_sis_course" model="ir.module.category">
        <field name="name">sis Course</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_course_officer" model="res.groups.privilege">
        <field name="name">Course Officer</field>
        <field name="category_id" ref="category_sis_course"/>
    </record>

    <record id="group_course_viewer" model="res.groups">
        <field name="name">Course: Viewer</field>
        <field name="comment">Read-only access to courses.</field>
        <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
    </record>

    <record id="group_course_officer" model="res.groups">
        <field name="name">Course: Officer</field>
        <field name="comment">Create and edit courses.</field>
        <field name="privilege_id" ref="privilege_course_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_course_viewer'))]"/>
    </record>

    <record id="group_course_manager" model="res.groups">
        <field name="name">Course: Manager</field>
        <field name="comment">Full access including deletion of courses.</field>
        <field name="privilege_id" ref="privilege_course_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_course_officer'))]"/>
    </record>
</odoo>
```

**`sis_course/security/ir.model.access.csv`**:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sis_course_system,sis.course / System,model_sis_course,base.group_system,1,1,1,1
access_sis_course_user,sis.course / User,model_sis_course,base.group_user,1,0,0,0
access_sis_course_officer,sis.course / Officer,model_sis_course,group_course_officer,1,1,1,0
access_sis_course_manager,sis.course / Manager,model_sis_course,group_course_manager,1,1,1,1
```

Note the pattern:

- **Row 1**: `base.group_system` — admin always gets full CRUD
- **Row 2**: `base.group_user` — all internal users can read (for dropdowns in other modules)
- **Row 3**: Officer — create, read, write (no delete)
- **Row 4**: Manager — full CRUD

### Step 2.6 — Create Views

**`sis_course/views/course_views.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Course form view -->
    <record id="view_sis_course_form" model="ir.ui.view">
        <field name="name">sis.course.form</field>
        <field name="model">sis.course</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" placeholder="Course Name"/>
                        </h1>
                    </div>
                    <group>
                        <group string="Details">
                            <field name="code"/>
                            <field name="credit_hours"/>
                        </group>
                        <group string="Status">
                            <field name="active" invisible="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description" name="description">
                            <field name="description"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Course list view -->
    <record id="view_sis_course_list" model="ir.ui.view">
        <field name="name">sis.course.list</field>
        <field name="model">sis.course</field>
        <field name="arch" type="xml">
            <list>
                <field name="code"/>
                <field name="name"/>
                <field name="credit_hours"/>
            </list>
        </field>
    </record>

    <!-- Course search view -->
    <record id="view_sis_course_search" model="ir.ui.view">
        <field name="name">sis.course.search</field>
        <field name="model">sis.course</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="code"/>
                <filter name="archived" string="Archived"
                        domain="[('active', '=', False)]"/>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_sis_course" model="ir.actions.act_window">
        <field name="name">Courses</field>
        <field name="res_model">sis.course</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

**`sis_course/views/menus.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="menu_sis_course"
              name="Courses"
              parent="sis_student.menu_sis_root"
              action="action_sis_course"
              sequence="20"/>
</odoo>
```

Note: We reuse the root SIS menu from `sis_student` via `sis_student.menu_sis_root` — this is why `sis_student` is in
the `depends` list. The course model itself only needs `base`, but the menu reference creates the dependency.

### Step 2.7 — Run Tests

```bash
./odoo-project test sis_course
```

All 4 tests should pass.

### Step 2.8 — Verify in the UI

Restart Odoo to pick up the new module:

```bash
./odoo-project stop -v -y
./odoo-project start --demo=base
```

Then install `sis_course`:

1. Go to **Apps**, search for "Course"
2. Install the module
3. Navigate to **SIS → Courses**
4. Create a few courses (CS101, MATH201, ENG102)

**Checkpoint**: `sis_course` tests pass, courses appear in the UI, duplicate codes are rejected.

---

## Phase 3: Enrollment Module — `sis_enrollment` (20 min)

**Goal**: Link students to courses with a state machine workflow.

**What you'll learn**: Many2one relations, state machines, action buttons, SQL constraints, status bar.

### Step 3.1 — Create the Module Scaffold

```bash
mkdir -p sis_enrollment/{models,views,security,tests}
```

**`sis_enrollment/__init__.py`**:

```python
from . import models
```

**`sis_enrollment/models/__init__.py`**:

```python
from . import enrollment
```

**`sis_enrollment/tests/__init__.py`**:

```python
from . import test_enrollment
```

### Step 3.2 — Write the Manifest

**`sis_enrollment/__manifest__.py`**:

```python
{
    "name": "Enrollment",
    "version": "19.0.1.0.0",
    "category": "Student Information System/Core",
    "summary": "Student course enrollment with state management",
    "license": "LGPL-3",
    "depends": ["sis_student", "sis_course"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/enrollment_views.xml",
        "views/menus.xml",
    ],
    "development_status": "Alpha",
    "application": False,
    "auto_install": False,
    "installable": True,
    "maintainers": [],
}
```

### Step 3.3 — Write Tests First

**`sis_enrollment/tests/test_enrollment.py`**:

```python
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestEnrollment(TransactionCase):
    """Tests for the sis.enrollment model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.Course = cls.env["sis.course"]
        cls.Enrollment = cls.env["sis.enrollment"]

        cls.student = cls.Partner.create(
            {
                "name": "Alice Johnson",
                "is_student": True,
                "student_number": "STU-ENR-001",
            }
        )
        cls.course = cls.Course.create(
            {
                "name": "Intro to CS",
                "code": "CS101-ENR",
            }
        )

    def test_create_enrollment(self):
        """An enrollment can be created linking student and course."""
        enrollment = self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        self.assertEqual(enrollment.state, "draft")
        self.assertTrue(enrollment.enrollment_date)

    def test_enroll_transition(self):
        """Draft enrollment can be moved to enrolled state."""
        enrollment = self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        enrollment.action_enroll()
        self.assertEqual(enrollment.state, "enrolled")

    def test_complete_transition(self):
        """Enrolled state can transition to completed."""
        enrollment = self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        enrollment.action_enroll()
        enrollment.action_complete()
        self.assertEqual(enrollment.state, "completed")

    def test_drop_transition(self):
        """Enrolled state can transition to dropped."""
        enrollment = self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        enrollment.action_enroll()
        enrollment.action_drop()
        self.assertEqual(enrollment.state, "dropped")

    def test_cannot_enroll_from_completed(self):
        """Cannot transition back to enrolled from completed."""
        enrollment = self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        enrollment.action_enroll()
        enrollment.action_complete()
        with self.assertRaises(UserError):
            enrollment.action_enroll()

    def test_duplicate_enrollment_rejected(self):
        """A student cannot enroll in the same course twice."""
        self.Enrollment.create(
            {
                "student_id": self.student.id,
                "course_id": self.course.id,
            }
        )
        with self.assertRaises(Exception):
            self.Enrollment.create(
                {
                    "student_id": self.student.id,
                    "course_id": self.course.id,
                }
            )
```

### Step 3.4 — Implement the Model

**`sis_enrollment/models/enrollment.py`**:

```python
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Enrollment(models.Model):
    _name = "sis.enrollment"
    _description = "Enrollment"
    _order = "enrollment_date desc"

    student_id = fields.Many2one(
        "res.partner",
        string="Student",
        required=True,
        index=True,
        domain="[('is_student', '=', True)]",
        ondelete="restrict",
    )
    course_id = fields.Many2one(
        "sis.course",
        string="Course",
        required=True,
        index=True,
        ondelete="restrict",
    )
    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("completed", "Completed"),
            ("dropped", "Dropped"),
        ],
        string="Status",
        default="draft",
        required=True,
        index=True,
    )

    _student_course_unique = models.Constraint(
        "UNIQUE(student_id, course_id)",
        "A student cannot enroll in the same course twice.",
    )

    def action_enroll(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("Only draft enrollments can be confirmed. "
                      "Current state: %s.") % record.state
                )
            record.state = "enrolled"

    def action_complete(self):
        for record in self:
            if record.state != "enrolled":
                raise UserError(
                    _("Only enrolled records can be marked as completed. "
                      "Current state: %s.") % record.state
                )
            record.state = "completed"

    def action_drop(self):
        for record in self:
            if record.state != "enrolled":
                raise UserError(
                    _("Only enrolled records can be dropped. "
                      "Current state: %s.") % record.state
                )
            record.state = "dropped"
```

### Step 3.5 — Add Security

**`sis_enrollment/security/security_groups.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="category_sis_enrollment" model="ir.module.category">
        <field name="name">sis Enrollment</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_enrollment_officer" model="res.groups.privilege">
        <field name="name">Enrollment Officer</field>
        <field name="category_id" ref="category_sis_enrollment"/>
    </record>

    <record id="group_enrollment_viewer" model="res.groups">
        <field name="name">Enrollment: Viewer</field>
        <field name="comment">Read-only access to enrollments.</field>
        <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
    </record>

    <record id="group_enrollment_officer" model="res.groups">
        <field name="name">Enrollment: Officer</field>
        <field name="comment">Create and edit enrollments.</field>
        <field name="privilege_id" ref="privilege_enrollment_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_enrollment_viewer'))]"/>
    </record>

    <record id="group_enrollment_manager" model="res.groups">
        <field name="name">Enrollment: Manager</field>
        <field name="comment">Full access including deletion of enrollments.</field>
        <field name="privilege_id" ref="privilege_enrollment_officer"/>
        <field name="implied_ids" eval="[Command.link(ref('group_enrollment_officer'))]"/>
    </record>
</odoo>
```

**`sis_enrollment/security/ir.model.access.csv`**:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sis_enrollment_system,sis.enrollment / System,model_sis_enrollment,base.group_system,1,1,1,1
access_sis_enrollment_user,sis.enrollment / User,model_sis_enrollment,base.group_user,1,0,0,0
access_sis_enrollment_officer,sis.enrollment / Officer,model_sis_enrollment,group_enrollment_officer,1,1,1,0
access_sis_enrollment_manager,sis.enrollment / Manager,model_sis_enrollment,group_enrollment_manager,1,1,1,1
```

### Step 3.6 — Create Views

**`sis_enrollment/views/enrollment_views.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Enrollment form view -->
    <record id="view_sis_enrollment_form" model="ir.ui.view">
        <field name="name">sis.enrollment.form</field>
        <field name="model">sis.enrollment</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_enroll" string="Enroll"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_complete" string="Complete"
                            type="object" class="btn-primary"
                            invisible="state != 'enrolled'"/>
                    <button name="action_drop" string="Drop"
                            type="object" class="btn-danger"
                            invisible="state != 'enrolled'"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,enrolled,completed"/>
                </header>
                <sheet>
                    <group>
                        <group string="Enrollment">
                            <field name="student_id"/>
                            <field name="course_id"/>
                        </group>
                        <group string="Details">
                            <field name="enrollment_date"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Enrollment list view -->
    <record id="view_sis_enrollment_list" model="ir.ui.view">
        <field name="name">sis.enrollment.list</field>
        <field name="model">sis.enrollment</field>
        <field name="arch" type="xml">
            <list>
                <field name="student_id"/>
                <field name="course_id"/>
                <field name="enrollment_date"/>
                <field name="state" widget="badge"
                       decoration-info="state == 'draft'"
                       decoration-success="state == 'enrolled'"
                       decoration-muted="state == 'completed'"
                       decoration-danger="state == 'dropped'"/>
            </list>
        </field>
    </record>

    <!-- Enrollment search view -->
    <record id="view_sis_enrollment_search" model="ir.ui.view">
        <field name="name">sis.enrollment.search</field>
        <field name="model">sis.enrollment</field>
        <field name="arch" type="xml">
            <search>
                <field name="student_id"/>
                <field name="course_id"/>
                <filter name="draft" string="Draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter name="enrolled" string="Enrolled"
                        domain="[('state', '=', 'enrolled')]"/>
                <filter name="completed" string="Completed"
                        domain="[('state', '=', 'completed')]"/>
                <separator/>
                <group string="Group By">
                    <filter name="group_student" string="Student"
                            context="{'group_by': 'student_id'}"/>
                    <filter name="group_course" string="Course"
                            context="{'group_by': 'course_id'}"/>
                    <filter name="group_state" string="Status"
                            context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_sis_enrollment" model="ir.actions.act_window">
        <field name="name">Enrollments</field>
        <field name="res_model">sis.enrollment</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

**`sis_enrollment/views/menus.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="menu_sis_enrollment"
              name="Enrollments"
              parent="sis_student.menu_sis_root"
              action="action_sis_enrollment"
              sequence="30"/>
</odoo>
```

### Step 3.7 — Run Tests

```bash
./odoo-project test sis_enrollment
```

All 6 tests should pass.

### Step 3.8 — Verify in the UI

Restart and install:

```bash
./odoo-project stop -v -y
./odoo-project start --demo=base
```

1. Install `sis_enrollment` from **Apps**
2. Create a student and a course if you don't have any
3. Go to **SIS → Enrollments**, create a new enrollment
4. Walk through the state machine: Draft → **Enroll** → **Complete** (or **Drop**)
5. Notice the status bar at the top and the colored badges in the list view
6. Try enrolling the same student in the same course twice — it should be rejected

**Checkpoint**: `sis_enrollment` tests pass, state machine works in the UI, duplicate enrollments are rejected.

---

## Phase 4: Student Portal — `sis_portal` (20 min)

**Goal**: Let logged-in students view their enrollments on the web frontend.

**What you'll learn**: Portal controllers, QWeb templates, record rules for portal users.

### Step 4.1 — Create the Module Scaffold

```bash
mkdir -p sis_portal/{controllers,views,security,tests}
```

**`sis_portal/__init__.py`**:

```python
from . import controllers
```

**`sis_portal/controllers/__init__.py`**:

```python
from . import portal
```

**`sis_portal/tests/__init__.py`**:

```python
from . import test_portal
```

### Step 4.2 — Write the Manifest

**`sis_portal/__manifest__.py`**:

```python
{
    "name": "Student Portal",
    "version": "19.0.1.0.0",
    "category": "Student Information System/Core",
    "summary": "Web portal for students to view enrollments",
    "license": "LGPL-3",
    "depends": ["portal", "sis_enrollment"],
    "data": [
        "security/ir.model.access.csv",
        "security/security_rules.xml",
        "views/portal_templates.xml",
    ],
    "development_status": "Alpha",
    "application": False,
    "auto_install": False,
    "installable": True,
    "maintainers": [],
}
```

### Step 4.3 — Write Tests First

**`sis_portal/tests/test_portal.py`**:

```python
from odoo import Command
from odoo.tests.common import HttpCase


class TestPortal(HttpCase):
    """Tests for the student portal."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a portal user with student data
        cls.portal_user = cls.env["res.users"].with_context(
            tracking_disable=True, no_reset_password=True
        ).create(
            {
                "name": "Portal Student",
                "login": "portal_student@example.com",
                "password": "portal_student@example.com",
                "email": "portal_student@example.com",
                "groups_id": [
                    Command.set([cls.env.ref("base.group_portal").id])
                ],
            }
        )
        cls.portal_user.partner_id.write(
            {
                "is_student": True,
                "student_number": "STU-PORTAL-001",
            }
        )
        cls.course = cls.env["sis.course"].create(
            {
                "name": "Portal Test Course",
                "code": "PTC101",
            }
        )
        cls.enrollment = cls.env["sis.enrollment"].create(
            {
                "student_id": cls.portal_user.partner_id.id,
                "course_id": cls.course.id,
                "state": "enrolled",
            }
        )

    def test_portal_enrollments_page(self):
        """Portal user can access their enrollments page."""
        self.authenticate("portal_student@example.com", "portal_student@example.com")
        response = self.url_open("/my/enrollments")
        self.assertEqual(response.status_code, 200)

    def test_portal_enrollment_detail(self):
        """Portal user can access an enrollment detail page."""
        self.authenticate("portal_student@example.com", "portal_student@example.com")
        response = self.url_open(f"/my/enrollments/{self.enrollment.id}")
        self.assertEqual(response.status_code, 200)

    def test_portal_user_sees_only_own_enrollments(self):
        """Portal user can only access their own enrollment records."""
        # Create another student's enrollment
        other_student = self.env["res.partner"].with_context(
            tracking_disable=True
        ).create(
            {
                "name": "Other Student",
                "is_student": True,
                "student_number": "STU-PORTAL-002",
            }
        )
        other_enrollment = self.env["sis.enrollment"].create(
            {
                "student_id": other_student.id,
                "course_id": self.course.id,
            }
        )
        self.authenticate("portal_student@example.com", "portal_student@example.com")
        # Trying to access another student's enrollment should not return 200
        response = self.url_open(
            f"/my/enrollments/{other_enrollment.id}", allow_redirects=False
        )
        self.assertNotEqual(response.status_code, 200)
```

### Step 4.4 — Add Security

Portal users need read access to enrollments and courses, but only for their own records.

**`sis_portal/security/ir.model.access.csv`**:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sis_enrollment_portal,sis.enrollment / Portal,sis_enrollment.model_sis_enrollment,base.group_portal,1,0,0,0
access_sis_course_portal,sis.course / Portal,sis_course.model_sis_course,base.group_portal,1,0,0,0
```

**`sis_portal/security/security_rules.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Portal users can only see their own enrollments -->
        <record id="rule_enrollment_portal_own" model="ir.rule">
            <field name="name">Portal: own enrollments only</field>
            <field name="model_id" ref="sis_enrollment.model_sis_enrollment"/>
            <field name="domain_force">[('student_id', '=', user.partner_id.id)]</field>
            <field name="groups" eval="[Command.link(ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="False"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

### Step 4.5 — Implement the Controller

**`sis_portal/controllers/portal.py`**:

```python
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "enrollment_count" in counters:
            partner = request.env.user.partner_id
            values["enrollment_count"] = (
                request.env["sis.enrollment"].search_count(
                    [("student_id", "=", partner.id)]
                )
            )
        return values

    @http.route(
        ["/my/enrollments"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_enrollments(self, **kwargs):
        partner = request.env.user.partner_id
        enrollments = request.env["sis.enrollment"].search(
            [("student_id", "=", partner.id)],
            order="enrollment_date desc",
        )
        values = {
            "enrollments": enrollments,
            "page_name": "enrollments",
        }
        return request.render(
            "sis_portal.portal_my_enrollments", values
        )

    @http.route(
        ["/my/enrollments/<int:enrollment_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_enrollment_detail(self, enrollment_id, **kwargs):
        try:
            enrollment = self._document_check_access(
                "sis.enrollment", enrollment_id
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = {
            "enrollment": enrollment,
            "page_name": "enrollment_detail",
        }
        return request.render(
            "sis_portal.portal_enrollment_detail", values
        )
```

### Step 4.6 — Create QWeb Templates

**`sis_portal/views/portal_templates.xml`**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add "Enrollments" card to /my home page -->
    <template id="portal_my_home_enrollment"
              name="Show Enrollments"
              inherit_id="portal.portal_my_home"
              customize_show="True"
              priority="40">
        <xpath expr="//div[hasclass('o_portal_docs')]" position="before">
            <t t-set="portal_client_category" t-value="'main'"/>
        </xpath>
        <div id="portal_client_category_main" position="inside">
            <t t-call="portal.portal_docs_entry">
                <t t-set="icon" t-value="'/sis_portal/static/description/icon.png'"/>
                <t t-set="title">Enrollments</t>
                <t t-set="url" t-value="'/my/enrollments'"/>
                <t t-set="text">View your course enrollments</t>
                <t t-set="placeholder_count" t-value="'enrollment_count'"/>
            </t>
        </div>
    </template>

    <!-- Enrollment list page -->
    <template id="portal_my_enrollments" name="My Enrollments">
        <t t-call="portal.portal_layout">
            <t t-set="breadcrumbs_searchbar" t-value="1"/>

            <t t-call="portal.portal_searchbar">
                <t t-set="title">Enrollments</t>
            </t>

            <t t-if="enrollments">
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Course</th>
                                <th>Course Code</th>
                                <th>Enrollment Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="enrollments" t-as="enrollment">
                                <tr>
                                    <td>
                                        <a t-attf-href="/my/enrollments/#{enrollment.id}">
                                            <t t-out="enrollment.course_id.name"/>
                                        </a>
                                    </td>
                                    <td>
                                        <t t-out="enrollment.course_id.code"/>
                                    </td>
                                    <td>
                                        <span t-field="enrollment.enrollment_date"/>
                                    </td>
                                    <td>
                                        <span t-attf-class="badge rounded-pill
                                            #{enrollment.state == 'enrolled' and 'text-bg-success'
                                            or enrollment.state == 'completed' and 'text-bg-info'
                                            or enrollment.state == 'dropped' and 'text-bg-danger'
                                            or 'text-bg-secondary'}">
                                            <t t-out="dict(enrollment._fields['state'].selection).get(enrollment.state)"/>
                                        </span>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                </div>
            </t>
            <t t-else="">
                <div class="alert alert-info" role="alert">
                    You are not enrolled in any courses yet.
                </div>
            </t>
        </t>
    </template>

    <!-- Enrollment detail page -->
    <template id="portal_enrollment_detail" name="Enrollment Detail">
        <t t-call="portal.portal_layout">
            <t t-set="o_portal_fullwidth_alert" groups="sis_enrollment.group_enrollment_officer">
                <t t-call="portal.portal_back_in_edit_mode">
                    <t t-set="backend_url"
                       t-value="'/odoo/sis-enrollment/%s' % enrollment.id"/>
                </t>
            </t>

            <div class="row mt-3">
                <div class="col-12 col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <t t-out="enrollment.course_id.name"/>
                            </h3>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-6">
                                    <strong>Course Code:</strong>
                                    <span t-out="enrollment.course_id.code"/>
                                </div>
                                <div class="col-6">
                                    <strong>Credit Hours:</strong>
                                    <span t-out="enrollment.course_id.credit_hours"/>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-6">
                                    <strong>Enrollment Date:</strong>
                                    <span t-field="enrollment.enrollment_date"/>
                                </div>
                                <div class="col-6">
                                    <strong>Status:</strong>
                                    <span t-attf-class="badge rounded-pill
                                        #{enrollment.state == 'enrolled' and 'text-bg-success'
                                        or enrollment.state == 'completed' and 'text-bg-info'
                                        or enrollment.state == 'dropped' and 'text-bg-danger'
                                        or 'text-bg-secondary'}">
                                        <t t-out="dict(enrollment._fields['state'].selection).get(enrollment.state)"/>
                                    </span>
                                </div>
                            </div>
                            <t t-if="enrollment.course_id.description">
                                <hr/>
                                <h5>Course Description</h5>
                                <div t-field="enrollment.course_id.description"/>
                            </t>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-3">
                <a href="/my/enrollments" class="btn btn-secondary">
                    &lt; Back to Enrollments
                </a>
            </div>
        </t>
    </template>
</odoo>
```

### Step 4.7 — Run Tests

```bash
./odoo-project test sis_portal
```

The portal tests use `HttpCase`, which starts a real HTTP server — they take longer than unit tests.

All 3 tests should pass.

### Step 4.8 — Verify in the UI

Restart and install:

```bash
./odoo-project stop -v -y
./odoo-project start --demo=base
```

1. Install `sis_portal` from **Apps**
2. Create a portal user:
   - Go to **Settings → Users**, create a new user
   - Set type to "Portal"
   - Set the contact as a student with a student number
3. Create an enrollment for that student
4. Log out of admin, log in as the portal user
5. Visit `/my` — you should see an "Enrollments" card
6. Click through to see the enrollment list and detail pages

**Checkpoint**: Portal user can see their enrollments at `/my/enrollments`, detail page shows course info, and they
cannot see other students' enrollments.

---

## Wrap-Up

### Run All Tests

```bash
./odoo-project test sis_student
./odoo-project test sis_course
./odoo-project test sis_enrollment
./odoo-project test sis_portal
```

All tests across all 4 modules should pass.

### What You Built

| Module           | Model                     | Key Pattern                                   |
| ---------------- | ------------------------- | --------------------------------------------- |
| `sis_student`    | `res.partner` (inherited) | Inherit & extend, vocabulary fields           |
| `sis_course`     | `sis.course` (standalone) | New model, full ACLs                          |
| `sis_enrollment` | `sis.enrollment`          | State machine, M2O relations, SQL constraints |
| `sis_portal`     | (controllers + templates) | Portal, QWeb, record rules                    |

### Using Claude Code to Continue

Try these exercises with Claude Code:

1. **Add a GPA field**: Ask Claude Code to add a computed GPA to students based on completed enrollments
2. **Add course prerequisites**: Use `/implement` to add a self-referential M2M on `sis.course`
3. **Add an attendance module**: Enter Plan mode and design `sis_attendance`
4. **Review your code**: Run `/expert-review` to get feedback on security, naming, and patterns

### Key Takeaways

- **Inherit vs. standalone**: Use `_inherit` for extending existing models (Phase 1), create new models for new concepts
  (Phase 2)
- **Security first**: Every model needs ACLs — `base.group_system` row is mandatory
- **Test-driven**: Write tests before code — they catch issues early and document expected behavior
- **Vocabulary over Selection**: Use `sis.vocabulary.code` with `namespace_uri` domains instead of hard-coded
  `fields.Selection` for configurable values
- **State machines**: Use `fields.Selection` for workflow states with explicit action methods for transitions
- **Portal**: Extend `CustomerPortal`, add record rules for data isolation, use QWeb templates
