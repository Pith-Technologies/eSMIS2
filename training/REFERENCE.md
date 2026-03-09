# Quick Reference Card

> **Author**: Edwin Gonzales **Last Updated**: March 4, 2026
>
> Keep this open during the hands-on lab.

---

## CLI Commands

| Command                        | Alias | Description              | Common Options                                 |
| ------------------------------ | ----- | ------------------------ | ---------------------------------------------- |
| `./odoo-project doctor`        |       | Check prerequisites      |                                                |
| `./odoo-project build`         | `b`   | Build Docker image       | `--no-cache`                                   |
| `./odoo-project start`         | `s`   | Start Odoo (port 8069)   | `--demo=base`, `--wipe`, `--profile=[dev\|ui]` |
| `./odoo-project stop`          |       | Stop services            | `-v` (delete volumes), `-y` (skip prompt)      |
| `./odoo-project restart`       | `r`   | Restart container        |                                                |
| `./odoo-project test <module>` | `t`   | Run module tests         | `--tags=`, `--local`                           |
| `./odoo-project update`        | `u`   | Upgrade changed modules  |                                                |
| `./odoo-project resetdb`       |       | Drop & recreate database | `--demo=base`, `-y`                            |
| `./odoo-project logs`          | `l`   | View container logs      | `-f` (follow), `--tail=N`                      |
| `./odoo-project shell`         | `sh`  | Open Odoo shell          | `--db` (use PostgreSQL)                        |
| `./odoo-project sql`           |       | Run SQL query            | `"<query>"`, `-f <file>`                       |
| `./odoo-project url`           |       | Show server URL          | `-o` (open browser)                            |
| `./odoo-project lint`          |       | Run linters              | `<files>` (default: changed)                   |
| `./odoo-project status`        | `st`  | Show running containers  |                                                |
| `./odoo-project init`          |       | Bootstrap from template  | `<prefix> "<name>"`, `-n` (dry-run)            |

**Command chaining**: `./odoo-project resetdb --demo=base start`

---

## Module Structure

```
sis_mymodule/
├── __init__.py                  # from . import models
├── __manifest__.py              # Module metadata
├── models/
│   ├── __init__.py              # from . import my_model
│   └── my_model.py             # Model definitions
├── views/
│   ├── my_model_views.xml       # Form, list, search views
│   └── menus.xml                # Menu items and actions
├── security/
│   ├── ir.model.access.csv      # Access control lists
│   └── security_groups.xml      # Group definitions (if needed)
├── data/                        # Reference data (noupdate=1)
├── demo/                        # Demo data (only with --demo)
├── tests/
│   ├── __init__.py              # from . import test_my_model
│   └── test_my_model.py        # Test cases
└── readme/
    └── DESCRIPTION.md           # Module description (25-60 lines)
```

---

## Manifest Template

```python
{
    "name": "My Module",
    "version": "19.0.1.0.0",
    "category": "Student Information System/Core",
    "summary": "One-line summary of what this module does",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/my_model_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
    "application": False,
    "auto_install": False,
    "installable": True,
    "maintainers": [],
}
```

---

## Naming Conventions

| Element          | Convention                    | Example                     |
| ---------------- | ----------------------------- | --------------------------- |
| Module directory | `sis_{domain}`                | `sis_student`               |
| Model `_name`    | `sis.{domain}`                | `sis.course`                |
| Inherited model  | `_inherit = "res.partner"`    | (no new `_name`)            |
| Boolean fields   | `is_*` / `has_*`              | `is_student`                |
| Many2one         | `{model}_id`                  | `course_id`                 |
| One2many / M2M   | `{model}_ids`                 | `enrollment_ids`            |
| Date fields      | `*_date`                      | `enrollment_date`           |
| State fields     | `state`                       | `state` (Selection)         |
| XML record IDs   | Descriptive, no abbreviations | `view_sis_course_form`      |
| ACL entry IDs    | `access_{model}_{group}`      | `access_sis_course_officer` |
| Menu IDs         | `menu_{module}_*`             | `menu_sis_student_list`     |
| Action IDs       | `action_sis_{model}`          | `action_sis_course`         |

---

## Security Checklist

For every module, configure these in order:

### 1. Groups (`security/security_groups.xml`)

```xml
<record id="category_sis_mymodule" model="ir.module.category">
    <field name="name">sis My Module</field>
    <field name="sequence">10</field>
</record>

<record id="privilege_mymodule_officer" model="res.groups.privilege">
    <field name="name">My Module Officer</field>
    <field name="category_id" ref="category_sis_mymodule"/>
</record>

<record id="group_mymodule_viewer" model="res.groups">
    <field name="name">My Module: Viewer</field>
    <field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
</record>

<record id="group_mymodule_officer" model="res.groups">
    <field name="name">My Module: Officer</field>
    <field name="privilege_id" ref="privilege_mymodule_officer"/>
    <field name="implied_ids" eval="[Command.link(ref('group_mymodule_viewer'))]"/>
</record>

<record id="group_mymodule_manager" model="res.groups">
    <field name="name">My Module: Manager</field>
    <field name="privilege_id" ref="privilege_mymodule_officer"/>
    <field name="implied_ids" eval="[Command.link(ref('group_mymodule_officer'))]"/>
</record>
```

### 2. ACLs (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sis_mymodel_system,sis.mymodel / System,model_sis_mymodel,base.group_system,1,1,1,1
access_sis_mymodel_user,sis.mymodel / User,model_sis_mymodel,base.group_user,1,0,0,0
access_sis_mymodel_officer,sis.mymodel / Officer,model_sis_mymodel,group_mymodule_officer,1,1,1,0
access_sis_mymodel_manager,sis.mymodel / Manager,model_sis_mymodel,group_mymodule_manager,1,1,1,1
```

**Rules:**

- First data row = `base.group_system` with full CRUD (always)
- Model ID format: `model_{model_name_with_underscores}` (e.g., `model_sis_course`)
- Reference data (vocabularies): give `base.group_user` read access

### 3. Record Rules (optional — for row-level security)

```xml
<data noupdate="1">
    <record id="rule_sis_enrollment_portal" model="ir.rule">
        <field name="name">Portal: own enrollments only</field>
        <field name="model_id" ref="model_sis_enrollment"/>
        <field name="domain_force">[('student_id', '=', user.partner_id.id)]</field>
        <field name="groups" eval="[Command.link(ref('base.group_portal'))]"/>
    </record>
</data>
```

---

## Odoo 19 Quick Reference

### Command API (replaces tuples)

```python
from odoo import Command

# One2many / Many2many write operations:
Command.create({'name': 'New'})      # was (0, 0, {'name': 'New'})
Command.update(id, {'name': 'Edit'}) # was (1, id, {'name': 'Edit'})
Command.delete(id)                   # was (2, id, 0)
Command.unlink(id)                   # was (3, id, 0)
Command.link(id)                     # was (4, id, 0)
Command.clear()                      # was (5, 0, 0)
Command.set([ids])                   # was (6, 0, [ids])
```

### Privilege + Group Definitions

```xml
<!-- Odoo 19: privilege records use res.groups.privilege model -->
<record id="privilege_student_officer" model="res.groups.privilege">
    <field name="name">Student Officer</field>
    <field name="category_id" ref="category_sis_student"/>
</record>

<!-- Functional groups reference the privilege via privilege_id -->
<record id="group_student_officer" model="res.groups">
    <field name="name">Student: Officer</field>
    <field name="privilege_id" ref="privilege_student_officer"/>
    <field name="implied_ids" eval="[Command.link(ref('group_student_viewer'))]"/>
</record>
```

### XPath in Views

```xml
<!-- Odoo 19: use hasclass() instead of @class="..." -->
<xpath expr="//div[hasclass('oe_title')]" position="after">
    <field name="my_field"/>
</xpath>
```

### group_expand Signature

```python
# Odoo 19: 2-parameter signature
@api.model
def _group_expand_states(self, stages, domain):
    return [key for key, _ in self._fields['state'].selection]
```

---

## Claude Code Reference

### Key Commands

| Command          | Purpose                                       |
| ---------------- | --------------------------------------------- |
| `/implement`     | Full TDD workflow with parallel subagents     |
| `/verify-tests`  | Check no tests were removed or weakened       |
| `/commit`        | Conventional commit (`feat:`, `fix:`, etc.)   |
| `/pr`            | Create GitHub Pull Request                    |
| `/expert-review` | Parallel review: security + UX + verification |
| `/analyze`       | Deep analysis without code changes            |

### Subagents

| Agent              | Use For                                |
| ------------------ | -------------------------------------- |
| `@odoo-developer`  | Core implementation work               |
| `@code-reviewer`   | Security, naming, compliance review    |
| `@ux-expert`       | UI/UX patterns, form layouts           |
| `@code-simplifier` | Reduce complexity after implementation |
| `@verify-module`   | End-to-end module verification         |

### Plan Mode

1. Press **Shift+Tab** twice to enter Plan mode
2. Describe what you want to build
3. Claude researches and proposes a plan
4. Review and approve before implementation

---

## Common Errors & Fixes

| Error                                   | Cause                                            | Fix                                                              |
| --------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| `AccessError: ... has no access to ...` | Missing ACL in `ir.model.access.csv`             | Add ACL row for the model and user group                         |
| `KeyError: 'field_name'` in view        | Field not in model or missing `_inherit`         | Add field to model, check `depends` includes parent module       |
| `Module not found`                      | Missing entry in `depends` list                  | Add dependency to `__manifest__.py` `depends`                    |
| `ParseError: ... not valid ...`         | XML syntax error in view                         | Check XML validity, ensure `<field name="...">` references exist |
| `ValidationError: Expected singleton`   | Operating on multiple records where one expected | Use `ensure_one()` or iterate with `for rec in self:`            |
| `ValueError: External ID not found`     | XML ID reference doesn't exist                   | Check module is installed, verify `ref()` points to correct ID   |
| `IntegrityError: duplicate key`         | Unique constraint violated                       | Check SQL constraints, handle duplicates in code                 |
| Test hangs / times out                  | Missing `tracking_disable=True` in test          | Add `with_context(tracking_disable=True)` to test setup          |

---

## Vocabulary Pattern — Quick Usage

```python
# Define a vocabulary field on your model:
gender_id = fields.Many2one(
    "sis.vocabulary.code",
    string="Gender",
    domain="[('namespace_uri', '=', 'urn:iso:std:iso:5218')]",
)

# Look up a code programmatically:
code = self.env["sis.vocabulary.code"].get_code("urn:iso:std:iso:5218", "1")

# Resolve by full URI:
code = self.env["sis.vocabulary.code"].resolve_by_uri("urn:iso:std:iso:5218#1")
```

Pre-loaded vocabularies after `init`:

- **Gender** — `urn:iso:std:iso:5218` (ISO 5218: Not Known, Male, Female, Not Applicable)
- **Civil Status** — `urn:un:unsd:pop-census:marital-status` (UN standard)
- **Blood Type** — `urn:tpl:vocab:blood-type` (ABO/Rh: A+, A-, B+, B-, AB+, AB-, O+, O-)
