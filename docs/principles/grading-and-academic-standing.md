# Grading and Academic Standing Principles

Standards for grading systems, GWA computation, academic standing determination, and
related workflows in eSMIS — the Student Management Information System for Philippine
higher education institutions (HEIs).

> **Scope:** Philippine HEIs use varied grading systems. This document covers the
> configurable grading architecture defined in ADR-028, the rules that govern GWA
> and academic standing computation, and the workflows for INC resolution, grade
> changes, and Latin honors. Hardcoded institutional values belong in
> `esmis_grading_ph`, not in this document.

---

## Table of Contents

1. [Philippine Grading Systems](#1-philippine-grading-systems)
2. [Configurable Grading Model](#2-configurable-grading-model)
3. [Component-Based Grading](#3-component-based-grading)
4. [GWA Computation](#4-gwa-computation)
5. [Academic Standing](#5-academic-standing)
6. [INC Grade Resolution](#6-inc-grade-resolution)
7. [Grade Change Workflow](#7-grade-change-workflow)
8. [Latin Honors](#8-latin-honors)
9. [Testing Requirements](#9-testing-requirements)

---

## 1. Philippine Grading Systems

CHED does not prescribe a single grading system. Three systems are in common use.

### System A: 1.0–5.0 Numeric Scale

The most common system in SUCs and many private universities.

| Grade | Label |
|-------|-------|
| 1.00 | Excellent |
| 1.25 | Excellent |
| 1.50 | Very Good |
| 1.75 | Very Good |
| 2.00 | Good |
| 2.25 | Good |
| 2.50 | Satisfactory |
| 2.75 | Satisfactory |
| 3.00 | Passing |
| 4.00 | Conditional |
| 5.00 | Failure |

Scale direction: `ascending_is_worse` — 1.0 is the highest (best) grade; 5.0 is the
lowest (worst). This is the opposite of the 4.0 GPA scale. Any comparison or sorting
logic must account for this direction.

Passing threshold is typically 3.00. The 4.00 Conditional grade indicates a student
must satisfy conditions set by the instructor; if conditions are not met, 4.00 converts
to 5.00 (Failure).

### System B: Percentage-Based Scale

Common in professional programs (Nursing, Engineering, Education). Grades are raw
percentages. Passing threshold is typically 70% or 75% depending on institutional
policy. Transmutation tables map raw scores to percentage equivalents; these tables
are stored as `esmis.grading.scale` entries.

### System C: 4.0 GPA Scale

Used by some internationally-aligned institutions. Scale direction: `ascending_is_better`
— 4.0 is the highest grade. Rare in purely Philippine HEIs but must be supported for
cross-institution transfer credit computation.

### Special Grade Marks

The following marks are not numeric grades and must not be included in GWA computation.

| Mark | Meaning | Effect |
|------|---------|--------|
| INC | Incomplete | Tracked with resolution deadline; converts to failing grade if unresolved |
| DRP | Dropped | Student officially dropped the course after the free drop period |
| W | Withdrawn | Student withdrew from the institution |
| NG | No Grade | Grade not yet submitted by faculty |
| FD | Forced Drop | Administrative drop (e.g., non-payment, disciplinary) |

Each mark is modeled as an `esmis.grading.scale` entry with the appropriate boolean
flag (`is_incomplete`, `is_dropped`) set. This allows the grading system to be
institution-specific while the business logic remains flag-driven.

---

## 2. Configurable Grading Model

Per ADR-028, grading rules are data-driven. No grading logic is hardcoded.

### `esmis.grading.system`

Defines a complete grading configuration for an institution or program.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Display name (e.g., "Standard Philippine 1.0–5.0 Scale") |
| `scale_direction` | Selection | `ascending_is_worse` or `ascending_is_better` |
| `passing_threshold` | Float | The lowest passing numeric value on this scale |
| `gpa_equivalent_enabled` | Boolean | Whether scale entries carry a 4.0 GPA equivalent |

### `esmis.grading.scale`

One row per valid grade value within a grading system.

| Field | Type | Description |
|-------|------|-------------|
| `grading_system_id` | Many2one | Parent `esmis.grading.system` |
| `numeric_value` | Float | The grade value (e.g., 1.25, 75.0, 3.5) |
| `label` | Char | Display label (e.g., "Excellent", "Passed") |
| `gpa_equivalent` | Float | 4.0-scale equivalent for cross-system computation |
| `is_passing` | Boolean | Whether this grade value counts as passing |
| `is_incomplete` | Boolean | Marks the INC grade entry |
| `is_dropped` | Boolean | Marks officially dropped entries (DRP, W, FD) |

### Philippine Defaults

Default Philippine grading scales — the standard 1.0–5.0 scale, the percentage-based
scale, and the DOST-SEI scale — are provided as XML data files in `esmis_grading_ph`.
The base `esmis_grading` module contains all models and workflows with no hardcoded
Philippine values. Institutions create custom scales through the UI without code changes.

> **Rule:** Never hardcode grade values, passing thresholds, or scale labels in Python
> or XML outside of `esmis_grading_ph` data files.

---

## 3. Component-Based Grading

Grades are computed from weighted components, not entered as a single value by default.

### `esmis.grade.component.template`

Defines a reusable grading breakdown for a course or program.

- Each template has one or more weighted lines (e.g., Midterm 30%, Final 30%,
  Quizzes 20%, Projects 20%).
- Component weights must sum to 100%. An `@api.constrains` validation enforces this.
- Templates are assigned to course sections (offerings), not to individual students.
- Faculty enter component scores per student; the system computes the final grade
  from the weighted components.
- Templates are configurable per department or program without code changes.

### Component Score Flow

```
Faculty enters component scores
        ↓
System computes weighted average
        ↓
Raw computed value mapped to nearest esmis.grading.scale entry
        ↓
Mapped grade stored on esmis.grade (draft state)
        ↓
Faculty submits → Dean approves → Registrar locks
```

> **Note:** The mapping from a computed numeric average to a scale entry uses the
> `esmis.grading.system` associated with the course section. Rounding rules (round
> up, round to nearest, truncate) are configured on `esmis.grading.system`.

---

## 4. GWA Computation

### Formula

```
GWA = Σ(grade_value × units) / Σ(units)
```

Where `grade_value` is the `numeric_value` from `esmis.grading.scale` for the
enrolled course.

For `ascending_is_worse` scales, if `gpa_equivalent_enabled` is true, the
`gpa_equivalent` value is used in the formula instead of `numeric_value` to produce
a meaningful weighted average.

### Inclusion Rules

Not all grade records are included in GWA computation. The following are always
excluded:

- Grades with `is_incomplete = True` (INC) — excluded until resolved or auto-converted
- Grades with `is_dropped = True` (DRP, W, FD)
- Grades in `NG` (No Grade) state

Additional inclusion rules are configured on `esmis.grading.system`:

| Rule | Options |
|------|---------|
| Repeated subject handling | First attempt / Last attempt / Best attempt |
| Transfer credits | Include / Exclude |
| INC before resolution | Exclude (default) / Include as failing |

### Term GWA vs Cumulative GWA

- **Term GWA**: computed from courses in a single enrollment term only.
- **Cumulative GWA**: computed across all terms from first enrollment to the current
  term, using the configured inclusion rules.

Both are stored as computed fields on `esmis.student.program` (the per-student,
per-program enrollment record). GWA is recomputed when any `esmis.grade` record
linked to the student's program changes state to `locked` or when a grade change
is applied by the registrar.

> **Implementation note:** GWA computation lives on `esmis.student.program`, not on
> `esmis.grade`, so it can aggregate across terms. Do not compute GWA on individual
> grade records.

---

## 5. Academic Standing

Academic standing is determined at the end of each term, after all grades for the
term are locked. It is not computed continuously during a term.

### Standing States

| State | Meaning |
|-------|---------|
| `good_standing` | GWA meets retention threshold; no policy violations |
| `dean_list` | GWA meets Dean's List threshold; all eligibility criteria satisfied |
| `probation` | GWA below retention threshold for one term |
| `warning` | GWA below retention threshold for two consecutive terms |
| `dismissed` | GWA below retention threshold for three consecutive terms, or fails hard retention policy |

### Determination Rules

Standing rules are configurable per program via `esmis.standing.policy`. Default
rules follow common Philippine HEI practice:

- **Good Standing**: Cumulative GWA at or above retention threshold; no failing grades
  in the current term; no unresolved INC grades older than one term.
- **Dean's List**: Cumulative GWA at or above Dean's List threshold (e.g., ≤ 1.75 on
  the 1.0–5.0 scale); no failing grades in any term; no INC grades in any term; full
  load in the evaluated term.
- **Probation**: Cumulative GWA drops below retention threshold at the end of one term.
- **Warning**: Cumulative GWA remains below retention threshold at the end of two
  consecutive terms.
- **Dismissed**: Cumulative GWA remains below retention threshold at the end of three
  consecutive terms, or any single-term condition specified in `esmis.standing.policy`
  is met (e.g., failing more than half of enrolled units).

> **Threshold direction:** For `ascending_is_worse` scales, "below threshold" means
> the GWA numeric value is *higher* than the threshold. Comparison logic must
> use `scale_direction` from `esmis.grading.system` to interpret the direction
> correctly.

### Consecutive Term Tracking

`esmis.student.program` stores a `consecutive_below_threshold_count` integer field
that is incremented when a term ends in probation or warning, and reset to zero when
the student returns to good standing. This counter drives the probation → warning →
dismissed transitions.

---

## 6. INC Grade Resolution

### Deadline Tracking

Every `esmis.grade` record with `is_incomplete = True` carries a `resolution_deadline`
date field. The deadline is set when the INC grade is locked, using the institutional
policy configured in `esmis.grading.system` (e.g., end of the next enrolled term,
or one calendar year from the INC date).

### Resolution Flow

```
Faculty submits completion grade (wizard)
        ↓
Registrar reviews and approves
        ↓
esmis.grade updated: is_incomplete = False, final grade value applied
        ↓
Audit trail entry created: resolution_date, resolved_by, completion_grade
        ↓
GWA recomputed for affected student
```

### Auto-Conversion

A scheduled action runs daily. For any `esmis.grade` with `is_incomplete = True`
and `resolution_deadline < today`, the grade is automatically converted to the
institution-configured failing grade value. The conversion creates an audit trail
entry with `reason = 'auto_resolved_incomplete'`.

> **Warning:** Auto-conversion is irreversible without initiating a grade change
> workflow. Institutions must configure `resolution_deadline` policies correctly
> before go-live and communicate them to faculty.

---

## 7. Grade Change Workflow

Grades in `locked` state cannot be edited directly. All changes go through
`esmis.grade.change`.

### States

```
request → dean_review → registrar_apply → locked
```

| State | Actor | Action |
|-------|-------|--------|
| `request` | Faculty | Submits change request with justification and proposed new grade |
| `dean_review` | Dean | Approves or rejects; rejection returns to `request` with comments |
| `registrar_apply` | Registrar | Applies approved change; original `esmis.grade` is updated and re-locked |
| `locked` | System | Change record is immutable; audit trail is complete |

### `esmis.grade.change` Fields

| Field | Description |
|-------|-------------|
| `original_grade_id` | Reference to the locked `esmis.grade` record |
| `requested_by` | Faculty who initiated the request |
| `requested_at` | Timestamp of submission |
| `old_grade_value` | Captured from `original_grade_id` at request time |
| `new_grade_value` | Proposed replacement grade value |
| `reason` | Mandatory justification text |
| `dean_approved_by` | Dean who approved |
| `dean_approved_at` | Timestamp of dean approval |
| `registrar_locked_by` | Registrar who applied and locked |
| `registrar_locked_at` | Timestamp of registrar lock |

The original `esmis.grade` record is not mutated until the registrar locks the change.
This preserves the original value throughout the approval process.

> **Audit requirement:** Every grade change must have a complete `esmis.grade.change`
> record. Direct writes to `esmis.grade.numeric_value` on locked grades are blocked
> by an ORM-level constraint.

---

## 8. Latin Honors

Latin honors eligibility is computed at graduation clearance, not continuously and
not by a cron job. Premature honors assignment is avoided by design.

### Honors Levels

| Level | Typical GWA Threshold (1.0–5.0 scale) |
|-------|---------------------------------------|
| Summa Cum Laude | ≤ 1.20 |
| Magna Cum Laude | ≤ 1.45 |
| Cum Laude | ≤ 1.75 |

Thresholds vary by institution and sometimes by college within an institution.
Actual thresholds are configured in `esmis.latin.honors.config`, not hardcoded.
The values above are examples only.

### `esmis.latin.honors.config`

| Field | Description |
|-------|-------------|
| `honors_level` | Selection: `summa_cum_laude`, `magna_cum_laude`, `cum_laude` |
| `min_gwa` / `max_gwa` | GWA range qualifying for this level (direction-aware) |
| `min_units_completed` | Minimum units that must be completed in residence |
| `no_failing_grade_required` | If true, any failing grade in any term disqualifies |

### Eligibility Criteria (per CMO No. 8 and typical institutional policy)

- All courses for the degree must have been taken in residence at the institution
  (transfer credits may disqualify depending on policy).
- No failing grade in any course throughout the program.
- No INC grade at any point in the program (resolved or unresolved).
- Must not have exceeded the maximum residency period.
- Cumulative GWA must fall within the configured threshold range.

Honors eligibility is evaluated by the graduation clearance process. The result is
stored on the graduation record, not on `esmis.student.program`, to avoid triggering
premature honors labels.

---

## 9. Testing Requirements

### GWA Computation

- Test GWA with a known dataset of grades and units; assert the exact numeric result.
- Test that INC, DRP, W, NG grades are excluded from the GWA denominator and numerator.
- Test repeated subject handling for all three configured modes (first, last, best).
- Test cumulative GWA vs term GWA produce different values when expected.
- Test that GWA recomputes correctly after a grade change is applied by the registrar.

### Academic Standing Transitions

- Test the full sequence: good standing → probation → warning → dismissed over
  three consecutive terms below threshold.
- Test that returning above threshold resets the consecutive counter and restores
  good standing.
- Test Dean's List eligibility: GWA meets threshold, no failing grades, no INC.
- Test Dean's List disqualification: GWA meets threshold but one INC present.

### INC Auto-Conversion

- Test that a scheduled action run after the deadline converts the INC grade to the
  configured failing value.
- Test that the audit trail entry has `reason = 'auto_resolved_incomplete'`.
- Test that a resolved INC before the deadline is not auto-converted.

### Grade Change Audit Trail

- Test that every field in `esmis.grade.change` is populated after the full workflow
  completes: `old_grade_value`, `new_grade_value`, `reason`, `dean_approved_by`,
  `dean_approved_at`, `registrar_locked_by`, `registrar_locked_at`.
- Test that a direct write to a locked `esmis.grade` record raises a constraint error.
- Test that rejection at the dean stage returns the request to `request` state without
  modifying the original grade.

### Latin Honors Computation

- Test that a student with cumulative GWA ≤ threshold and no failing grades is
  assigned the correct honors level.
- Test that a student with a single failing grade in any term is disqualified regardless
  of GWA.
- Test honors threshold boundaries: a student at exactly the threshold, one step
  above, and one step below.
- Test that honors are only assigned at graduation clearance, not earlier.

### Configurable Grading Scale

- Test that creating a new `esmis.grading.system` and `esmis.grading.scale` entries
  through the ORM (no code changes) produces correct GWA computation for grades using
  that system.
- Test that component weights that do not sum to 100% raise a `ValidationError`.

---

**Authoritative Sources:**

- ADR-028: [Grading System Flexibility](../architecture/decisions/ADR-028-grading-system-flexibility.md)
- `esmis_grading` module — models and workflows
- `esmis_grading_ph` module — Philippine default scales and thresholds

**See also:** [Audit & Compliance](audit-compliance.md), [Approval Workflows](approval-workflows.md), [Regulatory Compliance](regulatory-compliance.md)
