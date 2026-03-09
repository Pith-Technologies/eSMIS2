# Phase 1B Build Plan: Student Profile & Address Modules

Detailed implementation blueprint for the second batch of Phase 1 modules. This plan
covers `esmis_address`, `esmis_student`, `esmis_ph`, and the `esmis_starter` →
`esmis_starter_ph` rename.

A developer reading this plan should not need to reference any other document to
implement these modules.

**Created:** 2026-03-10
**Status:** Approved — 2026-03-10
**Prerequisite:** Phase 1A modules (`esmis_base`, `esmis_vocabulary`, `esmis_security`,
`esmis_consent`, `esmis_approval`) must be built and tested first.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Key Design Decisions](#2-key-design-decisions)
3. [Module Build Order](#3-module-build-order)
4. [Module Spec: esmis_address](#4-module-spec-esmis_address)
5. [Module Spec: esmis_student](#5-module-spec-esmis_student)
6. [Module Spec: esmis_ph](#6-module-spec-esmis_ph)
7. [Module Spec: esmis_starter_ph (rename)](#7-module-spec-esmis_starter_ph)
8. [Vocabulary Seed Data](#8-vocabulary-seed-data)
9. [Cross-Cutting Requirements](#9-cross-cutting-requirements)
10. [Parallelization Strategy](#10-parallelization-strategy)
11. [Risk Register](#11-risk-register)

---

## 1. Executive Summary

Phase 1B delivers the student profile infrastructure. It builds four modules on top of
Phase 1A:

| Order | Module | Size | New Models | Purpose |
|-------|--------|------|------------|---------|
| 1 | `esmis_address` | S | 1 | Structured address model linked to `res.partner` |
| 2 | `esmis_student` | L | 2 | Universal student demographics on `res.partner`, education history |
| 3 | `esmis_ph` | L | 4 | Philippine-specific fields, PSGC geographic hierarchy, PH vocabs |
| 4 | `esmis_starter_ph` | S | 0 | Rename from `esmis_starter`; PH localization + dependency aggregator |

**Phase 1B goal:** The institution can create student profiles with structured names,
addresses, education history, and government identifiers. Philippine deployments get
PSGC-based address selection, Filipino name conventions (middle name before marriage,
suffixes), and PH-specific vocabularies.

**What the system can do after Phase 1B:**

- Create student profiles with structured name fields (first, last, middle)
- Record multiple typed addresses per student (permanent, mailing, residency, emergency)
- Track education history (elementary through senior high school)
- Store encrypted government identifiers (PhilSys, LRN, TIN)
- Philippine deployments: select address from PSGC hierarchy (Region → Province →
  City/Municipality → Barangay), use Filipino name format with suffixes

---

## 2. Key Design Decisions

These decisions were made during the design discussion. They are recorded here for
traceability — no further input needed.

### Decision 1: Where do Philippine-specific fields go?

**Decision:** Approach B — a single `esmis_ph` module for all foundation-level Philippine
extensions. Domain-specific PH modules (`esmis_grading_ph`, `esmis_curriculum_ph`, etc.)
come later when those domain modules are built.

**Rationale:** Centralizes PH partner extensions, PSGC data, and PH vocabularies in one
place. Avoids a proliferation of small `_ph` modules at the foundation layer. Follows the
country module pattern from `docs/principles/module-architecture.md`.

### Decision 2: middle_name — universal or PH-specific?

**Decision:** `middle_name` is universal (in `esmis_student`). `middle_name_b4_marriage`
is PH-specific (in `esmis_ph`).

**Rationale:** Middle names exist in most cultures. The Philippines has a unique convention
where a woman's maiden surname becomes her middle name after marriage — that field
belongs in `esmis_ph`.

### Decision 3: Address architecture

**Decision:** `esmis_address` provides the base address model with generic fields
(`address_text` computed, `address_type_id`, `is_primary`, `country_id`). `esmis_ph`
extends `esmis.address` with PSGC fields (`region_id`, `province_id`,
`city_municipality_id`, `barangay_id`, `zip_code`) and overrides the computed
`address_text` to use the Philippine format.

No separate `esmis_address_ph` module — the PH address fields are injected by `esmis_ph`
alongside the other PH partner extensions. This keeps the dependency graph simpler.

### Decision 4: PSGC data loading strategy

**Decision:** Bundle all PSGC records as CSV files in `esmis_ph/data/psgc/`. Use a
`post_init_hook` with raw SQL `COPY` for the ~42,000 barangay records to achieve
seconds-not-minutes install time. Regions (~17), provinces (~82), and
cities/municipalities (~1,500) use standard XML data files.

**Rationale:** The PSGC dataset is stable (updated annually by PSA). Bundling avoids
external API dependencies. Raw SQL for barangays avoids the ORM overhead of 42K
individual `create()` calls.

### Decision 5: Name suffixes

**Decision:** `suffix_ids` is a Many2many field on `res.partner` defined in `esmis_ph`,
linking to `esmis.vocabulary.code` with domain
`[('namespace_uri', '=', 'urn:esmis:name-suffix')]`. Common suffixes (Jr, Sr, II, III,
IV, PhD, MD, EdD, LLB, CPA, RN) are seeded as vocabulary data.

**Rationale:** Many2many allows multiple suffixes (e.g., "Juan dela Cruz Jr, PhD"). Using
vocabulary codes means new suffixes can be added via data files.

### Decision 6: Family relationships

**Decision:** Use `res.partner` relationships rather than flat text fields for
family/guardian data. The `guardian_id` (Many2one to `res.partner`) field on
`res.partner` is defined in `esmis_student`. The relationship type vocabulary
(`urn:esmis:vocabulary:relationship-type`) already exists in `esmis_vocabulary`.

**Rationale:** Flat text fields from the old eSMIS code (father_name, mother_name,
guardian_name, etc.) cannot be deduplicated, linked to consent records, or used for
contact management.

### Decision 7: Education history

**Decision:** `esmis.education.history` is a One2many model in `esmis_student` linked to
`res.partner`. Replaces the 18 flat fields from the old code (elementary_school,
elementary_year_graduated, etc.) with structured records.

**Rationale:** Structured records can accommodate any number of education levels, are
extensible by country modules, and support transfer credit evaluation.

### Decision 8: Admission number

**Decision:** Deferred to the `esmis_enrollment` module (Phase 2). The admission workflow
assigns this number, not the student profile.

### Decision 9: `application` flag

**Decision:** Only `esmis_starter_ph` has `application=True`. `esmis_student` does NOT
have `application=True` (changed from the original Phase 1 plan).

**Rationale:** The starter module is the only user-facing entry point in the Apps menu.
This was decided during the menu architecture redesign (ADR-018).

---

## 3. Module Build Order

```
1. esmis_address         ← Small, no domain dependencies beyond esmis_base.
                           Provides the address model that esmis_student and
                           esmis_ph both depend on.

2. esmis_student         ← Extends res.partner with student demographics.
                           Depends on esmis_address, esmis_vocabulary,
                           esmis_security, esmis_consent.

3. esmis_ph              ← Philippine extensions. Depends on esmis_student and
                           esmis_address. Contains PSGC data, PH vocabs,
                           PH-specific partner fields.

4. esmis_starter_ph      ← Rename from esmis_starter. Update dependencies
                           to include esmis_ph. Localization defaults.
```

**Rationale:** Address is a dependency of both student and PH modules. Student must exist
before PH can extend it. Starter comes last as the aggregator.

---

## 4. Module Spec: esmis_address

### 4.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_address` |
| Description | Structured address model linked to res.partner |
| Dependencies | `esmis_base`, `esmis_vocabulary` |
| Version | `19.0.1.0.0` |
| `application` | `False` |
| `auto_install` | `False` |
| Category | `eSMIS/Core` |

### 4.2 Module Structure

```
esmis_address/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── address.py
│   └── res_partner.py          # Adds address_ids One2many to res.partner
├── security/
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── views/
│   ├── address_views.xml       # Inline form for partner addresses
│   └── res_partner_views.xml   # Inherit partner form to add address tab
├── data/
│   └── vocabulary_address_type.xml
├── tests/
│   ├── __init__.py
│   ├── test_address.py
│   └── test_address_primary.py
└── readme/
    └── DESCRIPTION.md
```

### 4.3 Models

#### 4.3.1 `esmis.address`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.address` |
| `_description` | Structured address linked to a contact |
| `_order` | `is_primary desc, id` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `partner_id` | Many2one | `res.partner`, required=True, ondelete='cascade', index=True | Contact this address belongs to |
| `address_type_id` | Many2one | `esmis.vocabulary.code`, required=True, domain=`[('namespace_uri', '=', 'urn:esmis:address-type')]` | Address type (permanent, mailing, etc.) |
| `is_primary` | Boolean | default=False | Primary address flag |
| `address_text` | Text | compute=`_compute_address_text`, store=True | Full formatted address (computed from components) |
| `street1` | Char | | Street line 1 |
| `street2` | Char | | Street line 2 |
| `city` | Char | | City or municipality (free text in base; overridden by PH module) |
| `state_province` | Char | | State or province (free text in base) |
| `postal_code` | Char | | Postal/ZIP code |
| `country_id` | Many2one | `res.country` | Country |
| `notes` | Text | | Additional notes |

**Computed field `address_text`:**

The base implementation concatenates non-empty address components:

```python
def _compute_address_text(self):
    for rec in self:
        parts = filter(None, [
            rec.street1,
            rec.street2,
            rec.city,
            rec.state_province,
            rec.postal_code,
            rec.country_id.name if rec.country_id else None,
        ])
        rec.address_text = ", ".join(parts)
```

Country modules override this to produce locale-specific formatting. `esmis_ph`
overrides to produce: `street1, street2, Barangay, City/Municipality, Province, Region ZIP`.

**Constraints:**

- Python: Only one `is_primary=True` per `partner_id`. When setting a new primary, the
  old primary is automatically unflagged (handled in `write()`/`create()`).
- Python: `address_type_id` + `partner_id` should be unique (one address per type per
  partner). Enforced via SQL constraint.

**Methods:**

| Method | Description |
|--------|-------------|
| `create()` | If `is_primary=True` and another primary exists, unflag the old one |
| `write()` | Same primary-flag management |

#### 4.3.2 `res.partner` extension

```python
class ResPartner(models.Model):
    _inherit = "res.partner"

    address_ids = fields.One2many("esmis.address", "partner_id", string="Addresses")
    primary_address_text = fields.Text(
        compute="_compute_primary_address_text",
        string="Primary Address",
    )

    def _compute_primary_address_text(self):
        for partner in self:
            primary = partner.address_ids.filtered("is_primary")[:1]
            partner.primary_address_text = primary.address_text if primary else ""
```

### 4.4 Vocabulary Seed Data

**`urn:esmis:address-type`** — loaded in `data/vocabulary_address_type.xml`:

| Code | Display | Sequence |
|------|---------|----------|
| `permanent` | Permanent Address | 10 |
| `mailing` | Mailing Address | 20 |
| `residency` | Current Residence | 30 |
| `emergency` | Emergency Contact Address | 40 |

### 4.5 Security

**ACL Matrix (`ir.model.access.csv`):**

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_address_system,esmis.address / System,model_esmis_address,base.group_system,1,1,1,1
access_esmis_address_user,esmis.address / Internal User,model_esmis_address,base.group_user,1,1,1,1
```

**Rationale:** Addresses are edited inline on the partner form by any internal user who
has access to the partner. Finer-grained control is enforced at the partner level, not
the address level.

**Record Rules:**

None specific to `esmis.address`. Access is controlled by the partner record rules. The
`partner_id` field links to `res.partner`, whose record rules already handle visibility.

### 4.6 Views

**Inline form view** for use in the partner form's Addresses tab:

```xml
<record id="view_esmis_address_form_inline" model="ir.ui.view">
    <field name="name">esmis.address.form.inline</field>
    <field name="model">esmis.address</field>
    <field name="arch" type="xml">
        <form string="Address">
            <group>
                <group>
                    <field name="address_type_id"/>
                    <field name="is_primary"/>
                </group>
                <group>
                    <field name="country_id"/>
                    <field name="postal_code"/>
                </group>
            </group>
            <group>
                <field name="street1"/>
                <field name="street2"/>
                <field name="city"/>
                <field name="state_province"/>
            </group>
            <field name="notes"/>
        </form>
    </field>
</record>
```

**Partner form extension** adds an "Addresses" page:

```xml
<record id="view_res_partner_form_address" model="ir.ui.view">
    <field name="name">res.partner.form.address</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//page[@name='internal_notes']" position="before">
            <page string="Addresses" name="addresses">
                <field name="address_ids" context="{'default_partner_id': active_id}">
                    <list>
                        <field name="address_type_id"/>
                        <field name="is_primary"/>
                        <field name="address_text"/>
                    </list>
                    <form>
                        <!-- Uses inline form defined above -->
                    </form>
                </field>
            </page>
        </xpath>
    </field>
</record>
```

### 4.7 Acceptance Criteria

- [ ] `esmis.address` creates and links to `res.partner`
- [ ] `address_text` computed correctly from components
- [ ] Only one `is_primary=True` per partner (auto-unflag old primary)
- [ ] Unique constraint on `partner_id` + `address_type_id`
- [ ] Address tab visible on `res.partner` form
- [ ] `primary_address_text` computed on partner
- [ ] Vocabulary seed data for address types loads correctly
- [ ] Tests cover primary flag management
- [ ] Tests cover address_text computation
- [ ] Tests cover unique-per-type constraint

---

## 5. Module Spec: esmis_student

### 5.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_student` |
| Description | Universal student demographics on res.partner with education history |
| Dependencies | `esmis_base`, `esmis_vocabulary`, `esmis_security`, `esmis_consent`, `esmis_address` |
| Version | `19.0.1.0.0` |
| `application` | `False` |
| `auto_install` | `False` |
| Category | `eSMIS/Core` |

**Changes from Phase 1 plan (phase-1-plan.md section 6):**

- `application` changed from `True` to `False` (Decision 9)
- `esmis_address` added as dependency
- `religion` and `ethnicity` moved to `esmis_ph` (PH-specific)
- Name fields added (`first_name`, `last_name`, `middle_name`)
- `esmis.education.history` added (replaces flat fields from old code)
- `esmis.student.program` deferred — it references Phase 2 models and has no Phase 1 UI
- `consent_given`, `consent_date`, `consent_given_by`, `is_consent_for_minor` removed —
  consent is managed via `esmis.consent` records, not direct fields
- `gwa` and `academic_standing` deferred to Phase 2 (`esmis_grading`)
- `transfer_state` and `transfer_date` deferred to Phase 2 (`esmis_enrollment`)
- `program_id` and `curriculum_id` deferred to Phase 2

### 5.2 Module Structure

```
esmis_student/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py          # Extends res.partner with is_student + demographics
│   ├── identifier.py           # esmis.identifier (multi-type encrypted IDs)
│   └── education_history.py    # esmis.education.history
├── security/
│   ├── categories.xml
│   ├── privileges.xml
│   ├── groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── views/
│   ├── res_partner_student_views.xml   # Student-specific partner form
│   ├── identifier_views.xml
│   ├── education_history_views.xml
│   └── menus.xml
├── data/
│   └── vocabulary_education_level.xml
├── demo/
│   ├── demo_students.xml
│   └── demo_identifiers.xml
├── tests/
│   ├── __init__.py
│   ├── test_student_partner.py
│   ├── test_student_state_machine.py
│   ├── test_identifier_encryption.py
│   ├── test_education_history.py
│   ├── test_guardian_minor.py
│   ├── test_campus_isolation.py
│   ├── test_display_name.py
│   └── test_consent_integration.py
└── readme/
    └── DESCRIPTION.md
```

### 5.3 Models

#### 5.3.1 `res.partner` extension (student demographics)

| Attribute | Value |
|-----------|-------|
| `_inherit` | `res.partner` |
| Extended by | `esmis_student` |

**New fields on `res.partner`:**

| Field | Type | Attributes | Description | PII Tier |
|-------|------|------------|-------------|----------|
| `is_student` | Boolean | default=False, index=True | Marks this contact as a student | — |
| `student_number` | Char | copy=False, index=True | Institution-assigned student number | 0 (Public) |
| `first_name` | Char | | Given name | 1 |
| `last_name` | Char | | Family name / surname | 1 |
| `middle_name` | Char | | Middle name | 1 |
| `birthdate` | Date | | Date of birth | 2 |
| `birthplace` | Char | | Place of birth (free text) | 1 |
| `age` | Integer | compute=`_compute_age`, store=True | Age in years (recomputed daily via cron) | 0 |
| `gender_id` | Many2one | `esmis.vocabulary.code`, domain=`[('namespace_uri', '=', 'urn:iso:std:iso:5218')]` | Gender (ISO 5218) | 1 |
| `civil_status_id` | Many2one | `esmis.vocabulary.code`, domain=`[('namespace_uri', '=', 'urn:un:unsd:pop-census:marital-status')]` | Civil status | 1 |
| `nationality_id` | Many2one | `res.country` | Nationality | 0 |
| `blood_type_id` | Many2one | `esmis.vocabulary.code`, domain=`[('namespace_uri', '=', 'urn:tpl:vocab:blood-type')]` | Blood type | 1 |
| `disability_type_id` | Many2one | `esmis.vocabulary.code`, domain=`[('namespace_uri', '=', 'urn:esmis:vocabulary:disability-type')]` | PWD type (RA 7277/10754) | 2 |
| `is_pwd` | Boolean | default=False | Person with disability flag | 1 |
| `is_indigenous_people` | Boolean | default=False | Indigenous peoples flag (IPRA RA 8371) | 1 |
| `guardian_id` | Many2one | `res.partner` | Parent/guardian for minors | 2 |
| `guardian_relationship_id` | Many2one | `esmis.vocabulary.code`, domain=`[('namespace_uri', '=', 'urn:esmis:vocabulary:relationship-type')]` | Relationship to guardian | 1 |
| `student_state` | Selection | See state machine; default=`'applicant'`, tracking=True | Student lifecycle state | 1 |
| `identifier_ids` | One2many | `esmis.identifier`, `partner_id` | Government/institutional identifiers | — |
| `education_history_ids` | One2many | `esmis.education.history`, `partner_id` | Education background | — |
| `display_name` | Char | compute=`_compute_student_display_name`, store=True | Student display name | — |

**Computed fields:**

`_compute_age`:
```python
@api.depends("birthdate")
def _compute_age(self):
    today = fields.Date.today()
    for partner in self:
        if partner.birthdate:
            delta = relativedelta(today, partner.birthdate)
            partner.age = delta.years
        else:
            partner.age = 0
```

`_compute_student_display_name` (hook method):

The base implementation concatenates `last_name, first_name middle_name`. Country
modules override this to add locale-specific formatting. `esmis_ph` overrides to
include suffixes and the `middle_name_b4_marriage` field.

```python
@api.depends("first_name", "last_name", "middle_name", "is_student")
def _compute_student_display_name(self):
    for partner in self:
        if partner.is_student and partner.last_name:
            parts = [partner.last_name + ",", partner.first_name]
            if partner.middle_name:
                parts.append(partner.middle_name)
            partner.display_name = " ".join(filter(None, parts))
        else:
            # Fallback to Odoo's default name computation
            partner.display_name = partner._get_default_display_name()

def _get_default_display_name(self):
    """Hook for Odoo's default display name. Avoids recursion."""
    return self.name or ""
```

> **Note:** The exact `depends` list must include all fields that country modules add
> to the name. `esmis_ph` extends `_compute_student_display_name` with additional
> `@api.depends('suffix_ids', 'middle_name_b4_marriage')`.

**Student state machine:**

```
applicant ──▶ admitted ──▶ enrolled ──▶ active ──▶ graduated ──▶ alumni
     │              │                       │
     │              │                       ├──▶ loa ──▶ enrolled (re-enroll)
     │              │                       │
     │              │                       ├──▶ dismissed
     │              │                       │
     │              │                       └──▶ transferred_out
     │              │
     │              └──▶ denied
     │
     └──▶ denied
```

**Valid transitions (enforced in `write()`):**

| From | To |
|------|----|
| `applicant` | `admitted`, `denied` |
| `admitted` | `enrolled`, `denied` |
| `enrolled` | `active` |
| `active` | `enrolled` (next term), `loa`, `graduated`, `dismissed`, `transferred_out` |
| `loa` | `enrolled` (re-enroll), `dismissed` |
| `graduated` | `alumni` |

State transition values:

```python
STUDENT_STATES = [
    ("applicant", "Applicant"),
    ("admitted", "Admitted"),
    ("enrolled", "Enrolled"),
    ("active", "Active"),
    ("loa", "Leave of Absence"),
    ("graduated", "Graduated"),
    ("alumni", "Alumni"),
    ("dismissed", "Dismissed"),
    ("transferred_out", "Transferred Out"),
    ("denied", "Denied"),
]
```

**Guardian/minor logic:**

- When `birthdate` indicates age < 18 at current date:
  - `guardian_id` is required (raise `ValidationError` if missing)
- When student turns 18:
  - System generates a `mail.activity` for the registrar's office to collect direct consent
  - Parent consent remains valid until student provides their own

**`_pii_fields` classification:**

```python
_pii_fields = {
    "first_name": {"tier": 1, "masking_pattern": None, "groups": None},
    "last_name": {"tier": 1, "masking_pattern": None, "groups": None},
    "middle_name": {"tier": 1, "masking_pattern": None, "groups": None},
    "birthdate": {"tier": 2, "masking_pattern": "****-**-##", "groups": "esmis_security.group_esmis_security_officer"},
    "birthplace": {"tier": 1, "masking_pattern": None, "groups": None},
    "guardian_id": {"tier": 2, "masking_pattern": None, "groups": "esmis_security.group_esmis_security_officer"},
}
```

---

#### 5.3.2 `esmis.identifier`

Unchanged from Phase 1 plan (section 6.3.3). Key points:

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.identifier` |
| `_description` | Multi-type identifier store with encryption |
| `_inherit` | `esmis.pii.aware` |

**Fields:** `partner_id`, `type_id`, `system_uri`, `value`, `value_ciphertext`,
`value_blind_index`.

The identifier type vocabulary codes are seeded by the appropriate country module.
`esmis_ph` seeds PH-specific types (PhilSys, LRN, TIN, SSS, GSIS, PWD ID, Solo Parent
ID, Passport).

**Encryption:** AES-256-GCM per Phase 1 plan Decision 2.

---

#### 5.3.3 `esmis.education.history`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.education.history` |
| `_description` | Educational background record |
| `_order` | `education_level_sequence, id` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `partner_id` | Many2one | `res.partner`, required=True, ondelete='cascade', index=True | Student |
| `education_level_id` | Many2one | `esmis.vocabulary.code`, required=True, domain=`[('namespace_uri', '=', 'urn:esmis:education-level')]` | Level (elementary, JHS, SHS, tertiary) |
| `education_level_sequence` | Integer | related=`education_level_id.sequence`, store=True | For ordering |
| `school_name` | Char | required=True | Name of institution attended |
| `school_address` | Char | | School location |
| `year_started` | Integer | | Year started (e.g., 2018) |
| `year_graduated` | Integer | | Year completed/graduated |
| `honors_received` | Char | | Academic honors or awards |
| `is_graduated` | Boolean | default=False | Whether the student completed this level |

**Constraints:**

- Python: `year_graduated >= year_started` when both are set

---

### 5.4 Security Groups

| XML ID | Name | Category | `implied_ids` |
|--------|------|----------|---------------|
| `category_esmis_student` | eSMIS / Student Management | — | — |
| `privilege_esmis_registrar` | Registrar | `category_esmis_student` | — |
| `group_esmis_student_self` | Student (Self) | — | — |
| `group_esmis_registrar_viewer` | Registrar: Viewer | `privilege_esmis_registrar` | — |
| `group_esmis_registrar_officer` | Registrar: Officer | `privilege_esmis_registrar` | `group_esmis_registrar_viewer` |
| `group_esmis_registrar_manager` | Registrar: Manager | `privilege_esmis_registrar` | `group_esmis_registrar_officer` |

**Settings admin inheritance:** Extend `base.group_system` implied_ids to include
`group_esmis_registrar_manager`.

### 5.5 ACL Matrix (`ir.model.access.csv`)

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# --- System admin ---
access_esmis_identifier_system,esmis.identifier / System,model_esmis_identifier,base.group_system,1,1,1,1
access_esmis_education_history_system,esmis.education.history / System,model_esmis_education_history,base.group_system,1,1,1,1
# --- Registrar Officer ---
access_esmis_identifier_registrar_officer,esmis.identifier / Registrar Officer,model_esmis_identifier,group_esmis_registrar_officer,1,1,1,0
access_esmis_education_history_registrar_officer,esmis.education.history / Registrar Officer,model_esmis_education_history,group_esmis_registrar_officer,1,1,1,0
# --- Registrar Manager ---
access_esmis_identifier_registrar_manager,esmis.identifier / Registrar Manager,model_esmis_identifier,group_esmis_registrar_manager,1,1,1,1
access_esmis_education_history_registrar_manager,esmis.education.history / Registrar Manager,model_esmis_education_history,group_esmis_registrar_manager,1,1,1,1
# --- Registrar Viewer ---
access_esmis_identifier_registrar_viewer,esmis.identifier / Registrar Viewer,model_esmis_identifier,group_esmis_registrar_viewer,1,0,0,0
access_esmis_education_history_registrar_viewer,esmis.education.history / Registrar Viewer,model_esmis_education_history,group_esmis_registrar_viewer,1,0,0,0
# --- Student Self (read own via record rule) ---
access_esmis_identifier_self,esmis.identifier / Student Self,model_esmis_identifier,group_esmis_student_self,1,0,0,0
access_esmis_education_history_self,esmis.education.history / Student Self,model_esmis_education_history,group_esmis_student_self,1,0,0,0
```

**Note:** `res.partner` already has ACLs from Odoo core. The student-specific fields are
controlled via `groups=` attributes on field definitions and record rules, not additional
ACL rows.

### 5.6 Record Rules

| XML ID | Model | Domain | Groups | Purpose |
|--------|-------|--------|--------|---------|
| `rule_student_partner_campus` | `res.partner` | `[('is_student', '=', True), ('company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation for student partners |
| `rule_student_self` | `res.partner` | `[('id', '=', user.partner_id.id)]` | `group_esmis_student_self` | Student sees own record only |
| `rule_student_registrar_all` | `res.partner` | `[(1, '=', 1)]` | `group_esmis_registrar_manager` | Registrar manager sees all campuses |
| `rule_identifier_partner` | `esmis.identifier` | `[('partner_id.company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation via partner→campus |
| `rule_identifier_self` | `esmis.identifier` | `[('partner_id', '=', user.partner_id.id)]` | `group_esmis_student_self` | Student sees own identifiers |
| `rule_education_history_partner` | `esmis.education.history` | `[('partner_id.company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation |
| `rule_education_history_self` | `esmis.education.history` | `[('partner_id', '=', user.partner_id.id)]` | `group_esmis_student_self` | Student sees own history |

### 5.7 Menus

Under the eSMIS main menu (`esmis_base.menu_esmis_main`):

```
eSMIS (seq 80)
├── Students (seq 10, group: registrar_viewer)
│   ├── All Students (seq 10, action: student list filtered by is_student=True)
│   └── Identifiers (seq 20, action: identifier list)
├── Configuration (seq 99, group: registrar_manager)
│   └── Education Levels (seq 10, action: vocabulary codes filtered by education-level)
```

### 5.8 Vocabulary Seed Data

**`urn:esmis:education-level`** — loaded in `data/vocabulary_education_level.xml`:

| Code | Display | Sequence |
|------|---------|----------|
| `pre_school` | Pre-School | 10 |
| `elementary` | Elementary | 20 |
| `junior_high_school` | Junior High School | 30 |
| `senior_high_school` | Senior High School | 40 |
| `tertiary` | Tertiary | 50 |
| `graduate` | Graduate Studies | 60 |
| `post_graduate` | Post-Graduate Studies | 70 |

### 5.9 Demo Data

- 20 student partners at "Rizal State University" (Main campus):
  - 3 applicants, 2 admitted, 5 enrolled/active, 2 on LOA, 3 graduated,
    2 alumni, 1 dismissed, 1 transferred out, 1 denied
- Each student has: first_name, last_name, middle_name, birthdate, gender, civil status
- 3 minor students (age < 18) with `guardian_id` linked to guardian partners
- 5 students with encrypted identifiers (PhilSys, LRN)
- 10 students with education history records (elementary through SHS)
- All demo data uses fictional names and `@rsu.edu.ph` emails
- Use `with_context(tracking_disable=True)`

### 5.10 Acceptance Criteria

- [ ] `res.partner` extended with `is_student` and all demographic fields
- [ ] `display_name` computed from structured name fields when `is_student=True`
- [ ] `age` computed from `birthdate`
- [ ] Student state machine enforces valid transitions (invalid raises `UserError`)
- [ ] `esmis.identifier` encrypts values and supports blind index search
- [ ] `esmis.education.history` creates education records linked to partner
- [ ] Guardian required when student age < 18
- [ ] Campus isolation via `company_id` record rules on student partners
- [ ] Student Self record rule works (student sees only own record)
- [ ] Registrar viewer/officer/manager permissions enforced
- [ ] Complete ACLs for `esmis.identifier` and `esmis.education.history`
- [ ] No PII in log messages or exception text
- [ ] Demo data creates students across multiple lifecycle states
- [ ] Tests cover state machine (valid and invalid transitions)
- [ ] Tests cover encryption round-trip and blind index search
- [ ] Tests cover education history CRUD
- [ ] Tests cover guardian requirement for minors
- [ ] Tests cover display_name computation
- [ ] Tests cover campus isolation
- [ ] Tests cover consent integration via `esmis.consent.mixin`

---

## 6. Module Spec: esmis_ph

### 6.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_ph` |
| Description | Philippine-specific extensions for eSMIS |
| Dependencies | `esmis_student`, `esmis_address` |
| Version | `19.0.1.0.0` |
| `application` | `False` |
| `auto_install` | `False` |
| `excludes` | (future country modules: `esmis_ke`, `esmis_ng`, etc.) |
| Category | `eSMIS/Localization` |

### 6.2 Module Structure

```
esmis_ph/
├── __manifest__.py
├── __init__.py
├── hooks.py                    # post_init_hook for barangay bulk load
├── models/
│   ├── __init__.py
│   ├── res_partner.py          # PH-specific fields on res.partner
│   ├── address.py              # PH-specific fields on esmis.address
│   ├── psgc_region.py
│   ├── psgc_province.py
│   ├── psgc_city_municipality.py
│   └── psgc_barangay.py
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── res_partner_views.xml   # Inherit to add PH fields
│   ├── address_views.xml       # Inherit to add PSGC fields
│   └── psgc_views.xml          # PSGC browser (read-only reference)
├── data/
│   ├── vocabulary_name_suffix.xml
│   ├── vocabulary_ethnicity_ph.xml
│   ├── vocabulary_religion_ph.xml
│   ├── vocabulary_identifier_type_ph.xml
│   ├── psgc_regions.xml
│   ├── psgc_provinces.xml
│   ├── psgc_cities_municipalities.xml
│   └── psgc/
│       └── barangays.csv       # ~42,000 rows for bulk SQL load
├── demo/
│   └── demo_ph_data.xml        # PH-specific demo data extensions
├── tests/
│   ├── __init__.py
│   ├── test_ph_partner_fields.py
│   ├── test_ph_address.py
│   ├── test_ph_display_name.py
│   ├── test_psgc_hierarchy.py
│   └── test_psgc_data_load.py
└── readme/
    └── DESCRIPTION.md
```

### 6.3 Models

#### 6.3.1 `res.partner` extension (PH-specific fields)

```python
class ResPartner(models.Model):
    _inherit = "res.partner"

    middle_name_b4_marriage = fields.Char(
        string="Middle Name (Before Marriage)",
        help="Woman's maiden surname, which becomes the middle name after marriage "
             "per Philippine naming convention.",
    )
    suffix_ids = fields.Many2many(
        "esmis.vocabulary.code",
        "res_partner_suffix_rel",
        "partner_id",
        "suffix_id",
        string="Name Suffixes",
        domain="[('namespace_uri', '=', 'urn:esmis:name-suffix')]",
    )
    ethnicity_id = fields.Many2one(
        "esmis.vocabulary.code",
        string="Ethnicity",
        domain="[('namespace_uri', '=', 'urn:esmis:ethnicity-ph')]",
    )
    religion_id = fields.Many2one(
        "esmis.vocabulary.code",
        string="Religion",
        domain="[('namespace_uri', '=', 'urn:esmis:religion-ph')]",
    )
    is_solo_parent = fields.Boolean(
        default=False,
        help="Solo Parent per RA 8972/11861. Eligible for scholarship programs.",
    )
    is_4ps_beneficiary = fields.Boolean(
        string="4Ps Beneficiary",
        default=False,
        help="Pantawid Pamilyang Pilipino Program beneficiary.",
    )
```

**Display name override:**

```python
@api.depends(
    "first_name", "last_name", "middle_name",
    "middle_name_b4_marriage", "suffix_ids", "is_student",
)
def _compute_student_display_name(self):
    """Philippine name format: LAST NAME, FIRST NAME MIDDLE_INITIAL. SUFFIX"""
    for partner in self:
        if partner.is_student and partner.last_name:
            parts = [partner.last_name + ",", partner.first_name]
            # Use maiden name as middle name if married
            mi_source = partner.middle_name_b4_marriage or partner.middle_name
            if mi_source:
                parts.append(mi_source[0] + ".")  # Middle initial
            if partner.suffix_ids:
                parts.append(
                    ", ".join(partner.suffix_ids.mapped("display"))
                )
            partner.display_name = " ".join(filter(None, parts))
        else:
            partner.display_name = partner._get_default_display_name()
```

**PII classification additions:**

```python
_pii_fields = {
    "ethnicity_id": {"tier": 1, "masking_pattern": None, "groups": None},
    "religion_id": {"tier": 1, "masking_pattern": None, "groups": None},
    "middle_name_b4_marriage": {"tier": 1, "masking_pattern": None, "groups": None},
}
```

---

#### 6.3.2 `esmis.address` extension (PH address fields)

```python
class EsmisAddress(models.Model):
    _inherit = "esmis.address"

    region_id = fields.Many2one("esmis.psgc.region", string="Region")
    province_id = fields.Many2one(
        "esmis.psgc.province",
        string="Province",
        domain="[('region_id', '=', region_id)]",
    )
    city_municipality_id = fields.Many2one(
        "esmis.psgc.city.municipality",
        string="City / Municipality",
        domain="[('province_id', '=', province_id)]",
    )
    barangay_id = fields.Many2one(
        "esmis.psgc.barangay",
        string="Barangay",
        domain="[('city_municipality_id', '=', city_municipality_id)]",
    )
    zip_code = fields.Char(related="city_municipality_id.zip_code", store=True)
```

**`address_text` override:**

```python
@api.depends(
    "street1", "street2", "barangay_id", "city_municipality_id",
    "province_id", "region_id", "zip_code",
)
def _compute_address_text(self):
    for rec in self:
        if rec.region_id:
            # Philippine address format
            parts = filter(None, [
                rec.street1,
                rec.street2,
                rec.barangay_id.name if rec.barangay_id else None,
                rec.city_municipality_id.name if rec.city_municipality_id else None,
                rec.province_id.name if rec.province_id else None,
                rec.region_id.name if rec.region_id else None,
                rec.zip_code,
            ])
            rec.address_text = ", ".join(parts)
        else:
            # Fall back to base computation
            super(EsmisAddress, rec)._compute_address_text()
```

**Cascading onchange:**

When `region_id` changes, clear `province_id`, `city_municipality_id`, `barangay_id`.
When `province_id` changes, clear `city_municipality_id`, `barangay_id`. Etc.

```python
@api.onchange("region_id")
def _onchange_region_id(self):
    self.province_id = False
    self.city_municipality_id = False
    self.barangay_id = False

@api.onchange("province_id")
def _onchange_province_id(self):
    self.city_municipality_id = False
    self.barangay_id = False

@api.onchange("city_municipality_id")
def _onchange_city_municipality_id(self):
    self.barangay_id = False
```

---

#### 6.3.3 PSGC Geographic Models

Four models representing the Philippine Standard Geographic Code hierarchy.

##### `esmis.psgc.region`

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Region name (e.g., "NCR") |
| `psgc_code` | Char | required=True, index=True | PSGC code (e.g., "130000000") |
| `designation` | Char | | Full designation (e.g., "National Capital Region") |

**Constraint:** `UNIQUE(psgc_code)`

##### `esmis.psgc.province`

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Province name |
| `psgc_code` | Char | required=True, index=True | PSGC code |
| `region_id` | Many2one | `esmis.psgc.region`, required=True, index=True | Parent region |

**Constraint:** `UNIQUE(psgc_code)`

##### `esmis.psgc.city.municipality`

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | City/municipality name |
| `psgc_code` | Char | required=True, index=True | PSGC code |
| `province_id` | Many2one | `esmis.psgc.province`, required=True, index=True | Parent province |
| `is_city` | Boolean | default=False | True for cities, False for municipalities |
| `zip_code` | Char | | ZIP code |

**Constraint:** `UNIQUE(psgc_code)`

##### `esmis.psgc.barangay`

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Barangay name |
| `psgc_code` | Char | required=True, index=True | PSGC code |
| `city_municipality_id` | Many2one | `esmis.psgc.city.municipality`, required=True, index=True | Parent city/municipality |

**Constraint:** `UNIQUE(psgc_code)`

---

### 6.4 PSGC Data Loading

**Regions, provinces, cities/municipalities** (~1,600 total records): Loaded via standard
XML data files with `noupdate="1"`. These are manageable volumes for the ORM.

**Barangays** (~42,000 records): Loaded via `post_init_hook` using raw SQL.

```python
# esmis_ph/hooks.py
import csv
import os
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """Bulk-load barangay records from CSV using raw SQL COPY."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "data", "psgc", "barangays.csv"
    )
    if not os.path.exists(csv_path):
        _logger.warning("PSGC barangay CSV not found at %s", csv_path)
        return

    cr = env.cr

    # Check if barangays already loaded
    cr.execute("SELECT COUNT(*) FROM esmis_psgc_barangay")
    if cr.fetchone()[0] > 0:
        _logger.info("PSGC barangays already loaded, skipping.")
        return

    _logger.info("Loading PSGC barangays from CSV...")

    # Build city_municipality psgc_code → id mapping
    cr.execute("SELECT psgc_code, id FROM esmis_psgc_city_municipality")
    city_map = dict(cr.fetchall())

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            cm_id = city_map.get(row["city_municipality_psgc_code"])
            if cm_id:
                batch.append((row["name"], row["psgc_code"], cm_id))

        if batch:
            from psycopg2.extras import execute_values
            execute_values(
                cr,
                """INSERT INTO esmis_psgc_barangay
                   (name, psgc_code, city_municipality_id, create_uid, write_uid,
                    create_date, write_date)
                   VALUES %s""",
                [(name, code, cm_id, 1, 1, 'now()', 'now()')
                 for name, code, cm_id in batch],
                page_size=5000,
            )
            _logger.info("Loaded %d barangay records.", len(batch))
```

**CSV format (`barangays.csv`):**

```csv
psgc_code,name,city_municipality_psgc_code
133901001,Barangay 1,133901000
133901002,Barangay 2,133901000
...
```

**`__manifest__.py` hook registration:**

```python
"post_init_hook": "post_init_hook",
```

### 6.5 Vocabulary Seed Data

**`urn:esmis:name-suffix`** — `data/vocabulary_name_suffix.xml`:

| Code | Display | Sequence |
|------|---------|----------|
| `jr` | Jr. | 10 |
| `sr` | Sr. | 20 |
| `ii` | II | 30 |
| `iii` | III | 40 |
| `iv` | IV | 50 |
| `phd` | PhD | 60 |
| `md` | MD | 70 |
| `edd` | EdD | 80 |
| `llb` | LLB | 90 |
| `cpa` | CPA | 100 |
| `rn` | RN | 110 |

**`urn:esmis:ethnicity-ph`** — `data/vocabulary_ethnicity_ph.xml`:

| Code | Display |
|------|---------|
| `tagalog` | Tagalog |
| `cebuano` | Cebuano |
| `ilocano` | Ilocano |
| `bisaya` | Bisaya/Binisaya |
| `hiligaynon` | Hiligaynon/Ilonggo |
| `bikol` | Bikol |
| `waray` | Waray |
| `pangasinan` | Pangasinan |
| `kapampangan` | Kapampangan |
| `maranao` | Maranao |
| `maguindanao` | Maguindanao |
| `tausug` | Tausug |
| `other_ip` | Other Indigenous People |
| `other` | Other |

**`urn:esmis:religion-ph`** — `data/vocabulary_religion_ph.xml`:

| Code | Display |
|------|---------|
| `roman_catholic` | Roman Catholic |
| `islam` | Islam |
| `iglesia_ni_cristo` | Iglesia ni Cristo |
| `philippine_independent` | Philippine Independent Church (Aglipayan) |
| `seventh_day_adventist` | Seventh Day Adventist |
| `bible_baptist` | Bible Baptist Church |
| `uccp` | United Church of Christ in the Philippines |
| `jehovahs_witnesses` | Jehovah's Witnesses |
| `evangelical` | Evangelical |
| `born_again` | Born Again Christian |
| `buddhist` | Buddhist |
| `mormon` | The Church of Jesus Christ of Latter-day Saints |
| `other` | Other |
| `none` | None |

**`urn:esmis:identifier-type-ph`** — `data/vocabulary_identifier_type_ph.xml`:

| Code | Display | Description |
|------|---------|-------------|
| `philsys` | PhilSys (PSN) | Philippine Identification System number |
| `lrn` | Learner Reference Number | DepEd learner tracking number |
| `tin` | Tax Identification Number | BIR tax ID |
| `sss` | SSS Number | Social Security System number |
| `gsis` | GSIS Number | Government Service Insurance System |
| `pwd_id` | PWD ID | Person with Disability identification |
| `solo_parent_id` | Solo Parent ID | RA 8972/11861 Solo Parent |
| `passport` | Passport Number | Philippine passport |

### 6.6 Security

**ACL Matrix (`ir.model.access.csv`):**

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# --- PSGC reference data (read-only for all internal users) ---
access_psgc_region_user,esmis.psgc.region / User,model_esmis_psgc_region,base.group_user,1,0,0,0
access_psgc_province_user,esmis.psgc.province / User,model_esmis_psgc_province,base.group_user,1,0,0,0
access_psgc_city_municipality_user,esmis.psgc.city.municipality / User,model_esmis_psgc_city_municipality,base.group_user,1,0,0,0
access_psgc_barangay_user,esmis.psgc.barangay / User,model_esmis_psgc_barangay,base.group_user,1,0,0,0
# --- System admin (full access for data maintenance) ---
access_psgc_region_system,esmis.psgc.region / System,model_esmis_psgc_region,base.group_system,1,1,1,1
access_psgc_province_system,esmis.psgc.province / System,model_esmis_psgc_province,base.group_system,1,1,1,1
access_psgc_city_municipality_system,esmis.psgc.city.municipality / System,model_esmis_psgc_city_municipality,base.group_system,1,1,1,1
access_psgc_barangay_system,esmis.psgc.barangay / System,model_esmis_psgc_barangay,base.group_system,1,1,1,1
```

**No record rules:** PSGC data is public reference data — no campus isolation needed.

### 6.7 Views

**Partner form extension** — adds PH fields to the student form:

- "Personal Information" group: `ethnicity_id`, `religion_id`, `middle_name_b4_marriage`,
  `suffix_ids`, `is_solo_parent`, `is_4ps_beneficiary`
- These fields only appear when `is_student=True` (use `invisible` attribute)

**Address form extension** — replaces generic `city`, `state_province` with PSGC cascading
dropdowns:

```xml
<!-- Hide generic fields, show PSGC fields when country is PH -->
<field name="region_id" invisible="country_id != ref('base.ph')"/>
<field name="province_id" invisible="country_id != ref('base.ph')"/>
<field name="city_municipality_id" invisible="country_id != ref('base.ph')"/>
<field name="barangay_id" invisible="country_id != ref('base.ph')"/>
```

**PSGC browser** — read-only list views for regions, provinces, cities, and barangays.
Available under Settings > eSMIS > PSGC Reference (superuser only, for data
verification).

### 6.8 Demo Data

- Extend existing demo students with PH-specific fields:
  - `ethnicity_id`, `religion_id` for all 20 students
  - `suffix_ids` for 3 students (Jr, PhD, etc.)
  - `middle_name_b4_marriage` for 2 married female students
  - `is_solo_parent=True` for 1 student
  - `is_4ps_beneficiary=True` for 2 students
- Extend existing demo addresses with PSGC references:
  - Link 10 addresses to specific regions/provinces/cities/barangays
- Create 5 PH identifier records (PhilSys, LRN) for demo students

### 6.9 Acceptance Criteria

- [ ] PH-specific fields appear on student partner form
- [ ] `middle_name_b4_marriage` field works correctly
- [ ] `suffix_ids` Many2many stores and displays correctly
- [ ] `ethnicity_id` and `religion_id` use PH vocabulary codes
- [ ] PSGC hierarchy loads: 17 regions, ~82 provinces, ~1,500 cities/municipalities
- [ ] Barangay bulk load completes in < 30 seconds
- [ ] PSGC cascading dropdowns filter correctly (region → province → city → barangay)
- [ ] `address_text` computed correctly in PH format
- [ ] Onchange cascading clears lower-level PSGC fields
- [ ] Display name includes suffix and uses middle initial format
- [ ] PH identifier types (PhilSys, LRN, TIN, etc.) seeded
- [ ] All 4 PSGC models have complete ACLs
- [ ] `excludes` declared in manifest (empty for now, ready for future country modules)
- [ ] Tests cover PH partner fields
- [ ] Tests cover PSGC cascading selection
- [ ] Tests cover PH address format computation
- [ ] Tests cover PH display name override
- [ ] Tests cover barangay data load

---

## 7. Module Spec: esmis_starter_ph

### 7.1 Overview

Rename `esmis_starter` → `esmis_starter_ph`. This is a **directory rename and manifest
update**, not a new module.

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_starter_ph` |
| Description | eSMIS for Philippine Higher Education Institutions |
| Dependencies | `esmis_base`, `esmis_vocabulary`, `esmis_security`, `esmis_consent`, `esmis_approval`, `esmis_student`, `esmis_address`, `esmis_ph` |
| Version | `19.0.1.0.0` |
| `application` | `True` |
| `auto_install` | `False` |
| Category | `eSMIS` |

### 7.2 Changes from `esmis_starter`

1. **Rename directory:** `esmis_starter/` → `esmis_starter_ph/`
2. **Update manifest `name`:** `"eSMIS"` → `"eSMIS - Philippines"`
3. **Add dependencies:** `esmis_student`, `esmis_address`, `esmis_ph`
4. **Existing localization data retained:**
   - `data/res_company_data.xml` — activates PHP currency, sets PH country,
     Asia/Manila timezone (already correct)

### 7.3 Module Structure

```
esmis_starter_ph/
├── __manifest__.py
├── __init__.py
├── data/
│   └── res_company_data.xml     # PH localization defaults (unchanged)
└── readme/
    └── DESCRIPTION.md
```

### 7.4 Acceptance Criteria

- [ ] `esmis_starter_ph` installs successfully and pulls all dependencies
- [ ] All Phase 1 modules install in correct order
- [ ] Philippine localization defaults applied (PHP currency, PH country, Asia/Manila TZ)
- [ ] Module appears in Apps menu as "eSMIS - Philippines"
- [ ] No `esmis_starter` directory remains

---

## 8. Vocabulary Seed Data Summary

Vocabularies defined across Phase 1B modules:

| Namespace URI | Module | Codes |
|---------------|--------|-------|
| `urn:esmis:address-type` | `esmis_address` | permanent, mailing, residency, emergency |
| `urn:esmis:education-level` | `esmis_student` | pre_school, elementary, junior_high_school, senior_high_school, tertiary, graduate, post_graduate |
| `urn:esmis:name-suffix` | `esmis_ph` | jr, sr, ii, iii, iv, phd, md, edd, llb, cpa, rn |
| `urn:esmis:ethnicity-ph` | `esmis_ph` | tagalog, cebuano, ilocano, bisaya, hiligaynon, bikol, waray, pangasinan, kapampangan, maranao, maguindanao, tausug, other_ip, other |
| `urn:esmis:religion-ph` | `esmis_ph` | roman_catholic, islam, iglesia_ni_cristo, philippine_independent, seventh_day_adventist, bible_baptist, uccp, jehovahs_witnesses, evangelical, born_again, buddhist, mormon, other, none |
| `urn:esmis:identifier-type-ph` | `esmis_ph` | philsys, lrn, tin, sss, gsis, pwd_id, solo_parent_id, passport |

**Already existing vocabularies** (from `esmis_vocabulary`, used by `esmis_student`):

| Namespace URI | Used For |
|---------------|----------|
| `urn:iso:std:iso:5218` | Gender |
| `urn:un:unsd:pop-census:marital-status` | Civil status |
| `urn:tpl:vocab:blood-type` | Blood type |
| `urn:esmis:vocabulary:disability-type` | Disability type |
| `urn:esmis:vocabulary:relationship-type` | Guardian relationship |

---

## 9. Cross-Cutting Requirements

### 9.1 Dependency Graph

```
esmis_starter_ph (application=True, PH localization)
├── esmis_ph (PH fields, PSGC, PH vocabs)
│   ├── esmis_student (universal student demographics)
│   │   ├── esmis_security (groups, mixins)
│   │   ├── esmis_vocabulary (code lists)
│   │   ├── esmis_consent (consent records)
│   │   └── esmis_address (address model)
│   │       └── esmis_base (root menus)
│   └── esmis_address
├── esmis_approval (approval workflows)
├── (all Phase 1A modules transitively)
└── esmis_base
```

### 9.2 Update Phase 1 Plan

After Edwin approves this plan, update `phase-1-plan.md` section 6 (esmis_student) to
reference this document for the revised design. Add a note that esmis_student no longer
has `application=True` and that `esmis.student.program` is deferred to Phase 2.

### 9.3 TDD, commits, verification

Same requirements as Phase 1A — see `phase-1-plan.md` section 7.

---

## 10. Parallelization Strategy

| Work Stream | Can Start When | Blocked Until |
|-------------|---------------|---------------|
| `esmis_address` models + tests | Phase 1A complete | esmis_base exists |
| `esmis_student` models + tests | After esmis_address stable | Address model passes tests |
| `esmis_ph` PSGC models | After esmis_address stable | Address model exists |
| `esmis_ph` partner extensions | After esmis_student stable | Student partner fields exist |
| `esmis_ph` PSGC data prep | Immediately (data work) | — |
| `esmis_starter_ph` rename | After all Phase 1B modules built | All modules pass tests |
| Demo data (all modules) | After core models pass tests | Models exist |

**With 2 developers:**

- Developer A: `esmis_address` → `esmis_student`
- Developer B: Prepare PSGC CSV data → `esmis_ph` PSGC models → `esmis_ph` partner/address extensions
- Both: Demo data, starter rename

**With 1 developer:**

1. Build `esmis_address` (small, quick)
2. Build `esmis_student` (largest module)
3. Prepare PSGC data (can happen between coding sessions)
4. Build `esmis_ph` (PSGC models → partner/address extensions → vocabs → data load)
5. Rename `esmis_starter` → `esmis_starter_ph`
6. Write demo data for all modules
7. Final integration test

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PSGC data file too large for git | LOW | LOW | CSV is ~3MB compressed; well within git limits |
| Barangay bulk SQL load fails on different DB engines | LOW | MEDIUM | Test with PostgreSQL (Odoo's only supported DB); fallback to ORM batch if needed |
| `res.partner` `display_name` computation conflicts with Odoo core | MEDIUM | HIGH | Use `_compute_display_name` override carefully; test with Odoo's own partner tests |
| Country module `excludes` not testable until second country exists | LOW | LOW | Add empty `excludes` now; test when Kenya/Nigeria modules are built |
| 42K barangay records slow down address form Many2one search | MEDIUM | MEDIUM | Use `limit` on search; add `name_search` override with parent filtering; cascading onchange ensures small result sets |
| `middle_name` in base conflicts with locales that don't use middle names | LOW | LOW | Field is optional; only displayed when `is_student=True` |
| PSGC codes change annually (PSA updates) | LOW | LOW | Data files can be updated; `psgc_code` is the stable key; `noupdate="1"` allows manual overrides |

---

## Appendix A: Old Code Field Mapping

Mapping from `custom_res_partner.py` (old eSMIS) to new module design:

| Old Field | New Location | New Field | Notes |
|-----------|-------------|-----------|-------|
| `x_first_name` | `esmis_student` | `first_name` | |
| `x_last_name` | `esmis_student` | `last_name` | |
| `x_middle_name` | `esmis_student` | `middle_name` | |
| `x_suffix` | `esmis_ph` | `suffix_ids` | Changed from Char to Many2many vocabulary |
| `x_gender` | `esmis_student` | `gender_id` | Changed from Selection to vocabulary |
| `x_civil_status` | `esmis_student` | `civil_status_id` | Changed from Selection to vocabulary |
| `x_birthdate` | `esmis_student` | `birthdate` | |
| `x_birthplace` | `esmis_student` | `birthplace` | |
| `x_age` | `esmis_student` | `age` | Now computed from birthdate |
| `x_nationality` | `esmis_student` | `nationality_id` | Changed from Char to Many2one res.country |
| `x_blood_type` | `esmis_student` | `blood_type_id` | Changed from Selection to vocabulary |
| `x_religion` | `esmis_ph` | `religion_id` | PH-specific; changed to vocabulary |
| `x_ethnicity` | `esmis_ph` | `ethnicity_id` | PH-specific; changed to vocabulary |
| `x_pwd_type` | `esmis_student` | `disability_type_id` | Universal (RA 7277/10754) |
| `x_street`, `x_city`, etc. | `esmis_address` / `esmis_ph` | PSGC fields | Structured address model |
| `x_father_*`, `x_mother_*`, `x_guardian_*` | `esmis_student` | `guardian_id` + `guardian_relationship_id` | Partner relationships, not flat text |
| `x_elem_school`, `x_elem_year_graduated`, etc. (18 fields) | `esmis_student` | `education_history_ids` | One2many structured records |
| `x_lrn`, `x_philsys_id` | `esmis_student` | `identifier_ids` | Encrypted identifier model |
| `x_admission_no` | Deferred | — | Phase 2 (`esmis_enrollment`) |
| `x_student_status` | `esmis_student` | `student_state` | |
| `x_middle_name_b4_marriage` | `esmis_ph` | `middle_name_b4_marriage` | PH-specific naming convention |

## Appendix B: PSGC Data Source

**Source:** Philippine Statistics Authority (PSA)
**URL:** https://psa.gov.ph/classification/psgc
**Publication format:** Excel spreadsheet, updated annually
**Latest version used:** PSGC as of Q4 2025

The CSV files in `esmis_ph/data/psgc/` are derived from the PSA publication. The
conversion process:

1. Download latest PSGC Excel from PSA
2. Run conversion script (`scripts/convert_psgc.py` — to be created) that:
   - Reads the Excel file
   - Outputs `psgc_regions.xml`, `psgc_provinces.xml`, `psgc_cities_municipalities.xml`
   - Outputs `barangays.csv`
3. Review diffs and commit updated data files
4. Conversion script is NOT part of the Odoo module — it's a development tool
