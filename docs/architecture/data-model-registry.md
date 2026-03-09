# Data Model Registry

Central specification of all `esmis.*` models — implemented and planned. This document
is derived from the full project documentation: principle docs, ADRs, guides, and research
documents. It is the authoritative reference for what models exist, where they live, and
what governs them.

**Last Updated:** 2026-03-09

---

## Model Count Summary

| Architecture Layer | Module Count | Model Count | Implemented | Planned |
|--------------------|-------------|-------------|-------------|---------|
| Layer 1: Foundation | 4 | 19 | 2 | 17 |
| Layer 2: Domain Core | 7 | 30 | 0 | 30 |
| Layer 3: Domain Extensions | 4 | 16 | 0 | 16 |
| Layer 4: Portals & Integrations | 4 | 9 | 0 | 9 |
| Cross-Cutting (Mixins/Abstract) | — | 7 | 0 | 7 |
| **Total** | **19** | **81** | **2** | **79** |

> **Note:** Layer 1 includes privacy/compliance models (`esmis.consent`, `esmis.data.breach`,
> `esmis.data.subject.request`, `esmis.disposal.review`, `esmis.retention.schedule`,
> `esmis.consent.scope`) as they belong to `esmis_security`. Layer 3 includes DMS models
> and `esmis.attendance.log`.

---

## Table of Contents

1. [Cross-Cutting Mixins and Abstract Models](#cross-cutting-mixins-and-abstract-models)
2. [Layer 1: Foundation](#layer-1-foundation)
3. [Layer 2: Domain Core](#layer-2-domain-core)
4. [Layer 3: Domain Extensions](#layer-3-domain-extensions)
5. [Layer 4: Portals & Integrations](#layer-4-portals--integrations)

---

## Cross-Cutting Mixins and Abstract Models

These abstract models are inherited by domain models across multiple modules. They do not
have their own database tables.

### `esmis.approval.mixin`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Status | Planned |
| Governed by | [Approval Workflows](../principles/approval-workflows.md) |
| Description | Provides standardized approval workflow states and methods for any approvable model. |

| Field | Type | Description |
|-------|------|-------------|
| `approval_state` | Selection | `draft`, `pending`, `approved`, `rejected`, `revision` |
| `submitted_by_id` | Many2one (`res.users`) | User who submitted for approval |
| `submitted_date` | Datetime | Submission timestamp |
| `approved_by_id` | Many2one (`res.users`) | Approver |
| `approved_date` | Datetime | Approval timestamp |
| `rejected_by_id` | Many2one (`res.users`) | User who rejected |
| `rejected_date` | Datetime | Rejection timestamp |
| `rejection_reason` | Text | Reason for rejection |

**Key methods:** `action_submit_for_approval()`, `action_approve()`, `action_reject()`, `action_reset_to_draft()`, `action_request_revision()`

### `esmis.consent.mixin`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` (or `esmis_consent`) |
| Status | Planned |
| Governed by | [Consent Management](../principles/consent-management.md), [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md) |
| Description | Provides consent checking for models that process PII for consent-required purposes. |

| Field | Type | Description |
|-------|------|-------------|
| (no stored fields) | — | Mixin provides methods only |

**Key methods:** `_has_active_consent(purpose)`, `_check_consent_for_export()`

### `esmis.pii.aware`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` (or `esmis_data_classification`) |
| Status | Planned |
| Governed by | [Data Privacy and PII](../principles/data-privacy-and-pii.md), [ADR-005](decisions/ADR-005-data-classification-system.md), [ADR-006](decisions/ADR-006-pii-encryption-strategy.md) |
| Description | Mixin for models storing PII. Provides field-level classification metadata, masking, encryption hooks, and audit logging on read/write of classified fields. |

| Field | Type | Description |
|-------|------|-------------|
| (no stored fields) | — | Mixin provides classification metadata and encryption hooks |

### `esmis.campus.aware` (campus-scoping mixin)

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Status | Planned |
| Governed by | [Multi-Campus Architecture](../principles/multi-campus-architecture.md), [ADR-010](decisions/ADR-010-multi-campus-architecture.md) |
| Description | Adds `company_id` field with standard campus isolation record rule pattern. All campus-scoped transactional models should inherit this. |

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | Many2one (`res.company`) | Campus; required, indexed, default=current company |

### `esmis.audit.mixin`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_audit` (planned) |
| Status | Planned |
| Governed by | [Audit & Compliance](../principles/audit-compliance.md) |
| Description | Extends `mail.thread` with additional audit capabilities: soft delete tracking, legal hold, and retention policy enforcement. |

| Field | Type | Description |
|-------|------|-------------|
| `legal_hold` | Boolean | Prevents automated disposal when True |
| `legal_hold_reason` | Text | Reason for legal hold |
| `legal_hold_set_by` | Many2one (`res.users`) | User who set the hold |
| `archived_date` | Datetime | When the record was archived |
| `archived_by_id` | Many2one (`res.users`) | User who archived |
| `archive_reason` | Text | Reason for archival |

### `esmis.retention.aware`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Status | Planned |
| Governed by | [Data Retention and Disposal](../principles/data-retention-and-disposal.md) |
| Description | Marks models subject to the retention schedule. Provides fields for legal hold and disposal tracking. |

| Field | Type | Description |
|-------|------|-------------|
| `legal_hold` | Boolean | Prevents automated disposal |
| `legal_hold_reason` | Text | Reason |
| `legal_hold_set_by` | Many2one (`res.users`) | Who set hold |

### `esmis.encrypted.field.mixin`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_pii_encryption` (planned) |
| Status | Planned |
| Governed by | [ADR-006](decisions/ADR-006-pii-encryption-strategy.md) |
| Description | Provides AES-256-GCM encryption, blind index generation, and masked field widget support for Tier 3 PII fields. |

---

## Layer 1: Foundation

### Module: `esmis_vocabulary`

**Purpose:** Unified vocabulary/terminology system for controlled code lists.
**Status:** Implemented (v19.0.1.0.0)
**Governed by:** [ADR-003](decisions/ADR-003-terminology-system.md), [Module Architecture](../principles/module-architecture.md)

#### `esmis.vocabulary`

| Status | **Implemented** |
|--------|-----------------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Human-readable name (e.g., "Gender") |
| `namespace_uri` | Char | Globally unique URI (e.g., `urn:iso:std:iso:5218`) |
| `version` | Char | Version of the vocabulary |
| `description` | Text | Description |
| `reference_url` | Char | Link to official documentation |
| `is_system` | Boolean | System vocabularies cannot be edited by users |
| `is_hierarchical` | Boolean | Codes can have parent/child relationships |
| `domain` | Selection | `core`, `operations`, `administrative`, `identity`, `regulatory`, `health`, `education` |
| `code_ids` | One2many (`esmis.vocabulary.code`) | Codes in this vocabulary |
| `code_count` | Integer (computed) | Number of codes |
| `active` | Boolean | Active flag |

**Key relationships:** Parent of `esmis.vocabulary.code`

#### `esmis.vocabulary.code`

| Status | **Implemented** |
|--------|-----------------|

| Field | Type | Description |
|-------|------|-------------|
| `vocabulary_id` | Many2one (`esmis.vocabulary`) | Parent vocabulary |
| `namespace_uri` | Char (related) | From parent vocabulary |
| `code` | Char | Machine-readable code (e.g., "M", "1") |
| `display` | Char | Human-readable label |
| `definition` | Text | Formal definition |
| `sequence` | Integer | Display order |
| `parent_id` | Many2one (`esmis.vocabulary.code`) | Parent code (for hierarchical vocabularies) |
| `child_ids` | One2many (`esmis.vocabulary.code`) | Children |
| `level` | Integer (computed) | Hierarchy depth |
| `active` | Boolean | Active flag |
| `deprecated` | Boolean | Deprecated flag |
| `deprecated_date` | Date | When deprecated |
| `replaced_by_id` | Many2one (`esmis.vocabulary.code`) | Superseding code |
| `mapping_ids` | One2many (`esmis.vocabulary.mapping`) | Mappings to other vocabularies |

**Key relationships:** Child of `esmis.vocabulary`; used as a Many2one target throughout the system for extensible code lists (gender, civil status, academic standing, learning modality, etc.)

#### `esmis.vocabulary.mapping`

| Status | Planned (deferred from v1) |
|--------|----------------------------|

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | Many2one (`esmis.vocabulary.code`) | Source code |
| `target_id` | Many2one (`esmis.vocabulary.code`) | Target code |
| `equivalence` | Selection | `equivalent`, `wider`, `narrower`, `inexact` |
| `comment` | Text | Notes |

---

### Module: `esmis_security`

**Purpose:** Security groups, privileges, access control architecture, DPO role, and cross-cutting security mixins.
**Status:** Planned (partial implementation of group hierarchy exists)
**Governed by:** [Access Rights](../principles/access-rights.md), [ADR-001](decisions/ADR-001-access-rights-management.md)

#### `esmis.audit.rule`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Rule name |
| `model_id` | Many2one (`ir.model`) | Model to audit |
| `log_create` | Boolean | Log create events |
| `log_write` | Boolean | Log write events |
| `log_unlink` | Boolean | Log delete events |
| `field_to_log_ids` | Many2many (`ir.model.fields`) | Fields to track |

#### `esmis.audit.log`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `audit_rule_id` | Many2one (`esmis.audit.rule`) | Link to rule configuration |
| `user_id` | Many2one (`res.users`) | Who made the change |
| `create_date` | Datetime | When |
| `model_id` | Many2one (`ir.model`) | Which model |
| `res_id` | Integer | Which record |
| `method` | Selection | `create`, `write`, `unlink` |
| `data` | Text (JSON) | Old/new values |

#### `esmis.pii.access.log`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | Many2one (`res.users`) | Accessor |
| `create_date` | Datetime | Timestamp |
| `model` | Char | Model accessed |
| `res_id` | Integer | Record ID |
| `field_name` | Char | Field accessed |
| `access_type` | Selection | `read`, `reveal`, `write`, `export`, `search`, `btg` |
| `ip_address` | Char | IP address |
| `session_id` | Char | Session identifier |

**Key constraint:** Append-only; `unlink()` and `write()` on immutable fields are blocked.

#### `esmis.approval.definition`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Definition name |
| `model_id` | Many2one (`ir.model`) | Model this applies to |
| `stage_ids` | One2many | Approval stages (ordered) |

---

### Module: `esmis_student`

**Purpose:** Core student profile linked to `res.partner`.
**Status:** Planned
**Governed by:** [Student Data Lifecycle](../principles/student-data-lifecycle.md), [Data Privacy and PII](../principles/data-privacy-and-pii.md)

#### `esmis.student`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one (`res.partner`) | Linked Odoo contact |
| `student_number` | Char | Institution-assigned student number |
| `company_id` | Many2one (`res.company`) | Campus (campus-scoped) |
| `state` | Selection | `applicant`, `admitted`, `enrolled`, `active`, `loa`, `graduated`, `alumni`, `dismissed`, `transferred_out` |
| `curriculum_id` | Many2one (`esmis.curriculum`) | Bound curriculum version |
| `program_id` | Many2one (`esmis.program`) | Enrolled program |
| `year_level` | Integer | Current year level |
| `gwa` | Float | Cumulative GWA |
| `academic_standing` | Selection | `good_standing`, `dean_list`, `probation`, `warning`, `dismissed` |
| `guardian_id` | Many2one (`res.partner`) | Parent/guardian for minors |
| `religion` | Char | Religious affiliation (Tier 1) |
| `ethnicity` | Char | Ethnic/IP membership (Tier 1) |
| `consent_given` | Boolean | Privacy consent flag |
| `consent_date` | Datetime | When consent was given |
| `consent_given_by` | Char | Name of signatory |
| `is_consent_for_minor` | Boolean | Parent/guardian consent indicator |
| `transfer_state` | Selection | `none`, `transferred_in`, `transferred_out` |
| `transfer_date` | Date | Date of transfer |
| `diploma_released_date` | Date | When diploma was released |

**Key relationships:** Links to `res.partner`, `esmis.curriculum`, `esmis.program`, `esmis.enrollment`, `esmis.grade`, `esmis.consent`

#### `esmis.student.program`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `program_id` | Many2one (`esmis.program`) | Program |
| `curriculum_id` | Many2one (`esmis.curriculum`) | Curriculum version |
| `term_gwa` | Float (computed) | GWA for current term |
| `cumulative_gwa` | Float (computed) | Cumulative GWA |
| `consecutive_below_threshold_count` | Integer | Counter for probation tracking |
| `academic_standing` | Selection | Standing for this program |

#### `esmis.student.course.history`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `course_id` | Many2one (`esmis.course`) | Course |
| `grade_id` | Many2one (`esmis.grade`) | Grade record |
| `term_id` | Many2one (`esmis.academic.term`) | Term taken |
| `is_passed` | Boolean | Whether the course was passed |

#### `esmis.identifier`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one (`res.partner`) | Linked partner |
| `type_id` | Many2one (`esmis.vocabulary.code`) | Identifier type (PhilSys, LRN, TIN, etc.) |
| `system_uri` | Char (related) | URI from type (stored, indexed) |
| `value` | Char | Identifier value (encrypted for Tier 3) |
| `value_ciphertext` | Binary | Encrypted value |
| `value_blind_index` | Char | HMAC blind index for exact-match search |

**Key relationships:** Links to `res.partner` via One2many; type defined by `esmis.vocabulary.code`

---

### Module: `esmis_academic_term`

**Purpose:** Academic year and term/semester definitions.
**Status:** Planned
**Governed by:** [Multi-Campus Architecture](../principles/multi-campus-architecture.md), [Enrollment Workflows](../principles/enrollment-workflows.md)

#### `esmis.academic.year`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | e.g., "AY 2025-2026" |
| `date_start` | Date | Start date |
| `date_end` | Date | End date |
| `term_ids` | One2many (`esmis.academic.term`) | Terms within this year |

**Note:** Shared (no `company_id`) — institution-wide academic year.

#### `esmis.academic.term`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | e.g., "1st Semester 2025-2026" |
| `academic_year_id` | Many2one (`esmis.academic.year`) | Parent year |
| `company_id` | Many2one (`res.company`) | Campus (campus-scoped) |
| `date_start` | Date | Term start |
| `date_end` | Date | Term end |
| `enrollment_open_date` | Datetime | When enrollment opens |
| `enrollment_close_date` | Datetime | When enrollment closes |
| `add_drop_deadline` | Date | Last day for add/drop |
| `state` | Selection | `draft`, `enrollment_open`, `in_progress`, `grading`, `closed` |

---

## Layer 2: Domain Core

### Module: `esmis_curriculum`

**Purpose:** Programs, courses, curriculum plans, prerequisite chains, and PQF mappings.
**Status:** Planned
**Governed by:** [Architecture Vision](vision.md), [Grading and Academic Standing](../principles/grading-and-academic-standing.md), [Regulatory Compliance](../principles/regulatory-compliance.md)

#### `esmis.program`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | e.g., "Bachelor of Science in Computer Science" |
| `code` | Char | CHED program code |
| `degree_type` | Many2one (`esmis.vocabulary.code`) | Bachelor's, Master's, Doctoral, etc. |
| `pqf_level` | Integer | PQF level (1-8) |
| `college_id` | Many2one (`esmis.college`) | Owning college |
| `curriculum_ids` | One2many (`esmis.curriculum`) | Curriculum versions |
| `grading_system_id` | Many2one (`esmis.grading.system`) | Default grading system |

**Note:** Shared (no `company_id`) — CHED-recognized programs are institution-level.

#### `esmis.college`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | College name |
| `company_id` | Many2one (`res.company`) | Campus |
| `program_ids` | One2many (`esmis.program`) | Programs offered |

#### `esmis.course`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Course title |
| `code` | Char | Course code (e.g., "CS 101") |
| `units` | Float | Credit units |
| `prerequisite_ids` | Many2many (`esmis.course`) | Prerequisite courses |
| `corequisite_ids` | Many2many (`esmis.course`) | Co-requisite courses |
| `description` | Text | Course description |

**Note:** Shared (no `company_id`) — same course code across campuses.

#### `esmis.curriculum`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Curriculum version name |
| `program_id` | Many2one (`esmis.program`) | Program |
| `version` | Char | Version identifier |
| `effective_year` | Char | Effective academic year |
| `course_ids` | Many2many (`esmis.course`) | Required courses |
| `total_units` | Float | Total units for graduation |
| `elective_units` | Float | Required elective units |
| `residency_units` | Float | Minimum in-residence units |

**Note:** Shared (no `company_id`).

#### `esmis.pqf.mapping`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `program_id` | Many2one (`esmis.program`) | Program |
| `pqf_level` | Integer | PQF level (1-8) |
| `qualification_title` | Char | PQF qualification title |

**Note:** Shared (no `company_id`) — national standards.

---

### Module: `esmis_enrollment`

**Purpose:** Enrollment lifecycle: admissions, cart, validation, assessment, add/drop, cross-enrollment.
**Status:** Planned
**Governed by:** [Enrollment Workflows](../principles/enrollment-workflows.md), [Student Data Lifecycle](../principles/student-data-lifecycle.md)

#### `esmis.applicant`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one (`res.partner`) | Applicant contact |
| `company_id` | Many2one (`res.company`) | Campus applied to |
| `student_id` | Many2one (`esmis.student`) | Created on admission |
| `program_id` | Many2one (`esmis.program`) | Target program |
| `state` | Selection | `application`, `evaluation`, `admitted`, `waitlisted`, `denied`, `conditional`, `enrolled`, `declined` |
| `lrn` | Char | Learner Reference Number (12-digit, DepEd) |
| `entrance_exam_scores` | Text (JSON) | Exam component scores |
| `philsys_verified` | Boolean | PhilSys verification status |
| `philsys_verification_date` | Datetime | Verification timestamp |
| `philsys_verification_mode` | Selection | `qr`, `everify` |
| `philsys_psn` | Char | PhilSys Number (Restricted) |
| `consent_given` | Boolean | Privacy consent |
| `consent_date` | Datetime | Consent timestamp |
| `consent_given_by` | Char | Signatory name |
| `is_consent_for_minor` | Boolean | Minor consent flag |

#### `esmis.admission.decision`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `applicant_id` | Many2one (`esmis.applicant`) | Applicant |
| `decision` | Selection | `admitted`, `waitlisted`, `denied`, `conditional` |
| `conditions` | Text | Conditions for conditional admission |
| `resolution_deadline` | Date | Deadline for conditions |
| `decided_by` | Many2one (`res.users`) | Decision maker |

#### `esmis.enrollment`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `term_id` | Many2one (`esmis.academic.term`) | Academic term |
| `company_id` | Many2one (`res.company`) | Home campus |
| `section_company_id` | Many2one (`res.company`) | Host campus (for cross-enrollment) |
| `state` | Selection | `cart`, `validated`, `hold`, `assessed`, `cancelled`, `paid`, `waitlisted`, `enrolled` |
| `is_cross_enrolled` | Boolean (computed) | Cross-enrollment flag |
| `line_ids` | One2many (`esmis.enrollment.line`) | Course selections |

#### `esmis.enrollment.line`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `enrollment_id` | Many2one (`esmis.enrollment`) | Parent enrollment |
| `section_id` | Many2one (`esmis.section`) | Selected section |
| `course_id` | Many2one (`esmis.course`) | Course (related from section) |
| `units` | Float | Credit units |
| `state` | Selection | `selected`, `confirmed`, `waitlisted`, `dropped` |

#### `esmis.enrollment.change`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `enrollment_id` | Many2one (`esmis.enrollment`) | Parent enrollment |
| `change_type` | Selection | `add`, `drop` |
| `section_id` | Many2one (`esmis.section`) | Affected section |
| `reason` | Text | Change reason |
| `refund_amount` | Float | Computed refund for drops |
| `changed_by` | Many2one (`res.users`) | User who made the change |
| `change_date` | Datetime | Timestamp |

#### `esmis.enrollment.hold`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `hold_type` | Selection | `financial`, `disciplinary`, `library`, `registrar` |
| `reason` | Text | Hold reason |
| `is_active` | Boolean | Whether hold is currently active |
| `placed_by` | Many2one (`res.users`) | Who placed the hold |

#### `esmis.enrollment.window`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `term_id` | Many2one (`esmis.academic.term`) | Term |
| `company_id` | Many2one (`res.company`) | Campus |
| `priority_group` | Selection | `pwd_solo_parent`, `graduating`, `4th_year`, `3rd_year`, `2nd_year`, `1st_year` |
| `date_start` | Datetime | Window opens |
| `date_end` | Datetime | Window closes |

#### `esmis.cross.enrollment.permit`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `home_company_id` | Many2one (`res.company`) | Home campus |
| `host_company_id` | Many2one (`res.company`) | Host campus |
| `section_id` | Many2one (`esmis.section`) | Target section |
| `state` | Selection | `draft`, `approved`, `used`, `expired` |

#### `esmis.credit.transfer`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | Many2one (`res.company`) | Receiving campus |
| `source_company_id` | Many2one (`res.company`) | Source campus |
| `student_id` | Many2one (`res.partner`) | Student |
| `source_enrollment_ids` | Many2many (`esmis.enrollment`) | Source enrollments |
| `evaluated_units` | Float | Units evaluated |
| `approved_units` | Float | Units approved for credit |
| `state` | Selection | `draft`, `evaluated`, `approved`, `rejected` |

---

### Module: `esmis_grading`

**Purpose:** Grade entry, component-based grading, GWA computation, grade change workflow, INC resolution.
**Status:** Planned
**Governed by:** [Grading and Academic Standing](../principles/grading-and-academic-standing.md), [ADR-015](decisions/ADR-015-grading-system-flexibility.md)

#### `esmis.grading.system`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | e.g., "Standard Philippine 1.0-5.0 Scale" |
| `scale_direction` | Selection | `ascending_is_worse`, `ascending_is_better` |
| `passing_threshold` | Float | Lowest passing numeric value |
| `gpa_equivalent_enabled` | Boolean | Whether scale entries carry 4.0 GPA equivalent |
| `scale_ids` | One2many (`esmis.grading.scale`) | Scale entries |

**Note:** Shared by default; campus overrides possible.

#### `esmis.grading.scale`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `grading_system_id` | Many2one (`esmis.grading.system`) | Parent system |
| `numeric_value` | Float | Grade value (e.g., 1.25) |
| `label` | Char | Display label (e.g., "Excellent") |
| `gpa_equivalent` | Float | 4.0-scale equivalent |
| `is_passing` | Boolean | Passing grade flag |
| `is_incomplete` | Boolean | Marks INC grade entry |
| `is_dropped` | Boolean | Marks DRP/W/FD entries |

#### `esmis.grade.component.template`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Template name |
| `line_ids` | One2many | Component lines with weights |

#### `esmis.grade`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `section_id` | Many2one (`esmis.section`) | Section |
| `enrollment_line_id` | Many2one (`esmis.enrollment.line`) | Enrollment line |
| `state` | Selection | `draft`, `submitted`, `approved`, `locked` |
| `final_grade` | Float | Final grade value |
| `numeric_value` | Float | Numeric value from grading scale |
| `units` | Float | Credit units |
| `is_incomplete` | Boolean | INC flag |
| `is_dropped` | Boolean | DRP flag |
| `is_included_in_gwa` | Boolean | Whether included in GWA |
| `is_midterm` | Boolean | Midterm grade flag |
| `resolution_deadline` | Date | INC resolution deadline |
| `source` | Selection | `manual`, `lms` — origin of grade |

#### `esmis.grade.component`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `grade_id` | Many2one (`esmis.grade`) | Parent grade |
| `component_type` | Selection | `midterm`, `final`, `project`, `recitation`, `attendance`, `other` |
| `weight` | Float | Weight (%) |
| `raw_score` | Float | Raw score |
| `weighted_score` | Float (computed) | Weighted score |

#### `esmis.grade.change`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `original_grade_id` | Many2one (`esmis.grade`) | Original locked grade |
| `requested_by` | Many2one (`res.users`) | Faculty who initiated |
| `requested_at` | Datetime | Submission timestamp |
| `old_grade_value` | Float | Captured original value |
| `new_grade_value` | Float | Proposed replacement |
| `reason` | Text | Mandatory justification |
| `state` | Selection | `request`, `dean_review`, `registrar_apply`, `locked` |
| `dean_approved_by` | Many2one (`res.users`) | Dean approver |
| `dean_approved_at` | Datetime | Dean approval timestamp |
| `registrar_locked_by` | Many2one (`res.users`) | Registrar who applied |
| `registrar_locked_at` | Datetime | Registrar lock timestamp |

#### `esmis.standing.policy`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `program_id` | Many2one (`esmis.program`) | Program |
| `retention_threshold` | Float | GWA threshold for retention |
| `warning_threshold` | Float | GWA warning band |
| `deans_list_threshold` | Float | Dean's List GWA threshold |
| `company_id` | Many2one (`res.company`) | Campus override (optional) |

#### `esmis.latin.honors.config`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `honors_level` | Selection | `summa_cum_laude`, `magna_cum_laude`, `cum_laude` |
| `min_gwa` | Float | Minimum GWA for this level |
| `max_gwa` | Float | Maximum GWA for this level |
| `min_units_completed` | Float | Minimum residency units |
| `no_failing_grade_required` | Boolean | Any failing grade disqualifies |

---

### Module: `esmis_scheduling`

**Purpose:** Class sections, room assignments, faculty-section assignments, schedule conflict detection.
**Status:** Planned
**Governed by:** [Architecture Vision](vision.md), [ADR-014](decisions/ADR-014-lms-integration-standards.md)

#### `esmis.section`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Section identifier |
| `course_id` | Many2one (`esmis.course`) | Course |
| `term_id` | Many2one (`esmis.academic.term`) | Academic term |
| `company_id` | Many2one (`res.company`) | Campus |
| `room_id` | Many2one (`esmis.room`) | Assigned room |
| `faculty_id` | Many2one (`hr.employee`) | Instructor |
| `capacity` | Integer | Maximum students |
| `enrolled_count` | Integer (computed) | Current enrollment |
| `learning_modality` | Selection | `face_to_face`, `online`, `blended`, `asynchronous` |
| `grading_system_id` | Many2one (`esmis.grading.system`) | Grading system for this section |
| `schedule_ids` | One2many | Schedule time slots |

#### `esmis.room`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Room name/number |
| `company_id` | Many2one (`res.company`) | Campus |
| `capacity` | Integer | Seating capacity |
| `building` | Char | Building name |
| `floor` | Char | Floor |

---

### Module: `esmis_billing`

**Purpose:** Fee schedules, financial assessment, payment tracking, student ledger.
**Status:** Planned
**Governed by:** [Enrollment Workflows](../principles/enrollment-workflows.md), [Financial Aid Patterns](../principles/financial-aid-patterns.md)

#### `esmis.fee.schedule`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Schedule name |
| `company_id` | Many2one (`res.company`) | Campus |
| `term_id` | Many2one (`esmis.academic.term`) | Term |
| `rate_per_unit` | Float | Tuition rate per credit unit |
| `miscellaneous_fee_ids` | One2many | Miscellaneous fee lines |

#### `esmis.financial.assessment`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `enrollment_id` | Many2one (`esmis.enrollment`) | Enrollment record |
| `student_id` | Many2one (`esmis.student`) | Student |
| `company_id` | Many2one (`res.company`) | Campus |
| `base_tuition` | Float | Computed base tuition |
| `miscellaneous_fees` | Float | Total miscellaneous fees |
| `discount_amount` | Float | Total discounts applied |
| `net_amount` | Float | Net amount due |
| `state` | Selection | `draft`, `computed`, `locked` |

---

### Module: `esmis_financial_aid`

**Purpose:** Financial aid programs, eligibility rules, award lifecycle, discount stacking.
**Status:** Planned
**Governed by:** [Financial Aid Patterns](../principles/financial-aid-patterns.md), [ADR-013](decisions/ADR-013-financial-aid-modeling.md)

#### `esmis.financial.aid.program`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Program name |
| `program_type` | Selection | `government`, `institutional`, `external`, `statutory_discount` |
| `governing_law` | Char | Legal basis (e.g., "RA 10931") |
| `funding_source` | Char | Funding source |
| `eligibility_domain` | Char | Odoo domain expression for eligibility |
| `benefit_amount` | Float | Per-term benefit amount |
| `stacking_policy` | Selection | `stackable`, `exclusive`, `capped` |
| `max_combined_amount` | Float | Cap for `capped` stacking |
| `renewable` | Boolean | Whether the award auto-renews |
| `renewal_criteria_domain` | Char | Domain for renewal checks |
| `application_order` | Integer | Order in discount stacking sequence |

**Note:** Philippine-specific defaults (TES, DOST-SEI, PWD) provided by `esmis_financial_aid_ph` data files.

#### `esmis.financial.aid.award`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `program_id` | Many2one (`esmis.financial.aid.program`) | Aid program |
| `student_id` | Many2one (`esmis.student`) | Student |
| `term_id` | Many2one (`esmis.academic.term`) | Term |
| `company_id` | Many2one (`res.company`) | Campus |
| `state` | Selection | `draft`, `evaluated`, `approved`, `disbursed`, `completed`, `ineligible`, `rejected` |
| `approved_amount` | Float | Approved award amount |
| `disbursement_date` | Date | When disbursed |
| `stacking_order_applied` | Text (JSON) | Record of stacking order used |

#### `esmis.financial.aid.application`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Applicant |
| `program_id` | Many2one (`esmis.financial.aid.program`) | Target program |
| `family_income_bracket` | Selection | Income bracket |
| `supporting_documents` | Many2many (`ir.attachment`) | Uploaded documents |
| `state` | Selection | `draft`, `submitted`, `under_review`, `approved`, `rejected` |

---

### Module: `esmis_faculty`

**Purpose:** Faculty profiles, teaching load management.
**Status:** Planned
**Governed by:** [Architecture Vision](vision.md), [Multi-Campus Architecture](../principles/multi-campus-architecture.md)

#### `esmis.faculty.load`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `employee_id` | Many2one (`hr.employee`) | Faculty member |
| `company_id` | Many2one (`res.company`) | Campus |
| `term_id` | Many2one (`esmis.academic.term`) | Term |
| `section_ids` | Many2many (`esmis.section`) | Assigned sections |
| `total_units` | Float (computed) | Total teaching units |

---

## Layer 3: Domain Extensions

### Module: `esmis_documents`

**Purpose:** Document management, TOR/diploma generation, eCAV export, credential verification.
**Status:** Planned
**Governed by:** [Student Data Lifecycle](../principles/student-data-lifecycle.md), [Government Integrations](../principles/government-integrations.md), [ADR-007](decisions/ADR-007-dms-security-and-storage-enhancements.md)

#### `esmis.document`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Document title |
| `student_id` | Many2one (`esmis.student`) | Student |
| `document_type` | Selection | `tor`, `diploma`, `certification`, `clearance`, `coe` |
| `generated_by` | Many2one (`res.users`) | Generating user |
| `generated_date` | Datetime | Generation timestamp |
| `file_id` | Many2one (`ir.attachment`) | Generated file |
| `qr_token` | Char | QR verification token |
| `digital_signature_id` | Many2one (`esmis.digital.signature`) | Digital signature |

#### `esmis.document.request`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Requesting student/alumnus |
| `document_type` | Selection | Type of document requested |
| `purpose` | Text | Purpose of request |
| `state` | Selection | `submitted`, `processing`, `ready`, `released` |
| `payment_required` | Boolean | Whether payment is required |

#### `esmis.digital.signature`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Signer name and title |
| `user_id` | Many2one (`res.users`) | Linked user |
| `signature_image` | Binary | Signature image |

#### `esmis.graduation`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Graduate |
| `program_id` | Many2one (`esmis.program`) | Program |
| `graduation_date` | Date | Graduation date |
| `honors_level` | Selection | `none`, `cum_laude`, `magna_cum_laude`, `summa_cum_laude` |
| `special_order_number` | Char | CHED Special Order number |
| `clearance_id` | Many2one (`esmis.clearance`) | Linked clearance |
| `state` | Selection | `candidate`, `cleared`, `graduated` |

#### `esmis.graduation.policy`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `program_id` | Many2one (`esmis.program`) | Program |
| `min_gwa` | Float | Minimum GWA for graduation |
| `honors_config_ids` | One2many (`esmis.latin.honors.config`) | Honors thresholds |

#### `esmis.clearance`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `state` | Selection | `pending`, `complete` |
| `line_ids` | One2many (`esmis.clearance.line`) | Per-office clearance lines |

#### `esmis.clearance.line`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `clearance_id` | Many2one (`esmis.clearance`) | Parent clearance |
| `office` | Selection | `library`, `finance`, `registrar`, `department`, `student_affairs` |
| `is_cleared` | Boolean | Whether cleared |
| `cleared_by` | Many2one (`res.users`) | Clearing officer |
| `cleared_date` | Datetime | Clearance timestamp |
| `notes` | Text | Notes or conditions |

---

### Module: `esmis_reports`

**Purpose:** Reporting dashboards, HEMIS export wizards, accreditation evidence packages.
**Status:** Planned
**Governed by:** [Government Integrations](../principles/government-integrations.md), [ADR-011](decisions/ADR-011-government-integration-architecture.md), [Government Export Guide](../guides/government-export-guide.md)

#### `esmis.hemis.export.wizard` (TransientModel)

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `academic_year_id` | Many2one (`esmis.academic.year`) | Target year |
| `institution_type` | Selection | `suc`, `private`, `luc` |
| `form_ids` | Many2many | Forms to include |
| `company_id` | Many2one (`res.company`) | Campus (or blank for system-wide) |

---

### Module: `esmis_alumni`

**Purpose:** Alumni status transition, tracer studies, alumni directory, credential verification.
**Status:** Planned
**Governed by:** [Student Data Lifecycle](../principles/student-data-lifecycle.md)

#### `esmis.tracer.response`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Alumnus |
| `survey_date` | Date | Response date |
| `employment_status` | Selection | `employed`, `self_employed`, `unemployed`, `further_study` |
| `employer_name` | Char | Employer |
| `job_title` | Char | Position |
| `is_degree_related` | Boolean | Whether job is degree-related |
| `months_to_first_job` | Integer | Time to first employment |

---

### Module: `esmis_student_services`

**Purpose:** Student advising, counseling records, disciplinary records, health records.
**Status:** Planned
**Governed by:** [Data Privacy and PII](../principles/data-privacy-and-pii.md), [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md)

#### `esmis.health.record`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `disability_status` | Char | PWD classification (Tier 3) |
| `medical_notes` | Text | Medical records (Tier 3) |
| `immunization_records` | Text | Immunization data (Tier 3) |

#### `esmis.counseling.note`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `counselor_id` | Many2one (`res.users`) | Assigned counselor |
| `session_date` | Datetime | Session date |
| `notes` | Text | Counseling notes (Tier 3 / Restricted) |

#### `esmis.disciplinary.record`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `violation` | Text | Violation description |
| `sanction` | Text | Applied sanction |
| `state` | Selection | `open`, `resolved`, `dismissed` |
| `company_id` | Many2one (`res.company`) | Campus |

---

## Layer 4: Portals & Integrations

### Module: `esmis_api`

**Purpose:** REST API facade, OAuth 2.0 authentication, external identifier enforcement, API client management.
**Status:** Planned
**Governed by:** [API Design](../principles/api-design.md), [ADR-004](decisions/ADR-004-api-v2-architecture.md), [ADR-009](decisions/ADR-009-api-v2-application-level-authorization.md)

#### `esmis.api.client`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Client name |
| `client_id` | Char | OAuth client ID |
| `client_secret_hash` | Char | Scrypt-hashed secret |
| `partner_id` | Many2one (`res.partner`) | Organization |
| `scope_ids` | One2many (`esmis.api.client.scope`) | Granted scopes |
| `active` | Boolean | Active flag |

#### `esmis.api.client.scope`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | Many2one (`esmis.api.client`) | Client |
| `resource` | Selection | `individual`, `group`, `program`, etc. |
| `actions` | Selection | `read`, `search`, `write` |
| `require_consent` | Boolean | Whether consent check applies |

#### `esmis.api.audit.log`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `api_client_id` | Many2one (`esmis.api.client`) | API client |
| `request_id` | Char | Correlation ID |
| `ip_address` | Char | Client IP |
| `operation` | Selection | `read`, `search`, `export`, `create`, `update`, `patch`, `delete` |
| `resource_type` | Char | Resource type |
| `resource_identifier` | Char | External identifier (never DB ID) |
| `consent_id` | Many2one (`esmis.consent`) | Consent record (optional) |
| `status` | Selection | `success`, `access_denied`, `not_found`, `error` |
| `timestamp` | Datetime | Event time |

#### `esmis.api.extension`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Extension name |
| `module_id` | Many2one (`ir.module.module`) | Owning module |
| `base_resource` | Selection | Resource type to extend |
| `field_ids` | Many2many (`ir.model.fields`) | Extended fields |
| `schema_definition` | Text (JSON) | JSON Schema fragment |

#### `esmis.api.path`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `path` | Char | API endpoint path |
| `field_ids` | Many2many (`ir.model.fields`) | Fields returned |
| `filter_domain` | Char | Record filter domain |
| `limit` | Integer | Max records per request |

---

### Module: `esmis_lms_bridge`

**Purpose:** LMS integration via LTI 1.3 and OneRoster 1.2 for roster sync and grade passback.
**Status:** Planned
**Governed by:** [Government Integrations](../principles/government-integrations.md), [ADR-014](decisions/ADR-014-lms-integration-standards.md)

#### `esmis.lms.platform`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | LMS name (e.g., "Campus Moodle") |
| `platform_type` | Selection | `moodle`, `canvas`, `google_classroom`, `other` |
| `base_url` | Char | LMS base URL |
| `client_id` | Char | LTI/OneRoster client ID |
| `client_secret` | Char | Encrypted secret |
| `lti_private_key` | Text | RSA private key for LTI 1.3 |
| `last_sync_cursor` | Char | OneRoster delta sync cursor |
| `company_id` | Many2one (`res.company`) | Campus |

---

### Module: `esmis_philsys`

**Purpose:** Philippine National ID verification via QR (offline) and eVerify (online).
**Status:** Planned
**Governed by:** [Government Integrations](../principles/government-integrations.md), [PhilSys Integration Guide](../guides/philsys-integration-guide.md), [ADR-011](decisions/ADR-011-government-integration-architecture.md)

#### `esmis.philsys.verification`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student (or applicant) |
| `verification_mode` | Selection | `qr`, `everify` |
| `verification_date` | Datetime | Timestamp |
| `result` | Selection | `pass`, `fail`, `pending` |
| `verified_by` | Many2one (`res.users`) | Operator |
| `consent_id` | Many2one (`esmis.consent`) | PhilSys consent record |

---

### Module: `esmis_payment`

**Purpose:** Payment gateway integration (PayMongo, Maya, Dragonpay) via webhooks.
**Status:** Planned
**Governed by:** [Government Integrations](../principles/government-integrations.md), [ADR-011](decisions/ADR-011-government-integration-architecture.md)

#### `esmis.payment`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `enrollment_id` | Many2one (`esmis.enrollment`) | Enrollment |
| `amount` | Float | Payment amount |
| `gateway` | Selection | `paymongo`, `maya`, `dragonpay`, `otc` |
| `gateway_reference` | Char | Gateway transaction reference |
| `state` | Selection | `pending`, `confirmed`, `failed`, `refunded` |
| `bank_account_number` | Char | Bank account (Tier 3, encrypted) |

#### `esmis.payment.event`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `payment_id` | Many2one (`esmis.payment`) | Payment record |
| `gateway` | Selection | Gateway source |
| `event_type` | Char | Webhook event type |
| `payload` | Text (JSON) | Raw webhook payload |
| `processed` | Boolean | Whether event was processed |
| `processed_date` | Datetime | Processing timestamp |

---

## Privacy & Compliance Models (Cross-Module)

These models support RA 10173 compliance and are used across multiple modules. They
are architecturally part of `esmis_security` or a dedicated `esmis_consent` module
at Layer 1.

### `esmis.consent`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` (or `esmis_consent`) |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [Consent Management](../principles/consent-management.md), [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md) |

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `purpose` | Selection | `consent_enrollment`, `consent_ched_reporting`, `consent_financial_aid`, `consent_emergency_contact`, `consent_alumni_tracking`, `consent_research`, `consent_lms_sync`, `consent_payment`, `consent_philsys` |
| `lawful_basis` | Selection | `consent`, `contract`, `legal_obligation`, `vital_interest`, `legitimate_interest` |
| `date_given` | Datetime | When recorded |
| `date_withdrawn` | Datetime | When withdrawn (False if active) |
| `evidence_type` | Selection | `electronic`, `written`, `verbal` |
| `evidence_ref` | Many2one (`ir.attachment`) | Supporting document |
| `captured_by` | Many2one (`res.users`) | Recording user |
| `ip_address` | Char | IP at capture time |
| `form_version` | Char | Consent form version |
| `is_active` | Boolean (computed) | Active if not withdrawn |
| `parent_consent` | Boolean | True for parent/guardian consent |

**Key constraint:** Unique `student_id` + `purpose` among active records.

### `esmis.consent.scope`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` (or `esmis_consent`) |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [ADR-004](decisions/ADR-004-api-v2-architecture.md), [ADR-009](decisions/ADR-009-api-v2-application-level-authorization.md) |

| Field | Type | Description |
|-------|------|-------------|
| `consent_id` | Many2one (`esmis.consent`) | Parent consent |
| `resource_type` | Selection | Resource type |
| `fields_allowed` | Many2many (`ir.model.fields`) | Allowed fields |
| `purpose` | Selection | Processing purpose |
| `third_party_id` | Many2one (`res.partner`) | Authorized party |
| `valid_until` | Date | Expiry date |

### `esmis.data.breach`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md), [Breach Response Guide](../guides/breach-response-guide.md) |

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Internal reference |
| `discovery_date` | Datetime | When breach was confirmed |
| `npc_deadline` | Datetime (computed) | discovery_date + 72 hours |
| `description` | Text | Non-PII description |
| `affected_count` | Integer | Number of data subjects |
| `severity` | Selection | `critical`, `high`, `medium`, `low` |
| `npc_notified` | Boolean | Whether NPC was notified |
| `npc_notification_date` | Datetime | When NPC was notified |
| `npc_filing_reference` | Char | PDBNF reference number |
| `dpo_id` | Many2one (`res.users`) | Assigned DPO |
| `subject_notification_datetime` | Datetime | When subjects were notified |
| `containment_log` | Text | Timestamped containment actions |
| `remediation_item_ids` | One2many | Remediation actions |
| `post_incident_report` | Many2one (`ir.attachment`) | Final report |
| `closed_datetime` | Datetime | When all remediation complete |
| `legal_hold` | Boolean | Legal hold flag |

### `esmis.data.subject.request` (DSAR)

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` (or `esmis_data_classification`) |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [Data Privacy and PII](../principles/data-privacy-and-pii.md), [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md) |

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Requesting student |
| `request_type` | Selection | `access`, `rectification`, `erasure`, `portability`, `objection` |
| `receipt_date` | Date | When received |
| `deadline` | Date (computed) | receipt_date + 30 working days |
| `state` | Selection | `received`, `processing`, `completed`, `escalated` |
| `dpo_id` | Many2one (`res.users`) | Assigned DPO |

### `esmis.disposal.review`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [Data Retention and Disposal](../principles/data-retention-and-disposal.md) |

| Field | Type | Description |
|-------|------|-------------|
| `state` | Selection | `draft`, `approved`, `executed`, `complete` |
| `data_type` | Char | Category of data |
| `record_count` | Integer | Number of records |
| `proposed_action` | Selection | `anonymize`, `delete`, `archive` |
| `dpo_approved_by` | Many2one (`res.users`) | Approving DPO |
| `nap_approval_reference` | Char | NAP approval (public HEIs only) |
| `execution_date` | Datetime | When disposal was executed |

### `esmis.retention.schedule`

| Attribute | Value |
|-----------|-------|
| Module | `esmis_security` |
| Layer | 1 (Foundation) |
| Status | Planned |
| Governed by | [Data Retention and Disposal](../principles/data-retention-and-disposal.md) |

| Field | Type | Description |
|-------|------|-------------|
| `data_type` | Char | Category label |
| `model_id` | Many2one (`ir.model`) | Target model |
| `retention_period_years` | Integer | Years to retain |
| `action_at_expiry` | Selection | `anonymize`, `delete`, `archive` |
| `legal_basis` | Char | Governing law/regulation |
| `is_permanent` | Boolean | Never dispose |

---

## DMS Models (Planned)

These belong to `esmis_dms` at Layer 3, governed by [ADR-007](decisions/ADR-007-dms-security-and-storage-enhancements.md).

### `esmis.dms.file`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | File name |
| `content` | Binary | File content |
| `checksum` | Char | SHA-512 checksum |
| `mimetype` | Char | MIME type |
| `size` | Integer | File size in bytes |
| `directory_id` | Many2one (`esmis.dms.directory`) | Parent directory |
| `category_id` | Many2one (`esmis.dms.category`) | Category |

### `esmis.dms.directory`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Directory name |
| `parent_id` | Many2one (`esmis.dms.directory`) | Parent directory |
| `file_ids` | One2many (`esmis.dms.file`) | Files |

### `esmis.dms.category`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Category name |
| `file_ids` | One2many (`esmis.dms.file`) | Files in category |

---

## Attendance Model (Planned)

Belongs to `esmis_attendance` or `esmis_enrollment`, governed by [Student Data Lifecycle](../principles/student-data-lifecycle.md).

### `esmis.attendance.log`

| Status | Planned |
|--------|---------|

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | Many2one (`esmis.student`) | Student |
| `section_id` | Many2one (`esmis.section`) | Section |
| `session_date` | Date | Class session date |
| `status` | Selection | `present`, `absent`, `late`, `excused` |

---

## Governance Index

Quick reference for which document governs which model groups.

| Document | Models Governed |
|----------|----------------|
| [Student Data Lifecycle](../principles/student-data-lifecycle.md) | `esmis.applicant`, `esmis.student`, `esmis.enrollment`, `esmis.grade`, `esmis.graduation`, `esmis.clearance`, `esmis.tracer.response`, `esmis.document`, `esmis.document.request` |
| [Enrollment Workflows](../principles/enrollment-workflows.md) | `esmis.enrollment`, `esmis.enrollment.line`, `esmis.enrollment.change`, `esmis.enrollment.hold`, `esmis.enrollment.window`, `esmis.cross.enrollment.permit`, `esmis.financial.assessment`, `esmis.fee.schedule` |
| [Grading and Academic Standing](../principles/grading-and-academic-standing.md) | `esmis.grading.system`, `esmis.grading.scale`, `esmis.grade`, `esmis.grade.component`, `esmis.grade.component.template`, `esmis.grade.change`, `esmis.standing.policy`, `esmis.latin.honors.config` |
| [Financial Aid Patterns](../principles/financial-aid-patterns.md) | `esmis.financial.aid.program`, `esmis.financial.aid.award`, `esmis.financial.aid.application` |
| [Consent Management](../principles/consent-management.md) | `esmis.consent`, `esmis.consent.scope` |
| [Data Privacy and PII](../principles/data-privacy-and-pii.md) | `esmis.identifier`, `esmis.pii.access.log`, `esmis.data.subject.request`, `esmis.health.record`, `esmis.counseling.note`, `esmis.disciplinary.record` |
| [Data Retention and Disposal](../principles/data-retention-and-disposal.md) | `esmis.disposal.review`, `esmis.retention.schedule` |
| [Multi-Campus Architecture](../principles/multi-campus-architecture.md) | `esmis.credit.transfer`, `esmis.faculty.load`, `esmis.college` |
| [Audit & Compliance](../principles/audit-compliance.md) | `esmis.audit.rule`, `esmis.audit.log`, `esmis.pii.access.log` |
| [Approval Workflows](../principles/approval-workflows.md) | `esmis.approval.mixin`, `esmis.approval.definition` |
| [API Design](../principles/api-design.md) | `esmis.api.client`, `esmis.api.client.scope`, `esmis.api.audit.log`, `esmis.api.extension`, `esmis.api.path` |
| [Government Integrations](../principles/government-integrations.md) | `esmis.philsys.verification`, `esmis.lms.platform`, `esmis.payment`, `esmis.payment.event`, `esmis.hemis.export.wizard` |
| [ADR-003](decisions/ADR-003-terminology-system.md) | `esmis.vocabulary`, `esmis.vocabulary.code`, `esmis.vocabulary.mapping` |
| [ADR-005](decisions/ADR-005-data-classification-system.md) | `esmis.pii.aware` mixin, classification field metadata |
| [ADR-007](decisions/ADR-007-dms-security-and-storage-enhancements.md) | `esmis.dms.file`, `esmis.dms.directory`, `esmis.dms.category` |
| [ADR-012](decisions/ADR-012-student-data-privacy-ra10173.md) | `esmis.consent`, `esmis.data.breach`, `esmis.data.subject.request` |
| [ADR-013](decisions/ADR-013-financial-aid-modeling.md) | `esmis.financial.aid.program`, `esmis.financial.aid.award` |
| [ADR-014](decisions/ADR-014-lms-integration-standards.md) | `esmis.lms.platform`, `esmis.section.learning_modality` |
| [ADR-015](decisions/ADR-015-grading-system-flexibility.md) | `esmis.grading.system`, `esmis.grading.scale`, `esmis.grade.change`, `esmis.latin.honors.config` |
| [Breach Response Guide](../guides/breach-response-guide.md) | `esmis.data.breach` (referred to as `esmis.breach.record` in guide) |
