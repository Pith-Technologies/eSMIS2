# Regulatory Compliance Principles

Requirements, implementation guidance, and checklists for Philippine regulatory compliance
in eSMIS — the Student Management Information System for Philippine higher education
institutions (HEIs).

> **Scope:** This document covers compliance obligations that directly affect system design
> and data architecture. It is not a legal opinion. When in doubt, consult the HEI's legal
> counsel and/or Data Protection Officer.

---

## Table of Contents

1. [RA 10173 — Data Privacy Act](#1-ra-10173--data-privacy-act)
2. [CHED MORPHE (CMO 40, s. 2008) — Academic Records](#2-ched-morphe-cmo-40-s-2008--academic-records)
3. [RA 10931 — Free Tuition Law](#3-ra-10931--free-tuition-law)
4. [RA 10687 — UniFAST Act](#4-ra-10687--unifast-act)
5. [RA 7277/9442/10754 — PWD Rights](#5-ra-727794421075--pwd-rights)
6. [RA 8972/11861 — Solo Parent Welfare](#6-ra-897211861--solo-parent-welfare)
7. [RA 10968 — Philippine Qualifications Framework](#7-ra-10968--philippine-qualifications-framework)
8. [CMO 4, s. 2020 — Flexible Learning](#8-cmo-4-s-2020--flexible-learning)
9. [CMO 1, s. 2025 — Microcredentials](#9-cmo-1-s-2025--microcredentials)
10. [RA 9470 — National Archives Act](#10-ra-9470--national-archives-act)
11. [Accreditation Bodies (AACCUP/PACUCOA/PAASCU)](#11-accreditation-bodies-aaccuppacucoapaascu)
12. [Master Compliance Checklist](#12-master-compliance-checklist)

---

## 1. RA 10173 — Data Privacy Act

**Law:** Republic Act No. 10173 (Data Privacy Act of 2012)
**Enforcing body:** National Privacy Commission (NPC)
**IRR:** NPC Circular 16-01 to 16-04

> **Important NPC Circular Updates:** NPC Circular 16-01 has been repealed by NPC Circular
> 2023-06. NPC Circular 16-02 has been superseded by NPC Circular 2020-03. Only NPC Circular
> 16-03 (breach management) remains in force from the original set.

### Key Provisions

Student data — including academic records, health information, financial standing, and
disciplinary history — is classified as **sensitive personal information** under RA 10173.
Processing requires a lawful basis and must comply with the principles of transparency,
legitimate purpose, and proportionality.

**Lawful bases for student data processing:**

| Basis | Example Use |
|-------|-------------|
| Consent | Processing of optional profile data |
| Contract | Enrollment, grade recording, graduation processing |
| Legal obligation | CHED HEMIS reporting, RA 10931 subsidy tracking |
| Vital interests | Emergency health information |
| Public authority | Public HEI functions |

**Organizational requirements:**

- Register all data processing systems with the NPC
- Appoint a Data Protection Officer (DPO)
- Maintain a Record of Processing Activities (ROPA)
- Conduct a Privacy Impact Assessment (PIA) before deploying eSMIS and after
  significant changes
- Report personal data breaches to the NPC **within 72 hours** of discovery
- Implement organizational, physical, and technical security measures

**Data subject rights (students and parents/guardians of minors):**

| Right | What the System Must Support |
|-------|------------------------------|
| Be informed | Privacy notice at enrollment; ROPA maintained |
| Access | Downloadable record of personal data on request |
| Rectification | Correction workflow with audit trail |
| Erasure/blocking | Erasure of unlawfully processed data; permanent academic records are exempt |
| Data portability | Export of personal data in a structured, machine-readable format |
| Object | Mechanism to record and honour objections to specific processing activities |
| Damages | Documented breach response process |

**Consent for minors:**

- Students **under 18**: parental or guardian consent required for all data processing
  beyond what is strictly necessary for enrollment
- Students **18 and above**: can provide their own consent
- Consent forms must be stored as evidence and retrievable on request

**Grades are SPI:** NPC advisory opinions confirm that test scores, grade levels, and
section assignments are sensitive personal information under Section 3(l)(2). Public
posting of grades — even by student number — violates the DPA.

**MFA required per NPC Circular 2023-06** for all online access to SPI. Compliance
deadline: March 30, 2025.

**50% penalty increase for SPI violations involving minors** (Section 36). This is
critical for a SIS where many freshmen are under 18.

**30 working days** response deadline for data subject rights requests (NPC Advisory
2021-01).

**Penalties for non-compliance:**

- Administrative fines up to PHP 5,000,000 per violation
- Criminal penalties: 1–6 years imprisonment and PHP 500,000–4,000,000 in fines
  depending on the offense (unauthorized processing, negligent access, improper
  disposal, unauthorized disclosure)
- SPI violations involving minors carry an additional 50% penalty increase (Section 36)

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Consent capture and storage | `esmis_enrollment` |
| DPO role and ROPA | `esmis_privacy` (planned) |
| Data subject rights requests | `esmis_privacy` (planned) |
| Breach notification workflow | `esmis_privacy` (planned) |
| Role-based access controls | `esmis_security` |
| Audit trails | `esmis_audit` (planned) |

### Implementation Checklist

- [ ] At enrollment, distinguish minor (under 18) vs. adult students and route to the
      correct consent form
- [ ] Parental/guardian consent form captured and stored with the enrollment record;
      linked to the student's file
- [ ] Consent forms are versioned — if the privacy policy changes, re-consent is
      triggered for affected students
- [ ] A `esmis.privacy.consent` model (or equivalent) records: student, consent type,
      date given, date withdrawn (if applicable), captured by whom
- [ ] DPO is a named user role in the system with read access to the ROPA and
      consent records
- [ ] ROPA is maintained as a live document (not just a spreadsheet); the system
      should track all data flows involving personal data
- [ ] PIA documentation is attached to the eSMIS deployment record before go-live;
      re-assessed on major version upgrades
- [ ] Breach notification workflow: incident → internal escalation → NPC notification
      within 72 hours → affected-student notification → post-incident review; all steps
      logged with timestamps
- [ ] Data subject rights requests are tracked: received, acknowledged (within 30 days),
      fulfilled, or lawfully rejected with reason
- [ ] Access request fulfillment: system can export a student's complete personal data
      in a structured format (JSON or PDF) on demand
- [ ] Rectification: correction of personal data creates an audit log entry with old
      value, new value, requestor, approver, and date
- [ ] Erasure: permanent academic records (TOR, grades) are exempt from erasure;
      non-academic personal data (e.g., marketing preferences) must be erasable;
      the system enforces this distinction
- [ ] Data portability export does not include data that would expose other students'
      personal information
- [ ] Role-based access: registrar staff cannot access financial records; finance staff
      cannot access disciplinary records; access logs are maintained
- [ ] All personal data at rest is encrypted; connections use TLS in transit
- [ ] Cross-border transfer of student records (e.g., to foreign credential verification
      services) requires NPC approval or adequacy determination; transfers are logged
- [ ] MFA enabled for all users accessing Tier 3 (SPI) data
- [ ] Grade data treated as SPI — no public posting, no exposure without authorization,
      no inclusion in list exports accessible to unauthorized roles
- [ ] Data subject rights requests tracked with 30-working-day deadline (NPC Advisory
      2021-01); overdue requests escalate to the DPO

### Testing Requirements

- Unit test: consent form creation sets `is_minor` flag correctly based on birth date
- Unit test: erasure request on a permanent academic record raises `UserError` with
  explanation
- Unit test: data export for a student returns all personal data fields and excludes
  other students' data
- Integration test: breach notification workflow completes all steps and timestamps
  each transition
- Security test: a user with registrar role cannot read financial ledger records;
  a user with finance role cannot read disciplinary records

---

## 2. CHED MORPHE (CMO 40, s. 2008) — Academic Records

**Law/CMO:** CMO No. 40, Series of 2008 (Manual of Regulations for Private Higher
Education — MORPHE)
**Effective:** July 31, 2008
**Scope:** All private HEIs; SUCs follow equivalent regulations under their charters and
CHED En Banc resolutions

### Key Provisions

#### Permanent Academic Records

HEIs must maintain a **permanent academic record** for every student. The official
document of academic standing is the **Transcript of Records (TOR)**. Records must include:

- Admission credentials (Form 137, SHS Diploma, LRN)
- Enrollment forms for every semester
- Academic transcript (course, units, grade, semester, year)
- Disciplinary records (if any)
- Financial ledger (tuition and fee payment history)
- Personal information file (name, address, contact, guardian)

Secure storage is mandatory to prevent tampering. Release of records requires student
consent.

#### Enrollment and Registration

- Students must meet HEI admission requirements within CHED minimums
- Cross-enrollment requires written approval from the home institution
- Transfer students must present honorable dismissal and TOR from the previous HEI
- Maximum residency requirements apply per program (typically 1.5× the standard
  program length)

#### Grading System

CHED does not mandate a single unified grading scale. The system must be configurable:

| Scale Type | Example |
|------------|---------|
| Numerical (1.0–5.0) | 1.00 highest, 5.00 failing; 3.00 passing |
| Letter (A–F) | A/B/C/D/F |
| Percentage | 70% or above as passing |

- Grade changes require a formal process with documented justification and approver
  signatures
- Incomplete (INC) grades have a resolution timeline (typically one academic year);
  unresolved INC converts to a failing grade per institutional policy
- GWA/GPA computation must follow the institutional formula consistently

#### Academic Standing

- Retention policies (probation, dismissal) are per-program and must be enforced
  consistently
- Latin honors computation is governed by CMO No. 8, s. 1976 and institutional
  supplements; requires cumulative GWA calculation across all enrolled units

**Latin honors thresholds (common baseline — each HEI publishes its own):**

| Honor | Typical GWA Range (1.0 scale) |
|-------|-------------------------------|
| Summa Cum Laude | 1.00–1.20 |
| Magna Cum Laude | 1.21–1.45 |
| Cum Laude | 1.46–1.75 |

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Academic records management | `esmis_academics` |
| Enrollment and registration | `esmis_enrollment` |
| Grading and GWA computation | `esmis_grades` |
| TOR generation | `esmis_records` |
| Latin honors | `esmis_graduation` |

### Implementation Checklist

- [ ] The grading scale is configurable per HEI (numerical, letter, or percentage) and
      per program if the HEI runs multiple scales; the scale used for a grade is stored
      alongside the grade itself
- [ ] GWA/GPA computation is formula-driven per institutional settings; the formula is
      documented in system configuration, not hard-coded
- [ ] Grade change workflow: original grade → change request (with reason) → department
      head approval → registrar confirmation → audit log entry; original grade is
      preserved in history and never overwritten
- [ ] INC grade records store: course, original INC date, resolution deadline, resolved
      grade (or auto-converted failing grade), and resolver; a scheduled job flags
      overdue INC resolutions
- [ ] Cross-enrollment records link the home institution, the host institution, the
      course, the units, and the approved grade; transferred units are flagged as
      cross-enrolled in GWA computation if the HEI excludes them
- [ ] Transfer student admission captures: honorable dismissal number and date,
      source institution TOR reference, and credited units with equivalency decisions
- [ ] Maximum residency tracking: system computes expected end date based on program
      length × 1.5 (or configured multiplier) and flags students approaching the limit
- [ ] TOR generation: produces a complete, accurate transcript that includes all
      enrolled semesters, grades, units, and GWA; shows academic standing per semester
- [ ] Academic standing is computed automatically after each grading period (regular,
      probation, dismissed); probation triggers a notification to the student and
      academic adviser
- [ ] Latin honors eligibility is computed at graduation clearance time; computation
      uses all enrolled units across the full program unless institutional policy
      excludes specific semester types (e.g., cross-enrolled units, advanced credit)
- [ ] Permanent records are immutable once certified; corrections go through the
      grade change workflow, not direct edits

### Testing Requirements

- Unit test: GWA computation matches expected value for a known set of grades and
  units under numerical, letter, and percentage scales
- Unit test: unresolved INC beyond the deadline converts to the configured failing
  grade
- Unit test: grade change preserves original grade in audit history
- Unit test: Latin honors threshold correctly awards or denies each honor level
- Integration test: TOR generated for a student with transfers, INC resolutions, and
  a grade change reflects all history correctly
- Integration test: maximum residency flag is triggered at the correct semester

---

## 3. RA 10931 — Free Tuition Law

**Law:** Republic Act No. 10931 (Universal Access to Quality Tertiary Education Act, 2017)
**IRR approved:** February 22, 2018
**Also known as:** UAQTEA or Free Tuition Law
**Implementing agency:** CHED, UniFAST

### Key Provisions

#### Free Tuition (SUCs and LUCs)

Eligible students at State Universities and Colleges (SUCs) and Local Universities and
Colleges (LUCs) are **exempt from tuition and other school fees**.

**Eligibility criteria — all four must be met:**

1. Filipino citizenship
2. Enrolled in a recognized SUC, LUC, or state-run Technical-Vocational Institution
3. Does **not** hold an existing bachelor's degree or equivalent qualification
4. Complies with the institution's retention policies and academic standards

#### Tertiary Education Subsidy (TES)

TES extends financial support to students in both private and public HEIs who are not
covered by free tuition. TES beneficiaries are identified and ranked by UniFAST using
a means test.

#### SMIS Data Requirements

| Data Point | Purpose |
|------------|---------|
| Filipino citizenship status | Eligibility gate for free tuition |
| Prior degree status | Second eligibility gate; must not hold existing bachelor's degree |
| Institutional type (SUC/LUC/private) | Determines which program applies |
| Academic standing | Retention compliance check |
| Tuition subsidy amount per student per semester | Budget reporting to CHED |
| TES recipient flag and amount | UniFAST reporting |
| StuFAP summary per student | Consolidated financial assistance tracking |

#### Reporting Requirements

- SUCs and LUCs report exact tuition subsidy amounts to CHED each semester
- Governing boards compute annual budgets based on projected enrollee counts
- Annual reports submitted to the UniFAST Board by implementing agencies
- CHED devises specific reporting mechanisms and formats

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Citizenship and prior degree tracking | `esmis_enrollment` |
| Free tuition eligibility determination | `esmis_fees` |
| TES and StuFAP tracking | `esmis_financial_aid` |
| CHED subsidy reporting | `esmis_reporting` |

### Implementation Checklist

- [ ] Citizenship field on the student record captures Filipino citizenship status;
      this field is required at enrollment and drives free tuition eligibility
- [ ] Prior degree field captures whether the student holds an existing bachelor's
      degree or equivalent; automatically disqualifies from free tuition
- [ ] Institutional type is configured at the HEI level (SUC, LUC, or private);
      eligibility rules are keyed to this configuration
- [ ] Free tuition eligibility is computed automatically at enrollment using all four
      criteria; result is stored and surfaced to the registrar before fee posting
- [ ] Fee computation for eligible students zeros out tuition and other school fees
      covered by the law; non-covered fees (e.g., student organization fees, optional
      services) are computed normally
- [ ] Tuition subsidy amount per eligible student is stored as a separate line in the
      fee ledger (not silently removed); this enables audit and CHED reporting
- [ ] TES beneficiary flag and awarded amount are stored per semester; TES amounts
      are separate from free tuition subsidy amounts
- [ ] Academic standing is checked each semester as part of retention compliance;
      a student who fails retention is flagged and free tuition eligibility for the
      next semester is suspended pending review
- [ ] CHED subsidy report: generates a per-student, per-semester breakdown of tuition
      subsidy amounts in CHED-specified format
- [ ] UniFAST annual report: generates consolidated StuFAP summary per student
      across all financial assistance programs received during the year
- [ ] All eligibility determinations and fee adjustments are logged with timestamps
      and the user who processed them; these logs support audits

### Testing Requirements

- Unit test: student with Filipino citizenship, no prior degree, enrolled in SUC,
  meeting retention → eligible; each criterion failure → ineligible
- Unit test: fee computation for eligible student produces zero tuition; non-tuition
  fees remain
- Unit test: tuition subsidy amount is stored as a positive ledger entry representing
  the subsidy value
- Integration test: TES beneficiary flag propagates to the UniFAST annual report
- Integration test: a student who fails retention mid-year is flagged and the next
  semester's free tuition eligibility is suspended

---

## 4. RA 10687 — UniFAST Act

**Law:** Republic Act No. 10687 (Unified Student Financial Assistance System for
Tertiary Education Act, 2015)
**Purpose:** Unifies all government-funded Student Financial Assistance Programs
(StuFAPs) under one coordinating body — the UniFAST Board
**Implementing agencies:** CHED, TESDA, DOST, DOLE, DSWD, DND, DA, DILG, DENR,
NCIP, OPAPP, and both Houses of Congress

### Key Provisions

UniFAST consolidates:
- Scholarships
- Grants-in-Aid
- Government student loans
- Government partnership programs

Each implementing agency retains its specific eligibility criteria and award amounts,
but all programs are reportable to the UniFAST Board.

#### StuFAP Modalities

| Modality | Description |
|----------|-------------|
| Merit-based scholarship | Academic performance criterion |
| Need-based grant | Means-tested financial need |
| Government loan | Repayable assistance |
| Combined need and merit | Both criteria |
| Sector-specific programs | DOST S&T scholarships, DILG scholarships, etc. |

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| StuFAP tracking per student | `esmis_financial_aid` |
| Eligibility verification | `esmis_financial_aid` |
| UniFAST Board annual reporting | `esmis_reporting` |

### Implementation Checklist

- [ ] Every financial assistance program received by a student is recorded as a
      separate `esmis.financial.aid.grant` record (or equivalent) with: program name,
      implementing agency, modality (scholarship/grant/loan), semester, and amount
- [ ] Multiple StuFAP programs per student per semester are supported; there is no
      artificial one-program-per-student limit
- [ ] Implementing agency is a required field on each grant record; reporting can
      be filtered and grouped by agency
- [ ] Eligibility criteria per program are configurable; the system records which
      criteria were verified and by whom at the time of award
- [ ] UniFAST annual report: per-student summary of all StuFAP awards across the
      academic year, grouped by implementing agency and modality
- [ ] Separate accounting per implementing agency: reports can disaggregate totals
      by agency for budget reconciliation
- [ ] Interaction with RA 10931 TES is tracked: TES is one StuFAP modality within
      the UniFAST framework; it is stored as such and is not a duplicate field
- [ ] Historical StuFAP records are retained per the records retention policy
      (minimum 10 years for financial records; see Section 10)

### Testing Requirements

- Unit test: a student with multiple StuFAP awards in one semester has all awards
  recorded independently and summed correctly in the report
- Unit test: report grouped by implementing agency matches expected totals
- Integration test: UniFAST annual report includes all students with at least one
  active StuFAP grant during the reporting year

---

## 5. RA 7277/9442/10754 — PWD Rights

**Laws:**
- RA 7277 (Magna Carta for Persons with Disability, 1992) — foundational rights
- RA 9442 (2007 amendment) — introduced the 20% discount
- RA 10754 (2016 amendment) — expanded the discount to cover additional services
**Enforcing body:** National Council on Disability Affairs (NCDA)

### Key Provisions

#### Non-Discrimination in Education

It is unlawful to deny admission to any course solely on the basis of disability. HEIs
must accommodate students with disabilities.

#### Financial Benefits

- **20% discount** on educational fees and related services for PWD students
- Financial assistance (scholarships, loans, subsidies) for economically marginalized
  PWD students

#### Accessibility

HEIs must provide reasonable accommodations: accessible facilities, assistive
technology, modified assessment methods, and other support as needed.

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| PWD status and ID capture | `esmis_enrollment` |
| 20% discount computation | `esmis_fees` |
| Accessibility accommodation tracking | `esmis_student_services` (planned) |
| PWD enrollment statistics for HEMIS | `esmis_reporting` |

### Implementation Checklist

- [ ] Student record has a `is_pwd` boolean and a `pwd_id_number` field; PWD ID
      expiry date is also stored so expired IDs can be flagged
- [ ] PWD ID number is treated as sensitive personal information with restricted access
- [ ] When `is_pwd` is `True`, the fee computation module automatically applies the
      20% discount on applicable fees as defined by RA 9442/10754; non-applicable
      fees are not discounted
- [ ] The discount is recorded as a named line item in the fee ledger (e.g.,
      "PWD Discount — RA 9442") for audit traceability
- [ ] Accommodations provided to the student are recorded (e.g., extended exam time,
      accessible seating, assistive device issued); this supports accreditation evidence
- [ ] Scholarship eligibility for PWD programs is flagged automatically when `is_pwd`
      is `True`; financial aid officers are notified of eligible programs
- [ ] HEMIS enrollment report includes PWD count disaggregated by program, year level,
      and disability type; disability type is a configurable vocabulary (see
      `esmis_vocabulary`)
- [ ] Non-discrimination: admission system does not allow disability to be set as a
      reason for rejection; rejection reasons are a controlled vocabulary that
      excludes disability

### Testing Requirements

- Unit test: fee computation with `is_pwd = True` applies exactly 20% discount on
  qualifying fee lines and leaves non-qualifying lines unchanged
- Unit test: expired PWD ID triggers a warning but does not automatically remove
  the discount (staff review required)
- Unit test: PWD count in the HEMIS report matches the number of active enrolled
  students with `is_pwd = True`
- Security test: `pwd_id_number` is not readable by users without the registrar or
  student services role

---

## 6. RA 8972/11861 — Solo Parent Welfare

**Laws:**
- RA 8972 (Solo Parents' Welfare Act of 2000)
- RA 11861 (Expanded Solo Parents Welfare Act, 2022)

### Key Provisions

#### Education Benefits for Dependents

A **full scholarship** is available for **one dependent child** of a qualified solo
parent enrolled in HEIs and Technical-Vocational Institutions. The dependent must be:

- Dependent on the solo parent for support
- Unmarried
- Unemployed
- 22 years old or below

#### Solo Parent Identification

Solo parents must present a **Solo Parent ID** issued by the City/Municipal Social
Welfare and Development Office (C/MSWDO). The ID is renewed annually.

#### Dual-Benefit Scenario

A student who is both a PWD and a solo parent dependent may receive both sets of
benefits. The system must not prevent this combination.

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Solo parent dependent status capture | `esmis_enrollment` |
| Solo Parent ID verification | `esmis_enrollment` |
| Scholarship eligibility flagging | `esmis_financial_aid` |
| Dual-benefit handling | `esmis_fees` |

### Implementation Checklist

- [ ] Student record has an `is_solo_parent_dependent` boolean and a
      `solo_parent_id_number` field; Solo Parent ID expiry date is stored
- [ ] Solo Parent ID number is sensitive personal information with restricted access
- [ ] Dependency eligibility criteria are enforced at data entry: age ≤ 22,
      marital status unmarried, employment status unemployed
- [ ] When eligibility criteria are met, the student is flagged for solo parent
      scholarship programs in the financial aid module
- [ ] Solo Parent ID expiry is tracked; expired IDs trigger a renewal reminder to
      the student services office; benefit is not automatically removed until staff
      review confirms expiry
- [ ] Dual-benefit scenario: a student who is both `is_pwd = True` and
      `is_solo_parent_dependent = True` receives both the PWD discount and solo
      parent scholarship eligibility without conflict; the fee computation handles
      both concurrently
- [ ] Financial aid record for the solo parent scholarship links to the student's
      solo parent dependent record for audit purposes
- [ ] Annual verification: system prompts renewal of Solo Parent ID each academic
      year as part of enrollment re-verification

### Testing Requirements

- Unit test: a student who is 23 years old at enrollment is not flagged as an
  eligible solo parent dependent
- Unit test: a student who is both `is_pwd` and `is_solo_parent_dependent` has
  both benefit flags active simultaneously without conflict in fee computation
- Unit test: expired Solo Parent ID generates a warning but does not auto-remove
  benefit; staff review step is required
- Integration test: solo parent scholarship grant is created in `esmis_financial_aid`
  when all eligibility criteria are met

---

## 7. RA 10968 — Philippine Qualifications Framework

**Law:** Republic Act No. 10968 (PQF Act, 2018)
**Implementing agencies:** DepEd, TESDA, CHED, PRC, DOLE
**Coordinating body:** PQF National Coordinating Council (PQF-NCC)

### Framework Structure

| Level | Qualification | Subsystem |
|-------|--------------|-----------|
| 1–4 | National Certificates I–IV | TESDA |
| 5 | Diploma | TESDA/CHED interface |
| 6 | Baccalaureate (Bachelor's Degree) | CHED |
| 7 | Post-Baccalaureate / Master's Degree | CHED |
| 8 | Doctoral Degree | CHED |

eSMIS covers **Levels 5–8** (HEI programs). Descriptors are differentiated along three
domains: knowledge, skills, and values; application; and degree of independence.

### Key Provisions for HEIs

- Every academic program must be mapped to a PQF level
- Curriculum learning outcomes must align with PQF level descriptors
- PQF levels facilitate credit recognition and transfer across institutions
- Microcredentials must map to PQF Levels 5–8 (per CMO No. 1, s. 2025)
- The PQF-NCC maintains a national registry of qualifications

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Program-to-PQF-level mapping | `esmis_curriculum` (planned) |
| Curriculum learning outcome alignment | `esmis_curriculum` (planned) |
| Qualification pathway tracking | `esmis_academics` |
| PQF-NCC registry data generation | `esmis_reporting` |

### Implementation Checklist

- [ ] Every academic program record has a `pqf_level` field (Selection: 5, 6, 7, 8);
      this field is required before a program can be activated
- [ ] Curriculum records link each course to the program's PQF level descriptors
      in the three domains; learning outcome statements are stored in the system
- [ ] Credit transfer decisions record the PQF-level equivalency rationale; when
      a student transfers credits, the receiving program's PQF level is used to
      determine acceptability
- [ ] Qualification pathways: system supports lateral mobility (between programs at
      the same PQF level) and vertical mobility (from Level 6 to Level 7); pathway
      records link the entry qualification, the exit qualification, and any bridging
      requirements
- [ ] Microcredential records inherit the PQF level field and follow the same
      mapping requirement (see Section 9)
- [ ] PQF-NCC registry export: generates a list of active programs with their PQF
      levels, learning outcome summaries, and graduate counts for the period

### Testing Requirements

- Unit test: a program cannot be saved without a `pqf_level` value
- Unit test: a microcredential record without a `pqf_level` raises `ValidationError`
- Integration test: PQF-NCC export includes all active programs with correct levels
  and graduate counts

---

## 8. CMO 4, s. 2020 — Flexible Learning

**CMO:** CHED Memorandum Order No. 4, Series of 2020
**Purpose:** Guidelines for implementing flexible learning during and beyond COVID-19
**Status:** Ongoing; flexible modalities are now a permanent feature of Philippine HE

### Key Provisions

- HEIs may offer face-to-face, online, blended, and distance learning modalities
- Modality is set at the **section level**, not the course level (a course may be
  offered in multiple modalities in different sections in the same semester)
- HEIs must maintain learning management systems (LMS) for non-face-to-face delivery
- GWA computation adjustments for online modalities are permitted if the HEI
  publishes its policy
- Student assessment methods may be adapted to the modality

**Learning modalities:**

| Modality | Description |
|----------|-------------|
| Face-to-face (F2F) | Traditional in-person delivery |
| Online synchronous | Live online sessions via videoconference |
| Online asynchronous | Self-paced online modules |
| Blended | Combination of F2F and online |
| Distance learning | Correspondence, printed modules, broadcast |

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Modality field on sections | `esmis_academics` |
| Modality reporting for CHED | `esmis_reporting` |
| LMS integration (if applicable) | `esmis_lms` (planned) |

### Implementation Checklist

- [ ] Course section record has a `learning_modality` field (Selection: face_to_face,
      online_synchronous, online_asynchronous, blended, distance); required before
      a section can be published for enrollment
- [ ] Modality is stored per section per semester; historical modality data is never
      overwritten so that past semesters reflect the modality actually used
- [ ] If GWA computation differs by modality, the computation rule is linked to the
      modality configuration; the rule used is stored alongside the computed GWA
- [ ] HEMIS and CHED enrollment reports include a modality column per section;
      aggregate enrollment by modality per program per semester is reportable
- [ ] LMS URL or reference can be linked to a section record for non-F2F sections,
      supporting audit evidence for accreditation

### Testing Requirements

- Unit test: a section cannot be saved without a `learning_modality` value
- Unit test: historical section records retain the modality set during that semester
  even if the course's default modality changes later
- Integration test: enrollment report aggregates correctly by modality

---

## 9. CMO 1, s. 2025 — Microcredentials

**CMO:** CHED Memorandum Order No. 1, Series of 2025
**Purpose:** National guidelines for microcredential development, CHED approval,
and recognition

### Key Provisions

- Microcredentials must map to PQF Levels 5–8
- Learning outcomes must be measurable and standardized
- May stand alone or **stack toward larger qualifications** (certificates, degrees)
- Verifiable credential issuance is required; CHED recognizes **Open Badges 3.0**
  and **W3C Verifiable Credentials (VC)** standards
- Microcredentials require CHED approval before award

#### Stacking Pathways

A student may accumulate microcredentials that count toward a diploma or degree.
The system must track:

1. Which microcredentials the student has earned
2. Which degree program (if any) they are stacking toward
3. How many units of the target degree have been satisfied by stacked credentials

#### Verifiable Credential Issuance

eSMIS must support generation of verifiable credentials that recipients can share with
employers, other institutions, and verification services.

- **Open Badges 3.0**: JSON-LD assertion signed by the HEI; hosted or embedded
- **W3C Verifiable Credentials**: JSON-LD with cryptographic proof; enables
  decentralized verification

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Microcredential program records | `esmis_credentials` (planned) |
| Credential stacking tracking | `esmis_credentials` (planned) |
| Open Badges / W3C VC issuance | `esmis_credentials` (planned) |
| PQF level mapping | `esmis_curriculum` (planned) |
| CHED approval tracking | `esmis_credentials` (planned) |

### Implementation Checklist

- [ ] `esmis.microcredential` model (or equivalent) stores: title, PQF level,
      learning outcomes, CHED approval reference and date, stackable-toward program
      (nullable), and unit equivalency value
- [ ] A student's earned microcredential record links to: the student, the
      microcredential, the completion date, the issuing HEI, and the issued
      credential object (badge or VC)
- [ ] Stacking: when a student earns a microcredential that is stackable toward a
      degree, the target degree program record is updated with the earned units;
      the stacking ledger is auditable
- [ ] CHED approval reference is required before a microcredential can be awarded;
      the system blocks issuance if no approval reference is recorded
- [ ] Open Badges 3.0 issuance: system generates a conformant JSON-LD badge
      assertion signed with the HEI's key; badge is hosted at a stable URL and can
      be embedded in a student's profile
- [ ] W3C VC issuance: system generates a conformant VC document; cryptographic
      proof mechanism is configurable (JWT or JSON-LD proof)
- [ ] Issued credentials are stored with a revocation capability; if a credential is
      revoked, the revocation is reflected in the credential status URL or list
- [ ] Credential verification endpoint: an unauthenticated endpoint allows third
      parties to verify a credential by ID without exposing other student data

### Testing Requirements

- Unit test: a microcredential cannot be awarded without a CHED approval reference
- Unit test: stacking a credential toward a degree correctly increments the earned
  unit count on the target program
- Unit test: generated Open Badge 3.0 JSON-LD is schema-valid
- Unit test: revoking an issued credential updates the credential status correctly
- Integration test: a student with three stacked microcredentials toward a diploma
  shows the correct remaining unit requirement on the degree progress view

---

## 10. RA 9470 — National Archives Act

**Law:** Republic Act No. 9470 (National Archives of the Philippines Act of 2007)
**Enforcing body:** National Archives of the Philippines (NAP)
**Scope:** All government agencies including public HEIs (SUCs and LUCs); private
HEIs follow equivalent CHED retention guidelines (CHED En Banc Resolution No. 170-2018)

### Key Provisions

- The NAP is the custodian of all public records in the Philippines
- Government records cannot be disposed of without **NAP approval**
- HEIs must maintain a records disposition schedule approved by the NAP
- Violations carry administrative or criminal penalties
- Records involved in ongoing legal cases or audits **cannot be disposed** regardless
  of scheduled retention end dates

### Retention Schedules

| Record Type | Retention Period | Disposition |
|-------------|-----------------|-------------|
| Core academic records (TOR, grade sheets, diploma records) | Permanent | Never disposed |
| Transfer credentials (honorable dismissal, incoming TOR) | 10 years minimum | Secure disposal after NAP approval (public HEIs) |
| Enrollment forms and registration documents | Minimum 5 years (per institutional policy) | Secure disposal after NAP approval (public HEIs) |
| Disciplinary records | Per institutional policy | Secure disposal |
| Financial ledgers | 10 years (align with COA rules for public HEIs) | Secure disposal |
| Consent forms (RA 10173) | Duration of processing + reasonable retention period | Secure disposal |
| Disposal logs | 5 years after disposal event | Archive |

**Secure disposal methods:** physical shredding for paper records; certified digital
erasure (e.g., DoD 5220.22-M or equivalent) for digital records.

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Records retention schedule configuration | `esmis_records` (planned) |
| Retention end date tracking | `esmis_records` (planned) |
| Disposal workflow with NAP approval step | `esmis_records` (planned) |
| Disposal log | `esmis_audit` (planned) |

### Implementation Checklist

- [ ] Every record type in the system is classified with a retention category
      (permanent, 10-year, 5-year, institutional policy); this classification is set
      at the model level in configuration, not on individual records
- [ ] Permanent records (TOR, grade sheets, diploma records) cannot be deleted
      through the UI or API; the `unlink()` method raises `UserError` with a
      reference to the legal basis
- [ ] Records with a finite retention period have a computed `retention_end_date`
      field based on the record's closing date plus the retention period
- [ ] A scheduled job (running monthly) identifies records whose `retention_end_date`
      has passed and creates a disposal review task for the records officer
- [ ] Disposal workflow for public HEIs: disposal review → department head approval
      → NAP approval request generated → NAP approval reference recorded → secure
      disposal executed → disposal log entry created
- [ ] Disposal workflow for private HEIs: disposal review → department head approval
      → CHED-aligned retention verification → secure disposal executed → disposal
      log entry created
- [ ] Records under active legal hold (litigation, audit) are flagged `is_legal_hold
      = True`; the disposal workflow blocks records with this flag and surfaces them
      to the legal/compliance officer
- [ ] Disposal logs record: record type, record identifier, disposal date, disposal
      method, authorized by (user), approval reference (NAP or internal), and
      attestation that no legal hold was active
- [ ] Disposal logs are themselves retained for 5 years and are immutable after
      creation
- [ ] Digital erasure is logged separately from the record deletion; the log confirms
      the erasure method used

### Testing Requirements

- Unit test: `unlink()` on a permanent academic record raises `UserError` citing
  the legal basis
- Unit test: a record with `is_legal_hold = True` cannot proceed past the disposal
  review step
- Unit test: disposal log entry is created with all required fields after a
  successful disposal
- Integration test: the monthly scheduled job correctly identifies records past
  their `retention_end_date` and creates disposal review tasks
- Integration test: disposal workflow for a public HEI requires a NAP approval
  reference before disposal can complete

---

## 11. Accreditation Bodies (AACCUP/PACUCOA/PAASCU)

**Bodies:**

| Body | Full Name | Accredits |
|------|-----------|-----------|
| AACCUP | Accrediting Agency of Chartered Colleges and Universities in the Philippines | SUCs and government HEIs |
| PACUCOA | Philippine Association of Colleges and Universities Commission on Accreditation | Private HEIs (PACU member schools) |
| PAASCU | Philippine Accrediting Association of Schools, Colleges, and Universities | Private HEIs (broader membership) |

All three are recognized by CHED through the Federation of Accrediting Agencies of
the Philippines (FAAP).

### Accreditation Levels

| Level | Significance | Typical Duration |
|-------|-------------|-----------------|
| Candidate | Preliminary; indicates readiness | Varies |
| Level I | Initial accredited status | 3 years |
| Level II | Re-accredited; sustained quality | 3–5 years |
| Level III | High quality; partial autonomy | 5 years |
| Level IV | Highest; full autonomy | 5 years |

### Key Metrics eSMIS Must Produce

Accreditation bodies evaluate evidence of data-driven quality assurance. The required
metrics that eSMIS must generate include:

| Metric | Accreditation Area |
|--------|--------------------|
| Enrollment trends (per program, year level, modality) | Teaching & Learning; Administration |
| Retention rates (semester-to-semester and year-to-year) | Teaching & Learning; Support to Students |
| Completion/graduation rates (per program, per cohort) | Teaching & Learning |
| Grade distributions (per course, per semester) | Teaching & Learning; Curriculum |
| Faculty-student ratios (per program, per semester) | Faculty; Administration |
| Student services utilization (guidance, health, financial aid) | Support to Students |
| Research output (thesis/dissertation tracking for graduate programs) | Research |
| Scholarship and financial assistance data | Support to Students |
| Disciplinary case statistics | Administration; Support to Students |
| Accommodation and PWD support records | Support to Students |

### Historical Data Requirements

Accreditation visits occur on cycles of 3–5 years. The system must retain historical
data across **at least two full accreditation cycles** (minimum 10 years of operational
data) to support trend analysis and evidence generation.

### eSMIS Modules

| Responsibility | Planned Module |
|----------------|----------------|
| Enrollment, retention, and graduation metrics | `esmis_reporting` |
| Grade distribution reports | `esmis_grades` + `esmis_reporting` |
| Faculty-student ratio computation | `esmis_reporting` |
| Student services utilization | `esmis_student_services` (planned) |
| Accreditation evidence packaging | `esmis_accreditation` (planned) |

### Implementation Checklist

- [ ] Enrollment trend report: produces counts by program, year level, sex, and
      modality; comparable across semesters and academic years; exportable to CSV
      and PDF
- [ ] Retention rate report: for a given cohort (entering AY), tracks how many
      students remain enrolled at each subsequent semester; displayed as a cohort
      retention table
- [ ] Completion rate report: for a given cohort, tracks graduates vs. dropouts vs.
      still enrolled; can be filtered by program and entry year
- [ ] Grade distribution report: for a given course and semester, shows the
      frequency of each grade; can be aggregated across sections and semesters;
      exportable for evidence binder
- [ ] Faculty-student ratio: computes the ratio per program per semester using
      the number of active enrolled students and the number of full-time-equivalent
      faculty assigned to the program
- [ ] Student services utilization: tracks service type (guidance session, health
      consultation, financial aid counseling, career services), date, student (or
      anonymous count), and outcome notes; produces utilization frequency reports
- [ ] Research output tracking: for graduate programs, records thesis/dissertation
      title, student, adviser, panel members, defense date, and final status;
      supports aggregate counts by program and year
- [ ] Historical data is never purged for non-permanent records within the 10-year
      active retention window; archiving to cold storage is separate from deletion
- [ ] Accreditation evidence export: produces a packaged report covering a specified
      date range with all required metrics; formatted for submission to the relevant
      accrediting body
- [ ] Each report includes the data source, computation method, and the period
      covered; this supports reproducibility if the accreditor questions a figure
- [ ] Report generation does not lock tables; use asynchronous generation via
      `queue_job` for large historical reports (see
      [Performance & Scalability](performance-scalability.md))

### Testing Requirements

- Unit test: enrollment trend report counts match the actual enrollment records for
  a known test dataset
- Unit test: retention rate for a cohort where one student dropped and one graduated
  is computed correctly at each semester step
- Unit test: grade distribution report groups grades correctly across multiple
  sections of the same course
- Unit test: faculty-student ratio rounds to two decimal places and handles the
  zero-student edge case
- Integration test: accreditation evidence export for a 3-year period completes
  without error and includes all required metric sections
- Performance test: enrollment trend report for 10 years of data completes in under
  30 seconds using the async job path

---

## 12. Master Compliance Checklist

This checklist is organized by functional area. Use it as a go/no-go gate before
declaring any functional area complete. Each item maps to at least one regulation
covered in this document.

### Enrollment

- [ ] Filipino citizenship captured; drives free tuition eligibility (RA 10931)
- [ ] Prior degree status captured; disqualifies from free tuition (RA 10931)
- [ ] DepEd Learner Reference Number (LRN) captured for incoming freshmen
- [ ] K-12 credentials recorded and verified (Form 137, Form 138, SHS Diploma)
- [ ] Parental/guardian consent obtained for minor students; adult consent for
      students 18 and above (RA 10173)
- [ ] Consent forms stored and linked to student record; versioned (RA 10173)
- [ ] PWD status and PWD ID number captured; ID expiry tracked (RA 7277/9442/10754)
- [ ] Solo parent dependent status and Solo Parent ID captured; ID expiry tracked
      (RA 8972/11861)
- [ ] Cross-enrollment: home institution approval documented; credits flagged as
      cross-enrolled (MORPHE)
- [ ] Transfer students: honorable dismissal and source TOR recorded; unit
      equivalency decisions documented (MORPHE)
- [ ] Maximum residency tracked per program; students approaching limit are flagged
      (MORPHE)
- [ ] Institutional type configured (SUC/LUC/private); eligibility rules keyed to
      this (RA 10931)
- [ ] Learning modality captured per section at time of enrollment (CMO 4, s. 2020)

### Academics

- [ ] Grading scale configurable per HEI and per program (MORPHE)
- [ ] GWA/GPA computation is formula-driven and formula is documented in
      configuration (MORPHE)
- [ ] Grade change workflow enforces: formal request, approver, reason, audit trail;
      original grade preserved in history (MORPHE)
- [ ] INC grade resolution: deadline tracked, auto-conversion to failing grade on
      expiry (MORPHE)
- [ ] Academic standing computed automatically per grading period (MORPHE)
- [ ] Retention policy rules configured per program; probation and dismissal
      enforced (MORPHE)
- [ ] Latin honors eligibility computed at graduation clearance using all applicable
      enrolled units (MORPHE)
- [ ] Every program mapped to a PQF level (5–8); required field (RA 10968)
- [ ] Curriculum learning outcomes aligned to PQF level descriptors (RA 10968)
- [ ] Qualification pathways (lateral and vertical mobility) recorded (RA 10968)
- [ ] Learning modality stored per section per semester; historical data immutable
      (CMO 4, s. 2020)
- [ ] Microcredential records include: PQF level, CHED approval reference, learning
      outcomes, stackability target (CMO 1, s. 2025)
- [ ] Microcredential stacking correctly reduces remaining unit requirement in target
      degree (CMO 1, s. 2025)
- [ ] Verifiable credential (Open Badges 3.0 or W3C VC) issuable for earned
      microcredentials; revocation supported (CMO 1, s. 2025)

### Financial

- [ ] Free tuition eligibility determined automatically using all four criteria
      (RA 10931)
- [ ] Tuition subsidy stored as a named ledger line per student per semester
      (RA 10931)
- [ ] TES beneficiary flag and amount stored separately from free tuition subsidy
      (RA 10931)
- [ ] 20% PWD discount applied automatically to qualifying fee lines when `is_pwd =
      True`; discount is a named ledger line (RA 7277/9442/10754)
- [ ] Solo parent scholarship eligibility flagged when dependency criteria are met
      (RA 8972/11861)
- [ ] Dual PWD + solo parent benefits coexist without conflict in fee computation
      (RA 8972/11861 + RA 7277)
- [ ] All StuFAP grants recorded per student per semester with implementing agency
      and modality (RA 10687)
- [ ] All fee adjustments and grants are audit-logged with timestamps and processor
      identity (RA 10931, RA 10687)

### Privacy and Data Governance

- [ ] NPC registration completed for eSMIS as a data processing system (RA 10173)
- [ ] DPO appointed; role exists in system with appropriate access (RA 10173)
- [ ] ROPA maintained and current (RA 10173)
- [ ] PIA conducted before go-live and updated on major changes (RA 10173)
- [ ] Breach notification workflow: 72-hour NPC notification; all steps timestamped
      (RA 10173)
- [ ] Data subject rights requests tracked: received, acknowledged within 30 days,
      fulfilled or lawfully rejected (RA 10173)
- [ ] Data access export available per student on request (RA 10173)
- [ ] Erasure enforced for non-permanent data; permanent academic records blocked
      from erasure with legal basis cited (RA 10173)
- [ ] Sensitive fields (PWD ID, Solo Parent ID, health data) restricted by role
      (RA 10173 + RA 7277 + RA 8972)
- [ ] Cross-border data transfer requires NPC approval; transfers logged (RA 10173)
- [ ] Data at rest encrypted; TLS enforced in transit (RA 10173)

### Records Management and Retention

- [ ] Permanent records (TOR, grade sheets, diploma records) cannot be deleted;
      `unlink()` blocked by code (RA 9470, MORPHE)
- [ ] Retention end dates computed for all finite-retention record types (RA 9470)
- [ ] Monthly scheduled job identifies records past retention end date and creates
      disposal review tasks (RA 9470)
- [ ] Legal hold flag (`is_legal_hold`) blocks disposal workflow (RA 9470)
- [ ] Disposal workflow for public HEIs requires NAP approval reference (RA 9470)
- [ ] Disposal logs created for every disposal event; logs retained 5 years;
      immutable after creation (RA 9470)
- [ ] Digital erasure method documented in the disposal log (RA 9470)
- [ ] Historical operational data retained for minimum 10 years to support
      accreditation cycles (AACCUP/PACUCOA/PAASCU)

### Reporting

- [ ] HEMIS-compatible exports: Forms A, B/BC, E1/E2/E5, GH, Graduate List (CMO 45,
      s. 2016)
- [ ] HEMIS export includes modality column per section (CMO 4, s. 2020)
- [ ] HEMIS export includes PWD count disaggregated by program, year level, and
      disability type (RA 7277)
- [ ] Free tuition subsidy report per student per semester for CHED (RA 10931)
- [ ] UniFAST annual StuFAP report grouped by implementing agency and modality
      (RA 10687)
- [ ] PQF-NCC registry export of active programs with levels and graduate counts
      (RA 10968)
- [ ] Accreditation evidence reports: enrollment trends, retention rates, graduation
      rates, grade distributions, faculty-student ratios, student services
      utilization (AACCUP/PACUCOA/PAASCU)
- [ ] Large historical reports generated asynchronously via `queue_job` to avoid
      locking tables (see [Performance & Scalability](performance-scalability.md))
- [ ] Every report includes: data source, computation method, and reporting period
      (AACCUP/PACUCOA/PAASCU)
- [ ] eCAV-compatible credential format for TOR and diploma verification (CHED
      OneTouch)

---

**Authoritative Sources:**
- [RA 10173 Full Text and NPC Circulars](https://privacy.gov.ph)
- [CMO No. 40, s. 2008 — MORPHE](https://ched.gov.ph/cmo-40-s-2008/)
- [RA 10931 — Official Gazette](https://www.officialgazette.gov.ph/2017/08/03/republic-act-no-10931/)
- [RA 10687 — UniFAST Act](https://lawphil.net/statutes/repacts/ra2015/ra_10687_2015.html)
- [RA 9442 IRR (NCDA)](https://ncda.gov.ph/disability-laws/implementing-rules-and-regulations-irr/implementing-rules-and-regulations-of-republic-act-no-9442/)
- [RA 11861 — Expanded Solo Parents Welfare Act](https://pcw.gov.ph/republic-act-no-11861-expanded-solo-parents-welfare-act/)
- [RA 10968 — PQF Act](https://pqf.gov.ph/Uploads/Legal%20Basis/RA%2010968.pdf)
- [CMO No. 4, s. 2020 — Flexible Learning](https://ched.gov.ph/)
- [CMO No. 1, s. 2025 — Microcredentials](https://ched.gov.ph/)
- [RA 9470 — National Archives Act](https://lawphil.net/statutes/repacts/ra2007/ra_9470_2007.html)
- [AACCUP Accreditation](http://www.aaccupqa.org.ph/)
- [PACUCOA Accreditation](https://www.pacucoa.com/)
- [PAASCU](https://paascu.org.ph/)
- Research summary: [Philippine Regulatory Landscape for SMIS](../research/philippine-smis-regulatory-landscape.md)

**See also:** [Audit & Compliance](audit-compliance.md), [Access Rights](access-rights.md),
[Performance & Scalability](performance-scalability.md), [API Design](api-design.md)
