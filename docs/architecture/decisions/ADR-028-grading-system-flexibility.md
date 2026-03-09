# ADR-028: Grading System Flexibility

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

CHED does not prescribe a single grading system for Philippine HEIs. Institutions use varied scales:

- **1.0–5.0 numeric scale** — most common in SUCs and many private universities; 1.0 is the highest mark, 5.0 (or 3.0 in some institutions) is failing; passing threshold is typically 3.0
- **Percentage-based scale** — common in some professional programs; passing threshold is typically 70% or 75%
- **4.0 GPA scale** — used in institutions modeled on the American system; 1.0 or below is failing

Beyond scale direction and passing threshold, institutions also differ on:

- **GWA computation rules:** which grades to include (all terms, last N terms, specific programs only), how to handle repeated subjects, whether INC grades are included before resolution
- **Latin honors thresholds:** Summa Cum Laude, Magna Cum Laude, Cum Laude GWA cutoffs vary by institution and sometimes by college within an institution
- **INC (Incomplete) grade handling:** resolution deadlines, automatic conversion to failing grade if unresolved, whether INC grades affect GWA computation during the incomplete period
- **Grade change workflow:** some institutions require dean approval only; others require registrar countersignature

Hardcoding any of these rules would make the system unusable for a significant portion of Philippine HEIs without code modifications.

### Problems to Solve

1. Grading scale configuration requires code changes under the current design
2. GWA computation logic is not inspectable or configurable by registrar staff
3. INC grade deadlines are tracked manually and resolution is not automated
4. Grade change audit trail is insufficient for CHED audit requirements
5. Latin honors computation is not institution-configurable

## Decision

### 1. Configurable Grading System Model

`esmis.grading.system` defines a complete grading configuration:

- `name` — display name (e.g., "Standard Philippine 1.0–5.0 Scale")
- `scale_direction` — selection: `ascending_is_worse` (1.0 = best, 5.0 = worst) or `ascending_is_better` (4.0 = best, 0.0 = worst)
- `passing_threshold` — numeric value on the defined scale
- `gpa_equivalent_enabled` — boolean, whether to map each scale entry to a 4.0 GPA equivalent for transfer/honors computation

### 2. Grade Scale Entries

`esmis.grading.scale` stores one row per valid grade value:

| Field | Purpose |
|-------|---------|
| `grading_system_id` | Parent system |
| `numeric_value` | The grade value (e.g., 1.25, 75.0) |
| `label` | Display label (e.g., "Excellent", "Passed") |
| `gpa_equivalent` | 4.0-scale equivalent for cross-system computation |
| `is_passing` | Boolean |
| `is_incomplete` | Boolean — marks the INC grade entry |
| `is_dropped` | Boolean — marks officially dropped (W/WP/WF) entries |

### 3. Component-Based Grading Templates

`esmis.grade.component.template` allows per-course (or per-program) grading breakdowns:

- Midterm weight, final weight, quiz weight, attendance weight, etc.
- Weights must sum to 100%; a validation constraint enforces this
- Templates are assigned to course offerings; faculty enter component scores which are aggregated by the system

### 4. GWA Computation Rules

GWA is computed as: `Σ(grade × units) / Σ(units)`, where:

- The grade value used is the numeric value from `esmis.grading.scale`
- For `ascending_is_worse` scales, the numeric value is inverted to a GPA equivalent before averaging (if `gpa_equivalent_enabled` is true)
- Configurable inclusion rules on `esmis.grading.system`: whether to include INC grades (as zero/fail), whether to include grades from repeated subjects (first attempt, last attempt, or best attempt), and whether transfer credits count

### 5. INC Grade Resolution Workflow

`esmis.grade` records with `is_incomplete = True` carry a `resolution_deadline` date. A scheduled action runs daily and converts unresolved INC grades to the institution-configured failing grade value after the deadline passes. The conversion is logged in the audit trail with reason `auto_resolved_incomplete`.

### 6. Grade Change Workflow

The grade change approval chain is: faculty submits change request → dean approves → registrar locks. Each step creates a new `esmis.grade.change` record referencing the original grade, preserving the full history. The original `esmis.grade` record is not mutated until the registrar locks the change.

### 7. Latin Honors Configuration

`esmis.latin.honors.config` stores institution-level thresholds:

- `honors_level` — selection: `summa_cum_laude`, `magna_cum_laude`, `cum_laude`
- `min_gwa` / `max_gwa` — GWA range qualifying for this level
- `min_units_completed` — minimum units required for eligibility
- `no_failing_grade_required` — boolean

Honors eligibility is computed at graduation clearance, not continuously.

### 8. Philippine-Specific Defaults in a Dedicated Module

Default Philippine grading scales (standard 1.0–5.0, percentage, DOST-SEI scale), default INC resolution deadlines, and standard Latin honors thresholds are provided as data files in `esmis_grading_ph`. The base `esmis_grading` module contains all models and workflows without any hardcoded Philippine values.

## Consequences

### Positive

- Any Philippine HEI grading system can be configured without code changes
- GWA computation is data-driven and therefore testable, auditable, and explainable to registrar staff
- INC deadline automation eliminates a significant source of manual error
- Grade change history is preserved as immutable records, satisfying CHED audit requirements

### Negative

- Institutions with multiple grading systems per college or program must maintain multiple `esmis.grading.system` records and assign them correctly to course offerings — misconfiguration will produce incorrect GWAs
- Component-based grading adds UI complexity for faculty; training is required
- INC auto-conversion is irreversible without a grade change workflow; institutions must configure deadlines correctly before go-live

## Implementation Notes

- Grade state machine on `esmis.grade`: `draft` → `submitted` → `approved` → `locked`. Locked grades cannot be edited; changes go through `esmis.grade.change`.
- `esmis.grade.change` stores: `original_grade_id`, `requested_by`, `requested_at`, `dean_approved_by`, `dean_approved_at`, `registrar_locked_by`, `registrar_locked_at`, `reason`, `new_grade_value`.
- Philippine grading scale data files in `esmis_grading_ph/data/grading_scales.xml`.
- GWA computation is implemented as a method on `esmis.student.program` (the enrollment record), not on `esmis.grade`, to allow recomputation across terms.
- The `is_incomplete` and `is_dropped` flags on `esmis.grading.scale` drive UI behavior (e.g., INC grades show a resolution deadline widget in the form view).
- Latin honors computation is triggered by the graduation clearance process, not by a cron job, to avoid premature honors assignment.

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09
