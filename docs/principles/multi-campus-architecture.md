# Multi-Campus Architecture Principles

Deployment and data isolation patterns for eSMIS serving Philippine universities with multiple campuses or constituent units.

---

## 1. Architecture Decision — One Company Per Campus

eSMIS uses **Odoo's native multi-company architecture**. Each campus is represented as a `res.company` record within a single Odoo database.

### Why Not Separate Databases?

| Approach | Trade-offs |
|----------|------------|
| **Single DB, multi-company** (chosen) | Shared master data out of the box. Native Odoo support. Consolidated reporting without an aggregation layer. Simpler deployment and maintenance. |
| **Separate DB per campus** | Full isolation, but cross-campus reporting requires a separate aggregation layer. Higher operational overhead: separate backups, upgrades, and support contracts per campus. |
| **Hybrid** | Adds complexity with little benefit when campuses share the same academic policies and CHED reporting obligations. |

### Benefits of Multi-Company in This Context

- **Shared master data** — Course catalog, curriculum definitions, grading templates, PQF mappings, and vocabulary codes are defined once and visible to all campuses. A curriculum revision does not need to be replicated across databases.
- **Native Odoo support** — `company_id` fields, record rules, and the company selector are built into Odoo 19. No custom isolation layer to maintain.
- **Consolidated reporting** — CHED HEMIS reports and system-wide enrollment dashboards work directly against the single database without ETL.
- **Shared employee records** — Faculty with appointments at multiple campuses are a single `hr.employee` record, avoiding duplicate PII and simplifying payroll.

### Naming Convention for Companies

Campus `res.company` records should follow a consistent naming scheme so they sort and display predictably:

```
University of the Philippines Diliman    → company_id = 1
University of the Philippines Los Baños  → company_id = 2
University of the Philippines Manila     → company_id = 3
```

Use the full institutional name, not abbreviations, as the company name. Abbreviations belong in a separate field or in the company's `short_name` if Odoo provides one.

---

## 2. What Is Shared vs. Campus-Specific

### Shared (No `company_id`, visible to all)

These are master data records that campuses reference but do not own. They have no `company_id` field and are not filtered by company.

| Data | Model (example) | Why shared |
|------|-----------------|------------|
| Course catalog | `esmis.course` | Same course code means the same course across campuses. Cross-enrollment and credit transfer require a shared catalog. |
| Curriculum definitions | `esmis.curriculum` | A program (e.g., BSCS) follows the same CMO-defined requirements system-wide. |
| Program definitions | `esmis.program` | CHED-recognized programs are institution-level, not campus-level. |
| PQF level mappings | `esmis.pqf.mapping` | Philippine Qualifications Framework levels are national standards. |
| Vocabulary / code lists | `esmis.vocabulary`, `esmis.vocabulary.code` | Controlled vocabularies (grade types, student statuses, gender codes) must be consistent. |
| Grading system templates | `esmis.grading.template` | Base templates are shared; campus customizations are separate records (see Configurable below). |
| Academic year definitions | `esmis.academic.year` | The institution observes a single academic calendar at the system level. |

### Campus-Specific (Has `company_id`, filtered by company)

These records are owned by a campus and are only visible to users of that company.

| Data | Model (example) | Why campus-specific |
|------|-----------------|---------------------|
| Course sections | `esmis.section` | A section is physically offered at a campus with a specific room and instructor. |
| Rooms and facilities | `esmis.room` | Physical infrastructure is campus-owned. |
| Enrollment records | `esmis.enrollment` | A student is enrolled at a specific campus for a specific term. |
| Fee schedules | `esmis.fee.schedule` | Tuition rates differ by campus (e.g., income-based at UP, flat-rate at a private university campus). |
| Academic calendar dates | `esmis.academic.term` | Exam weeks, registration periods, and holidays may differ by campus. |
| Faculty assignments | `esmis.faculty.load` | Teaching assignments are per campus, per term. |
| Admission records | `esmis.admission` | An applicant applies to a specific campus. |
| Financial transactions | `account.move` | Odoo's accounting is inherently company-scoped. |

### Configurable Per Campus (Campus can override the shared default)

These items have a system-wide default and a campus-level override record. The override takes precedence when it exists.

| Data | Pattern |
|------|---------|
| Grading scale | Campus creates its own `esmis.grading.scale` linked to its `company_id`. If none exists, the system falls back to the shared template. |
| Financial aid programs | Campus defines its own scholarship programs. Government scholarships (CHED, DOST-SEI, UniFAST/TES) are shared reference data. |
| Retention policies | System-wide policy is the baseline. Campus policy record overrides it for that company. |
| GWA computation rules | Some campuses weight units differently. A campus-level configuration record controls the formula. |

---

## 3. Record Rules

### The `company_id` Requirement

**Every domain model must carry a `company_id` field** if its records are campus-specific. Shared master data models (Section 2, "Shared") intentionally omit this field.

```python
# esmis_enrollment/models/esmis_enrollment.py
from odoo import fields, models


class EsmisEnrollment(models.Model):
    _name = "esmis.enrollment"
    _description = "Student Enrollment"

    company_id = fields.Many2one(
        "res.company",
        string="Campus",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    student_id = fields.Many2one("res.partner", string="Student", required=True)
    term_id = fields.Many2one("esmis.academic.term", string="Term", required=True)
    # ...
```

Always set `index=True` on `company_id`. It is used in every record rule domain query and in most reporting group-by clauses.

### Standard Record Rule — Campus Isolation

The default record rule restricts users to records belonging to their active company. This follows Odoo's standard `ir.rule` multi-company pattern.

```xml
<!-- esmis_enrollment/security/ir.rule.xml -->
<odoo>
    <data noupdate="1">

        <record id="rule_enrollment_campus" model="ir.rule">
            <field name="name">Enrollment: Campus Isolation</field>
            <field name="model_id" ref="model_esmis_enrollment"/>
            <field name="domain_force">
                [('company_id', 'in', company_ids)]
            </field>
            <field name="groups" eval="[
                Command.link(ref('base.group_user')),
            ]"/>
        </record>

    </data>
</odoo>
```

`company_ids` is an Odoo built-in rule variable that resolves to the list of companies the current user is allowed to access (their own company plus any companies they have been explicitly granted access to via `res.users.company_ids`).

### System-Level Rule — Consolidated Access

Users with the system admin role bypass campus isolation for reporting and oversight. This is achieved by omitting the record rule for the system admin group, or by defining an explicit unrestricted rule for it.

```xml
<record id="rule_enrollment_system_admin" model="ir.rule">
    <field name="name">Enrollment: System Admin Sees All</field>
    <field name="model_id" ref="model_esmis_enrollment"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[
        Command.link(ref('esmis_security.group_esmis_system_admin')),
    ]"/>
</record>
```

Note that Odoo evaluates rules per group using OR logic across groups and AND logic across rules within the same group. A user in both `group_user` and `group_esmis_system_admin` will satisfy the unrestricted rule and see all records.

### Rule for Registrar vs. VP Academic Affairs

The registrar role uses the standard campus isolation rule above — they see their campus only. The VP Academic Affairs role is granted system-admin-style unrestricted access:

```xml
<record id="rule_enrollment_vp_academic" model="ir.rule">
    <field name="name">Enrollment: VP Academic Affairs Sees All Campuses</field>
    <field name="model_id" ref="model_esmis_enrollment"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[
        Command.link(ref('esmis_security.group_esmis_vp_academic')),
    ]"/>
</record>
```

---

## 4. Security Groups Across Campuses

### Group Hierarchy

```
SYSTEM-WIDE GROUPS (cross-campus oversight)
├── group_esmis_system_admin          ← IT/system administrators
├── group_esmis_vp_academic           ← VP Academic Affairs, sees all campuses
├── group_esmis_president             ← President, sees all campuses
└── group_esmis_ched_reporter         ← CHED reporting officer, read-only across campuses

PER-CAMPUS FUNCTIONAL GROUPS (campus-scoped)
├── group_esmis_registrar_officer     ← Registrar staff (their campus only)
├── group_esmis_registrar_manager     ← University Registrar (their campus only)
├── group_esmis_admissions_officer    ← Admissions staff
├── group_esmis_admissions_manager    ← Admissions director
├── group_esmis_finance_officer       ← Cashier / billing staff
├── group_esmis_finance_manager       ← Finance director
├── group_esmis_faculty               ← Teaching faculty (grade entry only)
└── group_esmis_dean                  ← Dean (own college sections and grades)
```

### Implied Group Inheritance

Campus manager groups imply their officer groups. This prevents the need to assign both:

```xml
<record id="group_esmis_registrar_manager" model="res.groups">
    <field name="name">Registrar: Manager</field>
    <field name="privilege_id" ref="privilege_esmis_registrar"/>
    <field name="implied_ids" eval="[
        Command.link(ref('group_esmis_registrar_officer')),
    ]"/>
</record>
```

### Campus Assignment Enforced Through Company Membership

A user's campus access is controlled by `res.users.company_ids`. A registrar assigned to Campus A should have only Campus A in their allowed companies. This is set in Settings > Users > Allowed Companies — no custom code needed.

System-wide roles (VP, President, CHED reporter) have all campuses in their allowed companies list. Their unrestricted record rules (Section 3) then allow them to query across all.

---

## 5. Consolidated Reporting

### CHED HEMIS Reports

CHED's Higher Education Management Information System requires enrollment statistics at the institutional level (the whole university system), not per campus.

These reports must aggregate across all campuses. Use `sudo()` with an explicit domain or use a dedicated reporting user that belongs to all companies:

```python
def _get_system_enrollment_count(self, term_id):
    # Deliberately queries all companies — this is a CHED system-level report.
    return self.env["esmis.enrollment"].sudo().search_count([
        ("term_id", "=", term_id),
        ("state", "=", "enrolled"),
    ])
```

Document `sudo()` calls with a comment explaining the business justification. `sudo()` used without explanation is a red flag in code review.

### Accreditation Reports

Accreditation reports vary by accrediting body:

| Body | Scope |
|------|-------|
| AACCUP / PAASCU | Per campus — the campus is accredited, not the system |
| CHED COE / COD recognition | Per campus or per program across the system |
| ISO audit | May cover the whole system |

The `company_id` filter on report wizard fields controls scope. System-level reports leave `company_id` blank (all campuses). Campus-level reports pre-fill it with the current user's company and make the field read-only for campus staff.

### Enrollment Dashboard Drill-Down

The enrollment dashboard supports four drill-down levels:

```
System total
  └── Campus (res.company)
        └── College (esmis.college, scoped to campus)
              └── Program (esmis.program, shared catalog)
                    └── Section (esmis.section, scoped to campus)
```

Group-by at the `company_id` level is available only to users with cross-campus access. Campus users' dashboards start at the college level since they cannot see other campuses.

### Financial Consolidation

Odoo's native multi-company accounting handles financial consolidation. Each campus has its own chart of accounts and journal entries. The consolidation wizard in Odoo's accounting module produces system-wide financial statements. No custom code is needed for this layer.

---

## 6. Inter-Campus Operations

### Cross-Enrollment

A student enrolled at Campus A taking a section offered at Campus B.

**Data model:**

```python
class EsmisEnrollment(models.Model):
    _name = "esmis.enrollment"

    company_id = fields.Many2one(
        "res.company",
        string="Home Campus",
        required=True,
        index=True,
    )
    section_company_id = fields.Many2one(
        "res.company",
        string="Host Campus",
        index=True,
    )
    section_id = fields.Many2one("esmis.section", string="Section", required=True)
    is_cross_enrolled = fields.Boolean(
        string="Cross-Enrolled",
        compute="_compute_is_cross_enrolled",
        store=True,
    )

    @api.depends("company_id", "section_company_id")
    def _compute_is_cross_enrolled(self):
        for record in self:
            record.is_cross_enrolled = (
                bool(record.section_company_id)
                and record.company_id != record.section_company_id
            )
```

**Record rule consideration:** The host campus registrar must be able to see cross-enrollment records for their sections even though the student's home campus is different. Add an additional rule for this:

```xml
<record id="rule_enrollment_host_campus" model="ir.rule">
    <field name="name">Enrollment: Host Campus Sees Cross-Enrollments</field>
    <field name="model_id" ref="model_esmis_enrollment"/>
    <field name="domain_force">
        [('section_company_id', 'in', company_ids)]
    </field>
    <field name="groups" eval="[
        Command.link(ref('group_esmis_registrar_officer')),
        Command.link(ref('group_esmis_registrar_manager')),
    ]"/>
</record>
```

Odoo ORs rules within the same model for the same group. The registrar sees records where `company_id in company_ids` (their campus's enrollments) OR `section_company_id in company_ids` (cross-enrolled students in their sections).

### Credit Transfer Between Campuses

A student transferring from Campus A to Campus B brings their academic record. The canonical record stays with Campus A (their original home company). Campus B creates a credit evaluation record referencing the original:

```python
class EsmisCreditTransfer(models.Model):
    _name = "esmis.credit.transfer"
    _description = "Inter-Campus Credit Transfer"

    company_id = fields.Many2one(
        "res.company",
        string="Receiving Campus",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    source_company_id = fields.Many2one(
        "res.company",
        string="Source Campus",
        required=True,
    )
    student_id = fields.Many2one("res.partner", string="Student", required=True)
    source_enrollment_ids = fields.Many2many(
        "esmis.enrollment",
        string="Source Enrollments",
    )
    # ... evaluated_units, approved_units, approver_id, state ...
```

The credit transfer record lives in the receiving campus's company scope. The source enrollment records remain in the source campus's scope; the receiving registrar accesses them via a specific cross-campus read permission granted during the transfer workflow.

### Faculty Shared Appointments

A faculty member teaching at multiple campuses is a single `hr.employee` record. Teaching load records are campus-scoped:

```python
class EsmisFacultyLoad(models.Model):
    _name = "esmis.faculty.load"
    _description = "Faculty Teaching Load"

    company_id = fields.Many2one(
        "res.company",
        string="Campus",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Faculty Member", required=True)
    section_ids = fields.Many2many("esmis.section", string="Sections")
    term_id = fields.Many2one("esmis.academic.term", string="Term", required=True)
    total_units = fields.Float(string="Total Teaching Units", compute="_compute_units", store=True)
```

Faculty members with multi-campus appointments have both campuses in their `res.users.company_ids`, allowing them to switch context and see their load at each campus.

### Student Transfer Between Campuses

A student formally transferring their enrollment from Campus A to Campus B is handled as a status change on the student's profile plus a new admission record at Campus B:

1. The student's `esmis.student` record (scoped to Campus A) is marked with `transfer_state = 'transferred_out'` and a `transfer_date`.
2. Campus B creates a new `esmis.student` record (scoped to Campus B) with `transfer_state = 'transferred_in'` and a reference to the Campus A student record.
3. A credit evaluation is created to bring recognized units forward (see Credit Transfer above).
4. The student's `res.partner` record is shared — it is not company-scoped. Only the domain-specific student profile records are campus-scoped.

---

## 7. Implementation Checklist

Follow this checklist for every new campus-specific model:

- [ ] Add `company_id` field with `required=True`, `default=lambda self: self.env.company`, and `index=True`
- [ ] Add the standard campus isolation record rule in `security/ir.rule.xml`
- [ ] Add a system admin unrestricted rule if consolidated reporting requires it
- [ ] Add the model to `security/ir.model.access.csv` for all relevant groups
- [ ] Write a test confirming that an officer in Campus A cannot read Campus B records:

```python
def test_campus_isolation_enrollment(self):
    campus_a = self.env["res.company"].create({"name": "Campus A"})
    campus_b = self.env["res.company"].create({"name": "Campus B"})

    officer_a = self._create_officer(campus_a)

    enrollment_b = self.env["esmis.enrollment"].with_user(self.env.user).create({
        "company_id": campus_b.id,
        "student_id": self.student.id,
        "term_id": self.term.id,
    })

    # Officer A must not see Campus B's enrollment.
    results = self.env["esmis.enrollment"].with_user(officer_a).search([
        ("id", "=", enrollment_b.id),
    ])
    self.assertFalse(results, "Campus A officer must not see Campus B enrollments")
```

- [ ] Write a test confirming a system admin can see records from all campuses:

```python
def test_system_admin_sees_all_campuses(self):
    enrollment_a = self._create_enrollment(campus=self.campus_a)
    enrollment_b = self._create_enrollment(campus=self.campus_b)

    results = self.env["esmis.enrollment"].with_user(self.system_admin).search([
        ("id", "in", [enrollment_a.id, enrollment_b.id]),
    ])
    self.assertEqual(len(results), 2, "System admin must see all campus records")
```

- [ ] Write a test confirming consolidated reports aggregate correctly across campuses

---

## 8. Philippine Context

### University Systems in the Philippines

The multi-company model maps naturally onto the structure of Philippine university systems:

| System | Campuses / Constituent Units | Notes |
|--------|------------------------------|-------|
| UP System | 8 constituent universities (UPD, UPLB, UPM, UPV, UPB, UPOU, UPMIN, UPMSI) | Each CU has its own chancellor, autonomous operations, but shared Board of Regents and system-wide policies. |
| De La Salle Philippines | Multiple campuses (Manila, Dasmariñas, Lipa, Bacolod, Canlubang, etc.) | Shared La Salle brand standards and curriculum frameworks. |
| Ateneo de Manila University | Main campus plus affiliated Ateneo schools | Varying degrees of system integration. |
| SUC multi-campus systems | Many State Universities and Colleges with satellite campuses | CHED monitors at both campus and system level. |

### CHED Reporting Obligations

CHED requires data at two levels for HEMIS submissions:

1. **Institutional level** — The system as a whole (e.g., "University of the Philippines System"). Reports enrollment headcount, graduates, faculty FTE, and research output for the entire system.
2. **Campus level** — Each constituent unit or campus submits its own HEMIS data. CHED reconciles the two.

eSMIS must support both. The institutional-level report is the cross-campus consolidated query. The campus-level report uses the standard `company_id` filter.

### Accreditation Bodies and Scope

| Body | Scope of Accreditation |
|------|------------------------|
| AACCUP (Accrediting Agency of Chartered Colleges and Universities in the Philippines) | Per campus, per program |
| PAASCU (Philippine Accrediting Association of Schools, Colleges and Universities) | Per institution, which may mean per campus |
| PACUCOA | Per program at the campus level |
| ISO 9001 | Often system-wide for administrative processes |
| CHED Center of Excellence / Development | Per program, cross-campus eligibility possible |

Accreditation reports in eSMIS should support a `scope` field on the report wizard: `campus` or `system`. When `campus`, filter by `company_id`. When `system`, query all companies with appropriate permissions.

### CHED CMO Compliance

CHED Memorandum Orders define minimum curriculum requirements per program. These requirements are shared across campuses — they are part of the shared course catalog and curriculum definitions. A BSCS program at Campus A and Campus B follows the same CMO. The curriculum model is not campus-scoped.

Campus-level customizations (additional electives, local general education courses) are stored as campus-specific curriculum addenda linked to the shared curriculum definition.

---

**See also:** [Module Architecture](module-architecture.md), [Access Rights](access-rights.md), [Security](../architecture/decisions/)
