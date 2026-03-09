# Enrollment Workflows

Standardized patterns for the full enrollment lifecycle: from initial application through active enrollment, add/drop, cross-enrollment, and staggered scheduling.

## Admission Pipeline

```
[Application] → [Evaluation] → [Decision] → [Offer] → [Acceptance] → [Pre-Enrollment]
                                    ↓            ↓
                               [Waitlist]    [Deny]
                                    ↓
                            [Auto-Admitted on vacancy]
```

| Stage | Description |
|-------|-------------|
| Application | Applicant submits documents and application form |
| Evaluation | Admissions staff reviews credentials, entrance exam scores, and program quotas |
| Decision | Admit, waitlist, or deny; decision recorded with reason |
| Offer | Admission offer issued with deadline for acceptance |
| Acceptance | Applicant confirms acceptance and pays reservation fee (if applicable) |
| Conditional | Applicant admitted conditionally; conditions tracked and cleared before enrollment |
| Pre-Enrollment | Admitted student begins the enrollment process for their first term |

Waitlisted applicants are ranked. When a vacancy opens, the top-ranked waitlisted applicant is automatically promoted to "Offer" state, and a notification is sent.

---

## Pre-Enrollment

Before a student may proceed to section selection, the following gates must be cleared:

1. **Curriculum checklist review** — confirm the student is following the correct curriculum version and that all prior courses are properly credited or transferred
2. **Prerequisite validation** — identify courses the student is eligible to take based on prior grades (see Validation Steps below)
3. **Financial clearance** — confirm no outstanding balance from a prior term that would block enrollment
4. **Advising** — faculty adviser signs off on the proposed course load (may be waived for returning students with no flags)

Each gate is implemented as a hook method so campus-specific logic can be injected without modifying the core flow.

---

## Enrollment State Machine

```
[Cart] → [Validated] → [Assessed] → [Paid] → [Enrolled]
             ↓              ↓            ↓
           [Hold]      [Cancelled]  [Waitlisted → Auto-Enrolled]
```

| State | Description |
|-------|-------------|
| `cart` | Student is selecting courses; no validation has run |
| `validated` | All validation hooks passed; load and schedule confirmed |
| `hold` | One or more validation hooks blocked progression; reason recorded |
| `assessed` | Tuition and fees have been computed and posted to the student ledger |
| `cancelled` | Student or registrar cancelled the enrollment before payment |
| `paid` | Payment verified; enrollment pending final confirmation |
| `waitlisted` | Student is on the waitlist for one or more sections at capacity |
| `enrolled` | Enrollment is final; student appears on class lists |

A student in `waitlisted` state is auto-enrolled when a slot opens in all waitlisted sections. If the window closes before a slot opens, the enrollment moves to `cancelled` unless the student takes manual action.

---

## Validation Steps

Each step is a discrete hook method. Override only the hook you need; do not modify the orchestration loop.

```python
def _run_validation_hooks(self):
    self._check_prerequisites()
    self._check_academic_standing()
    self._check_load_limits()
    self._check_schedule_conflicts()
    self._check_section_capacity()
    self._check_enrollment_holds()
```

### 1. Prerequisite Check (`_check_prerequisites`)

For each course in the cart, verify that all prerequisite courses have been completed with a passing grade. Concurrent enrollment (co-requisites) is checked separately.

- Uses the student's academic history (`esmis.student.course.history`)
- Raises a validation error listing all unmet prerequisites rather than failing on the first one
- Transfer credits and advanced standing must be formally posted before this check runs

### 2. Academic Standing Check (`_check_academic_standing`)

- Verify the student is not on academic probation or disqualification hold
- Probation students may enroll but with a reduced maximum load (configured per program)
- Disqualified students cannot proceed; the enrollment moves to `hold`

### 3. Load Check (`_check_load_limits`)

- Minimum units: student must meet the minimum load for their scholarship or financial aid program
- Maximum units: cannot exceed the program-defined maximum (e.g., 21 units for regular students, 24 for graduating students with dean's approval)
- Overload requests require an explicit approval record before this check will pass

### 4. Schedule Conflict Check (`_check_schedule_conflicts`)

- No two sections in the cart may overlap on day and time
- Includes checking against sections the student is already formally enrolled in (e.g., from a prior add/drop)
- Reports all conflicts, not just the first one found

### 5. Section Capacity Check (`_check_section_capacity`)

- If a section is full, the course moves to `waitlisted` status in the student's cart rather than blocking the entire enrollment
- Section slots are reserved (not confirmed) at validation time; confirmation happens at payment
- Reserved slots expire if payment is not completed within the enrollment window

### 6. Enrollment Hold Check (`_check_enrollment_holds`)

Holds that block enrollment:

| Hold Type | Source |
|-----------|--------|
| Financial hold | Outstanding balance beyond the tolerance threshold |
| Disciplinary hold | Active disciplinary case |
| Library hold | Unreturned materials or unpaid fines |
| Registrar hold | Missing documents (e.g., birth certificate, transfer credentials) |

Each hold type is a record on `esmis.enrollment.hold`. The check reads all active holds for the student and, if any are present, moves the enrollment to `hold` state with the hold list attached.

### 7. Financial Assessment (`_compute_assessment`)

- Runs after all enrollment holds are cleared
- Computes tuition based on the number of units and program rate
- Applies miscellaneous fees (lab fees, ID, medical, etc.) based on the student's year level and courses
- Applies financial aid (see [Financial Aid Patterns](financial-aid-patterns.md)) in the defined stacking order
- Posts the net amount payable to the student's ledger

### 8. Payment Verification (`_verify_payment`)

- Checks the student's ledger for a payment matching (or exceeding) the assessed amount for the current term
- Accepts partial payment if the program allows installment enrollment
- On success, transitions the enrollment to `paid`; reserved section slots are confirmed

---

## Add/Drop Period

### Deadline Enforcement

- The add/drop window is a configurable date range per academic term.
- After the deadline, modifications require a petition approved by the dean and registrar.
- The system hard-blocks saves outside the window unless the user holds the `esmis_enrollment.group_registrar_officer` group.

### Financial Implications

- Dropped courses within the first week: full refund of tuition for those units.
- Dropped courses after the first week but before the midpoint: pro-rated refund per the institution's schedule of refunds.
- Dropped courses after the midpoint: no refund; units counted against the student's load history.
- The refund amount is computed at drop time and posted to the student's ledger immediately; the actual cash refund follows the finance office's disbursement schedule.

### Section Availability

- When a student drops a course, the confirmed slot is released back to the section immediately.
- The next student on the section's waitlist is notified automatically via mail activity.

---

## Cross-Enrollment

Cross-enrollment allows a student enrolled at one campus or program to take sections offered by another campus or program in the same institution.

### Rules

1. The home campus registrar must issue a cross-enrollment permit before the student can be added to a host campus section.
2. The host campus section must have available capacity.
3. Grades earned at the host campus are transmitted to the home campus registrar at the end of term.
4. Tuition for cross-enrolled units is charged by the home campus unless a memorandum of agreement specifies otherwise.

### Implementation

- Cross-enrollment permits are stored as `esmis.cross.enrollment.permit` records linked to the student and the target section.
- The section capacity check recognizes cross-enrollment students and validates against the permit record.
- The grade transmission step is triggered by the host campus grading workflow and creates a pending grade import on the home campus.

---

## Staggered Enrollment

Enrollment windows are opened in batches to prevent system overload and ensure priority access for students with the greatest need.

### Default Priority Order

1. Students with disabilities (PWD) and solo parents — any year level
2. Graduating students (final year, within 12 units of completion)
3. Fourth-year students
4. Third-year students
5. Second-year students
6. First-year students (new freshmen and transferees)

### Enrollment Windows

Each batch has a start datetime and an end datetime stored on `esmis.enrollment.window`. A student whose batch window has not yet opened sees a read-only cart with a countdown. A student whose window has closed can no longer modify their enrollment without a registrar override.

### Configuration

Windows are defined per academic term and per campus. The registrar officer can extend or reopen a window without a code change.

---

## Testing

### Unit Tests — Validation Steps

Each validation hook must have independent tests:

- Prerequisite check: student with a missing prerequisite is blocked; student with a completed prerequisite passes.
- Load check: student attempting to exceed the maximum units is blocked; overload with a valid approval record passes.
- Schedule conflict check: two overlapping sections are detected; non-overlapping sections pass.
- Section capacity check: enrolling when a section is full places the course in `waitlisted` state.
- Hold check: a student with an active financial hold cannot proceed; a cleared hold does not block enrollment.

### Integration Tests — Complete Workflow

- Run a student through the full cart → validated → assessed → paid → enrolled path.
- Verify that the student appears on the class list after enrollment is confirmed.
- Verify that section slot counts are decremented correctly at each stage (reserved at validation, confirmed at payment).

### Add/Drop Tests

- Verify that a drop within the refund window posts the correct refund amount to the ledger.
- Verify that a drop after the deadline is blocked for a student without the registrar role.
- Verify that the released slot is offered to the waitlisted student.

### Surge Handling

- Simulate concurrent enrollment requests for the last available slot in a section; verify that exactly one student is enrolled and the rest are waitlisted.
- Use database-level locking (SELECT FOR UPDATE) on the section slot count to prevent double-booking.

---

**See also:** [Financial Aid Patterns](financial-aid-patterns.md), [Approval Workflows](approval-workflows.md), [Performance & Scalability](performance-scalability.md), [Multi-Campus Architecture](multi-campus-architecture.md)
