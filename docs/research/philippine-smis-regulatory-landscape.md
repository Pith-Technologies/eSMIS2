# Philippine Regulatory Landscape for Student Management Information Systems (SMIS)

Research compiled: 2026-03-09

This document catalogs Philippine government policies, regulations, and guidelines that affect
the design and operation of a Student Management Information System for higher education
institutions (HEIs). It is organized by regulatory body and law.

---

## Table of Contents

1. [CHED (Commission on Higher Education)](#1-ched-commission-on-higher-education)
2. [DepEd (Department of Education)](#2-deped-department-of-education)
3. [Data Privacy Act (RA 10173) and NPC Guidelines](#3-data-privacy-act-ra-10173-and-npc-guidelines)
4. [Philippine Qualifications Framework (PQF)](#4-philippine-qualifications-framework-pqf)
5. [Accreditation Bodies (AACCUP, PACUCOA, PAASCU)](#5-accreditation-bodies-aaccup-pacucoa-paascu)
6. [Key Republic Acts](#6-key-republic-acts)
7. [SMIS Compliance Checklist](#7-smis-compliance-checklist)

---

## 1. CHED (Commission on Higher Education)

### 1.1 Enabling Law: RA 7722 (Higher Education Act of 1994)

- **Signed:** May 18, 1994
- **Purpose:** Created CHED as the governing body for all public and private higher education.
- **Relevant powers (Section 8):**
  - Formulate development plans, policies, priorities, and programs on higher education
  - Set minimum standards for programs and institutions of higher learning
  - Monitor and evaluate the performance of programs and institutions
  - Promulgate rules and regulations for effective operations
- **Coverage:** All public and private HEIs, including degree-granting programs in all
  post-secondary educational institutions.
- **SMIS implication:** The system must support data collection, reporting, and compliance
  structures that CHED mandates under this broad authority.

### 1.2 MORPHE — CMO No. 40, Series of 2008

**Manual of Regulations for Private Higher Education (MORPHE)**

- **Effective:** July 31, 2008 (15 days after publication)
- **Scope:** Governs the establishment, operation, and regulation of private HEIs.
- **Key provisions affecting SMIS:**

#### Student Records (Part IV)
- HEIs must maintain permanent academic records for every student
- Transcript of Records (TOR) is the official document for academic standing
- Records must include: admission credentials, enrollment forms, academic transcripts,
  disciplinary records, financial ledgers, personal information files
- Secure storage required to prevent tampering
- Records release requires student consent (pre-dating but consistent with RA 10173)

#### Enrollment and Registration (Part III)
- Students must meet admission requirements set by each HEI within CHED minimums
- Cross-enrollment requires written approval from the home institution
- Transfer students must present honorable dismissal and TOR from the previous institution
- Maximum residency requirements apply per program

#### Grading System
- CHED does not mandate a single unified grading scale
- Most CHED-accredited schools follow a numerical system: 1.00 (highest) to 5.00 (failing)
- Some institutions use letter grades (A-F) or percentage-based systems
- HEIs must publish their grading system and policies
- Grade changes require formal processes and documentation
- Incomplete (INC) grades have specific resolution timelines

#### Academic Standards
- Retention policies must be clearly defined per program
- Academic probation and dismissal criteria must be documented
- Latin honors criteria governed by CMO No. 8, s. 1976 (foundational), requiring cumulative
  GPA/GWA computation

### 1.3 CMO No. 46, Series of 2012 — Quality Assurance and HEI Typology

- **Purpose:** Establishes the classification of HEIs as autonomous or deregulated
- **Horizontal typology:** Professional Institution, College, or University
- **Vertical typology:** Recognized, Deregulated, or Autonomous
- **SMIS implication:** The system may need to flag institutional classification for reporting
  purposes and to determine which CHED approval processes apply to program changes.

### 1.4 CMO No. 15, Series of 2019 — Graduate Programs PSG

- **Purpose:** Policies, Standards, and Guidelines for graduate education
- **Key provisions:**
  - Master's programs align with PQF Level 7
  - Doctoral programs align with PQF Level 8
  - Specific admission, retention, and completion requirements
  - Research output requirements
- **SMIS implication:** Graduate student records need distinct handling for thesis/dissertation
  tracking, comprehensive exam results, and research output documentation.

### 1.5 CMO No. 4, Series of 2020 — Flexible Learning

- **Purpose:** Guidelines for implementing flexible learning during and beyond COVID-19
- **Key provisions:**
  - Allows blended, online, and distance learning modalities
  - HEIs must have learning management systems (LMS)
  - Adjusted GWA computation for online modalities permitted
  - Student assessment methods may be adapted
- **SMIS implication:** System must accommodate multiple learning modalities per course
  section and track delivery mode for reporting.

### 1.6 CMO No. 10, Series of 2023 — Student Interchange Assistance Program (SIAP)

- **Purpose:** Policies on student interchange (transfer/cross-enrollment between HEIs)
- **SMIS implication:** System must support inter-institutional credit transfer workflows,
  cross-enrollment tracking, and SIAP reporting.

### 1.7 CMO No. 1, Series of 2025 — Microcredentials

- **Purpose:** National guidelines for microcredential development, approval, and recognition
- **Key provisions:**
  - Microcredentials must map to PQF Levels 5–8
  - Learning outcomes must be measurable and standardized
  - May stand alone or stack toward larger qualifications
  - Verifiable credential issuance required
- **SMIS implication:** System must support non-degree credential tracking, stackable
  credential pathways, and verifiable credential issuance.

### 1.8 CHED Digital Platforms and Data Reporting

CHED operates several digital platforms that HEIs must interact with. An SMIS should
support data exchange with these systems:

#### CHED OneTouch (onetouch.ched.gov.ph)
Single portal to CHED's integrated digital systems. Sub-platforms include:

| Platform | Full Name | Function |
|----------|-----------|----------|
| **HEMIS** | Higher Education Management Information System | Annual institutional data collection |
| **HEIDA** | Higher Education Institution Data Analytics | Data analytics for HEIs, programs, personnel |
| **SOAIS** | Special Order Application & Issuance System | Processing of special orders (graduation) |
| **eCAV** | Electronic Certification, Authentication & Verification | Digital verification of academic records |
| **DEXUS** | (Data Exchange) | Unified data exchange for CHED services |

#### HEMIS Data Collection Requirements

HEIs must submit annual data through HEMIS. Required forms differ by institution type:

**SUCs (7 forms):**
| Form | Content |
|------|---------|
| Form A | Institutional Profile |
| Form B | Programs Offered, Enrollment Data, Graduate Data |
| Form E1 | Faculty-related data |
| Form E2 | Faculty and personnel data |
| Research Extension Form | Research and extension activities |
| Form GH | Allotment and expenditures |
| Graduate List Form | Comprehensive list of graduates |

**Private HEIs and LUCs (4 forms):**
| Form | Content |
|------|---------|
| Form A | Institutional Profile |
| Form BC | Programs Offered, Enrollment Data, Graduate Data |
| Form E5 | Faculty Profile |
| Graduate List Form | Comprehensive list of graduates |

- **Legal basis:** CMO No. 45, Series of 2016 mandates CHED to collect, collate, store, and
  disseminate higher education data.
- **SMIS implication:** The system must be able to generate HEMIS-compatible data exports.
  Enrollment counts, program data, graduate lists, and faculty profiles must be extractable
  in the required formats.

#### eCAV System
- Digitizes issuance and verification of academic records
- Reduces processing time and prevents document fraud
- CHED and DICT collaboration for national rollout
- **SMIS implication:** System should support eCAV-compatible record formats and potentially
  API integration for credential verification.

### 1.9 Student Records Retention and Disposal

Per CHED regulations and RA 9470 (National Archives of the Philippines Act of 2007):

| Record Type | Retention Period |
|-------------|-----------------|
| Core academic records (TOR, diploma records) | Permanent |
| Transfer credentials (honorable dismissal) | 10 years minimum |
| Enrollment forms and registration documents | Per institutional policy (minimum 5 years recommended) |
| Disciplinary records | Per institutional policy |
| Disposal logs | 5 years after disposal |

- **CHED En Banc Resolution No. 170-2018:** Updated retention schedules aligned with
  Data Privacy Act amendments
- Disposal prohibited for records involved in ongoing legal cases or audits
- Secure disposal methods required (shredding, digital erasure)
- National Archives of the Philippines (NAP) approval required before disposal of
  government records

---

## 2. DepEd (Department of Education)

### 2.1 Learner Reference Number (LRN)

- **What:** A permanent 12-digit number assigned to every learner in the Philippine basic
  education system
- **Managed by:** DepEd Learner Information System (LIS)
- **Scope:** All public and private elementary and secondary schools, including those operated
  by SUCs, LUCs, and HEIs
- **Permanence:** The LRN stays with the learner throughout basic education regardless of
  school transfers or promotion to secondary level
- **Documents containing LRN:** Permanent Record (Form 137), Report Card (Form 138),
  ALS Certificate, Diploma, National Achievement Test results

#### SMIS Implications
- The SMIS should capture the LRN during enrollment of incoming freshmen as a link to
  K-12 records
- LRN can serve as a cross-reference for verifying basic education completion
- Useful for validating senior high school track/strand for program eligibility
- The receiving HEI does not issue LRNs — it only records the existing one

### 2.2 Transfer Credentials

- **Form 137 (Permanent Record):** Official transcript of K-12 academic records
- **Form 138 (Report Card):** Year-end performance summary
- **Senior High School Diploma:** Required for HEI admission
- **SMIS implication:** System should have fields to record and verify these incoming
  documents during the admission process.

---

## 3. Data Privacy Act (RA 10173) and NPC Guidelines

### 3.1 Republic Act No. 10173 — Data Privacy Act of 2012

- **Effective:** September 8, 2012
- **Implementing Rules and Regulations:** NPC Circular 16-01 to 16-04
- **Enforcing body:** National Privacy Commission (NPC)

#### Lawful Bases for Processing Student Data

An SMIS may process student personal data under the following legal bases:

1. **Consent** — freely given, specific, informed, and evidenced (e.g., signed forms)
2. **Contract** — necessary to fulfill enrollment or educational service contracts
3. **Legal obligation** — compliance with laws like RA 10931 (free tuition reporting),
   CHED data collection mandates
4. **Vital interests** — protection of student's life or health
5. **Public authority** — for public HEIs exercising official functions
6. **Legitimate interest** — institutional interest that does not override student rights

#### Consent Requirements for Minors

- **Students under 18:** Parental or guardian consent required for data processing
- **Students 18 and above:** Can provide their own consent
- **SMIS implication:** The enrollment workflow must distinguish between minor and adult
  students and capture appropriate consent accordingly.

#### Student Data Rights

Students (and parents/guardians of minors) have the right to:
1. **Be informed** — know what data is collected and why
2. **Access** — request copies of their personal data
3. **Rectification** — correct inaccuracies in their records
4. **Erasure/blocking** — demand deletion of unlawfully processed data
5. **Data portability** — obtain data in a structured, commonly used format
6. **Damages** — claim compensation for violations
7. **Object** — object to processing in certain circumstances

#### Organizational Requirements

HEIs operating an SMIS must:
- Register their data processing systems with the NPC
- Appoint a Data Protection Officer (DPO)
- Maintain a Record of Processing Activities (ROPA)
- Implement organizational, physical, and technical security measures
- Report data breaches to the NPC within 72 hours
- Conduct Privacy Impact Assessments (PIAs) for new systems

#### Penalties

- Administrative fines up to PHP 5 million per violation
- Criminal penalties: imprisonment of 1–6 years and fines of PHP 500,000–4,000,000
  depending on the offense
- Offenses include unauthorized processing, accessing due to negligence, improper disposal,
  unauthorized disclosure

### 3.2 NPC Data Privacy Council — Education Sector Advisory No. 2020-1

- **Purpose:** Guidelines for protecting student privacy during online/flexible learning
- **Key provisions for SMIS:**

| Area | Requirement |
|------|-------------|
| Webcam/recording | Parental consent required for minors; consider guardian presence |
| Learning management systems | Must comply with data privacy principles |
| Storage of personal data | Secure storage with access controls |
| Proctoring | Must be proportional; cannot be excessively invasive |
| Online decorum | Clear policies on data collection during online activities |
| Social media | Unauthorized sharing of student grades/photos prohibited |

- **Core principles emphasized:** Accountability, transparency, legitimate purpose,
  proportionality, sensitivity of educational data
- **Education data classified as sensitive personal information** under certain circumstances

### 3.3 Privacy Impact Assessment (PIA) Requirements

Per NPC guidelines, a PIA must be conducted for:
- Every processing system involving personal data
- Off-the-shelf software and data processing systems
- New data processing initiatives

A PIA must evaluate:
- Nature of personal data to be protected
- Personal data flow through the system
- Risks to privacy and security
- Current data privacy best practices
- Cost of security implementation
- Size and resources of the organization

**SMIS implication:** Before deploying an SMIS, the institution must conduct a PIA and
document the findings. The PIA should be updated when significant system changes occur.

### 3.4 Data Retention and Disposal Alignment

- Retention periods must align with legitimate purposes
- CHED academic record retention requirements take precedence for academic records
- Non-academic personal data should be disposed of when no longer needed
- Consent forms for data processing must be retained as evidence
- Cross-border transfer of student records requires additional safeguards (NPC approval
  or adequacy determination)

---

## 4. Philippine Qualifications Framework (PQF)

### 4.1 RA 10968 — PQF Act

- **Signed:** January 16, 2018
- **Implementing agencies:** DepEd, TESDA, CHED, PRC, DOLE
- **Coordinating body:** PQF-National Coordinating Council (PQF-NCC)

### 4.2 Framework Structure

The PQF is an 8-level framework with Senior High School as the foundation:

| Level | Qualification | Subsystem |
|-------|--------------|-----------|
| 1 | National Certificate I (NC I) | TESDA |
| 2 | National Certificate II (NC II) | TESDA |
| 3 | National Certificate III (NC III) | TESDA |
| 4 | National Certificate IV (NC IV) | TESDA |
| 5 | Diploma | TESDA/CHED (interface) |
| 6 | Baccalaureate (Bachelor's Degree) | CHED |
| 7 | Post-Baccalaureate / Master's Degree | CHED |
| 8 | Doctoral Degree | CHED |

Descriptors are differentiated along three domains:
1. Knowledge, skills, and values
2. Application
3. Degree of independence

### 4.3 SMIS Implications

- **Program registration:** Each academic program must be mapped to a PQF level
- **Curriculum management:** Learning outcomes must align with PQF level descriptors
- **Credit transfer:** PQF levels facilitate equivalency and credit recognition across
  institutions and subsystems
- **Microcredentials:** Must map to PQF Levels 5–8 (per CMO No. 1, s. 2025)
- **Pathways and equivalencies:** System should support tracking of qualification pathways
  including lateral and vertical mobility
- **National Registry of Qualifications:** PQF-NCC maintains a national registry; the SMIS
  should generate data compatible with this registry

---

## 5. Accreditation Bodies (AACCUP, PACUCOA, PAASCU)

### 5.1 Overview of Philippine Accreditation Bodies

| Body | Full Name | Accredits |
|------|-----------|-----------|
| **AACCUP** | Accrediting Agency of Chartered Colleges and Universities in the Philippines | SUCs and government HEIs |
| **PACUCOA** | Philippine Association of Colleges and Universities Commission on Accreditation | Private HEIs (PACU member schools) |
| **PAASCU** | Philippine Accrediting Association of Schools, Colleges, and Universities | Private HEIs (broader membership) |

All three are recognized by CHED through the Federation of Accrediting Agencies of the
Philippines (FAAP).

### 5.2 Accreditation Levels

| Level | Significance | Duration |
|-------|-------------|----------|
| **Candidate** | Preliminary status; indicates readiness for accreditation | Varies |
| **Level I** | Initial accredited status | 3 years |
| **Level II** | Re-accredited status; demonstrates sustained quality | 3–5 years |
| **Level III** | High quality status; grants partial autonomy and deregulation | 5 years |
| **Level IV** | Highest accreditation; grants full autonomy, authority to open new programs without CHED approval | 5 years |

### 5.3 AACCUP Accreditation Areas (10 Areas for Program Accreditation)

1. Faculty
2. Curriculum and Instruction
3. Support to Students
4. Research
5. Extension and Community Involvement
6. Library
7. Physical Plant and Facilities
8. Laboratories
9. Administration
10. (Additional area varies by program)

**For Institutional Accreditation (9 Areas):**
1. Governance and Management
2. Teaching, Learning, and Evaluation
3. Faculty and Staff
4. Research
5. Extension, Consultancy, and Linkages
6. Support to Students
7. Library
8. Infrastructure and Other Learning Resources
9. Quality Assurance Culture

### 5.4 SMIS-Relevant Accreditation Requirements

Accreditation bodies evaluate:

- **Student records management:** Completeness, accuracy, security, and accessibility of
  student academic records
- **Student services:** Tracking of guidance, counseling, health services, scholarship
  administration
- **Administration:** Evidence of systematic data-driven decision making
- **Teaching and learning:** Assessment records, grade distribution analysis, retention and
  completion rates
- **Research:** Student research output tracking (especially for graduate programs)
- **Quality assurance:** Evidence of continuous improvement through data analysis

**SMIS implication:** The system should be able to generate reports and evidence documents
for each accreditation area. Key metrics include enrollment trends, retention rates,
graduation rates, grade distributions, faculty-student ratios, and student services
utilization.

---

## 6. Key Republic Acts

### 6.1 RA 10931 — Universal Access to Quality Tertiary Education Act (2017)

- **Signed:** August 3, 2017
- **IRR approved:** February 22, 2018
- **Also known as:** Free Tuition Law

#### Key Components

| Program | Description |
|---------|-------------|
| Free Tuition | Exemption from tuition and other school fees in SUCs and LUCs |
| Free TVET | Free tuition in TESDA technical-vocational training institutes |
| TES | Tertiary Education Subsidy for students in private and public HEIs |
| Student Loan Program | Government-backed student loans |

#### Student Eligibility (Free Tuition)

- Filipino citizenship
- Enrolled in a recognized SUC, LUC, or state-run TVI
- Must not hold an existing bachelor's degree or equivalent
- Must adhere to institutional retention policies
- Must complete degree within a reasonable time frame

#### SMIS Data Requirements

The system must track and report:
- **Citizenship verification** — Filipino citizenship status for free tuition eligibility
- **Prior degree status** — whether the student already holds a bachelor's degree
- **Enrollment in SUC/LUC** — institutional classification
- **Retention compliance** — academic standing relative to retention policies
- **Tuition subsidy amounts** — exact amount of tuition subsidy per student
- **TES recipient tracking** — identification and monitoring of TES beneficiaries
- **StuFAP tracking** — all student financial assistance programs received

#### Reporting Requirements

- SUCs/LUCs must report tuition payments and contributions to CHED
- Governing boards compute annual budget based on projected enrollee count
- CHED devises reporting mechanisms for exact tuition subsidy amounts
- Annual reports to UniFAST Board from implementing agencies

### 6.2 RA 10687 — UniFAST Act (2015)

- **Signed:** October 15, 2015
- **Purpose:** Unifies all government-funded student financial assistance programs (StuFAPs)
  under one coordinating body

#### Coverage

- Scholarships
- Grants-in-Aid
- Student Loans
- Government partnership programs

#### Implementing Agencies

CHED, TESDA, DOST, DOLE, DSWD, DND, DA, DILG, DENR, NCIP, OPAPP, and both
Houses of Congress

#### SMIS Implications

- Track all financial assistance received by each student across all StuFAP modalities
- Maintain separate accounting per implementing agency
- Support eligibility verification against UniFAST criteria
- Generate reports for UniFAST Board annual reporting

### 6.3 RA 9500 — University of the Philippines Charter (2008)

- **Signed:** April 19, 2008
- **Relevance:** Reference model for SUC governance

#### Key Governance Features

- Board of Regents with CHED Chair as Chairperson
- University Council (Chancellor + faculty of assistant professor rank and above)
- Democratic governance based on collegiality, representation, accountability, transparency
- Student councils at college, constituent university, and system levels

#### SMIS Implications

- While specific to UP, RA 9500 serves as a governance model for other SUCs
- Demonstrates the importance of student council representation tracking
- Multi-campus (constituent university) structure requires system support for federated
  governance and consolidated reporting

### 6.4 RA 10627 — Anti-Bullying Act of 2013

- **Signed:** September 12, 2013
- **Scope:** Elementary and secondary schools (NOT higher education directly)
- **IRR updated:** March 25, 2025

#### Key Provisions

- Schools must adopt anti-bullying policies
- Anti-bullying policies must be reported to division superintendents
- Annual reporting of bullying incidents and statistics required
- Internal reporting: any school member must immediately report bullying witnessed
- Multi-school incidents require inter-school notification

#### SMIS Implications

- **Limited direct applicability** to HEIs since the law covers K-12
- However, many HEIs voluntarily adopt anti-bullying policies
- CHED may issue separate guidance for HEIs on student welfare
- If the HEI operates a K-12 program (lab school), the SMIS must support bullying
  incident tracking and reporting for that component
- Student welfare/disciplinary modules should accommodate anti-bullying case management

### 6.5 RA 7277 (as amended by RA 9442 and RA 10754) — Magna Carta for Persons with Disability

#### Education Provisions

- **Non-discrimination:** Unlawful to deny admission to any course by reason of disability
- **Financial assistance:** Scholarships, student loans, subsidies for economically
  marginalized PWD students in post-secondary/tertiary education
- **Discount:** 20% discount on educational fees and related services (per RA 9442/RA 10754)
- **Applicability:** Both public and private education at all levels

#### SMIS Implications

- **PWD identification:** System must capture PWD status and PWD ID number
- **Discount computation:** Automated 20% discount on applicable fees
- **Accessibility tracking:** Document accommodations provided
- **Scholarship eligibility:** Flag PWD students for available financial assistance programs
- **Reporting:** Generate PWD enrollment statistics for CHED/HEMIS reporting

### 6.6 RA 8972 (as amended by RA 11861) — Solo Parents Welfare Act

- **Original law:** RA 8972 (Solo Parents' Welfare Act of 2000)
- **Amendment:** RA 11861 (Expanded Solo Parents Welfare Act, June 4, 2022)

#### Education Benefits

- Full scholarships for one child of a solo parent in HEIs and TVIs
- Child must be: dependent on the solo parent, unmarried, unemployed, 22 years old or below
- 10% discount on basic commodities (milk, medicines) for the solo parent
- Solo parents who are also PWDs may receive both sets of benefits

#### SMIS Implications

- **Solo parent status tracking:** Capture whether the student is a dependent of a solo parent
- **Solo Parent ID verification:** Record Solo Parent ID number
- **Scholarship eligibility:** Flag eligible students for solo parent scholarship programs
- **Discount integration:** Where applicable, compute fee adjustments
- **Dual-benefit tracking:** Handle cases where PWD and solo parent benefits overlap

### 6.7 RA 9470 — National Archives of the Philippines Act (2007)

- Establishes the National Archives as custodian of public records
- Mandates records disposition schedules for government agencies (including public HEIs)
- Records cannot be disposed of without NAP approval
- Violations carry administrative or criminal penalties

#### SMIS Implications

- Public HEI records are government records subject to NAP oversight
- Disposal workflows in the SMIS must include NAP approval steps
- System must maintain disposal logs for audit purposes

---

## 7. SMIS Compliance Checklist

### 7.1 Data Collection and Enrollment

- [ ] Capture Filipino citizenship status for RA 10931 eligibility
- [ ] Record DepEd Learner Reference Number (LRN) for incoming freshmen
- [ ] Verify and store K-12 credentials (Form 137, Form 138, SHS Diploma)
- [ ] Capture PWD status and PWD ID number
- [ ] Capture Solo Parent dependent status and Solo Parent ID
- [ ] Obtain and store data privacy consent forms (parental consent for minors under 18)
- [ ] Record prior degree status (for free tuition eligibility check)
- [ ] Track all financial assistance/scholarship programs per student (StuFAPs, TES, etc.)
- [ ] Support cross-enrollment and transfer workflows with proper credential verification

### 7.2 Academic Records Management

- [ ] Support institutional grading system (configurable: numerical, letter, percentage)
- [ ] Compute GWA/GPA per institutional rules
- [ ] Track academic standing: regular, probation, dismissed, leave of absence
- [ ] Apply retention policies per program
- [ ] Track incomplete (INC) grades with resolution deadlines
- [ ] Support Latin honors computation (per CMO No. 8 and institutional policies)
- [ ] Map programs to PQF levels (Levels 5–8)
- [ ] Track microcredentials and stackable qualifications (per CMO No. 1, s. 2025)
- [ ] Support multiple learning modalities per course (face-to-face, online, blended)
- [ ] Maintain permanent academic records with proper retention schedules

### 7.3 CHED Reporting and Data Exchange

- [ ] Generate HEMIS-compatible data exports (Forms A, B/BC, E1/E2/E5, GH, Graduate List)
- [ ] Support eCAV-compatible credential formats
- [ ] Generate enrollment statistics disaggregated by program, year level, sex, etc.
- [ ] Track and report free tuition subsidy amounts (RA 10931)
- [ ] Report financial assistance program data to UniFAST
- [ ] Support SOAIS (Special Order) processing for graduation
- [ ] Integrate with or export to CHED OneTouch/DEXUS platform

### 7.4 Data Privacy Compliance (RA 10173)

- [ ] Register data processing systems with NPC
- [ ] Appoint and document Data Protection Officer (DPO) role
- [ ] Maintain Record of Processing Activities (ROPA)
- [ ] Conduct Privacy Impact Assessment (PIA) before deployment
- [ ] Implement role-based access controls
- [ ] Encrypt personal data at rest and in transit
- [ ] Support data subject rights: access, rectification, erasure, portability
- [ ] Implement 72-hour breach notification workflow
- [ ] Maintain audit trails for all data access and modifications
- [ ] Implement secure disposal procedures for digital records
- [ ] Obtain proper consent (distinguish minor vs. adult students)
- [ ] Classify and protect sensitive personal information appropriately

### 7.5 Accreditation Support

- [ ] Generate enrollment trend reports
- [ ] Generate retention and completion rate reports
- [ ] Generate grade distribution analysis reports
- [ ] Track faculty-student ratios
- [ ] Document student services utilization
- [ ] Support evidence generation for all 10 AACCUP/PACUCOA accreditation areas
- [ ] Maintain historical data for trend analysis across accreditation cycles

### 7.6 Fee Management and Discounts

- [ ] Implement free tuition computation for eligible SUC/LUC students
- [ ] Apply 20% PWD discount on applicable fees
- [ ] Track solo parent dependent scholarship eligibility
- [ ] Maintain audit trail for all fee adjustments and discounts
- [ ] Generate financial reports per RA 10931 requirements

---

## Appendix A: Summary of Key Laws and Regulations

| Law/Regulation | Year | Subject |
|----------------|------|---------|
| RA 7722 | 1994 | Higher Education Act (CHED creation) |
| RA 7277 | 1992 | Magna Carta for Persons with Disability |
| RA 8972 | 2000 | Solo Parents' Welfare Act |
| RA 9442 | 2007 | Amendment to RA 7277 (PWD 20% discount) |
| RA 9470 | 2007 | National Archives of the Philippines Act |
| RA 9500 | 2008 | University of the Philippines Charter |
| CMO No. 40, s. 2008 | 2008 | MORPHE (Manual of Regulations for Private HE) |
| RA 10173 | 2012 | Data Privacy Act |
| CMO No. 46, s. 2012 | 2012 | HEI Typology and Quality Assurance |
| RA 10627 | 2013 | Anti-Bullying Act |
| RA 10687 | 2015 | UniFAST Act |
| CMO No. 45, s. 2016 | 2016 | HEMIS data collection mandate |
| RA 10931 | 2017 | Free Tuition Law (UAQTEA) |
| RA 10754 | 2016 | Amendment to RA 7277 (expanded PWD benefits) |
| RA 10968 | 2018 | Philippine Qualifications Framework Act |
| CHED En Banc Res. 170-2018 | 2018 | Updated records retention schedules |
| CMO No. 15, s. 2019 | 2019 | Graduate Programs PSG |
| NPC Education Sector Advisory 2020-1 | 2020 | Student privacy in online learning |
| CMO No. 4, s. 2020 | 2020 | Flexible Learning Guidelines |
| RA 11861 | 2022 | Expanded Solo Parents Welfare Act |
| CMO No. 10, s. 2023 | 2023 | Student Interchange Assistance Program |
| CMO No. 1, s. 2025 | 2025 | Microcredentials Guidelines |

## Appendix B: Key Regulatory Contacts and Portals

| Entity | Portal | Purpose |
|--------|--------|---------|
| CHED | ched.gov.ph | Policy issuances, CMOs |
| CHED OneTouch | onetouch.ched.gov.ph | Integrated digital services portal |
| HEIDA | heida.ched.gov.ph | Data analytics platform |
| eCAV | ecav.ched.gov.ph | Credential verification |
| NPC | privacy.gov.ph | Data privacy compliance, PIAs |
| PQF-NCC | pqf.gov.ph | Qualifications framework |
| UniFAST | unifast.gov.ph | Student financial assistance |
| AACCUP | aaccup.com / aaccupqa.org.ph | SUC accreditation |
| PACUCOA | pacucoa.com | Private HEI accreditation |
| PAASCU | paascu.org.ph | Private HEI accreditation |

## Appendix C: Research Gaps and Recommendations

The following areas require further investigation, ideally through direct engagement with
the relevant agencies:

1. **CHED API specifications:** No public API documentation was found for HEMIS, eCAV, or
   DEXUS. Direct engagement with CHED's IT division is recommended to determine integration
   options.

2. **MORPHE detailed sections:** The full text of CMO No. 40, s. 2008 should be obtained
   and reviewed section-by-section for detailed student records and grading provisions.
   Available at: https://ched.gov.ph/wp-content/uploads/2017/10/CMO-No.40-s2008.pdf

3. **AACCUP/PACUCOA accreditation manuals:** Specific requirements for information systems
   and records management are not publicly available in detail. Accreditation manuals should
   be obtained directly from these bodies.

4. **NPC Education Sector Code of Conduct:** The NPC initiated development of a Code of
   Conduct for the education sector. Current status and provisions should be verified with
   the NPC.

5. **CHED Memorandum Order on Student Services:** CMO No. 21, s. 2003 provides guidelines
   on student services. The full text should be obtained for detailed student welfare
   tracking requirements.

6. **SUC-specific regulations:** Individual SUC charters (beyond UP's RA 9500) may contain
   specific student records and governance provisions that affect SMIS design.

7. **Safe Spaces Act (RA 11313):** This 2019 law addresses gender-based harassment including
   in educational settings. Its reporting requirements should be evaluated for SMIS
   integration.

8. **Mental Health Act (RA 11036):** This 2018 law requires educational institutions to
   implement mental health programs. Student wellness tracking features may need to comply
   with its provisions.

---

## Sources

- [CHED Memoranda on Student Records Management](https://www.lawyer-philippines.com/articles/ched-memoranda-on-student-records-management-retention-and-disposal-in-the-philippines)
- [CMO No. 40, s. 2008 — MORPHE](https://ched.gov.ph/cmo-40-s-2008/)
- [MORPHE Full Text (LegalDex)](https://legaldex.com/laws/manual-of-regulations-for-private-higher-education-of-2008)
- [CHED Official Website](https://ched.gov.ph/)
- [CHED OneTouch Portal](https://onetouch.ched.gov.ph/about)
- [HEIDA Platform](https://heida.ched.gov.ph/)
- [eCAV System](https://ecav.ched.gov.ph/)
- [SUCs/HEMIS Web-Based Data Collection System](https://itdc.up.edu.ph/projects/design-and-implementation-of-the-sucs-hemis-web-based-data-collection-system)
- [HEMIS Annual Data Collection Orientation (CHED RO 11)](https://ro11.ched.gov.ph/2024/10/25/online-orientation-for-the-annual-data-collection-of-hemis-for-sy-2024-2025/9581/uncategorized/)
- [Digital Transformation of Philippine Higher Education (World Bank)](https://documents1.worldbank.org/curated/en/099925001062333685/pdf/P17757402843a10c90b3e30308406a38304.pdf)
- [Data Privacy Act (RA 10173) Explained](https://www.respicio.ph/commentaries/ra-10173-data-privacy-act-explained-philippines)
- [NPC Data Privacy Council Education Sector Advisory No. 2020-1](https://privacy.gov.ph/wp-content/uploads/2023/05/DP-Council-Education-Sector-Advisory-No.-2020-1.pdf)
- [NPC Privacy Impact Assessment Guidelines](https://privacy.gov.ph/wp-content/uploads/2022/01/NPC_PIA_0618.pdf)
- [NPC Online Learning Privacy Guidelines](https://privacy.gov.ph/online-learning-guidelines-issued-to-help-protect-student-privacy-and-reduce-data-breaches-in-schools/)
- [UP Diliman Data Privacy Portal — Student Privacy Policy](https://privacy.upd.edu.ph/privacy-policy-for-students-parents-and-guardians-2/)
- [DepEd Data Privacy Notice](https://www.deped.gov.ph/about-deped/data-privacy-notice/)
- [Philippine Qualifications Framework (PQF)](https://pqf.gov.ph/)
- [RA 10968 — PQF Act (Full Text)](https://pqf.gov.ph/Uploads/Legal%20Basis/RA%2010968.pdf)
- [PQF IRR (LegalDex)](https://legaldex.com/laws/implementing-rules-and-regulations-irr-of-the-pqf-act)
- [AACCUP Accreditation](http://www.aaccupqa.org.ph/index.php/aaccup-accreditation)
- [PACUCOA Accreditation](https://www.pacucoa.com/copy-of-about-accreditation)
- [PAASCU](https://paascu.org.ph/)
- [RA 7722 (Higher Education Act) — Full Text](https://lawphil.net/statutes/repacts/ra1994/ra_7722_1994.html)
- [RA 10931 (Free Tuition Law) — Official Gazette](https://www.officialgazette.gov.ph/2017/08/03/republic-act-no-10931/)
- [RA 10931 IRR (LegalDex)](https://legaldex.com/laws/implementing-rules-and-regulations-of-republic-act-no-10931-universal)
- [RA 10687 (UniFAST Act) — Full Text](https://lawphil.net/statutes/repacts/ra2015/ra_10687_2015.html)
- [UniFAST Official Website](https://unifast.gov.ph/uni-hist.html)
- [RA 9500 (UP Charter) — Official Gazette](https://www.officialgazette.gov.ph/2008/04/19/republic-act-no-9500/)
- [RA 10627 (Anti-Bullying Act) — Full Text](https://lawphil.net/statutes/repacts/ra2013/ra_10627_2013.html)
- [RA 7277 (Magna Carta for PWDs)](https://hrlibrary.umn.edu/research/Philippines/RA%207277%20-%20Magna%20Carta%20of%20Disabled%20Persons.pdf)
- [RA 9442 IRR (NCDA)](https://ncda.gov.ph/disability-laws/implementing-rules-and-regulations-irr/implementing-rules-and-regulations-of-republic-act-no-9442/)
- [RA 11861 (Expanded Solo Parents Welfare Act)](https://pcw.gov.ph/republic-act-no-11861-expanded-solo-parents-welfare-act/)
- [DepEd Learner Reference Number (LRN)](https://www.teacherph.com/deped-learner-reference-number-lrn/)
- [Learner Information System (LIS)](https://alapan1es.com/2021/08/02/learner-information-system-and-learner-reference-number/)
- [CHED Handbook on Typology](https://ched.gov.ph/wp-content/uploads/Handbook-on-Typology-Outcomes_June-20-version.pdf)
- [CMO No. 15, s. 2019 — Graduate Programs PSG](https://ched.gov.ph/wp-content/uploads/CMO-No.-15-Series-of-2019-%E2%80%93-Policies-Standards-and-Guidelines-for-Graduate-Programs-Updated.pdf)
- [CHED Grading System Overview](https://gwa-calculator.net/colleges-grading-system-in-philippine/)
- [EDCOM 2: UniFAST Implementation Status](https://edcom2.gov.ph/most-responsibilities-of-unifast-under-ra-10687-still-unimplemented-10-years-later/)
- [CHED Statistical Bulletin AY 2023-2024](https://chedcaraga.ph/wp-content/uploads/2024/04/STATISTICAL-BULLETIN-AY-2023-2024-Hires.pdf)
