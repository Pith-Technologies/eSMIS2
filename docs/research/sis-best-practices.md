# Student Information System (SIS) — Best Practices & Industry Standards Research

> **Purpose:** Inform the architecture of a production-grade Student Management Information System (eSMIS) built on Odoo 19.
> **Date:** 2026-03-09

---

## Table of Contents

1. [Core Functional Modules](#1-core-functional-modules)
2. [Architecture Best Practices](#2-architecture-best-practices)
3. [Security Best Practices for Education](#3-security-best-practices-for-education)
4. [API Standards](#4-api-standards)
5. [Performance Considerations](#5-performance-considerations)
6. [UX Best Practices](#6-ux-best-practices-for-education-systems)
7. [Data Models](#7-data-models)
8. [Philippine-Specific Considerations](#8-philippine-specific-considerations)
9. [Mapping to Odoo 19 / eSMIS Architecture](#9-mapping-to-odoo-19--esmis-architecture)

---

## 1. Core Functional Modules

A comprehensive SIS covers the full student lifecycle: from prospect to applicant, student, graduate, and alumnus. Below are the functional modules organized by lifecycle phase.

### 1.1 Admissions and Enrollment Management

**Admissions Pipeline:**
- Application intake (online forms, document upload)
- Applicant evaluation and scoring (entrance exams, interviews, credential review)
- Admission decision workflow (admit, waitlist, deny) with approval chains
- Offer letter generation and acceptance tracking
- Conditional admission handling (e.g., "admitted pending English proficiency")
- Transfer student credit evaluation
- Reapplication and readmission flows

**Enrollment Management:**
- Pre-enrollment advising (curriculum checklist, prerequisite validation)
- Course/section selection with real-time slot availability
- Enrollment hold management (financial holds, academic holds, disciplinary holds)
- Add/drop/withdrawal with deadline enforcement and financial implications
- Cross-enrollment between programs or campuses
- Batch enrollment (block scheduling for cohort-based programs)
- Enrollment slot reservation with time-limited locks
- Waitlist management with automatic promotion when slots open

**Key Workflow States (Enrollment):**
```
[Application] → [Evaluation] → [Admitted] → [Confirmed] → [Enrolled]
                      ↓                          ↓
                 [Waitlisted]              [Deferred]
                      ↓
                  [Denied]
```

### 1.2 Student Records and Academic History

- Student demographic data (with PII classification — see Section 3)
- Contact information (student, parent/guardian, emergency contacts)
- Academic history across institutions (transfer credits)
- Enrollment history per term (courses taken, grades, units earned)
- Cumulative GPA / GWA computation
- Academic standing (good standing, probation, dismissal)
- Honors and awards tracking
- Leave of absence and retention tracking
- Student status lifecycle: active, LOA, dismissed, graduated, withdrawn
- Student photo management (ID photo, with privacy controls)

### 1.3 Curriculum and Program Management

**Program Structure:**
- Degree programs (BS, BA, MA, PhD, certificates, diplomas)
- Program versions with effective dates (curriculum versioning)
- Majors, minors, concentrations, specializations
- Required units per program (lecture units, lab units, total units)

**Curriculum Structure:**
- Curriculum year/version (e.g., "BSCS Curriculum 2024")
- Year-level and term-level course mapping
- Course prerequisites, co-requisites, and anti-requisites
- Elective groups (choose N of M courses)
- General education requirements vs. major requirements
- Thesis/capstone/OJT tracking
- Curriculum effectivity rules: which students follow which version

**Course Catalog:**
- Course code, title, description
- Credit units (lecture, lab, total)
- Course type (lecture, lab, lecture+lab, seminar, practicum, thesis)
- Department/college ownership
- Offering frequency (every semester, annual, as needed)
- Maximum and minimum enrollment per section

### 1.4 Class Scheduling and Room Management

- Section creation (course + instructor + room + time slot)
- Room/facility catalog with capacity, type (lecture hall, lab, gym), and equipment
- Conflict detection: instructor schedule conflicts, room double-booking, student schedule conflicts
- Time slot templates (MWF 8:00-9:00, TTh 10:30-12:00, etc.)
- Block scheduling for cohort programs
- Online/hybrid section support (virtual room assignments)
- Room utilization reports
- Faculty preference and load balancing

### 1.5 Grading and Assessment Management

**Grade Entry:**
- Faculty grade submission portal with deadline enforcement
- Component-based grading (midterm, final, quizzes, projects — configurable weights)
- Incomplete (INC) grade management with completion deadlines
- Grade change request workflow with dean/registrar approval
- Forced-drop (FD) and no-grade (NG) handling
- Grade locking after submission deadline

**Grade Computation:**
- Configurable grading systems per institution (see Section 8 for Philippine systems)
- Weighted average computation
- GPA / GWA calculation with configurable rules
- Dean's List / honors computation
- Grade equivalency tables (for transfers, international students)
- Pass/fail vs. numeric grade modes

**Assessment Integration:**
- Rubric-based assessment support
- Outcome-based education (OBE) alignment: mapping assessments to program outcomes
- Course-level and program-level outcome attainment tracking

### 1.6 Faculty Workload Management

- Teaching load assignment (units per semester)
- Overload and underload tracking
- Faculty qualification matching (who can teach which courses)
- Faculty availability and preference capture
- Part-time vs. full-time load computation
- Administrative load credits (department chair, committee work)
- Faculty schedule generation and conflict detection
- Substitute/replacement instructor tracking

### 1.7 Financial / Billing Management

**Tuition and Fee Assessment:**
- Fee schedule configuration per program, year level, student type (new, old, foreign)
- Per-unit vs. flat-rate tuition computation
- Miscellaneous fees (lab fees, library fees, athletic fees, ID fees)
- Assessment generation at enrollment
- Installment plan management (payment schedules)
- Late payment penalty computation

**Payment Processing:**
- Payment recording (cash, check, bank transfer, online payment)
- Payment allocation to specific charges
- Refund computation for withdrawals (pro-rated by date)
- Receipt generation
- Statement of account generation
- Balance inquiry (student portal)

**Integration with Enrollment:**
- Financial hold prevents enrollment
- Payment confirmation triggers enrollment completion
- Withdrawal triggers refund computation

### 1.8 Scholarship and Financial Aid

- Scholarship program definition (eligibility criteria, benefits, duration)
- Application and evaluation workflow
- GPA/GWA-based automatic qualification
- Scholarship disbursement tracking (tuition credit, stipend)
- Scholarship renewal and loss conditions
- Government scholarship integration (e.g., CHED scholarship, DOST-SEI, UniFAST/TES in the Philippines)
- Financial need assessment
- Scholarship utilization reporting

### 1.9 Student Services

**Counseling:**
- Counseling session scheduling and tracking
- Case management with confidentiality controls
- Referral tracking

**Health Services:**
- Medical/dental record management
- Clinic visit tracking
- Medical clearance for enrollment/graduation

**Discipline:**
- Incident reporting
- Disciplinary case management with hearing workflow
- Sanction tracking (warning, suspension, expulsion)
- Appeal process management
- Integration with enrollment holds

**Student Organizations:**
- Organization registration and accreditation
- Membership tracking
- Activity/event management

### 1.10 Alumni Management

- Automatic transition from graduated student to alumnus
- Alumni directory with privacy controls
- Employment tracking (where alumni work, what positions)
- Alumni event management
- Donation and fundraising tracking
- Alumni engagement scoring
- Mentorship program management
- Alumni verification and credential confirmation services

### 1.11 Document Management

**Transcript of Records (TOR):**
- Automated TOR generation from academic records
- Official vs. unofficial transcript distinction
- TOR request workflow with payment
- Digital signature/QR code for verification
- Template management (layout, logos, signatories)

**Other Documents:**
- Diploma/certificate generation
- Certification/verification letters (enrollment, good moral, units earned)
- Clearance processing (library, finance, registrar)
- Document request tracking with payment integration
- Digital credential issuance (Open Badges, CLR — see Section 4)

### 1.12 Reporting and Analytics

**Operational Reports:**
- Enrollment statistics (by program, college, year level, gender, etc.)
- Class size reports
- Grade distribution reports
- Retention and attrition rates
- Graduation rates and time-to-degree
- Faculty workload summaries
- Revenue reports (tuition collected vs. assessed)

**Regulatory Reports:**
- CHED reports (enrollment, graduation, program compliance)
- Accreditation data (PAASCU, AACCUP, etc.)
- Government scholarship utilization reports

**Decision-Maker Dashboards:**
- President/VP: institutional KPIs, enrollment trends, financial health
- Dean: college-level enrollment, faculty utilization, grade distributions
- Department Chair: section fill rates, faculty loads, prerequisite failure rates
- Registrar: enrollment progress, document request queue, graduation clearance

### 1.13 Student Portal / Self-Service

- View grades, schedule, academic history
- Enroll in courses (during enrollment period)
- View and pay balance
- Request documents (TOR, certifications)
- View curriculum checklist and progress
- Update personal information
- View announcements and notifications
- Evaluate faculty (student evaluation of teaching)

### 1.14 Parent/Guardian Portal

- View student grades and academic standing (with student consent or for minors)
- View financial balance and payment history
- Receive notifications (grades posted, academic standing changes)
- Communication channel with school
- Configurable access levels (full read, grades only, financial only)

---

## 2. Architecture Best Practices

### 2.1 Multi-Tenant vs. Single-Tenant for Multi-Campus

| Approach | When to Use | Trade-offs |
|----------|-------------|------------|
| **Single database, multi-company** | Campuses share policies, curriculum, and faculty | Simplest. Odoo's native multi-company fits well. Shared master data. |
| **Separate databases per campus** | Autonomous campuses with different policies | Full isolation. Higher maintenance. Cross-campus reporting requires aggregation layer. |
| **Hybrid** | Shared academic policies, separate financials | Use Odoo multi-company for academic data; separate chart of accounts per company. |

**Recommendation for Odoo 19:** Use Odoo's native multi-company architecture. Each campus is a `res.company`. Academic master data (curriculum, course catalog) is shared. Campus-specific data (sections, rooms, enrollments) is company-scoped via record rules. This aligns with the existing eSMIS `esmis_security` approach.

### 2.2 Modular Architecture

Follow the existing eSMIS layered architecture principle, adapted for SIS domains:

```
Layer 4: PORTALS & INTEGRATIONS
├── esmis_student_portal    (Student self-service)
├── esmis_parent_portal     (Parent/guardian access)
├── esmis_api               (External API facade)
└── esmis_lms_bridge        (LMS integration via LTI)

Layer 3: DOMAIN EXTENSIONS
├── esmis_reports           (Reporting and analytics)
├── esmis_alumni            (Alumni management)
├── esmis_financial_aid     (Scholarships and aid)
├── esmis_student_services  (Counseling, health, discipline)
└── esmis_documents         (TOR, diplomas, certificates)

Layer 2: DOMAIN CORE
├── esmis_admissions        (Application and admission)
├── esmis_enrollment        (Registration and enrollment)
├── esmis_curriculum        (Programs, curricula, courses)
├── esmis_scheduling        (Sections, rooms, timetable)
├── esmis_grading           (Grades, GPA/GWA, assessments)
├── esmis_faculty           (Teaching load, assignments)
└── esmis_billing           (Tuition, fees, payments)

Layer 1: FOUNDATION
├── esmis_student           (Student profile, extends res.partner)
├── esmis_academic_term     (Semesters, trimesters, academic years)
├── esmis_security          (RBAC, data classification, audit)
└── esmis_vocabulary        (Configurable code lists)

Layer 0: ODOO CORE
├── base (res.partner, res.company, res.users)
├── hr (faculty as employees)
├── account (financial transactions)
├── calendar (scheduling foundation)
└── documents (document storage)
```

**Key principles:**
- Each module has a single, clear responsibility
- Dependencies flow downward only
- Foundation modules are country-agnostic
- Country-specific logic lives in `esmis_*_ph` modules

### 2.3 Academic Year / Semester / Term Management

This is foundational — nearly every other module references it.

**Data Model:**

```
esmis.academic.year
├── name: "AY 2025-2026"
├── date_start: 2025-08-01
├── date_end: 2026-07-31
├── state: draft | active | closed
└── term_ids → [esmis.academic.term]

esmis.academic.term
├── academic_year_id → esmis.academic.year
├── name: "1st Semester"
├── term_type: semester | trimester | quarter | summer | midyear
├── sequence: 1
├── date_start: 2025-08-01
├── date_end: 2025-12-15
├── enrollment_start: 2025-07-15
├── enrollment_end: 2025-08-15
├── grade_submission_deadline: 2026-01-15
├── state: draft | enrollment | ongoing | grading | closed
└── company_id → res.company (campus-specific dates)
```

**Design considerations:**
- Different campuses may have different calendar dates for the same term
- Summer and midyear terms are optional
- Term state machine controls what operations are allowed (enrollment only during enrollment period, grade entry only during grading period)
- Historical terms must remain queryable but immutable

### 2.4 Curriculum Versioning

Curricula change over time. Students admitted under a specific curriculum version must be tracked against that version throughout their stay.

**Approach:**

```
esmis.program
├── code: "BSCS"
├── name: "Bachelor of Science in Computer Science"
├── degree_type: bachelor | master | doctorate | diploma | certificate
├── college_id → (department/college)
├── total_units: 160
└── curriculum_ids → [esmis.curriculum]

esmis.curriculum
├── program_id → esmis.program
├── version: "2024"
├── effective_year_id → esmis.academic.year
├── state: draft | active | phasing_out | archived
├── total_units: 160
└── line_ids → [esmis.curriculum.line]

esmis.curriculum.line
├── curriculum_id → esmis.curriculum
├── course_id → esmis.course
├── year_level: 1 | 2 | 3 | 4
├── term_sequence: 1 | 2 | 3 (which term of that year)
├── requirement_type: required | elective | ge_required | ge_elective
├── elective_group_id → esmis.elective.group (for "choose N of M")
├── prerequisite_ids → [esmis.curriculum.line] (M2M)
├── corequisite_ids → [esmis.curriculum.line] (M2M)
└── anti_requisite_ids → [esmis.curriculum.line] (M2M)
```

**Student-Curriculum Binding:**
- When a student is admitted, they are bound to the active curriculum version
- If curriculum changes, existing students stay on their original version unless they petition to shift
- A "curriculum shift" workflow allows students to move to a newer version with course mapping/equivalency
- The system must track which curriculum version each student follows

### 2.5 Grade Computation Flexibility

Different institutions, programs, and even individual courses may use different grading systems.

**Configurable Grading System:**

```
esmis.grading.system
├── name: "1.0-5.0 Scale (UP System)"
├── passing_grade: 3.0
├── highest_grade: 1.0
├── lowest_grade: 5.0
├── grade_direction: ascending_is_worse (1.0 = best, 5.0 = worst)
├── gpa_computation: weighted_average
└── scale_ids → [esmis.grading.scale]

esmis.grading.scale
├── system_id → esmis.grading.system
├── grade_value: 1.0
├── grade_label: "Excellent"
├── grade_point: 4.0 (for GPA equivalence)
├── is_passing: True
├── is_incomplete: False
├── is_dropped: False
└── numeric_range_min / numeric_range_max (optional, for transmutation)
```

**Component-Based Grading:**

```
esmis.grade.component.template
├── name: "Standard Lecture Course"
├── line_ids → [esmis.grade.component.line]

esmis.grade.component.line
├── template_id → esmis.grade.component.template
├── name: "Midterm Exam"
├── weight_percent: 30.0
├── component_type: midterm | final | quiz | project | attendance | other
```

This allows each course section to define its own grading breakdown while providing institutional templates.

### 2.6 Enrollment Workflow Engine

Enrollment is the most complex workflow in an SIS. It touches curriculum, scheduling, finance, and student records.

**State Machine:**

```
[Cart/Planning] → [Validated] → [Assessed] → [Payment] → [Enrolled]
       ↑               ↓             ↓            ↓
       └── [Add/Drop] [Hold]    [Cancelled]   [Waitlisted]
                                                    ↓
                                              [Auto-Enrolled]
```

**Validation Steps:**
1. **Prerequisite check** — Has the student passed all prerequisites?
2. **Standing check** — Is the student in good academic standing?
3. **Load check** — Is the student within min/max unit limits?
4. **Schedule conflict check** — Do selected sections overlap?
5. **Section capacity check** — Are there available slots?
6. **Hold check** — Does the student have any enrollment holds?
7. **Financial assessment** — Compute tuition and fees
8. **Payment verification** — Has the student paid (or been granted a payment plan)?

Each step should be implemented as a hook method so extensions can add institution-specific validations.

---

## 3. Security Best Practices for Education

### 3.1 Data Classification

Adopt a tiered data classification system for all student data:

| Classification | Examples | Access Level | Storage |
|---------------|----------|--------------|---------|
| **Public** | Program catalog, course descriptions, academic calendar | Anyone | Standard |
| **Internal** | Enrollment statistics, faculty assignments, room schedules | Authenticated staff | Standard |
| **Confidential** | Student grades, GPA, enrollment status, financial records | Role-based, need-to-know | Encrypted at rest |
| **Restricted** | SSN/national ID, medical records, disciplinary records, counseling notes | Named individuals only | Encrypted, access-logged |

This aligns with the existing eSMIS ADR-011 (Data Classification System) and ADR-012 (PII Encryption Strategy).

### 3.2 Role-Based Access Control (RBAC) for Education

**Core Roles:**

| Role | Access Scope | Typical Functions |
|------|-------------|-------------------|
| **System Administrator** | Full system | Configuration, user management, system maintenance |
| **Registrar** | All student academic records | Enrollment, grades, TOR, graduation, curriculum management |
| **Dean** | College-scoped students and faculty | Approve grade changes, view college reports, faculty load |
| **Department Chair** | Department-scoped | Course offerings, section management, faculty assignments |
| **Faculty** | Own sections only | Grade entry, class list, attendance |
| **Cashier/Finance** | Financial records | Payment processing, assessment, refunds |
| **Scholarship Officer** | Scholarship records | Award management, disbursement |
| **Student (Self)** | Own records only | View grades, enroll, pay, request documents |
| **Parent/Guardian** | Linked student only | View grades, balance (with consent) |
| **Counselor** | Assigned students | Counseling records (restricted) |
| **Clinic Staff** | Medical records | Health records (restricted) |

**Implementation in Odoo:**
- Map each role to an `ir.module.category` group
- Use record rules for row-level security (e.g., faculty sees only their sections)
- Use field-level access for sensitive fields (e.g., hide disciplinary records from most roles)
- Multi-level groups: `viewer < officer < manager < admin` within each functional area

### 3.3 FERPA-Aligned Principles

While FERPA is U.S. law, its principles are good practice globally:

1. **Legitimate Educational Interest** — Staff access student records only for job-related purposes
2. **Directory Information** — Define what is "public" (name, program, enrollment status) and allow students to opt out
3. **Consent for Disclosure** — Student must consent before records are shared with third parties (including parents of adult students)
4. **Right to Inspect** — Students can view their own records
5. **Right to Amend** — Students can request corrections to their records
6. **Annual Notification** — Students are informed of their privacy rights

### 3.4 Audit Trail Requirements

Every SIS must maintain comprehensive audit logs:

- **Who** accessed or modified what record
- **When** the access or modification occurred
- **What** was the previous value and new value (for modifications)
- **Why** — the business context (e.g., "grade change approved by Dean Garcia")

**Critical audit points:**
- Grade entry and modification
- Enrollment status changes
- Financial transactions
- Student record access (especially restricted data)
- Document generation (TOR, diploma)
- User role/permission changes
- Login/logout events

This aligns with the existing eSMIS ADR-020 (Unified API Audit Log).

### 3.5 Session Management for Shared Environments

Universities often have shared computer labs. Session security must account for this:

- **Aggressive session timeout** — Shorter idle timeout (10-15 minutes) for student portals
- **Single active session** — Prevent concurrent logins (or warn the user)
- **Forced logout on browser close** — Do not persist sessions across browser restarts for student accounts
- **Clear session on logout** — Remove all cached data, tokens, and cookies
- **Kiosk mode** — For self-service terminals, auto-logout after transaction completion

---

## 4. API Standards

### 4.1 Ed-Fi Data Standard

The Ed-Fi Unifying Data Model (UDM) is primarily K-12 focused but provides useful patterns for higher education:

**Core Domain Entities:**
- Student, Staff, Parent
- EducationOrganization (School, LocalEducationAgency)
- Course, CourseOffering, Section
- StudentSectionAssociation (enrollment in a section)
- Grade, ReportCard, StudentAcademicRecord
- Session (academic term), GradingPeriod
- Calendar, CalendarDate

**Key Design Patterns from Ed-Fi:**
- Resources are organized into domain aggregates
- Associations are first-class resources (not just foreign keys)
- Descriptors (configurable code lists) similar to eSMIS vocabulary
- Natural keys preferred over surrogate keys for API resources
- REST API following OpenAPI specification

**Relevance to eSMIS:** The entity structure and association patterns are directly applicable. The enrollment composite (bundling student + section + grades in one API call) is a performance pattern worth adopting.

### 4.2 IMS Global / 1EdTech Standards

| Standard | Purpose | Relevance |
|----------|---------|-----------|
| **LTI 1.3** (Learning Tools Interoperability) | Securely launch and integrate external learning tools within an LMS | Medium — for LMS integration |
| **OneRoster 1.2** | Exchange class roster data (students, teachers, sections) between systems | High — standardized roster sync |
| **Open Badges 3.0** | Issue, verify, and share digital credentials (badges) | Medium — for micro-credentials |
| **CLR 2.0** (Comprehensive Learner Record) | Bundle multiple credentials into a verifiable learner record | High — modernized transcript |
| **QTI 3.0** (Question and Test Interoperability) | Standardize assessment content exchange | Low — primarily for assessment tools |
| **Caliper Analytics 1.2** | Standardize learning event data for analytics | Medium — learning analytics |
| **EDU-API** | Unified API standard for student information | High — new unified SIS API standard |

**CLR 2.0 is particularly relevant** for eSMIS. It extends the traditional transcript concept using W3C Verifiable Credentials, enabling digital, machine-readable, and tamper-evident academic records. AACRAO recommends CLR as the standard for lifetime learning records.

### 4.3 SIF (Schools Interoperability Framework)

SIF is an older standard primarily for K-12 in Australia, US, and UK. It uses a publish/subscribe messaging model. Less relevant for a new higher education system, but worth noting for government reporting integrations.

### 4.4 RESTful API Best Practices for Education

Align with the existing eSMIS API design principles (ADR-010), with education-specific considerations:

- **Resource naming** — Use education domain language: `/students`, `/enrollments`, `/sections`, `/grades`
- **Filtering** — Support filtering by term, program, college, year level
- **Pagination** — Essential for large datasets (student records spanning years)
- **Versioning** — API versioning to support gradual client migration
- **Bulk operations** — Grade submission, enrollment processing
- **Webhooks** — Notify external systems of grade postings, enrollment changes
- **HATEOAS** — Include links to related resources (student → enrollments → grades)

### 4.5 Authentication and Authorization

| Standard | Use Case |
|----------|----------|
| **OAuth 2.0** | API authorization, delegated access for third-party apps |
| **OpenID Connect** | User authentication, SSO for student/faculty portals |
| **SAML 2.0** | Enterprise SSO (Shibboleth federation common in higher ed) |

**Recommendation:** Support OIDC as the primary authentication protocol for portals and APIs. Support SAML 2.0 for institutional federation (common in Philippine HEIs that participate in PREGINET/AARNET-style federations). Use OAuth 2.0 for API authorization with scoped tokens.

---

## 5. Performance Considerations

### 5.1 Enrollment Surge Handling

Enrollment periods create massive traffic spikes. A university with 20,000 students might see 80% of enrollment activity in a 3-day window.

**Strategies:**

| Strategy | Implementation |
|----------|---------------|
| **Virtual waiting room** | Queue system that controls admission rate to the enrollment page |
| **Slot reservation with TTL** | When a student selects a section, reserve the slot for 10-15 minutes; release if not confirmed |
| **Optimistic concurrency** | Allow enrollment to proceed, check conflicts at commit time |
| **Staggered enrollment** | Assign enrollment windows by year level or program (seniors first) |
| **Read replicas** | Serve schedule/availability queries from read replicas |
| **Pre-computed availability** | Cache section availability; update via events, not live queries |
| **Background assessment** | Compute tuition fees asynchronously after enrollment is confirmed |

**Odoo-specific:** Use `queue_job` for background processing of fee assessments and enrollment confirmations. Pre-compute section availability in a materialized/cached field rather than counting enrollments on every request.

### 5.2 Report Generation Optimization

- **Pre-aggregated tables** — Maintain summary tables for enrollment counts, grade distributions, retention rates; update via scheduled actions
- **Asynchronous report generation** — Large reports (TOR for all graduates, enrollment statistics) run in background; notify user when ready
- **Report caching** — Cache generated reports with invalidation on underlying data change
- **Pagination for on-screen reports** — Never load unbounded result sets in the UI

### 5.3 Large Dataset Handling

A university operating for 20+ years accumulates millions of records.

- **Partitioning strategy** — Partition enrollment and grade records by academic year
- **Archival policy** — Define when records move from "active" to "archived" (e.g., 5 years after graduation). Archived records remain queryable but are in cold storage.
- **Indexed queries** — Ensure proper indexing on: student_id, term_id, section_id, course_id, program_id, state
- **Denormalization for reads** — Store computed GWA on the student record; recompute on grade changes (not on every read)

### 5.4 Caching Strategies

| Data Type | Cache Strategy | TTL | Invalidation |
|-----------|---------------|-----|-------------|
| Course catalog | Cache-aside (Redis) | 24h | On catalog update |
| Section availability | Write-through | 30s during enrollment | On enrollment/drop |
| Curriculum structure | Cache-aside | 24h | On curriculum edit |
| Student GWA | Computed field (stored) | N/A | Recompute on grade change |
| Academic calendar | Cache-aside | 24h | On calendar edit |
| Report data | Pre-aggregated tables | 1h | Scheduled refresh |

---

## 6. UX Best Practices for Education Systems

### 6.1 Dashboard Design for Decision Makers

**President/VP Academic Affairs:**
- Institutional enrollment trend (multi-year line chart)
- Retention and graduation rates (funnel visualization)
- Financial health (revenue vs. budget, collection rate)
- Program-level performance comparison
- Alerts: programs with declining enrollment, at-risk accreditation

**Dean:**
- College enrollment by program and year level
- Faculty utilization (% of load filled)
- Grade distribution per course (identify unusual patterns)
- Student performance summary (average GWA, failure rates)
- Pending approvals (grade changes, overload requests)

**Registrar:**
- Enrollment progress (% of target per program)
- Document request queue and turnaround time
- Graduation clearance status
- Curriculum compliance issues

**Design principles for dashboards:**
- Lead with actionable metrics, not vanity numbers
- Comparative context (vs. last term, vs. target)
- Drill-down capability (institution → college → program → section)
- Alert/exception-based design (highlight anomalies)
- Export/print for board presentations

### 6.2 Mobile-First for Students

Students primarily interact via smartphones. The student portal must be mobile-native:

- **Responsive design** — Minimum target: 360px wide (standard Android)
- **Touch targets** — Minimum 44x44px for interactive elements
- **Progressive disclosure** — Show summary first, details on demand
- **Offline capability** — Cache schedule and grades for offline viewing
- **Push notifications** — Grade posted, enrollment confirmed, payment due
- **Thumb-zone design** — Critical actions reachable with one hand

**Key mobile flows:**
1. Check grades (most frequent)
2. View schedule
3. Check balance / pay
4. Enroll in courses (during enrollment period)
5. View announcements

### 6.3 Accessibility (WCAG 2.1 AA)

Education systems must be accessible to students with disabilities:

- **Color contrast** — 4.5:1 for normal text, 3:1 for large text
- **Keyboard navigation** — All functions accessible via keyboard
- **Screen reader support** — Proper ARIA labels, semantic HTML
- **Form labels** — Every input field has a visible, associated label
- **Error handling** — Clear, specific error messages near the relevant field
- **Focus management** — Logical tab order; visible focus indicators
- **Text resizing** — Content remains usable at 200% zoom
- **Alternative text** — All images have descriptive alt text
- **Captions** — Video content has captions

### 6.4 Multi-Language Support

- Support Filipino (Tagalog) and English at minimum
- Use Odoo's native `_()` translation mechanism
- Store translatable strings in vocabulary records (not hardcoded)
- Allow institutions to customize terminology (e.g., "College" vs. "School" vs. "Faculty")
- Date and number formatting per locale

---

## 7. Data Models

### 7.1 Core Entity Relationship Overview

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  res.partner │────→│  esmis.student       │────→│  esmis.enrollment│
│  (Person)    │     │  (Student Profile)   │     │  (Per Term)      │
└──────────────┘     └─────────────────────┘     └──────────────────┘
       │                      │                          │
       │                      ↓                          ↓
       │              ┌──────────────────┐     ┌─────────────────────┐
       │              │  esmis.program   │     │esmis.enrollment.line│
       │              │  (Degree Program)│     │(Enrolled Section)   │
       │              └──────────────────┘     └─────────────────────┘
       │                      │                          │
       ↓                      ↓                          ↓
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  hr.employee │     │ esmis.curriculum  │     │  esmis.section   │
│  (Faculty)   │     │ (Versioned)      │     │  (Class Section) │
└──────────────┘     └──────────────────┘     └──────────────────┘
       │                      │                    │         │
       ↓                      ↓                    ↓         ↓
┌──────────────┐     ┌──────────────────┐  ┌────────┐ ┌──────────┐
│esmis.teaching│     │esmis.curriculum  │  │esmis.  │ │esmis.    │
│.assignment   │     │.line             │  │course  │ │room      │
└──────────────┘     └──────────────────┘  └────────┘ └──────────┘
                             │
                             ↓
                     ┌──────────────────┐
                     │  esmis.grade     │
                     │  (Student Grade) │
                     └──────────────────┘
```

### 7.2 Key Entity Details

**Person / Student (extends res.partner):**

```
res.partner (Odoo base)
├── name, email, phone, address (standard Odoo fields)
├── is_student: Boolean
├── is_faculty: Boolean
├── is_parent: Boolean
└── identifier_ids → esmis.identifier (SSN, student ID, LRN)

esmis.student (links to res.partner)
├── partner_id → res.partner
├── student_number: Char (unique institutional ID)
├── program_id → esmis.program (current program)
├── curriculum_id → esmis.curriculum (bound version)
├── year_level: Integer
├── student_type: new | old | transferee | returnee | cross_enrollee
├── admission_date: Date
├── expected_graduation: Date
├── academic_standing: good | probation | warning | dismissed
├── cumulative_gwa: Float (stored/computed)
├── status: applicant | active | loa | dismissed | graduated | withdrawn
├── campus_id → res.company
└── enrollment_ids → [esmis.enrollment]
```

**Enrollment (per student per term):**

```
esmis.enrollment
├── student_id → esmis.student
├── term_id → esmis.academic.term
├── state: cart | validated | assessed | paid | enrolled | cancelled
├── total_units: Float (computed from lines)
├── total_assessment: Float (computed tuition + fees)
├── total_paid: Float
├── balance: Float (computed)
├── enrollment_date: Datetime
├── line_ids → [esmis.enrollment.line]
└── hold_ids → [esmis.enrollment.hold]

esmis.enrollment.line
├── enrollment_id → esmis.enrollment
├── section_id → esmis.section
├── state: enrolled | dropped | withdrawn | waitlisted
├── drop_date: Date
├── grade_id → esmis.grade (after grading)
└── is_credit: Boolean (counted toward GWA)
```

**Section:**

```
esmis.section
├── course_id → esmis.course
├── term_id → esmis.academic.term
├── section_code: Char ("CSCI101-A")
├── instructor_id → hr.employee
├── room_id → esmis.room
├── schedule_ids → [esmis.section.schedule] (day/time slots)
├── capacity: Integer
├── enrolled_count: Integer (stored/computed)
├── available_slots: Integer (computed)
├── state: draft | open | closed | cancelled
├── company_id → res.company (campus)
└── grading_template_id → esmis.grade.component.template
```

**Grade:**

```
esmis.grade
├── student_id → esmis.student
├── section_id → esmis.section
├── course_id → esmis.course (denormalized for history)
├── term_id → esmis.academic.term (denormalized)
├── grade_value: Float (1.0, 1.25, 1.5, ... 5.0)
├── grade_label: Char (computed from grading system)
├── is_passing: Boolean (computed)
├── is_incomplete: Boolean
├── completion_deadline: Date (for INC grades)
├── submitted_by: → res.users (faculty who submitted)
├── submitted_date: Datetime
├── approved_by: → res.users (for grade changes)
├── state: draft | submitted | approved | locked
├── units: Float (from course)
└── component_ids → [esmis.grade.component] (detailed breakdown)
```

### 7.3 Curriculum Tracking Across Versions

When a student needs to be tracked across curriculum versions:

```
esmis.curriculum.shift
├── student_id → esmis.student
├── from_curriculum_id → esmis.curriculum
├── to_curriculum_id → esmis.curriculum
├── shift_date: Date
├── approved_by: → res.users
├── mapping_ids → [esmis.curriculum.shift.mapping]

esmis.curriculum.shift.mapping
├── shift_id → esmis.curriculum.shift
├── old_course_id → esmis.course (completed course)
├── new_course_id → esmis.course (equivalent in new curriculum)
├── credit_status: credited | not_credited | partial
├── notes: Text
```

**Curriculum Checklist** (computed per student):

For each student, the system computes progress against their bound curriculum:
- Courses completed (with passing grade)
- Courses in progress (currently enrolled)
- Courses remaining
- Elective requirements fulfilled vs. remaining
- Total units earned vs. required
- Estimated remaining terms to graduation

---

## 8. Philippine-Specific Considerations

### 8.1 Academic Calendar Types

Philippine HEIs use varied academic calendars:

| Type | Structure | Examples |
|------|-----------|----------|
| **Semestral** | 2 semesters (Aug-Dec, Jan-May) + optional summer (Jun-Jul) | UP, UST, Ateneo |
| **Trimestral** | 3 terms of roughly equal length | DLSU, Mapua |
| **Semestral + Midyear** | 2 semesters + a short midyear term | Some state universities |
| **Quarter** | 4 terms per year | Rare in PH |

The `esmis_academic_term` model must support all these via the `term_type` field without hardcoding a specific calendar structure.

### 8.2 Philippine Grading Systems

There is no single national grading system. Each institution defines its own:

**System A: 1.0-5.0 Scale (Most Common)**

| Grade | Description | Equivalent |
|-------|-------------|------------|
| 1.00 | Excellent | A+ |
| 1.25 | — | A |
| 1.50 | Very Good | A- |
| 1.75 | — | B+ |
| 2.00 | Good | B |
| 2.25 | — | B- |
| 2.50 | Satisfactory | C+ |
| 2.75 | — | C |
| 3.00 | Passing | C- |
| 4.00 | Conditional | D |
| 5.00 | Failure | F |
| INC | Incomplete | — |
| DRP | Dropped | — |

Note: 1.0 is the highest, 5.0 is the lowest. The `grade_direction` field in `esmis.grading.system` handles this inversion.

**System B: Percentage-Based (70% passing)**

Some institutions use raw percentages with transmutation tables to convert to letter or numeric grades.

**System C: 4.0 Scale**

A few institutions (like some international schools) use the American 4.0 GPA scale.

**GWA Computation:**
General Weighted Average = Sum(grade * units) / Sum(units)
- Only courses with numeric grades are included (INC, DRP excluded)
- Some institutions exclude non-major courses from GWA
- Latin honors thresholds vary by institution (Summa Cum Laude, Magna Cum Laude, Cum Laude)

### 8.3 CHED Compliance Requirements

- **CMO (CHED Memoranda Orders)** define Policies, Standards, and Guidelines (PSG) per program
- Programs must map to **CHED program codes** for reporting
- **Outcome-Based Education (OBE)** alignment required
- **Philippine Qualifications Framework (PQF)** levels must be trackable
- Enrollment reporting to CHED (typically via HEMIS — Higher Education Management Information System)
- Faculty qualifications tracking (for CHED compliance: minimum of master's degree for college teaching)

### 8.4 Accreditation Support

| Body | Scope | Data Needs |
|------|-------|------------|
| **PAASCU** | Catholic/private HEIs | Faculty profile, student outcomes, library, labs |
| **AACCUP** | State universities (SUCs) | Similar to PAASCU, government compliance |
| **CHED** | All HEIs | Program compliance, faculty qualifications, enrollment data |
| **PRC** (Professional Regulation Commission) | Board exam programs | Board exam pass rates, curriculum alignment |

The SIS should be able to generate data extracts for accreditation visits.

### 8.5 Government Scholarship Integration

| Program | Agency | Integration Need |
|---------|--------|------------------|
| **TES** (Tertiary Education Subsidy) | UniFAST | Enrollment verification, grade reporting |
| **DOST-SEI Scholarship** | DOST | GWA reporting, course load verification |
| **CHED Scholarship** | CHED | Eligibility tracking, disbursement |

These typically require periodic data submission (not real-time API integration), so export/reporting capabilities suffice initially.

---

## 9. Mapping to Odoo 19 / eSMIS Architecture

### 9.1 Leveraging Existing Odoo Modules

| SIS Function | Odoo Module | Extension Approach |
|-------------|-------------|-------------------|
| Student/Faculty/Parent profiles | `res.partner` (base) | `_inherit` — add `is_student`, `is_faculty`, `is_parent` flags |
| Faculty HR records | `hr` | `_inherit` — add academic rank, specialization, teaching load |
| Financial transactions | `account` | `_inherit` — tuition assessment as invoices, payments as journal entries |
| Room/facility scheduling | `calendar` | `_inherit` or custom — section schedules as calendar events |
| Document storage | `documents` | `_inherit` — TOR, diplomas as document records |
| Notifications | `mail` | Use Odoo's built-in notification system for enrollment, grade alerts |

### 9.2 Custom eSMIS Models Required

These have no Odoo equivalent and must be built from scratch:

| Model | Purpose |
|-------|---------|
| `esmis.academic.year` | Academic year management |
| `esmis.academic.term` | Semester/trimester/term management |
| `esmis.program` | Degree program definition |
| `esmis.curriculum` | Versioned curriculum |
| `esmis.curriculum.line` | Course requirements within curriculum |
| `esmis.course` | Course catalog |
| `esmis.section` | Class section (course + instructor + room + time) |
| `esmis.section.schedule` | Day/time slots for a section |
| `esmis.room` | Room/facility catalog |
| `esmis.student` | Student academic profile |
| `esmis.enrollment` | Per-student per-term enrollment |
| `esmis.enrollment.line` | Individual course enrollment |
| `esmis.grade` | Student grade record |
| `esmis.grade.component` | Grade breakdown (midterm, final, etc.) |
| `esmis.grading.system` | Configurable grading scale |
| `esmis.teaching.assignment` | Faculty-section assignment with load |
| `esmis.document.request` | TOR/certificate request workflow |
| `esmis.scholarship` | Scholarship program and awards |

### 9.3 Country Module Pattern

Following the existing eSMIS country module pattern:

```
esmis_grading_ph       — Philippine grading systems (1.0-5.0, percentage-based)
esmis_curriculum_ph    — CHED program codes, OBE mappings, PQF levels
esmis_financial_aid_ph — TES, DOST-SEI, CHED scholarship types
esmis_reporting_ph     — CHED/HEMIS reporting formats
```

Each `_ph` module excludes other country variants and is installed via `esmis_starter_ph`.

### 9.4 Implementation Phase Suggestion

| Phase | Modules | Focus |
|-------|---------|-------|
| **1** | `esmis_academic_term`, `esmis_student`, `esmis_curriculum`, `esmis_course` | Foundation: academic calendar, student records, curriculum catalog |
| **2** | `esmis_scheduling`, `esmis_enrollment`, `esmis_grading` | Core operations: sections, enrollment workflow, grade management |
| **3** | `esmis_billing`, `esmis_financial_aid`, `esmis_faculty` | Financial: tuition, scholarships, faculty workload |
| **4** | `esmis_documents`, `esmis_student_services`, `esmis_alumni` | Extended: TOR generation, counseling, alumni |
| **5** | `esmis_student_portal`, `esmis_parent_portal`, `esmis_reports` | Portals and analytics |
| **6** | `esmis_api`, `esmis_lms_bridge` | External integrations |

---

## Sources

- [SIS Architecture and Features — Creatrix Campus](https://www.creatrixcampus.com/blog/top-20-student-information-system-features)
- [Student Lifecycle SIS Integration — Creatrix Campus](https://www.creatrixcampus.com/blog/student-information-system-integration)
- [SIS for Higher Ed — Ellucian](https://www.ellucian.com/blog/what-student-information-system-higher-ed)
- [Best Practices for SIS Implementation — Modern Campus](https://moderncampus.com/blog/best-practices-for-implementing-an-sis-platform.html)
- [Ed-Fi Data Standard — Ed-Fi Alliance](https://docs.ed-fi.org/reference/data-exchange/udm/getting-started/core-concepts/)
- [Ed-Fi ODS/API Platform — Ed-Fi Alliance](https://docs.ed-fi.org/reference/ods-api-platform/)
- [Ed-Fi Domains — Ed-Fi Alliance](https://docs.ed-fi.org/reference/data-exchange/udm/getting-started/ed-fi-domains/)
- [Education Data Standards — Edlink](https://ed.link/community/data-standardization-in-education/)
- [1EdTech Standards (9 Standards) — Edlink](https://ed.link/community/ims-global-standards/)
- [CLR 2.0 Standard — 1EdTech](https://www.imsglobal.org/spec/clr/v2p0)
- [Open Badges 3.0 — 1EdTech](https://www.imsglobal.org/spec/ob/v3p0/impl)
- [CLR FAQ — 1EdTech](https://www.imsglobal.org/clr/faq)
- [EDU-API — 1EdTech](https://www.imsglobal.org/edu-api)
- [eLearning Standards — Aristek Systems](https://aristeksystems.com/blog/elearning-standards-2022/)
- [FERPA Compliance Guide (2026) — UpGuard](https://www.upguard.com/blog/ferpa-compliance-guide)
- [FERPA Best Practices — CampusGuard](https://campusguard.com/post/10-essential-ferpa-best-practices-for-educational-institutions/)
- [FERPA Compliance Best Practices — Kiteworks](https://www.kiteworks.com/regulatory-compliance/ferpa-compliance-best-practices/)
- [Student Data Privacy Guide — Integrate.io](https://www.integrate.io/blog/the-complete-guide-to-student-data-privacy/)
- [PII for Education Records — Protecting Student Privacy (US DoE)](https://studentprivacy.ed.gov/content/personally-identifiable-information-education-records)
- [Philippine Grading System — Wikipedia](https://en.wikipedia.org/wiki/Academic_grading_in_the_Philippines)
- [GWA Grading System Explained — GWA Calculator Blog](https://gwacalculator.blog/blog/gwa-grading-system-explained-how-philippine-universities-calculate-grades/)
- [College Grading System in Philippines 2026 — GwaCal](https://gwacalculator.com/college-grading-system-philippines/)
- [CHED — Commission on Higher Education](https://ched.gov.ph/)
- [Digital Transcript Shift in Philippines — Parchment](https://www.parchment.com/en-sea/blog/transcript-of-records-in-the-philippines/)
- [Enrollment Surge Handling — RadView](https://www.radview.com/blog/preventing-traffic-surge-using-ellucian-banner/)
- [University Registration Queue Systems — Queue-it](https://queue-it.com/blog/university-registrations-online-queue/)
- [Cloud Enrollment Scalability — EDMO (Medium)](https://medium.com/@support_54988/cloud-based-enrollment-scalability-how-universities-can-grow-without-growing-pains-97a6564a3e9c)
- [Cache Optimization Strategies — Redis](https://redis.io/blog/guide-to-cache-optimization-strategies/)
- [Database Caching Strategies — AWS](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html)
- [WCAG UX Tips for Designers — WCAG.com](https://www.wcag.com/resource/ux-quick-tips-for-designers/)
- [Designing for Web Accessibility — W3C WAI](https://www.w3.org/WAI/tips/designing/)
- [OAuth vs OIDC vs SAML — Okta](https://www.okta.com/identity-101/whats-the-difference-between-oauth-openid-connect-and-saml/)
- [SSO Authentication Guide — LoginRadius](https://www.loginradius.com/blog/engineering/guide-to-openid-saml-oauth)
- [Alumni Management — Hivebrite](https://hivebrite.io/alumni-management-software/)
- [Student Financials — Workday](https://www.workday.com/en-us/products/student/student-finance.html)
- [Unified Academic Hub — Classter](https://www.classter.com/blog/edtech/building-a-unified-academic-operations-hub-sis-lms-school-management-systems/)
- [SIS Reference — Microsoft 365 Education](https://learn.microsoft.com/en-us/microsoft-365/education/guide/1-reference/baseline-reference-sis)
