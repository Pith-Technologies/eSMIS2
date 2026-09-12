# Phase 1 Build Plan: Foundation Layer

Detailed implementation blueprint for Phase 1 of eSMIS. A developer reading this plan
should not need to reference any other document to implement these modules.

**Created:** 2026-03-09
**Status:** Approved — decisions finalized 2026-03-09

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Key Design Decisions Requiring Edwin's Input](#2-key-design-decisions-requiring-edwins-input)
3. [Module Build Order](#3-module-build-order)
4. [Module Spec: esmis_security](#4-module-spec-esmis_security)
5. [Module Spec: esmis_academic_term](#5-module-spec-esmis_academic_term)
6. [Module Spec: esmis_student](#6-module-spec-esmis_student)
7. [Cross-Cutting Implementation Requirements](#7-cross-cutting-implementation-requirements)
8. [Parallelization Strategy](#8-parallelization-strategy)
9. [Risk Register](#9-risk-register)

---

## 1. Executive Summary

Phase 1 builds the data backbone of eSMIS. It delivers three modules on top of the
already-completed `esmis_vocabulary`:

| Order | Module | Size | Models | Purpose |
|-------|--------|------|--------|---------|
| — | `esmis_vocabulary` | M | 3 | Done. Controlled code lists. |
| 1 | `esmis_security` | L | 6 abstract + 4 concrete = 10 | Security groups, mixins, consent, approval definitions |
| 2 | `esmis_audit` | M | 6 concrete | Audit logs, PII access logs, breach, DSAR, retention, disposal |
| 3 | `esmis_academic_term` | S | 2 | Academic year and term definitions |
| 4 | `esmis_student` | L | 3 (course history deferred) | Student profiles, identifiers, program bindings |

**Phase 1 goal:** The institution can configure its terminology, security groups, campuses,
academic calendar, and begin entering student profiles. No academic operations yet.

**What the system can do after Phase 1:**
- Configure campuses (via `res.company`)
- Define security groups and assign users to roles
- Set up consent scopes and retention schedules
- Define academic years and terms with enrollment windows
- Create and manage student profiles across lifecycle states
- Track encrypted government identifiers (PhilSys, LRN, TIN)
- Record consent per student per purpose (RA 10173)
- Handle data subject requests and breach notifications

---

## 2. Key Design Decisions Requiring Edwin's Input

### Decision 1: Should esmis_security be split into smaller modules?

The roadmap lists 16 models (6 abstract + 10 concrete). ADR-016 says "if it grows beyond
~15 models, consider extracting `esmis_audit` or `esmis_consent`."

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A** | Keep as one module | Simpler dependency graph; one install | XL module; 16 models is at the threshold |
| **B** | Split into 3: `esmis_security` (groups + mixins), `esmis_consent` (consent + scope), `esmis_audit` (logs + retention + disposal + breach + DSAR) | Each module is focused | 3 modules to coordinate; more dependency edges |
| **C** | Split into 2: `esmis_security` (groups + mixins + consent) and `esmis_audit` (logs + retention + disposal + breach + DSAR) | Consent tightly coupled to security (enforcement uses group checks); audit/retention/breach are operationally separate | Still 2 modules instead of 1 |

**Recommendation:** Option C. Consent enforcement checks security groups, so consent
belongs with security. Audit, retention, disposal, breach, and DSAR are operational
compliance models that share a "data lifecycle" concern distinct from access control.
This gives ~10 models in `esmis_security` and ~6 in `esmis_audit`.

**Doc contradiction:** The ERD mixin summary table (erd.md line 1156) lists
`esmis.audit.mixin` as belonging to `esmis_audit`, while the data model registry
(data-model-registry.md) lists it under `esmis_security`. The mixin summary also lists
`esmis.encrypted.field.mixin` as belonging to `esmis_pii_encryption`, a module not in our
Phase 1 scope.

> **Decision:** Option C — split into `esmis_security` + `esmis_audit`. Both built in
> Phase 1 since breach and DSAR acceptance criteria require the audit models.

---

### Decision 2: Encryption approach for Phase 1

ADR-006 specifies AES-256-GCM encryption via the `esmis_pii_encryption` module with a
full key management provider hierarchy (config, DB, Vault, cloud KMS). However, the
data-privacy-and-pii.md principle doc (line 129) says: "Tier 3 fields use Fernet
(AES-128-CBC with HMAC-SHA256 authentication) via the `cryptography` library."

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A** | Fernet (`cryptography` library) | Simpler; well-tested; built into Python ecosystem; sufficient for Phase 1; same blind index (HMAC-SHA256) either way | AES-128-CBC not AES-256-GCM; would need to migrate later if spec demands exact match |
| **B** | AES-256-GCM via `cryptography` library | Matches ADR-006 spec exactly; stronger encryption | More complex key management; more code to write and test |

**Recommendation:** Option A (Fernet) for Phase 1. The `esmis.identifier` model in
`esmis_student` is the only Phase 1 consumer. Fernet is simpler to implement correctly,
and the blind index (HMAC-SHA256) is identical either way. We can introduce the full
`esmis_pii_encryption` module with AES-256-GCM and tiered key management in a later
phase when payment encryption requires it.

**Doc contradiction:** ADR-006 "Implementation Summary" claims the encrypted field mixin
is "complete" with AES-256-GCM, but no `esmis_pii_encryption` module directory exists in
the codebase. The principle doc explicitly says Fernet. ADR-006 appears to be a
forward-looking design spec, not a description of existing code.

> **Decision:** AES-256-GCM from the start. Implement the full spec per ADR-006
> rather than taking on migration debt.

---

### Decision 3: Should esmis.student depend on esmis_academic_term?

The roadmap lists `esmis_student`'s dependencies as: `base`, `esmis_vocabulary`,
`esmis_security`. But `esmis.student.course.history` references `esmis.academic.term` via
`term_id`.

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A** | Add `esmis_academic_term` as a dependency | Cleaner; course history works out of the box | Couples two foundation modules; circular-ish feel |
| **B** | Defer `esmis.student.course.history` to `esmis_enrollment` (Phase 2) | Keeps `esmis_student` focused on profile and lifecycle; course history is really an enrollment artifact | Phase 1 has 3 models in `esmis_student` instead of 4 |

**Recommendation:** Option B. Course history records are created when grades are locked
(a Phase 2 operation). The model references `esmis.course` and `esmis.grade`, which are
Phase 2 models (`esmis_curriculum` and `esmis_grading`). Deferring it keeps `esmis_student`
dependency-free from academic operations.

> **Decision:** Yes — defer `esmis.student.course.history` to Phase 2
> (`esmis_enrollment`). Keeps `esmis_student` focused on profile and lifecycle.

---

### Decision 4: How to handle esmis.consent's student_id field

`esmis.consent` references `esmis.student` per the consent-management.md spec, but
`esmis_security` is built BEFORE `esmis_student`.

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A** | Use `res.partner` instead of `esmis.student` in consent | Works immediately; `res.partner` is universal | Less precise; consent records for non-students would be possible |
| **B** | Define consent model in `esmis_student` instead of `esmis_security` | Correct FK target | Consent is infrastructure, not student domain; breaks separation |
| **C** | Keep consent in `esmis_security` with generic `partner_id`; `esmis_student` adds a computed `student_id` field via `_inherit` | Consent stays in security; FK is correct for Odoo's model; student module enhances it | Slightly more complex inheritance |

**Recommendation:** Option C. Consent is infrastructure (it belongs in `esmis_security`).
Using `partner_id` (Many2one to `res.partner`) makes it work without circular
dependencies. When `esmis_student` installs, it can add helper methods or computed fields
to link consent records back to student records via the partner relationship. This is
standard Odoo extension pattern.

> **Decision:** Option C — `partner_id` in consent model. `esmis_student` adds
> computed helper to link consent records via the partner relationship.

---

### Decision 5: Security group scope — define all domain categories now or incrementally?

ADR-001 defines 26 domain categories in `esmis_security`. The question is whether Phase 1
defines all 26 upfront or only the categories needed for Phase 1 modules.

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A** | Define all 26 categories in `esmis_security` now | Single source of truth; no changes needed when Phase 2+ modules install | Unused categories clutter the UI until their modules install |
| **B** | Each module defines its own `ir.module.category` and privilege records | Distributed; follows Odoo pattern; categories only appear when module installs | Risk of inconsistency; requires coordination |

**Recommendation:** Option B. Each module defines its own `ir.module.category` and
privilege records. `esmis_security` only defines cross-cutting categories: `admin`,
`audit`, `consent`, `data_protection`, `approval`. Domain categories like `enrollment`,
`grading`, `billing` are defined by their respective modules. This follows Odoo's native
pattern where categories appear only when their module is installed.

**Note:** ADR-001's existing implementation defined all 26 categories centrally. If we
go with Option B, we should update ADR-001 to reflect this change.

> **Decision:** Option B — distributed. Each module owns its categories and
> privileges. `esmis_security` only defines cross-cutting ones (admin, audit,
> consent, data_protection, approval).

---

### Decision 6: Demo data scope

How much demo data should Phase 1 create?

**Recommendation:** Create a fictional university "Rizal State University" (RSU) with:

- **3 campuses** (Main, North, South) as `res.company` records
- **Security configuration:** all Phase 1 groups with demo users per role
- **1 academic year** (AY 2025-2026) with 2 semesters + 1 summer term
- **20 students** across different lifecycle states (applicant, admitted, enrolled,
  active, loa, graduated, alumni, dismissed, transferred_out)
- **5 demo users:** registrar officer, registrar manager, faculty, DPO, system admin
- **Sample consent records** for 10 students (various purposes)
- **1 retention schedule** with common data types
- **Sample identifiers** with encrypted values for 5 students

This makes the system immediately usable for evaluation and testing.

> **Decision:** Approved as recommended. Rizal State University, 3 campuses,
> 20 students, 5 demo users, AY 2025-2026 with 2 semesters + summer.

---

## 3. Module Build Order

```
1. esmis_security       ← All other modules depend on its mixins and groups.
                          Build abstract mixins first, then concrete models.
                          (If Decision 1 = Option C: also build esmis_audit here)

2. esmis_academic_term  ← Small, clean. Depends only on esmis_security for
                          campus.aware mixin. Can start as soon as the
                          campus.aware mixin exists.

3. esmis_student        ← Depends on esmis_vocabulary (identifier types) and
                          esmis_security (pii.aware, consent.mixin, campus.aware).
                          Cannot start until mixins are stable.
```

**Rationale:** Security must come before everything because `esmis.student` inherits
`esmis.campus.aware`, `esmis.pii.aware`, and `esmis.consent.mixin` from `esmis_security`.
Academic term inherits `esmis.campus.aware`. Both depend on the security mixins being
stable.

---

## 4. Module Spec: esmis_security

### 4.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_security` |
| Description | Security groups, ACLs, DPO role, consent management, breach notification, data retention, approval workflows, and cross-cutting security mixins |
| Dependencies | `base`, `mail`, `esmis_vocabulary` |
| Version | `19.0.1.0.0` |
| `application` | `False` |
| `auto_install` | `False` |
| Category | `eSMIS/Core` |

### 4.2 Module Structure

```
esmis_security/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── mixins/
│   │   ├── __init__.py
│   │   ├── approval_mixin.py
│   │   ├── consent_mixin.py
│   │   ├── pii_aware.py
│   │   ├── campus_aware.py
│   │   ├── audit_mixin.py
│   │   └── retention_aware.py
│   ├── consent.py
│   ├── consent_scope.py
│   ├── audit_rule.py
│   ├── audit_log.py
│   ├── pii_access_log.py
│   ├── approval_definition.py
│   ├── data_breach.py
│   ├── data_subject_request.py
│   ├── disposal_review.py
│   └── retention_schedule.py
├── security/
│   ├── categories.xml
│   ├── privileges.xml
│   ├── groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── views/
│   ├── consent_views.xml
│   ├── audit_views.xml
│   ├── breach_views.xml
│   ├── dsar_views.xml
│   ├── retention_views.xml
│   └── menus.xml
├── data/
│   ├── consent_purposes.xml
│   └── retention_defaults.xml
├── demo/
│   ├── demo_users.xml
│   ├── demo_consent.xml
│   └── demo_retention.xml
├── tests/
│   ├── __init__.py
│   ├── test_approval_mixin.py
│   ├── test_consent.py
│   ├── test_consent_mixin.py
│   ├── test_campus_aware.py
│   ├── test_pii_access_log.py
│   ├── test_data_breach.py
│   ├── test_dsar.py
│   ├── test_disposal_review.py
│   ├── test_retention_schedule.py
│   └── test_security_groups.py
└── readme/
    └── DESCRIPTION.md
```

> **Note:** If Decision 1 = Option C (split), the audit/retention/disposal/breach/DSAR
> models move to `esmis_audit`. The plan below documents all 16 models together; adjust
> module boundaries based on Edwin's decision.

### 4.3 Abstract Mixins

#### 4.3.1 `esmis.approval.mixin`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.approval.mixin` |
| `_description` | Standardized approval workflow states and methods |
| Type | `models.AbstractModel` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `approval_state` | Selection | `[('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('revision', 'Revision Requested')]`, default=`'draft'`, tracking=True | Approval workflow state |
| `submitted_by_id` | Many2one | `res.users`, readonly=True | User who submitted |
| `submitted_date` | Datetime | readonly=True | Submission timestamp |
| `approved_by_id` | Many2one | `res.users`, readonly=True | Approver |
| `approved_date` | Datetime | readonly=True | Approval timestamp |
| `rejected_by_id` | Many2one | `res.users`, readonly=True | User who rejected |
| `rejected_date` | Datetime | readonly=True | Rejection timestamp |
| `rejection_reason` | Text | readonly=True | Reason for rejection |

**Methods:**

| Method | Description |
|--------|-------------|
| `action_submit_for_approval()` | Sets state to `pending`; records submitter and timestamp; calls `_on_submit()` hook |
| `action_approve()` | Sets state to `approved`; records approver and timestamp; calls `_on_approve()` hook |
| `action_reject()` | Opens rejection wizard; sets state to `rejected`; records reason |
| `action_reset_to_draft()` | Resets to `draft`; clears approval fields |
| `action_request_revision()` | Sets state to `revision`; notifies submitter |
| `_on_submit()` | Hook for custom validation before submission (override in concrete models) |
| `_on_approve()` | Hook for custom logic after approval (override in concrete models) |

**State transitions:**

```
draft ──submit──▶ pending ──approve──▶ approved
                     │
                     ├──reject──▶ rejected ──reset──▶ draft
                     │
                     └──revision──▶ revision ──resubmit──▶ pending
```

**Permission checks:** `action_approve()` and `action_reject()` must verify that the
current user is not the same as `submitted_by_id` (four-eyes principle). The concrete
model specifies which group(s) can approve.

---

#### 4.3.2 `esmis.consent.mixin`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.consent.mixin` |
| `_description` | Consent checking for models that process PII |
| Type | `models.AbstractModel` |

**Fields:** None (methods only).

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `_has_active_consent` | `(self, purpose: str) -> bool` | Returns `True` if the linked partner has an active `esmis.consent` record for the given purpose. Returns `False` if no record exists, if `date_withdrawn` is set, or if the student is a minor and only parent consent exists after the student has turned 18. |
| `_check_consent_for_export` | `(self) -> None` | Raises `UserError` if any record in `self` lacks active consent for export-related purposes. Called before bulk export operations. |
| `_get_consent_partner` | `(self) -> res.partner` | Returns the `res.partner` record to check consent against. Default: `self.partner_id`. Override in models where the partner link has a different field name. |

**Implementation notes:**
- Consent checks happen at the boundary of every operation that processes PII.
- Never bypass with `sudo()` — consent is a legal obligation.
- Never cache consent status across request boundaries.

---

#### 4.3.3 `esmis.pii.aware`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.pii.aware` |
| `_description` | Field-level PII classification and masking |
| Type | `models.AbstractModel` |

**Fields:** None stored. Provides classification metadata via a class-level attribute.

**Class attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `_pii_fields` | `dict[str, dict]` | Maps field names to their PII classification. Each entry: `{'tier': int, 'masking_pattern': str or None, 'groups': str or None}` |

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `_get_pii_classification` | `(self, field_name: str) -> dict` | Returns the classification dict for a field, or `None` if not classified |
| `_log_pii_access` | `(self, field_name: str, access_type: str) -> None` | Creates an `esmis.pii.access.log` entry for the given field read/write/reveal |
| `_mask_value` | `(self, field_name: str, value: str) -> str` | Returns the masked representation of a value per the field's masking pattern |

**Example usage in a concrete model:**

```python
class EsmisStudent(models.Model):
    _name = "esmis.student"
    _inherit = ["esmis.pii.aware"]

    _pii_fields = {
        "religion": {"tier": 1, "masking_pattern": None, "groups": None},
        "gwa": {"tier": 2, "masking_pattern": None, "groups": "esmis_security.group_esmis_registrar_officer"},
        "academic_standing": {"tier": 2, "masking_pattern": None, "groups": "esmis_security.group_esmis_registrar_officer"},
    }
```

---

#### 4.3.4 `esmis.campus.aware`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.campus.aware` |
| `_description` | Campus isolation via company_id |
| Type | `models.AbstractModel` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `company_id` | Many2one | `res.company`, string="Campus", required=True, default=`lambda self: self.env.company`, index=True | Campus this record belongs to |

**Record rule pattern:** Every model inheriting this mixin gets a standard campus
isolation record rule. The rule is defined in the consuming module's
`security/record_rules.xml`, not in `esmis_security`. The mixin provides the field;
the module provides the rule.

**Standard record rule template:**

```xml
<record id="rule_{model}_campus" model="ir.rule">
    <field name="name">{Model}: Campus Isolation</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="groups" eval="[Command.link(ref('base.group_user'))]"/>
</record>
```

---

#### 4.3.5 `esmis.audit.mixin`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.audit.mixin` |
| `_description` | Soft delete, legal hold, retention enforcement |
| Type | `models.AbstractModel` |
| `_inherit` | `mail.thread` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `legal_hold` | Boolean | default=False | Prevents automated disposal when True |
| `legal_hold_reason` | Text | | Reason for legal hold |
| `legal_hold_set_by` | Many2one | `res.users`, readonly=True | User who set the hold |
| `archived_date` | Datetime | readonly=True | When the record was archived |
| `archived_by_id` | Many2one | `res.users`, readonly=True | User who archived |
| `archive_reason` | Text | | Reason for archival |

**Methods:**

| Method | Description |
|--------|-------------|
| `action_archive()` | Override of Odoo's archive: sets `active=False`, `archived_date`, `archived_by_id`; respects `legal_hold` |
| `action_set_legal_hold(reason)` | Sets `legal_hold=True`, records reason and user; requires DPO group |
| `action_remove_legal_hold(resolution)` | Sets `legal_hold=False`, documents resolution; requires DPO group |
| `unlink()` | Override: raises `UserError` if `legal_hold=True` or if the model is subject to retention schedule |

---

#### 4.3.6 `esmis.retention.aware`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.retention.aware` |
| `_description` | Marks models subject to retention schedule |
| Type | `models.AbstractModel` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `legal_hold` | Boolean | default=False | Prevents automated disposal |
| `legal_hold_reason` | Text | | Reason |
| `legal_hold_set_by` | Many2one | `res.users`, readonly=True | Who set hold |

**Note:** This mixin overlaps with `esmis.audit.mixin` in the legal hold fields. The
difference: `esmis.audit.mixin` also adds archival tracking and extends `mail.thread`.
`esmis.retention.aware` is a lighter version for models that need legal hold but not
full audit tracking. A model should inherit one or the other, not both.

---

### 4.4 Concrete Models

#### 4.4.1 `esmis.consent`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.consent` |
| `_description` | Per-student, per-purpose consent record |
| `_inherit` | `mail.thread` |
| `_order` | `create_date desc` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `partner_id` | Many2one | `res.partner`, required=True, index=True | The person whose data is being processed (Decision 4: use partner, not student) |
| `purpose` | Selection | See processing purposes table below; required=True | Processing purpose code |
| `lawful_basis` | Selection | `[('consent', 'Consent'), ('contract', 'Contract'), ('legal_obligation', 'Legal Obligation'), ('vital_interest', 'Vital Interest'), ('legitimate_interest', 'Legitimate Interest')]`, required=True | Legal basis for processing |
| `date_given` | Datetime | required=True, default=`fields.Datetime.now` | When consent/acknowledgment was recorded |
| `date_withdrawn` | Datetime | | Set when consent is withdrawn; False if active |
| `evidence_type` | Selection | `[('electronic', 'Electronic'), ('written', 'Written'), ('verbal', 'Verbal')]` | How evidence was captured |
| `evidence_ref` | Many2one | `ir.attachment` | Supporting document |
| `captured_by` | Many2one | `res.users`, default=`lambda self: self.env.user` | Staff who recorded consent |
| `ip_address` | Char | | IP at time of electronic consent |
| `form_version` | Char | | Version of consent form shown |
| `is_active` | Boolean | computed, store=True | `True` when `date_withdrawn` is not set |
| `parent_consent` | Boolean | default=False | True when this is parent/guardian consent for a minor |

**Processing purpose values:**

| Code | Description | Default Lawful Basis |
|------|-------------|---------------------|
| `consent_enrollment` | Enrollment data processing | `contract` |
| `consent_ched_reporting` | CHED HEMIS/eCAV submission | `legal_obligation` |
| `consent_financial_aid` | Scholarship/subsidy eligibility | `consent` |
| `consent_emergency_contact` | Emergency data sharing | `vital_interest` |
| `consent_alumni_tracking` | Post-graduation contact | `consent` |
| `consent_research` | Anonymized institutional research | `legitimate_interest` |
| `consent_lms_sync` | LMS roster and grade sync | `contract` |
| `consent_payment` | Payment processor data sharing | `contract` |
| `consent_philsys` | PhilSys identity verification | `consent` |

**Constraints:**
- SQL: `UNIQUE(partner_id, purpose)` among active records (where `date_withdrawn IS NULL`)
- Python: `evidence_type` required when `lawful_basis = 'consent'`
- Python: `parent_consent` may only be `True` when the partner is under 18 at `date_given`

**Key methods:**

| Method | Description |
|--------|-------------|
| `action_withdraw()` | Sets `date_withdrawn` to now; `is_active` becomes False; record is never deleted |
| `_check_is_active()` | Computes `is_active` from `date_withdrawn` |

---

#### 4.4.2 `esmis.consent.scope`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.consent.scope` |
| `_description` | Fine-grained consent scope |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `consent_id` | Many2one | `esmis.consent`, required=True, ondelete='cascade' | Parent consent |
| `resource_type` | Char | required=True | Type of resource (model name or data category) |
| `purpose` | Char | | Specific sub-purpose within the consent |
| `third_party_id` | Many2one | `res.partner` | Third party receiving data |
| `valid_until` | Date | | Expiry date for this scope |

---

#### 4.4.3 `esmis.audit.rule`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.audit.rule` |
| `_description` | Configurable audit rule per model |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Rule name |
| `model_id` | Many2one | `ir.model`, required=True | Model to audit |
| `log_create` | Boolean | default=True | Log create events |
| `log_write` | Boolean | default=True | Log write events |
| `log_unlink` | Boolean | default=True | Log delete events |
| `field_to_log_ids` | Many2many | `ir.model.fields` | Specific fields to track (empty = all) |
| `active` | Boolean | default=True | Active flag |

---

#### 4.4.4 `esmis.audit.log`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.audit.log` |
| `_description` | Immutable audit trail |
| `_order` | `create_date desc` |
| `_log_access` | `False` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `audit_rule_id` | Many2one | `esmis.audit.rule`, required=True, index=True | Link to rule |
| `user_id` | Many2one | `res.users`, required=True, index=True | Who made the change |
| `create_date` | Datetime | required=True, default=now | When |
| `model_id` | Many2one | `ir.model`, required=True | Which model |
| `res_id` | Integer | required=True, index=True | Which record |
| `method` | Selection | `[('create', 'Create'), ('write', 'Write'), ('unlink', 'Delete')]`, required=True | Operation type |
| `data` | Text | | JSON of old/new values (no PII values, only field names and hashes) |

**Immutability enforcement:**
- `unlink()` raises `UserError("Audit log entries cannot be deleted.")`
- `write()` raises `UserError` for all fields except non-existent admin-only fields

---

#### 4.4.5 `esmis.pii.access.log`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.pii.access.log` |
| `_description` | PII field access logging (append-only) |
| `_order` | `create_date desc` |
| `_log_access` | `False` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `user_id` | Many2one | `res.users`, required=True, index=True | Accessor |
| `create_date` | Datetime | required=True, default=now | Timestamp |
| `model` | Char | required=True, index=True | Model accessed (e.g., `esmis.student`) |
| `res_id` | Integer | required=True, index=True | Record ID |
| `field_name` | Char | required=True | Field accessed |
| `access_type` | Selection | `[('read', 'Read'), ('reveal', 'Reveal'), ('write', 'Write'), ('export', 'Export'), ('search', 'Search'), ('btg', 'Break-the-Glass')]`, required=True | Type of access |
| `ip_address` | Char | | IP address of accessor |
| `session_id` | Char | | Session identifier |

**Immutability enforcement:**
- `unlink()` always raises `UserError`
- `write()` blocks mutation of all fields listed in an immutable set: `{user_id, create_date, model, res_id, field_name, access_type}`

---

#### 4.4.6 `esmis.approval.definition`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.approval.definition` |
| `_description` | Multi-stage approval chain definition |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Definition name |
| `model_id` | Many2one | `ir.model`, required=True | Model this applies to |
| `stage_ids` | One2many | (future: approval stage model), inverse=`definition_id` | Ordered approval stages |
| `active` | Boolean | default=True | Active flag |

**Note:** Multi-stage approval definitions are defined in Phase 1 but the stage model can
be kept minimal. Full multi-stage routing is used in Phase 2 (enrollment approvals, grade
changes).

---

#### 4.4.7 `esmis.data.breach`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.data.breach` |
| `_description` | Data breach notification workflow |
| `_inherit` | `mail.thread`, `mail.activity.mixin` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | Breach identifier/title |
| `discovery_date` | Datetime | required=True | When the breach was discovered |
| `npc_deadline` | Datetime | computed, store=True | `discovery_date + 72 hours` |
| `affected_count` | Integer | | Number of affected data subjects |
| `severity` | Selection | `[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]`, required=True | Severity assessment |
| `data_types_affected` | Text | | Categories of data involved |
| `description` | Text | | Description of the breach |
| `containment_actions` | Text | | Actions taken to contain |
| `npc_notified` | Boolean | default=False | Whether NPC has been notified |
| `npc_notification_date` | Datetime | | When NPC was notified |
| `subjects_notified` | Boolean | default=False | Whether affected subjects have been notified |
| `dpo_id` | Many2one | `res.users` | Data Protection Officer handling this |
| `state` | Selection | `[('detected', 'Detected'), ('investigating', 'Investigating'), ('contained', 'Contained'), ('notified', 'Notified'), ('resolved', 'Resolved')]`, default='detected', tracking=True | Workflow state |

**Computed field logic:**
- `npc_deadline`: `discovery_date + timedelta(hours=72)`

**Constraint:** NPC notification must occur before `npc_deadline`.

---

#### 4.4.8 `esmis.data.subject.request`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.data.subject.request` |
| `_description` | Data Subject Access Request (DSAR) |
| `_inherit` | `mail.thread`, `mail.activity.mixin` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `partner_id` | Many2one | `res.partner`, required=True | Requesting data subject (using partner, not student; see Decision 4) |
| `request_type` | Selection | `[('access', 'Right of Access'), ('rectification', 'Rectification'), ('erasure', 'Erasure'), ('portability', 'Data Portability'), ('objection', 'Objection'), ('restriction', 'Restriction of Processing')]`, required=True | Type of DSAR |
| `receipt_date` | Date | required=True, default=`fields.Date.today` | Date the request was received |
| `deadline` | Date | computed, store=True | `receipt_date + 30 working days` |
| `description` | Text | | Details of the request |
| `state` | Selection | `[('received', 'Received'), ('verified', 'Verified'), ('processing', 'Processing'), ('completed', 'Completed'), ('denied', 'Denied')]`, default='received', tracking=True | Processing state |
| `dpo_id` | Many2one | `res.users` | DPO handling this request |
| `resolution_notes` | Text | | Notes on resolution |
| `response_date` | Date | | Date the response was provided |

**Computed field logic:**
- `deadline`: `receipt_date + 30 working days` (excluding weekends and Philippine holidays)

---

#### 4.4.9 `esmis.disposal.review`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.disposal.review` |
| `_description` | Data disposal approval workflow |
| `_inherit` | `esmis.approval.mixin` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `data_type` | Char | required=True | Category of data (e.g., "Enrollment Forms", "Counseling Records") |
| `record_count` | Integer | | Number of records identified for disposal |
| `proposed_action` | Selection | `[('anonymize', 'Anonymize'), ('delete', 'Delete'), ('archive', 'Archive')]`, required=True | What to do |
| `retention_schedule_id` | Many2one | `esmis.retention.schedule` | Link to the governing schedule |
| `dpo_approved_by` | Many2one | `res.users` | DPO who approved |
| `execution_date` | Datetime | | When disposal was executed |
| `nap_approval_ref` | Char | | National Archives approval reference (public HEIs) |
| `state` | Selection | `[('draft', 'Draft'), ('dpo_review', 'DPO Review'), ('approved', 'Approved'), ('executed', 'Executed')]`, default='draft', tracking=True | Workflow state |

---

#### 4.4.10 `esmis.retention.schedule`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.retention.schedule` |
| `_description` | Retention periods per data category |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `data_type` | Char | required=True | Data category label |
| `model_id` | Many2one | `ir.model` | Model this schedule applies to (optional; can be generic) |
| `retention_period_years` | Integer | | Number of years to retain |
| `action_at_expiry` | Selection | `[('anonymize', 'Anonymize'), ('delete', 'Delete'), ('archive', 'Archive')]`, required=True | Action when retention expires |
| `legal_basis` | Char | | Legal basis (e.g., "CHED MORPHE", "RA 10173", "BIR") |
| `is_permanent` | Boolean | default=False | If True, never disposed |
| `active` | Boolean | default=True | Active flag |

**Seed data (from data-retention-and-disposal.md):**

| Data Type | Period | Action | Basis |
|-----------|--------|--------|-------|
| TOR / academic transcript | Permanent | Archive | CHED MORPHE |
| Diploma records | Permanent | Archive | CHED MORPHE |
| Enrollment forms | 5 years after graduation | Anonymize | CHED Resolution 170-2018 |
| Transfer credentials | 10 years | Archive | CHED MORPHE |
| Financial records | 10 years | Anonymize | BIR, COA |
| Scholarship / financial aid | 10 years | Anonymize | UniFAST, COA |
| Counseling records | 5 years after last session | Delete | RA 10173 |
| Health / medical records | 5 years after graduation | Delete | RA 10173 |
| Consent records | Duration + 3 years | Archive | RA 10173 |
| Audit logs | 7 years | Archive | NPC guidelines |
| Session / login logs | 1 year | Delete | Institutional policy |
| Application data (denied) | 2 years from decision | Delete | RA 10173 |

---

### 4.5 Security Groups

#### 4.5.1 Module Categories (Cross-Cutting Only, per Decision 5)

| XML ID | Name | Description |
|--------|------|-------------|
| `category_esmis_admin` | eSMIS / Administration | System administration |
| `category_esmis_security` | eSMIS / Security | Security and access control |
| `category_esmis_data_protection` | eSMIS / Data Protection | DPO and privacy compliance |
| `category_esmis_audit` | eSMIS / Audit | Audit logging and compliance |

#### 4.5.2 Privileges

| XML ID | Name | Category |
|--------|------|----------|
| `privilege_esmis_security_officer` | Security Officer | `category_esmis_security` |
| `privilege_esmis_data_protection_officer` | Data Protection Officer | `category_esmis_data_protection` |
| `privilege_esmis_audit_officer` | Audit Officer | `category_esmis_audit` |

#### 4.5.3 Groups

| XML ID | Name | `privilege_id` | `implied_ids` | Purpose |
|--------|------|----------------|---------------|---------|
| `group_esmis_system_admin` | eSMIS System Admin | — | `base.group_system` | Full system access, cross-campus |
| `group_esmis_security_viewer` | Security: Viewer | `privilege_esmis_security_officer` | — | Read-only access to security config |
| `group_esmis_security_officer` | Security: Officer | `privilege_esmis_security_officer` | `group_esmis_security_viewer` | Manage consent, audit rules |
| `group_esmis_security_manager` | Security: Manager | `privilege_esmis_security_officer` | `group_esmis_security_officer` | Full security administration |
| `group_esmis_dpo` | Data Protection Officer | `privilege_esmis_data_protection_officer` | `group_esmis_security_viewer` | DPO role: breach, DSAR, disposal, legal hold |
| `group_esmis_audit_viewer` | Audit: Viewer | `privilege_esmis_audit_officer` | — | Read audit logs |
| `group_esmis_audit_officer` | Audit: Officer | `privilege_esmis_audit_officer` | `group_esmis_audit_viewer` | Manage audit rules |

**System-wide roles (from multi-campus doc):**

| XML ID | Name | Purpose |
|--------|------|---------|
| `group_esmis_vp_academic` | VP Academic Affairs | Cross-campus oversight |
| `group_esmis_president` | President | Cross-campus oversight |
| `group_esmis_ched_reporter` | CHED Reporter | Read-only cross-campus for HEMIS exports |

---

### 4.6 ACL Matrix (`ir.model.access.csv`)

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# --- System admin (full access to all models) ---
access_esmis_consent_system,esmis.consent / System,model_esmis_consent,base.group_system,1,1,1,1
access_esmis_consent_scope_system,esmis.consent.scope / System,model_esmis_consent_scope,base.group_system,1,1,1,1
access_esmis_audit_rule_system,esmis.audit.rule / System,model_esmis_audit_rule,base.group_system,1,1,1,1
access_esmis_audit_log_system,esmis.audit.log / System,model_esmis_audit_log,base.group_system,1,1,1,1
access_esmis_pii_access_log_system,esmis.pii.access.log / System,model_esmis_pii_access_log,base.group_system,1,1,1,1
access_esmis_approval_definition_system,esmis.approval.definition / System,model_esmis_approval_definition,base.group_system,1,1,1,1
access_esmis_data_breach_system,esmis.data.breach / System,model_esmis_data_breach,base.group_system,1,1,1,1
access_esmis_data_subject_request_system,esmis.data.subject.request / System,model_esmis_data_subject_request,base.group_system,1,1,1,1
access_esmis_disposal_review_system,esmis.disposal.review / System,model_esmis_disposal_review,base.group_system,1,1,1,1
access_esmis_retention_schedule_system,esmis.retention.schedule / System,model_esmis_retention_schedule,base.group_system,1,1,1,1
# --- Security Officer ---
access_esmis_consent_security_officer,esmis.consent / Security Officer,model_esmis_consent,group_esmis_security_officer,1,1,1,0
access_esmis_consent_scope_security_officer,esmis.consent.scope / Security Officer,model_esmis_consent_scope,group_esmis_security_officer,1,1,1,0
access_esmis_audit_rule_security_officer,esmis.audit.rule / Security Officer,model_esmis_audit_rule,group_esmis_security_officer,1,1,1,0
access_esmis_approval_definition_security_officer,esmis.approval.definition / Security Officer,model_esmis_approval_definition,group_esmis_security_officer,1,1,1,0
access_esmis_retention_schedule_security_officer,esmis.retention.schedule / Security Officer,model_esmis_retention_schedule,group_esmis_security_officer,1,1,1,0
# --- Security Viewer ---
access_esmis_consent_security_viewer,esmis.consent / Security Viewer,model_esmis_consent,group_esmis_security_viewer,1,0,0,0
access_esmis_consent_scope_security_viewer,esmis.consent.scope / Security Viewer,model_esmis_consent_scope,group_esmis_security_viewer,1,0,0,0
access_esmis_audit_rule_security_viewer,esmis.audit.rule / Security Viewer,model_esmis_audit_rule,group_esmis_security_viewer,1,0,0,0
access_esmis_retention_schedule_security_viewer,esmis.retention.schedule / Security Viewer,model_esmis_retention_schedule,group_esmis_security_viewer,1,0,0,0
# --- DPO ---
access_esmis_data_breach_dpo,esmis.data.breach / DPO,model_esmis_data_breach,group_esmis_dpo,1,1,1,0
access_esmis_data_subject_request_dpo,esmis.data.subject.request / DPO,model_esmis_data_subject_request,group_esmis_dpo,1,1,1,0
access_esmis_disposal_review_dpo,esmis.disposal.review / DPO,model_esmis_disposal_review,group_esmis_dpo,1,1,1,0
access_esmis_consent_dpo,esmis.consent / DPO,model_esmis_consent,group_esmis_dpo,1,1,0,0
access_esmis_retention_schedule_dpo,esmis.retention.schedule / DPO,model_esmis_retention_schedule,group_esmis_dpo,1,1,1,0
# --- Audit Viewer ---
access_esmis_audit_log_audit_viewer,esmis.audit.log / Audit Viewer,model_esmis_audit_log,group_esmis_audit_viewer,1,0,0,0
access_esmis_pii_access_log_audit_viewer,esmis.pii.access.log / Audit Viewer,model_esmis_pii_access_log,group_esmis_audit_viewer,1,0,0,0
# --- Internal user (read consent for consent checks) ---
access_esmis_consent_user,esmis.consent / Internal User,model_esmis_consent,base.group_user,1,0,0,0
```

---

### 4.7 Record Rules

| XML ID | Model | Domain | Groups | Purpose |
|--------|-------|--------|--------|---------|
| `rule_consent_campus` | `esmis.consent` | (no company_id — consent is partner-level, not campus-scoped) | — | Not campus-scoped |
| `rule_data_breach_dpo` | `esmis.data.breach` | `[(1, '=', 1)]` | `group_esmis_dpo` | DPO sees all breaches |
| `rule_data_breach_security_manager` | `esmis.data.breach` | `[(1, '=', 1)]` | `group_esmis_security_manager` | Security manager sees all |
| `rule_dsar_dpo` | `esmis.data.subject.request` | `[(1, '=', 1)]` | `group_esmis_dpo` | DPO sees all DSARs |
| `rule_disposal_dpo` | `esmis.disposal.review` | `[(1, '=', 1)]` | `group_esmis_dpo` | DPO sees all disposal reviews |

---

### 4.8 Acceptance Criteria

From the implementation roadmap, plus additional criteria from principle docs:

- [ ] All security groups created with correct `implied_ids` hierarchy
- [ ] `esmis.consent` enforces unique active consent per `partner_id + purpose`
- [ ] `esmis.pii.access.log` blocks `write()` and `unlink()` on immutable fields
- [ ] `esmis.data.breach` computes `npc_deadline` as `discovery_date + 72 hours`
- [ ] `esmis.data.subject.request` computes deadline as `receipt_date + 30 working days`
- [ ] `esmis.campus.aware` mixin adds `company_id` with default and record rule pattern
- [ ] `esmis.approval.mixin` state machine transitions enforce permission checks
- [ ] `esmis.approval.mixin` enforces four-eyes principle (approver != submitter)
- [ ] All 10 concrete models have complete `ir.model.access.csv` entries
- [ ] Tests cover consent creation, withdrawal, and per-purpose uniqueness
- [ ] Tests cover breach workflow state transitions and deadline computation
- [ ] Tests cover DSAR lifecycle and deadline computation
- [ ] Tests cover disposal review with DPO approval
- [ ] Tests cover audit log immutability (write and unlink blocked)
- [ ] Tests cover PII access log immutability
- [ ] Tests cover campus.aware mixin isolation
- [ ] No PII in log messages or exception text
- [ ] Demo data creates realistic security groups, consent records, and retention schedules

---

## 5. Module Spec: esmis_academic_term

### 5.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_academic_term` |
| Description | Academic year and term/semester definitions with enrollment windows |
| Dependencies | `base`, `esmis_security` |
| Version | `19.0.1.0.0` |
| `application` | `False` |
| `auto_install` | `False` |
| Category | `eSMIS/Core` |

### 5.2 Module Structure

```
esmis_academic_term/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── academic_year.py
│   └── academic_term.py
├── security/
│   ├── categories.xml
│   ├── privileges.xml
│   ├── groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── views/
│   ├── academic_year_views.xml
│   ├── academic_term_views.xml
│   └── menus.xml
├── demo/
│   └── demo_academic_terms.xml
├── tests/
│   ├── __init__.py
│   ├── test_academic_year.py
│   ├── test_academic_term.py
│   └── test_term_state_machine.py
└── readme/
    └── DESCRIPTION.md
```

### 5.3 Models

#### 5.3.1 `esmis.academic.year`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.academic.year` |
| `_description` | Institution-wide academic year |
| `_inherit` | `mail.thread` |
| `_order` | `date_start desc` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | e.g., "AY 2025-2026" |
| `date_start` | Date | required=True | Year start date |
| `date_end` | Date | required=True | Year end date |
| `term_ids` | One2many | `esmis.academic.term`, inverse=`academic_year_id` | Terms within this year |
| `active` | Boolean | default=True | Active flag |

**Shared:** No `company_id`. Academic years are institution-wide.

**Constraints:**
- Python: `date_end > date_start`
- SQL: `UNIQUE(name)`

---

#### 5.3.2 `esmis.academic.term`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.academic.term` |
| `_description` | Campus-scoped academic term |
| `_inherit` | `esmis.campus.aware`, `mail.thread` |
| `_order` | `date_start desc` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `name` | Char | required=True | e.g., "1st Semester 2025-2026" |
| `academic_year_id` | Many2one | `esmis.academic.year`, required=True, index=True | Parent year |
| `company_id` | Many2one | (inherited from `esmis.campus.aware`) | Campus |
| `date_start` | Date | required=True | Term start |
| `date_end` | Date | required=True | Term end |
| `enrollment_open_date` | Datetime | | When enrollment opens |
| `enrollment_close_date` | Datetime | | When enrollment closes |
| `add_drop_deadline` | Date | | Last day for add/drop |
| `state` | Selection | `[('draft', 'Draft'), ('enrollment_open', 'Enrollment Open'), ('in_progress', 'In Progress'), ('grading', 'Grading'), ('closed', 'Closed')]`, default='draft', tracking=True | Term state |

**State machine:**

```
draft ──▶ enrollment_open ──▶ in_progress ──▶ grading ──▶ closed
```

Transitions are strictly sequential. No backward transitions allowed.

**Constraints:**
- `date_end > date_start`
- `date_start >= academic_year_id.date_start`
- `date_end <= academic_year_id.date_end`
- `enrollment_open_date < enrollment_close_date` (when both are set)
- `enrollment_close_date <= add_drop_deadline` (when both are set)
- `add_drop_deadline <= date_end`

---

### 5.4 Security Groups

| XML ID | Name | Category | `implied_ids` |
|--------|------|----------|---------------|
| `category_esmis_academic_term` | eSMIS / Academic Calendar | — | — |
| `privilege_academic_term_officer` | Academic Calendar Officer | `category_esmis_academic_term` | — |
| `group_academic_term_viewer` | Academic Calendar: Viewer | `privilege_academic_term_officer` | — |
| `group_academic_term_officer` | Academic Calendar: Officer | `privilege_academic_term_officer` | `group_academic_term_viewer` |
| `group_academic_term_manager` | Academic Calendar: Manager | `privilege_academic_term_officer` | `group_academic_term_officer` |

### 5.5 ACL Matrix

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# --- System admin ---
access_esmis_academic_year_system,esmis.academic.year / System,model_esmis_academic_year,base.group_system,1,1,1,1
access_esmis_academic_term_system,esmis.academic.term / System,model_esmis_academic_term,base.group_system,1,1,1,1
# --- Internal user (reference data, read-only) ---
access_esmis_academic_year_user,esmis.academic.year / User,model_esmis_academic_year,base.group_user,1,0,0,0
access_esmis_academic_term_user,esmis.academic.term / User,model_esmis_academic_term,base.group_user,1,0,0,0
# --- Officer ---
access_esmis_academic_year_officer,esmis.academic.year / Officer,model_esmis_academic_year,group_academic_term_officer,1,1,1,0
access_esmis_academic_term_officer,esmis.academic.term / Officer,model_esmis_academic_term,group_academic_term_officer,1,1,1,0
# --- Manager ---
access_esmis_academic_year_manager,esmis.academic.year / Manager,model_esmis_academic_year,group_academic_term_manager,1,1,1,1
access_esmis_academic_term_manager,esmis.academic.term / Manager,model_esmis_academic_term,group_academic_term_manager,1,1,1,1
```

### 5.6 Record Rules

| XML ID | Model | Domain | Groups | Purpose |
|--------|-------|--------|--------|---------|
| `rule_academic_term_campus` | `esmis.academic.term` | `[('company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation |
| `rule_academic_term_manager_all` | `esmis.academic.term` | `[(1, '=', 1)]` | `group_academic_term_manager` | Manager sees all campuses |

**Note:** `esmis.academic.year` has no company_id and no record rules (shared).

### 5.7 Demo Data

- 1 academic year: "AY 2025-2026" (June 2025 – May 2026)
- 3 terms per campus (Main campus):
  - "1st Semester 2025-2026" (Jun – Oct)
  - "2nd Semester 2025-2026" (Nov – Mar)
  - "Summer 2026" (Apr – May)

### 5.8 Acceptance Criteria

- [ ] Academic year validates `date_end > date_start`
- [ ] Term validates dates fall within parent academic year
- [ ] Term state transitions enforce correct order (no backward transitions)
- [ ] Enrollment dates validated (open < close <= add_drop_deadline <= date_end)
- [ ] Campus-scoped terms: different campuses can have independent term dates
- [ ] Complete `ir.model.access.csv` for all groups
- [ ] Record rules enforce campus isolation for terms
- [ ] Demo data creates at least one academic year with two semesters and a summer term
- [ ] Tests cover all validation constraints
- [ ] Tests cover state machine (valid transitions succeed, invalid transitions raise)
- [ ] Tests cover campus isolation (user at Campus A cannot see Campus B terms)

---

## 6. Module Spec: esmis_student

### 6.1 Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `esmis_student` |
| Description | Core student profile linked to res.partner, with lifecycle states and identifiers |
| Dependencies | `base`, `mail`, `esmis_vocabulary`, `esmis_security` |
| Version | `19.0.1.0.0` |
| `application` | `True` |
| `auto_install` | `False` |
| Category | `eSMIS/Core` |

**Note:** `esmis_academic_term` is NOT a dependency (Decision 3: course history deferred).

### 6.2 Module Structure

```
esmis_student/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── student.py
│   ├── student_program.py
│   ├── identifier.py
│   └── res_partner.py          # Extends res.partner with student-related fields
├── security/
│   ├── categories.xml
│   ├── privileges.xml
│   ├── groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── views/
│   ├── student_views.xml
│   ├── identifier_views.xml
│   └── menus.xml
├── demo/
│   ├── demo_students.xml
│   └── demo_identifiers.xml
├── tests/
│   ├── __init__.py
│   ├── test_student.py
│   ├── test_student_state_machine.py
│   ├── test_identifier_encryption.py
│   ├── test_guardian_minor.py
│   ├── test_campus_isolation.py
│   └── test_consent_integration.py
└── readme/
    └── DESCRIPTION.md
```

### 6.3 Models

#### 6.3.1 `esmis.student`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.student` |
| `_description` | Core student record |
| `_inherit` | `esmis.campus.aware`, `esmis.pii.aware`, `esmis.consent.mixin`, `esmis.retention.aware`, `mail.thread`, `mail.activity.mixin` |
| `_order` | `student_number` |

**Fields:**

| Field | Type | Attributes | Description | PII Tier |
|-------|------|------------|-------------|----------|
| `partner_id` | Many2one | `res.partner`, required=True, ondelete='restrict', index=True | Linked Odoo contact | — |
| `student_number` | Char | required=True, copy=False, index=True | Institution-assigned student number | 0 (Public) |
| `company_id` | Many2one | (inherited from `esmis.campus.aware`) | Campus | 0 |
| `state` | Selection | See state machine below; default='applicant', tracking=True | Lifecycle state | 1 |
| `program_id` | Many2one | `esmis.program` (Phase 2 forward ref), index=True | Current program (Many2one to model defined in Phase 2; field exists but UI deferred) | 0 |
| `curriculum_id` | Many2one | `esmis.curriculum` (Phase 2 forward ref), index=True | Bound curriculum version | 0 |
| `year_level` | Integer | | Current year level (1-6) | 0 |
| `gwa` | Float | digits=(4,4), groups="esmis_security.group_esmis_security_officer" | Cumulative GWA | 2 (SPI) |
| `academic_standing` | Selection | `[('good_standing', 'Good Standing'), ('dean_list', "Dean's List"), ('probation', 'Probation'), ('warning', 'Warning'), ('dismissed', 'Dismissed')]` | Academic standing | 2 (SPI) |
| `guardian_id` | Many2one | `res.partner` | Parent/guardian for minors | 2 |
| `religion` | Char | | Religious affiliation | 1 |
| `ethnicity` | Char | | Ethnic/IP membership | 1 |
| `consent_given` | Boolean | default=False | Privacy consent flag | — |
| `consent_date` | Datetime | readonly=True | When consent was given | — |
| `consent_given_by` | Char | | Name of signatory | — |
| `is_consent_for_minor` | Boolean | | Parent/guardian consent indicator | — |
| `transfer_state` | Selection | `[('none', 'None'), ('transferred_in', 'Transferred In'), ('transferred_out', 'Transferred Out')]`, default='none' | Transfer tracking | 1 |
| `transfer_date` | Date | | Date of transfer | 1 |
| `diploma_released_date` | Date | | When diploma was released | 0 |
| `program_ids` | One2many | `esmis.student.program`, inverse=`student_id` | Program enrollments | — |
| `identifier_ids` | One2many | `esmis.identifier`, inverse=`partner_id`, related via partner | Identifiers (displayed via partner) | — |

**PII classification (`_pii_fields`):**

| Field | Tier | Masking | Groups |
|-------|------|---------|--------|
| `religion` | 1 | None | None (internal users) |
| `ethnicity` | 1 | None | None (internal users) |
| `gwa` | 2 | None | `group_esmis_registrar_officer` |
| `academic_standing` | 2 | None | `group_esmis_registrar_officer` |
| `guardian_id` | 2 | None | `group_esmis_registrar_officer` |

**Note:** `program_id` and `curriculum_id` reference models that will be defined in
Phase 2 (`esmis_curriculum`). In Phase 1, these fields exist on the model but are not
required and not exposed in views. They are populated when `esmis_enrollment` installs.

**State machine:**

```
applicant ──▶ admitted ──▶ enrolled ──▶ active ──▶ graduated ──▶ alumni
     │              │          │           │
     │              │          │           ├──▶ loa (leave of absence) ──▶ enrolled (re-enroll)
     │              │          │           │
     │              │          │           ├──▶ dismissed (terminal unless appeal)
     │              │          │           │
     │              │          │           └──▶ transferred_out (terminal)
     │              │          │
     │              │          └──▶ (back to active upon term start)
     │              │
     │              └──▶ denied (terminal)
     │
     └──▶ denied (terminal)
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

**Guardian/minor logic:**
- When `partner_id.birthdate` indicates age < 18 at current date:
  - `guardian_id` is required (raise `ValidationError` if missing)
  - `is_consent_for_minor` must be `True` on consent records
- When student turns 18:
  - System generates a `mail.activity` for the records office to collect direct consent
  - Parent consent remains valid until student provides their own

---

#### 6.3.2 `esmis.student.program`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.student.program` |
| `_description` | Student-program binding with GWA tracking |
| `_inherit` | `mail.thread` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `student_id` | Many2one | `esmis.student`, required=True, ondelete='cascade', index=True | Student |
| `program_id` | Many2one | `esmis.program` (Phase 2 forward ref), index=True | Program |
| `curriculum_id` | Many2one | `esmis.curriculum` (Phase 2 forward ref), index=True | Curriculum version |
| `cumulative_gwa` | Float | digits=(4,4), groups="esmis_security.group_esmis_security_officer" | Cumulative GWA for this program |
| `consecutive_below_threshold_count` | Integer | default=0 | Counter for probation tracking |
| `academic_standing` | Selection | Same as `esmis.student.academic_standing` | Standing for this program |

**Note:** `term_gwa` is listed in the data model registry as a computed field. In Phase 1,
this is a stub (returns 0.0). The actual computation depends on `esmis.grade` records
(Phase 2).

---

#### 6.3.3 `esmis.identifier`

| Attribute | Value |
|-----------|-------|
| `_name` | `esmis.identifier` |
| `_description` | Multi-type identifier store with encryption |
| `_inherit` | `esmis.pii.aware` |
| `_rec_name` | `display_name` |

**Fields:**

| Field | Type | Attributes | Description |
|-------|------|------------|-------------|
| `partner_id` | Many2one | `res.partner`, required=True, ondelete='cascade', index=True | Linked partner |
| `type_id` | Many2one | `esmis.vocabulary.code`, required=True, domain=`[('vocabulary_id.domain', '=', 'identity')]` | Identifier type (PhilSys, LRN, TIN, etc.) |
| `system_uri` | Char | related=`type_id.namespace_uri`, store=True, index=True | URI from type vocabulary |
| `value` | Char | groups="esmis_security.group_esmis_security_manager" | Plaintext identifier value (Tier 3; encrypted at rest) |
| `value_ciphertext` | Binary | attachment=False | Encrypted value (Fernet or AES-256-GCM per Decision 2) |
| `value_blind_index` | Char | index=True | HMAC-SHA256 blind index for exact-match search |

**Encryption behavior:**
- On write to `value`: encrypt with configured key, store in `value_ciphertext`, compute `value_blind_index`
- On read of `value`: decrypt from `value_ciphertext` (access-controlled by `groups=`)
- On search for `value`: compute blind index from search term, search `value_blind_index`
- Only exact-match search (`operator == '='`) supported on encrypted fields

**PII classification:** All identifier values are Tier 3 (Restricted/SPI).

**Masking patterns (from data-privacy-and-pii.md):**

| Identifier Type | Pattern | Permitted Roles |
|-----------------|---------|-----------------|
| PhilSys (PSN) | `****-****-####` | Registrar Manager |
| LRN | `********####` | Registrar |
| SSS / GSIS | `**-*******-#` | Finance Manager |
| TIN | `***-***-####` | Finance Manager |
| PWD ID | `****####` | Registrar, Financial Aid |
| Solo Parent ID | `****####` | Registrar, Financial Aid |
| Passport | `**####` | Registrar Manager |

---

### 6.4 Security Groups

| XML ID | Name | Category | `implied_ids` |
|--------|------|----------|---------------|
| `category_esmis_student` | eSMIS / Student Management | — | — |
| `privilege_esmis_registrar` | Registrar | `category_esmis_student` | — |
| `group_esmis_student_self` | Student (Self) | — | — |
| `group_esmis_faculty` | Faculty | — | — |
| `group_esmis_registrar_officer` | Registrar: Officer | `privilege_esmis_registrar` | — |
| `group_esmis_registrar_manager` | Registrar: Manager | `privilege_esmis_registrar` | `group_esmis_registrar_officer` |

### 6.5 ACL Matrix

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# --- System admin ---
access_esmis_student_system,esmis.student / System,model_esmis_student,base.group_system,1,1,1,1
access_esmis_student_program_system,esmis.student.program / System,model_esmis_student_program,base.group_system,1,1,1,1
access_esmis_identifier_system,esmis.identifier / System,model_esmis_identifier,base.group_system,1,1,1,1
# --- Registrar Officer ---
access_esmis_student_registrar_officer,esmis.student / Registrar Officer,model_esmis_student,group_esmis_registrar_officer,1,1,1,0
access_esmis_student_program_registrar_officer,esmis.student.program / Registrar Officer,model_esmis_student_program,group_esmis_registrar_officer,1,1,1,0
access_esmis_identifier_registrar_officer,esmis.identifier / Registrar Officer,model_esmis_identifier,group_esmis_registrar_officer,1,1,1,0
# --- Registrar Manager ---
access_esmis_student_registrar_manager,esmis.student / Registrar Manager,model_esmis_student,group_esmis_registrar_manager,1,1,1,1
access_esmis_student_program_registrar_manager,esmis.student.program / Registrar Manager,model_esmis_student_program,group_esmis_registrar_manager,1,1,1,1
access_esmis_identifier_registrar_manager,esmis.identifier / Registrar Manager,model_esmis_identifier,group_esmis_registrar_manager,1,1,1,1
# --- Faculty (read-only) ---
access_esmis_student_faculty,esmis.student / Faculty,model_esmis_student,group_esmis_faculty,1,0,0,0
access_esmis_student_program_faculty,esmis.student.program / Faculty,model_esmis_student_program,group_esmis_faculty,1,0,0,0
# --- Student Self (read own only, via record rule) ---
access_esmis_student_self,esmis.student / Student Self,model_esmis_student,group_esmis_student_self,1,0,0,0
access_esmis_student_program_self,esmis.student.program / Student Self,model_esmis_student_program,group_esmis_student_self,1,0,0,0
```

### 6.6 Record Rules

| XML ID | Model | Domain | Groups | Purpose |
|--------|-------|--------|--------|---------|
| `rule_student_campus` | `esmis.student` | `[('company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation |
| `rule_student_self` | `esmis.student` | `[('partner_id', '=', user.partner_id.id)]` | `group_esmis_student_self` | Student sees own record only |
| `rule_student_registrar_all` | `esmis.student` | `[(1, '=', 1)]` | `group_esmis_registrar_manager` | Registrar manager sees all |
| `rule_identifier_campus` | `esmis.identifier` | `[('partner_id.esmis_student_ids.company_id', 'in', company_ids)]` | `base.group_user` | Campus isolation via partner→student→campus chain |

### 6.7 Demo Data

- 20 students at "Rizal State University" (Main campus):
  - 3 applicants
  - 2 admitted
  - 5 enrolled/active (various year levels)
  - 2 on leave of absence
  - 3 graduated
  - 2 alumni
  - 1 dismissed
  - 1 transferred out
  - 1 denied
- 5 students with sample identifiers (PhilSys, LRN with synthetic values)
- Guardian records for 3 minor students (age < 18)
- 2 `esmis.student.program` records for students with program bindings
- All demo data uses fictional names and `example.edu.ph` email domain
- Use `with_context(tracking_disable=True)` to avoid notification noise

### 6.8 Acceptance Criteria

- [ ] `esmis.student` creates a linked `res.partner` or attaches to existing one
- [ ] Student state machine enforces valid transitions (invalid raises `UserError`)
- [ ] `esmis.identifier` encrypts Tier 3 values and generates blind index
- [ ] Blind index search works (exact match by identifier value)
- [ ] Guardian is required when student is a minor (age < 18)
- [ ] Consent fields track who gave consent and when
- [ ] Campus isolation via `company_id` record rules
- [ ] Student Self record rule: student can only see own record
- [ ] Faculty can read student records but not write
- [ ] Registrar officer can CRUD, registrar manager can also delete
- [ ] Complete ACLs for all 3 models
- [ ] No PII (names, student numbers) in log messages
- [ ] Demo data creates students across multiple lifecycle states
- [ ] Tests cover state machine transitions (valid and invalid)
- [ ] Tests cover encryption round-trip (write plaintext → read plaintext)
- [ ] Tests cover blind index search
- [ ] Tests cover guardian requirement for minors
- [ ] Tests cover campus isolation
- [ ] Tests cover consent integration (student has consent mixin methods)

---

## 7. Cross-Cutting Implementation Requirements

### 7.1 TDD Workflow

Write tests before implementation code. The cycle:
1. Write a failing test for the next requirement
2. Write the minimum code to make it pass
3. Refactor while keeping tests green
4. Commit

### 7.2 No PII in Logs or Errors

```python
# WRONG
_logger.error("Failed for student %s", student.name)

# CORRECT
_logger.error("Failed for student record id=%d", student.id)
```

### 7.3 Conventional Commits

Commit after each meaningful step. Format: `feat:`, `fix:`, `test:`, `chore:`, `docs:`,
`refactor:`.

### 7.4 Pre-commit Hooks

All code must pass `pre-commit run --files <changed_files>` before commit.

### 7.5 Every Model Needs ACL

Every `esmis.*` model must have:
- A `base.group_system` full CRUD row in `ir.model.access.csv`
- ACL rows for every relevant security group
- Related child models need their own ACLs

### 7.6 Demo Data

- Use `with_context(tracking_disable=True)` for bulk creation
- Create records under appropriate user context (not OdooBot)
- Use fictional data: "Rizal State University", Filipino-sounding but obviously fake names
- No real PII values in any demo or test data

### 7.7 Verification

Before marking any module complete:
1. `./esmis test <module>` passes
2. `pre-commit run --files <changed_files>` passes
3. Demo data installs without errors
4. ACLs verified by running operations as non-admin users in tests

---

## 8. Parallelization Strategy

| Work Stream | Can Start When | Blocked Until |
|-------------|---------------|---------------|
| `esmis_security` abstract mixins | Immediately | — |
| `esmis_security` concrete models | After mixins are stable | Mixins pass tests |
| `esmis_security` groups and ACLs | Can be drafted alongside mixins | Concrete models exist |
| `esmis_academic_term` | After `esmis.campus.aware` mixin exists | Mixin passes tests |
| `esmis_student` models | After all 6 mixins are stable | `pii.aware`, `consent.mixin`, `campus.aware` pass tests |
| `esmis_student` encryption | After encryption Decision 2 is made | Decision finalized |
| Demo data (all modules) | After core models pass tests | Models exist |

**With 2 developers:**
- Developer A: `esmis_security` (all of it)
- Developer B: `esmis_academic_term` (starts after campus.aware lands), then `esmis_student`

**With 1 developer:**
- Build `esmis_security` mixins → concrete models → groups/ACLs
- Build `esmis_academic_term` (small; quick break from security)
- Build `esmis_student`
- Write demo data for all three

---

## 9. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 16 models in `esmis_security` is too much test surface for one module | MEDIUM | MEDIUM | Decision 1 (split into security + audit) reduces per-module complexity |
| Encryption adds complexity to `esmis.identifier` | MEDIUM | LOW | Fernet (Decision 2) is simpler; defer AES-256-GCM to later phase |
| Abstract mixins must be stable before domain modules depend on them | HIGH | HIGH | Build and fully test mixins first; freeze the interface before starting consumers |
| Consent model's `partner_id` vs `student_id` causes confusion | LOW | MEDIUM | Decision 4 (partner_id with student helper) follows Odoo pattern; document clearly |
| `esmis.student` forward-references Phase 2 models (`program_id`, `curriculum_id`) | LOW | LOW | Fields exist but are not required and not in views; populated by Phase 2 modules |
| Working days computation for DSAR deadline is complex | LOW | LOW | Use `numpy.busday_count` or a simple Python loop; Philippine holidays from a data file |
| Demo data dependencies are fragile (order-sensitive) | MEDIUM | MEDIUM | Load demo data via XML with explicit `ref()` dependencies; test with `--init` |
| Consent unique constraint (active per student+purpose) requires a partial SQL index | LOW | LOW | Use `CREATE UNIQUE INDEX ... WHERE date_withdrawn IS NULL` via `init()` method |

---

## Appendix: Document Contradictions Found

These contradictions between docs should be resolved before or during implementation:

1. **Audit mixin module ownership:** ERD mixin summary says `esmis_audit`; data model
   registry says `esmis_security`. Resolution depends on Decision 1.

2. **Encrypted field mixin module:** ERD says `esmis_pii_encryption`; data-privacy doc
   says Fernet in whatever module defines the identifier. No `esmis_pii_encryption` module
   exists. Resolution: implement encryption directly in `esmis_student` for Phase 1.

3. **Consent model `student_id` vs `partner_id`:** consent-management.md says `student_id`
   (Many2one to `esmis.student`); data model registry also says `student_id`. But
   `esmis_security` is built before `esmis_student`, creating a dependency issue.
   Resolution: Decision 4 (use `partner_id`).

4. **ADR-006 claims "IMPLEMENTED"** for AES-256-GCM encrypted field mixin, but no
   implementation exists in the codebase. The principle doc says Fernet. Resolution:
   ADR-006 is aspirational; update status to "Accepted" not "Implemented".

5. **ADR-005 claims `esmis_data_classification` module is "Implemented"** with 2,523
   lines. No such module exists in the codebase. Resolution: same as above — ADR is
   aspirational.

6. **Number of models in esmis_security:** Roadmap says 14 (6 abstract + 8 concrete);
   data model registry lists 6 abstract + 10 concrete = 16; ADR-016 says "10+ models".
   Resolution: the data model registry (10 concrete) is the authoritative source.

7. **esmis.student.academic_standing values:** Data model registry uses
   `good_standing, dean_list, probation, warning, dismissed`. Implementation roadmap
   uses `good standing, Dean's List, probation, dismissed`. Resolution: use underscore
   format matching Selection field conventions.

---

**End of Phase 1 Build Plan**
