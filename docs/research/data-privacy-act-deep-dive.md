# Deep Research: Philippine Data Privacy Act (RA 10173) for Student Information Systems

Research compiled for eSMIS data privacy principle document.
Date: 2026-03-09

---

## Table of Contents

1. [RA 10173 Full Text Analysis — Key Sections Affecting SIS](#1-ra-10173-full-text-analysis)
2. [NPC Implementing Rules and Regulations (IRR)](#2-npc-implementing-rules-and-regulations)
3. [NPC Education Sector Guidance](#3-npc-education-sector-guidance)
4. [PII Classification for Student Data](#4-pii-classification-for-student-data)
5. [Consent Management Deep Dive](#5-consent-management-deep-dive)
6. [Data Subject Rights Implementation](#6-data-subject-rights-implementation)
7. [Security Measures Required by Law](#7-security-measures-required-by-law)
8. [Data Breach Management](#8-data-breach-management)
9. [Cross-Border Data Transfer](#9-cross-border-data-transfer)
10. [Data Retention and Disposal](#10-data-retention-and-disposal)
11. [Privacy Impact Assessment (PIA)](#11-privacy-impact-assessment)
12. [Accountability and Governance](#12-accountability-and-governance)

---

## 1. RA 10173 Full Text Analysis

**Law:** Republic Act No. 10173 (Data Privacy Act of 2012)
**Effective:** September 8, 2012
**Enforcing Body:** National Privacy Commission (NPC)
**IRR:** Published August 25, 2016 (as amended)

### Chapter III: Processing of Personal Information (Sections 11-12)

#### Section 11 — General Data Privacy Principles

All processing of personal data must adhere to three fundamental principles:

| Principle | Meaning |
|-----------|---------|
| **Transparency** | The data subject must be aware of the nature, purpose, and extent of the processing, including risks and safeguards, the identity of the PIC, and their rights |
| **Legitimate Purpose** | Processing must be compatible with a declared, specified, and legitimate purpose; further processing must be compatible with the original purpose |
| **Proportionality** | Processing must be adequate, relevant, suitable, necessary, and not excessive in relation to a declared and specified purpose |

The PIC must ensure implementation of these principles and is accountable for complying with the requirements of the Act.

#### Section 12 — Criteria for Lawful Processing of Personal Information

Six lawful bases for processing regular (non-sensitive) personal information:

1. **Consent** — freely given, specific, informed consent evidenced by written, electronic, or recorded means
2. **Contract** — necessary for performance of a contract or pre-contractual steps at the data subject's request
3. **Legal obligation** — necessary for compliance with a legal obligation to which the PIC is subject
4. **Vital interests** — necessary to protect vitally important interests of the data subject, including life and health
5. **Public authority** — necessary for a public authority or the PIC to perform functions of public authority (constitutional/statutory mandate)
6. **Legitimate interest** — necessary for purposes of legitimate interests pursued by the PIC or third parties, except where overridden by fundamental rights and freedoms of the data subject (requires balancing test)

**SIS relevance:** Most student data processing will fall under contract (enrollment agreement), legal obligation (CHED/DepEd reporting), or consent. Legitimate interest may apply to analytics and institutional research where data is anonymized.

### Chapter IV: Processing of Sensitive Personal Information (Sections 13-14)

#### Section 13 — Sensitive Personal Information and Privileged Information

Processing of sensitive personal information (SPI) is **generally prohibited** except when:

| Exception | Details |
|-----------|---------|
| **(a) Consent** | Data subject has given specific consent prior to processing |
| **(b) Existing law** | Processing is provided for by existing laws and regulations, with those regulatory enactments guaranteeing the protection of the SPI |
| **(c) Life and health** | Necessary to protect life and health, when the data subject cannot legally or physically give consent |
| **(d) Medical treatment** | Necessary for medical treatment, carried out by a medical practitioner or institution, with adequate safeguards |
| **(e) Legal proceedings** | Necessary for the protection of lawful rights and interests in court proceedings, establishment/exercise/defense of legal claims, or when provided to government pursuant to constitutional/statutory mandate |
| **(f) Medical treatment by medical practitioners** | Processing by medical practitioners or institutions for adequate medical care, with adequate level of protection |

For **privileged information**, all parties to the exchange must consent prior to processing.

#### Section 14 — Subcontract of Personal Information

A PIC may subcontract the processing of personal information, provided the PIC ensures that proper safeguards are in place, that the processor adheres to the Act, and that the rights of data subjects are upheld.

**SIS relevance:** Student grades, health records, disciplinary records, and enrollment data are all SPI. Processing requires one of the Section 13 exceptions — typically consent at enrollment plus legal obligation for CHED reporting.

### Chapter V: Rights of Data Subjects (Sections 16-18)

#### Section 16 — Rights of the Data Subject

Eight enumerated rights:

| # | Right | Description |
|---|-------|-------------|
| 1 | **Right to be informed** | Data subject must be informed before processing: what data is collected, why, how it will be used, who will receive it, retention periods, and the existence of their rights |
| 2 | **Right to access** | Right to reasonable access to personal data being processed, including what data is held, sources, recipients, manner of processing, reasons for disclosure, automated processing information, and date of last access/modification |
| 3 | **Right to object** | Right to object to processing, including processing for direct marketing, automated processing, or profiling |
| 4 | **Right to erasure or blocking** | Right to suspend, withdraw, block, remove, or destroy personal data from the PIC's filing system (both live and backup), upon determination that data is incomplete, outdated, false, unlawfully obtained, used for unauthorized purposes, or no longer necessary for the declared purpose |
| 5 | **Right to rectification** | Right to dispute inaccuracy or error and have the PIC correct it immediately, unless the request is vexatious or unreasonable |
| 6 | **Right to data portability** | Where data is processed electronically, right to obtain a copy in a structured, commonly used electronic format, and to have data transmitted to another PIC |
| 7 | **Right to damages** | Right to be indemnified for any damages sustained due to inaccurate, incomplete, outdated, false, unlawfully obtained, or unauthorized use of personal data |
| 8 | **Right to file a complaint** | Right to lodge a complaint with the NPC |

#### Section 17 — Transmissibility of Rights

Lawful heirs and assigns may invoke the data subject's rights after death or when the data subject is incapacitated.

**SIS relevance:** In an education context, parents/guardians exercise rights on behalf of minor students. Heirs may request academic records of deceased students.

#### Section 18 — Right to Data Portability

Specifically requires that where personal information is processed by electronic means and in a structured, commonly used format, the data subject may obtain from the PIC a copy of data in electronic/structured format that allows further use. The NPC may specify the electronic format and technical standards.

**SIS relevance:** The system must support export of student personal data in machine-readable format (CSV, JSON, XML) on request.

### Chapter VI: Security Measures (Sections 20-23)

#### Section 20 — Security of Personal Information

PICs must implement **reasonable and appropriate** measures to protect personal information against:
- Natural dangers (accidental loss, destruction)
- Human dangers (unlawful access, fraudulent misuse, unlawful destruction, alteration, contamination)

Security measures must include:
1. **Organizational measures** — privacy policies, employee training, designation of DPO
2. **Physical measures** — locked facilities, restricted access to workstations
3. **Technical measures** — encryption, firewalls, access controls, monitoring

#### Section 21 — Principle of Accountability

Each PIC is responsible for personal information under its control, including information transferred to a third party for processing, **whether domestically or internationally**, subject to cross-border arrangement guidelines.

#### Section 22 — Security of Sensitive Personal Information in Government

Government agencies must secure SPI using the **most appropriate standard recognized by the ICT industry**. The head of each government agency is personally responsible for compliance.

#### Section 23 — Requirements Relating to Access by Agency Personnel

Government employees may not access SPI unless they have adequate security clearance and are subject to confidentiality obligations. Access to SPI on grounds of national security requires written order from the NPC.

### Chapter VII: Accountability (Section 29 — actually this is the Unauthorized Access section)

**Note:** The Act's accountability principle is embedded throughout, particularly in Sections 20-21 and the IRR. Section 29 of the Act actually covers unauthorized access/intentional breach penalties.

### Chapter VIII: Penalties (Sections 25-34)

| Section | Offense | Personal Info Penalty | Sensitive Personal Info Penalty |
|---------|---------|----------------------|-------------------------------|
| **25** | Unauthorized processing | 1-3 years + PHP 500K-2M | 3-6 years + PHP 500K-4M |
| **26** | Accessing due to negligence | 1-3 years + PHP 500K-2M | 3-5 years + PHP 500K-2M |
| **27** | Improper disposal | 6 months-2 years + PHP 100K-500K | 3-6 years + PHP 100K-1M |
| **28** | Unauthorized purposes | 1.5-5 years + PHP 500K-1M | 2-7 years + PHP 500K-2M |
| **29** | Unauthorized access or intentional breach | 1-3 years + PHP 500K-2M | |
| **30** | Concealment of security breaches | 1.5-5 years + PHP 500K-1M | |
| **31** | Malicious disclosure | 1.5-5 years + PHP 500K-1M | |
| **32** | Unauthorized disclosure | 1-3 years + PHP 500K-1M | 2-5 years + PHP 500K-2M |
| **33** | Combination or series of acts | 3-6 years + PHP 1M-5M | |
| **34** | Large-scale (involving 100+ persons) | Penalties under Sec. 25-32 maximum | |

Additional penalty provisions:
- **Section 34:** If offender is a corporation/juridical person, the penalty is imposed on responsible officers who participated or whose gross negligence allowed the offense
- **Section 34:** If offender is a juridical person, the court may suspend or revoke its rights under the Act
- **Section 34:** If offender is an alien, deportation follows after serving the penalties
- **Section 36:** Penalties for SPI violations involving minors increase by **50%** (critical for SIS)

#### Administrative Fines (NPC Circular 2022-01)

Separate from criminal penalties, the NPC can impose administrative fines effective August 27, 2022:

| Severity | Fine Range |
|----------|-----------|
| Grave infractions | 0.5% to 3% of annual gross income |
| Major infractions | 0.25% to 2% of annual gross income |
| Other infractions | PHP 50,000 to PHP 200,000 |
| **Maximum cap** | **PHP 5,000,000 per single act or omission** |

Factors in determining fines: categories of data affected, mitigating actions adopted, number of data subjects affected, and whether the violation was intentional or negligent.

### Sensitive Personal Information in Education Context

Under Section 3(l) of RA 10173, the following are classified as SPI:

1. **Race, ethnic origin, marital status, age, color, religious/philosophical/political affiliations** — collected in student demographic forms
2. **Health, education, genetic or sexual life** — "education" is explicitly listed, meaning **grades, academic records, transcripts, enrollment status, and disciplinary records are all SPI**
3. **Any proceeding for any offense committed or alleged** — disciplinary hearing records
4. **Government-issued IDs peculiar to an individual** — SSS, GSIS, TIN, PhilSys Number, LRN (Learner Reference Number), PWD ID, Solo Parent ID

**Critical finding:** The NPC has confirmed in advisory opinions that "student's school name, grade level, section and test scores are considered sensitive personal information as these are related to the student's education." (Advisory Opinion context from NPC advisory opinions on education)

### Privileged Information in Education Context

Privileged information = any data that constitutes privileged communication under the Rules of Court and pertinent laws. In education context:

| Type | Example |
|------|---------|
| Attorney-client privilege | Legal advice to the HEI regarding a student matter |
| Doctor-patient privilege | Health records shared with the school physician |
| Court orders | Restraining orders, custody orders affecting student enrollment |
| Active legal proceedings | Lawsuits involving students, discrimination complaints |
| Guidance counselor records | May be privileged depending on counselor's professional obligations |

Evidence gathered from privileged information is **inadmissible** except for uses in court proceedings, legal claims, and constitutional/statutory mandates.

---

## 2. NPC Implementing Rules and Regulations

### Current Status of NPC Circulars

| Circular | Subject | Status |
|----------|---------|--------|
| NPC Circular 16-01 | Security of Personal Data in Government Agencies | **Repealed by NPC Circular 2023-06** |
| NPC Circular 16-02 | Data Sharing Agreements (Government Only) | **Superseded by NPC Circular 2020-03** |
| NPC Circular 16-03 | Personal Data Breach Management | **Still in effect** |
| NPC Circular 16-04 | Rules of Procedure | **Repealed by 2021 Rules of Procedure** |
| NPC Circular 17-01 | Registration of Data Processing Systems | Amended by NPC Circular 2022-04 |
| NPC Circular 18-01 | Rules on Advisory Opinion Requests | In effect |
| NPC Circular 18-03 | (Various procedural provisions) | **Repealed by 2021 Rules** |
| NPC Circular 2020-03 | Data Sharing Agreements (All Sectors) | **In effect** |
| NPC Circular 2021-01 | Rules of Procedure (replaced 16-04, 18-03) | Amended by NPC Circular 2024-01 |
| NPC Circular 2022-01 | Guidelines on Administrative Fines | **In effect** |
| NPC Circular 2022-04 | Registration of DPO and DPS | **In effect** |
| NPC Circular 2023-04 | Guidelines on Consent | **In effect** |
| NPC Circular 2023-05 | PPM Certification Prerequisites | **In effect** |
| NPC Circular 2023-06 | Security of Personal Data (All Sectors) | **In effect** (compliance deadline: March 30, 2025) |
| NPC Circular 2024-01 | Amendments to 2021 Rules of Procedure | **In effect** |
| NPC Circular 2024-02 | CCTV Systems Guidelines | **In effect** |
| NPC Circular 2025-01 | Body-Worn Camera Guidelines | **In effect** |

### NPC Circular 16-03: Personal Data Breach Management (Still Active)

Key requirements:
- PICs and PIPs must implement **security incident response policies and procedures**
- Must form a **Data Breach Response Team**
- Must implement technical and organizational security measures to prevent breaches
- Breach notification to NPC and affected data subjects within **72 hours**
- Full report within **5 days** (unless extended by NPC)

### NPC Circular 2020-03: Data Sharing Agreements

Replaced NPC Circular 16-02. Key changes:
- Applies to **both public and private sectors** (previously government only)
- Execution of a Data Sharing Agreement (DSA) is **not mandatory** but is strongly encouraged as a demonstration of accountability
- DSA must contain: terms and conditions, obligations to protect shared data, party responsibilities, mechanisms for data subjects to exercise their rights
- Data sharing remains subject to lawful criteria under the DPA

**SIS relevance:** When sharing student data with CHED, DepEd, UniFAST, or partner institutions, a DSA is strongly recommended even though not mandated.

### NPC Circular 2023-06: Security of Personal Data (Current Standard)

This is the most significant current security circular, replacing NPC Circular 16-01. Effective April 1, 2024, with a 12-month transition period (compliance deadline March 30, 2025).

General obligations of PIC/PIP:
1. Designate and register a Data Protection Officer
2. Register data processing systems
3. Conduct Privacy Impact Assessment
4. Implement a Privacy Management Program
5. Periodic training of personnel on privacy and data protection
6. Comply with NPC orders

Specific technical requirements:
- **Access controls:** Only authorized personnel may access personal data; secure authentication mechanisms required
- **Multi-factor authentication (MFA):** Required for online access to SPI and privileged data
- **Encryption:** Adequate protection for data transferred via email or electronic means; encryption of portable media
- **Acceptable Use Policy:** Must be documented, explained to all personnel, and signed before access is granted
- **Business continuity plan:** Required to mitigate disruptive events
- **Storage:** Data stored only as long as necessary for declared purpose; protected through industry standards

### NPC Advisory Opinions Relevant to Education

| Advisory Opinion | Subject | Key Finding |
|-----------------|---------|-------------|
| AO 2017-024 | Retention periods | Retention must be justified by valid business reason, legal requirement, or ongoing claims; must not be indefinite |
| AO 2020-046 | Student data access | Addressed scope of access to student records |
| AO 2022-014 | Recording online classes | Recording and uploading of online classes is not per se a violation, but must comply with DPA principles |
| AO 2025-017 | Access to student records | Educational institutions must preserve confidentiality while providing reasonable access to learners and parents/guardians |

### NPC Advisory No. 2024-03: Guidelines on Child-Oriented Transparency

Particularly relevant to SIS:
- Mandates **age-appropriate privacy notices** for services accessed by children
- Requires **Child Privacy Impact Assessments** for products/services likely accessed by children
- Age-assurance bands: **0-5, 6-12, and 13-17**
- Parent/guardian involvement necessary when determining whether children may participate in specific processing activities with heightened risks

### NPC Advisory No. 2024-04: AI Systems Processing Personal Data

Relevant if the SIS incorporates any AI/ML features (predictive analytics, early warning systems, etc.):
- Guidelines on applying RA 10173 to AI systems processing personal data
- Likely requires additional PIA considerations for automated decision-making

---

## 3. NPC Education Sector Guidance

### Education Sector Advisory No. 2020-1

Issued by the Data Privacy Council Education Sector (DPCES). Covers data protection in online learning and related activities.

**Key areas covered:**

1. **Online decorum** — rules for privacy-respecting behavior in online learning
2. **Learning Management Systems (LMS)** — privacy considerations for LMS selection and deployment
3. **Online productivity platforms** — data processing implications of tools like Google Workspace, Microsoft 365
4. **Social media** — guidelines for use in educational contexts
5. **Storage of personal data** — secure storage requirements for student data
6. **Webcams and recording** — consent requirements; webcam use should be **optional** whenever possible
7. **Proctoring** — privacy implications of online proctoring tools

**Specific requirements:**

| Area | Requirement |
|------|-------------|
| **Consent for recording** | Must obtain consent of parent/guardian for students under 18 before recording webcam-supported discussions |
| **Platform selection** | Must choose platforms with best security features and DPA compliance; evaluate before adoption |
| **Webcam usage** | Should be optional in synchronous online classes/sessions whenever possible |
| **Data minimization** | Collect only what is necessary for the educational purpose |
| **Accountability** | Educational institutions are accountable for processing through third-party platforms |

### Education Sector Code of Conduct — Status

- **Initiated:** June 28, 2020 by the NPC
- **Participating institutions:** Major Philippine universities (Ateneo, DLSU, UP, UST, BSU, etc.)
- **Purpose:** Set standard policies and measures schools must adopt to prevent data breaches
- **Context:** Education sector constituted 17% of breach notifications in first half of 2020
- **Current status:** The Advisory No. 2020-1 was published; the formal Code of Conduct appears to still be in development as a binding instrument. The DPCES advisory functions as interim guidance.

### NPC Enforcement in Education

- The NPC has received breach notifications from educational institutions (19 between January-June 2020 alone)
- Common violations in schools:
  - Unauthorized collection and sharing of excessive data
  - Unauthorized disclosure of student lists to third parties without data processing agreements
  - Data breaches from inadequate cybersecurity measures
- Penalties for SPI violations involving minors are **increased by 50%**

---

## 4. PII Classification for Student Data

### Comprehensive Classification Table

| Data Element | Classification | Legal Basis | Notes |
|-------------|---------------|-------------|-------|
| **PERSONAL INFORMATION** | | | |
| Full name | Personal Information | Sec. 3(g) | |
| Home address | Personal Information | Sec. 3(g) | |
| Phone number | Personal Information | Sec. 3(g) | |
| Email address | Personal Information | Sec. 3(g) | |
| Student ID number (institutional) | Personal Information | Sec. 3(g) | Assigned by institution, not government-issued |
| Parent/guardian name | Personal Information | Sec. 3(g) | |
| Emergency contact info | Personal Information | Sec. 3(g) | |
| Photograph | Personal Information | Sec. 3(g) | May become SPI if biometric |
| **SENSITIVE PERSONAL INFORMATION** | | | |
| Age / Date of birth | SPI | Sec. 3(l)(1) — age | |
| Sex / Gender | SPI | Sec. 3(l)(1) — related to sexual life | Debatable; treat as SPI conservatively |
| Race / Ethnicity | SPI | Sec. 3(l)(1) — race, ethnic origin | Including IP community membership |
| Religion | SPI | Sec. 3(l)(1) — religious affiliation | |
| Marital status | SPI | Sec. 3(l)(1) — marital status | Relevant for graduate/adult students |
| Nationality/Citizenship | SPI | Sec. 3(l)(1) — ethnic origin | |
| Grades / Academic marks | SPI | Sec. 3(l)(2) — education | **NPC confirmed: test scores are SPI** |
| Transcript of Records (TOR) | SPI | Sec. 3(l)(2) — education | |
| Enrollment status | SPI | Sec. 3(l)(2) — education | |
| Academic standing | SPI | Sec. 3(l)(2) — education | Dean's list, probation, etc. |
| Class schedule / Section | SPI | Sec. 3(l)(2) — education | Per NPC advisory |
| Disciplinary records | SPI | Sec. 3(l)(2) — education + Sec. 3(l)(3) — proceedings for offense | |
| Health records | SPI | Sec. 3(l)(2) — health | Medical certificates, immunization, disabilities |
| PWD status / Disability type | SPI | Sec. 3(l)(2) — health | Also protected under RA 7277/10754 |
| Psychological/counseling records | SPI | Sec. 3(l)(2) — health | May also be privileged |
| Financial information (tuition, payments) | SPI | Sec. 3(l)(2) — education | Related to student's educational record |
| Scholarship/financial aid status | SPI | Sec. 3(l)(2) — education | Including grant amounts |
| Solo parent status | SPI | Sec. 3(l)(1) — marital/family status | Protected under RA 8972/11861 |
| Indigenous Peoples membership | SPI | Sec. 3(l)(1) — ethnic origin | Protected under IPRA (RA 8371) |
| PhilSys Number (PSN) | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | Never store PSN if avoidable |
| Learner Reference Number (LRN) | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | Permanent 12-digit DepEd number |
| SSS/GSIS Number | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | For working students/employees |
| TIN (Tax ID Number) | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | |
| PWD ID Number | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | |
| Solo Parent ID Number | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | |
| Passport Number | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | For international students |
| Driver's License Number | SPI | Sec. 3(l)(4) — government-issued ID peculiar to individual | |
| **PRIVILEGED INFORMATION** | | | |
| Court orders (custody, restraining) | Privileged | Sec. 3(m) — Rules of Court | |
| Legal proceedings involving student | Privileged | Sec. 3(m) — Rules of Court | |
| Attorney-client communications | Privileged | Sec. 3(m) — Rules of Court | HEI legal counsel communications |
| Doctor-patient records (school physician) | Privileged | Sec. 3(m) — pertinent laws | |
| Guidance counselor privileged records | Privileged | Sec. 3(m) — pertinent laws | Depends on professional obligations |

### Key Finding: Grades ARE Sensitive Personal Information

This is explicitly confirmed by the NPC. Under Section 3(l)(2), information about "education" is SPI. The NPC has stated that "student's school name, grade level, section and test scores are considered sensitive personal information as these are related to the student's education."

**Implications for eSMIS:**
- Grade posting/viewing must have strict access controls
- Grade exports require SPI-level protection
- Public posting of grades (even by student number) violates the DPA
- Grade transmission to CHED must be under a lawful basis (legal obligation) with appropriate safeguards

---

## 5. Consent Management Deep Dive

### What Constitutes Valid Consent (NPC Circular 2023-04)

Five elements of valid consent:

| Element | Requirement |
|---------|-------------|
| **Freely given** | No imbalance of power that would compromise freedom to consent; consent cannot be a precondition for enrollment if the processing is not necessary for enrollment |
| **Specific** | Must be tied to specific, declared purposes; blanket consent is invalid |
| **Informed** | Data subject must be provided with all material information about the processing before giving consent |
| **Indication of will** | Must be an express and clear assenting action; silence or pre-ticked boxes do not constitute consent |
| **Evidenced** | Must be recorded in written, electronic, or recorded means; no preference among formats |

### When Consent is NOT Required

| Lawful Basis | SIS Example |
|-------------|-------------|
| **Contract** (Sec. 12(b)) | Processing enrollment data, recording grades, issuing TOR — necessary for the enrollment contract |
| **Legal obligation** (Sec. 12(c)) | CHED HEMIS reporting, RA 10931 subsidy tracking, DepEd LIS reporting |
| **Vital interests** (Sec. 12(d)) | Emergency health information access |
| **Public authority** (Sec. 12(e)) | Public HEI performing mandated functions |
| **Legitimate interest** (Sec. 12(f)) | Institutional research with anonymized data (requires balancing test) |

For **SPI**, the lawful bases under Section 13 apply (see Section 1 above). Most student data processing of SPI will rely on:
- Consent at enrollment
- Legal obligation (CHED, DepEd, CHED requirements)
- Medical treatment (health-related SPI)

### Consent for Minors

**Current law (RA 10173 + IRR + NPC guidance):**

| Age | Consent Requirement |
|-----|-------------------|
| **Under 18** | Parental or legal guardian consent required; minor cannot provide valid consent independently |
| **18 and above** | Can provide own consent |
| **Over 18 with disability** | Guardian consent required if unable to fully care for self |

**NPC Advisory 2024-03 (Child-Oriented Transparency)** adds age-assurance bands:
- **0-5 years** — Not applicable to typical HEI SIS
- **6-12 years** — Not applicable to typical HEI SIS (may apply to lab school)
- **13-17 years** — Relevant for early college/senior high school students

**Important:** There is no separate "digital age of consent" in Philippine law. A House Bill (HB 898) proposing a digital age of consent at 15 has been filed but remains pending and is NOT enacted law.

**SIS implementation requirements:**
- At enrollment, determine if student is under 18
- If under 18, require parent/guardian to provide consent
- Store consent record linked to both student and consenting adult
- Track the student's 18th birthday for consent transition

### Withdrawal of Consent

NPC Circular 2023-04 requirements:

1. **User-friendly withdrawal:** Mechanisms must be "as easy as, if not easier, than giving consent"
2. **Double-notice rule:** PIC must provide information about scope and consequences of withdrawal:
   - At the start of processing (when consent is first given)
   - At the point where consent is withdrawn
3. **Effect of withdrawal:** Processing based on consent must stop; does not affect lawfulness of processing before withdrawal
4. **Data after withdrawal:** If no other lawful basis applies, data must be blocked, erased, or destroyed

**SIS implication:** When consent is withdrawn for non-essential processing, the system must:
- Stop the specific processing activity
- Retain data that has other lawful bases (e.g., academic records under CHED legal obligation)
- Document the withdrawal with timestamps

### Re-consent When Privacy Policy Changes

**General rule:** When a PIC revises terms and conditions, re-consent may be necessary.

**Exception:** If the purpose, scope, method, and extent of processing remain consistent with the original information given to the data subject, re-consent is NOT required.

**Practical test:** Did anything material change that would have affected the data subject's decision to consent? If yes, re-consent is required.

**SIS implementation:**
- Version all consent forms/privacy notices
- When privacy policy changes materially, flag affected consent records
- Trigger re-consent workflow for affected students
- Document which changes triggered re-consent and which did not (with rationale)

### Consent Granularity

NPC Circular 2023-04 requires **granular consent** for multiple unrelated purposes:

- PIC must present the list of purposes
- Data subject must be able to choose individually which purposes to consent to
- Cannot bundle unrelated purposes into a single take-it-or-leave-it consent

**SIS example:**
- Consent for enrollment processing — may not require separate consent (contract basis)
- Consent for photo publication on school website — separate consent required
- Consent for sharing data with research partners — separate consent required
- Consent for alumni communications — separate consent required

### Electronic Consent Validity

Three equally valid formats (no preference among them):
1. **Written** — physical signature on paper consent form
2. **Electronic** — digital consent through online form, e-signature, checkbox with proper disclosure
3. **Recorded** — audio/video recording of consent

Documentation requirements for all formats:
- Date consent was obtained
- Method of obtaining consent
- Who obtained it
- What information was provided to the data subject
- Evidence that information was presented at the time of consent
- Evidence that the data subject performed an act to signify consent

**Assenting actions:** Consent can be ascertained from express and clear assenting actions (not just declarations), but only from express and clear acts that signify agreement to a specific purpose. Pre-ticked boxes, silence, or inactivity do NOT constitute consent.

**Validity period:** Consent remains valid as long as the scope, purpose, nature, and extent of processing has not materially changed.

---

## 6. Data Subject Rights Implementation

### NPC Advisory No. 2021-01: Data Subject Rights

This advisory provides the operational framework for implementing data subject rights.

### Right to be Informed

**What must be disclosed (privacy notice content):**
- Identity of the PIC (institution name, contact details)
- Contact details of the DPO
- Purpose of processing
- Categories of personal data processed
- Recipients or categories of recipients
- Existence of automated decision-making, including profiling
- Retention period
- Rights of the data subject
- Right to lodge a complaint with the NPC
- Whether provision of data is statutory/contractual requirement
- Consequences of not providing data

**When:** Before or at the time of collection.

**How:** Through a layered privacy notice — summary at point of collection, full notice accessible via link or document.

**SIS implementation:** Privacy notice at enrollment (physical and/or digital), accessible from student portal, updated when processing changes.

### Right to Access

| Aspect | Requirement |
|--------|-------------|
| **Response time** | Within **30 working days** of request |
| **Format** | Reasonable, accessible format; electronic if requested |
| **Fees** | No fees allowed, except reasonable fees for copies of personal information |
| **Scope** | All personal data being processed, sources, recipients, processing logic for automated decisions |
| **Verification** | PIC must verify identity of requester |

**SIS implementation:** Self-service data access through student portal; formal request process for comprehensive data export; audit trail of access requests.

### Right to Object

Data subjects can object to processing when:
- Processing is based on consent or legitimate interest
- Processing is for direct marketing
- Processing involves automated decision-making or profiling

**SIS implication:** Students can object to non-essential processing (e.g., marketing, research analytics) but NOT to processing required by law or contract (enrollment, grade recording, regulatory reporting).

### Right to Erasure/Blocking

Grounds for erasure:
- Data is incomplete, outdated, false, or unlawfully obtained
- Data is being used for unauthorized purposes
- Data is no longer necessary for the declared purpose
- Data subject withdraws consent (and no other lawful basis applies)
- Data subject objects and there is no overriding legitimate ground

**Critical education exception:** Academic records that must be retained permanently under CHED regulations CANNOT be erased. The erasure right is overridden by the legal obligation to maintain permanent academic records.

**What CAN be erased in education context:**
- Optional profile information (photo, personal preferences)
- Marketing/communication preferences
- Data collected for research (if consent is withdrawn)
- Temporary processing data (application data for rejected applicants, after appropriate period)

**What CANNOT be erased:**
- Official Transcript of Records (permanent retention under CHED)
- Enrollment records (permanent retention)
- Graduation records (permanent retention)
- Disciplinary records (5-year retention under CHED)
- Financial records (10-year retention under CHED)

### Right to Rectification

- Data subject disputes inaccuracy or error
- PIC must correct immediately unless request is vexatious or unreasonable
- Must notify third parties who received the incorrect data

**SIS implementation:** Correction request workflow with:
- Supporting documentation requirement
- Approval chain (registrar for academic data, department for administrative data)
- Audit trail of original and corrected values
- Notification to downstream systems/parties

### Right to Data Portability

Requirements:
- Copy of data in **structured, commonly used electronic format**
- Ability to transmit to another PIC
- NPC may specify format and technical standards

**SIS implementation:**
- Export personal data in CSV, JSON, or XML
- Include: personal info, enrollment history, grades, financial records
- Exclude: privileged information, internal assessment notes not attributable to the student

### Right to Damages

- Data subjects may claim compensation for damages due to inaccurate, incomplete, outdated, false, unlawfully obtained, or unauthorized use of personal data
- Creates liability exposure for the institution

### Filing Complaints with NPC

Process:
1. Data subject must **first inform the PIC** in writing of the privacy violation (exhaustion of remedies)
2. NPC may waive this requirement for serious violations
3. Complaint filed with the NPC using Complaint-Affidavit template
4. NPC investigation and fact-finding
5. Potential administrative fines, cease-and-desist orders, or referral for criminal prosecution

---

## 7. Security Measures Required by Law

### NPC Circular 2023-06 Detailed Requirements

#### Organizational Security Measures

| Measure | Details |
|---------|---------|
| **DPO designation** | Must designate and register with NPC; DPO must be organic employee (at least 2-year contract) with adequate privacy knowledge |
| **Privacy Management Program** | Codified into a Privacy Manual; covers entire data lifecycle |
| **Training** | Periodic training for all personnel on privacy and data protection policies |
| **Acceptable Use Policy** | Documented policy on ICT use; must be explained to all personnel; each user must sign before access |
| **Contracts with processors** | Must ensure continued protection with minimum standards |
| **Incident response** | Data Breach Response Team must be formed |
| **Record keeping** | ROPA must be maintained |

#### Physical Security Measures

| Measure | Details |
|---------|---------|
| **Facility access** | Policies and procedures to limit physical access to facilities and workstations |
| **Workstation security** | Proper usage guidelines for workstations |
| **Removable media** | Controls on use and storage of removable media |
| **Server room** | Restricted access, environmental controls |
| **Disposal** | Secure disposal of physical records and electronic storage media |

#### Technical Security Measures

| Measure | Details |
|---------|---------|
| **Access controls** | Only authorized personnel; role-based access controls |
| **Authentication** | Secure authentication mechanisms; **MFA required for online access to SPI** |
| **Encryption** | Encryption of portable media; adequate protection for data in transit |
| **Network security** | Firewalls, intrusion detection/prevention |
| **Monitoring and logging** | Audit trails of access to personal data |
| **Vulnerability management** | Regular assessment and patching |
| **Business continuity** | BCP to mitigate disruptive events |
| **Data storage** | Only as long as necessary; protected through industry standards |

#### Recommended Standards

The NPC recommends:
- **ISO/IEC 27001** — Information Security Management Systems
- **ISO/IEC 27701** — Privacy Information Management System (extension to ISO 27001)
- **ISO/IEC 27002** — Minimum control set for organizations processing 1,000+ records
- **ISO/IEC 29151** — Code of practice for PII protection

For **PPM Certification** (NPC Circular 2023-05):
- Must be certified ISO/IEC 27001 AND ISO/IEC 27701

---

## 8. Data Breach Management

### What Constitutes a Breach (NPC Circular 16-03)

A personal data breach is a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data transmitted, stored, or otherwise processed.

Types:
- **Confidentiality breach** — unauthorized or accidental disclosure/access
- **Integrity breach** — unauthorized or accidental alteration
- **Availability breach** — unauthorized or accidental loss of access/destruction

### 72-Hour Notification Timeline

| Step | Timeline | Action |
|------|----------|--------|
| 1 | Discovery | Become aware of or reasonably believe a breach has occurred |
| 2 | Within 72 hours of Step 1 | Notify NPC AND notify affected data subjects |
| 3 | Within 5 days of Step 1 | Submit full breach report to NPC (unless extension granted) |
| 4 | Post-incident | Conduct review and implement remediation |

### Required Content of NPC Notification

The notification to the NPC must include:
- Nature of the breach
- Personal data possibly involved
- Measures taken or proposed to address the breach
- Measures taken or proposed to mitigate possible adverse effects
- Name and contact details of the DPO or relevant contact
- Date of the breach (or best estimate)
- Description of the scope and likely consequences

### When to Notify Affected Data Subjects

Notification is required when the breach:
- Involves **100 or more data subjects**
- Involves **sensitive personal information** that will harm or adversely affect the data subject
- Is likely to give rise to a **real risk** to the rights and freedoms of data subjects

### Content of Data Subject Notification

Same content as NPC notification, PLUS:
- Instructions on how data subjects can get further information
- Recommendations on how to minimize risks resulting from the breach
- How to secure any form of assistance

### Method of Data Subject Notification

- Must be sent **individually** (not just a general announcement)
- May be by **written or electronic means**
- Must be based on available information within the 72-hour period

### Restrictions on Delay

Delay in notification is **prohibited** when:
- The breach involves at least 100 data subjects
- Disclosure of SPI will harm or adversely affect data subjects

### Breach Documentation Requirements

- All security incidents (even those not qualifying as reportable breaches) must be documented
- Breach log must include: date, nature, scope, response actions, notifications sent
- Documentation must be retained for audit purposes

### Breach Response Team

Requirements:
- Must be formed as part of organizational security measures
- Must include members with authority to make decisions
- Must have clear escalation procedures
- Must conduct post-breach review and remediation

### Section 30 Penalty — Concealment

Intentional or negligent concealment of a security breach involving SPI carries **1.5-5 years imprisonment** and PHP 500K-1M fine. This creates a strong incentive for prompt reporting.

---

## 9. Cross-Border Data Transfer

### Legal Framework

RA 10173 does NOT impose explicit restrictions on cross-border transfers of personal data. However:

- Transfer of data is considered **processing** under the DPA
- All requirements for lawful processing apply to cross-border transfers
- The PIC remains **accountable** for data transferred internationally (Section 21)

### When Student Data May Leave the Philippines

| Scenario | Example |
|----------|---------|
| Cloud hosting | AWS, GCP, Azure data centers outside PH |
| International partner universities | Student exchange programs, articulation agreements |
| Third-party SaaS | LMS platforms, email services, analytics tools |
| CHED international reporting | International education statistics |
| Accreditation | International accreditation body data submissions |

### NPC Advisory No. 2024-01: Model Contractual Clauses (MCCs)

Issued May 30, 2024. Key points:

- NPC does **not require** adoption of MCCs, but strongly encourages them
- MCCs are a means of upholding the **accountability principle** in cross-border transfers
- PICs must determine for themselves whether applicable laws impose additional obligations
- MCCs provide a standardized contractual framework covering:
  - Data protection obligations of the parties
  - Data subject rights
  - Security measures
  - Breach notification
  - Sub-processing restrictions
  - Audit rights

### Practical Requirements for SIS

1. **Inventory all cross-border data flows** — document where student data goes and why
2. **Assess adequacy** — no formal NPC adequacy determinations exist; assess the destination country's data protection regime
3. **Contractual safeguards** — use MCCs or equivalent contractual clauses with cloud providers and international partners
4. **Data localization preference** — where feasible, keep student data within PH; if not, document the justification
5. **Inform data subjects** — privacy notice must disclose international transfers

---

## 10. Data Retention and Disposal

### Retention Period Guidelines

There is no single retention period under RA 10173. The law requires retention only **as long as necessary** for the declared purpose. However, sector-specific laws create retention obligations that override the general minimization principle.

#### CHED Retention Requirements for HEIs

| Record Type | Retention Period | Authority |
|-------------|-----------------|-----------|
| Official Transcript of Records (TOR) | **Permanent (indefinite)** | CHED CMO |
| Diplomas and certificates of graduation | **Permanent** | CHED CMO |
| Enrollment records | **Permanent** | CHED CMO |
| Academic progress reports, grade sheets, evaluation forms | **At least 5 years** after last enrollment or graduation | CHED CMO |
| Transfer credentials (honorable dismissal) | **10 years** | CHED CMO |
| Student financial records | **10 years** | CHED CMO + NAP GRDS |
| Disciplinary records | **5 years** after resolution | CHED CMO |
| Health and counseling records | **7 years** with privacy safeguards | NAP GRDS for Education |

#### DPA vs. CHED Conflict Resolution

The tension between RA 10173 (minimize retention) and CHED (permanent academic records) is resolved by **Section 13(b)** of the DPA: processing of SPI is lawful when "provided for by existing laws and regulations" — CHED memorandum orders constitute such existing regulations.

**Practical approach:**
- Academic records covered by CHED retention: retain as required by CHED
- Data NOT covered by CHED retention requirements: apply the DPA proportionality principle — retain only as long as necessary
- When retention period expires: dispose securely

#### NPC Guidance on Determining Retention Periods (AO 2017-024)

Factors to consider:
1. Legal requirements to which the institution is subject (CHED, DepEd, BIR, etc.)
2. Applicable prescription periods in existing law
3. Industry standards
4. Ongoing legal claims or disputes
5. Legitimate business purposes

Retention must NOT be indefinite if based solely on speculative future uses.

### Disposal Methods

#### IRR Section 19(d)

Personal data shall be disposed or discarded in a **secure manner** that would prevent:
- Further processing
- Unauthorized access
- Disclosure to any other party or the public

#### Approved Disposal Methods

| Method | For | Standard |
|--------|-----|----------|
| **Shredding** | Paper records, electronic media | Cross-cut shredding; electronic media reduced to <2mm pieces |
| **Degaussing** | Magnetic storage (HDDs, tapes) | Disrupts magnetic fields, rendering data irrecoverable |
| **Overwriting** | Electronic storage | Multiple-pass overwriting per NIST 800-88 guidelines |
| **Incineration** | Paper records, electronic media | Complete destruction |
| **Cryptographic erasure** | Encrypted storage | Destroy encryption keys, rendering data unreadable |

#### Documentation Requirements

- Disposal must be **documented** in a disposal log
- Disposal logs must be retained for **5 years** post-disposal
- Unauthorized disposal is prohibited
- For private HEIs, CHED acts as intermediary for NAP-issued Certificates of Disposal
- Records involved in ongoing legal cases or audits may NOT be disposed

---

## 11. Privacy Impact Assessment (PIA)

### When PIA is Required

- Government agencies: **mandatory** for each program, process, or measure involving personal data (NPC Circular 2016-01, Sections 4-6, now under NPC Circular 2023-06)
- All PICs/PIPs: **required** under NPC Circular 2023-06 as a general obligation
- **Before deploying** new systems processing personal data
- **Before making significant changes** to existing data processing
- Answering "yes" to any threshold question (e.g., "Does this process personal data?") indicates a PIA is needed

### PIA Methodology

The NPC does **not prescribe** a particular method, but recommends:

| Standard | Description |
|----------|-------------|
| ISO/IEC 29134 | International standard for conducting PIAs |
| NPC Advisory 2017-003 | NPC considerations for PIA methodology |
| ISO/IEC 27002 | Recommended control set for 1,000+ record processors |
| ISO/IEC 29151 | Code of practice for PII protection |

### PIA Template Components (NPC Draft)

Six parts:

| Part | Content |
|------|---------|
| **(a) General Description** | Organization name, proposed project, processes involving personal data |
| **(b) Threshold Analysis** | Identify personal information currently used or to be used |
| **(c) Stakeholder Engagement** | Identify affected project stakeholders |
| **(d) Data Privacy Analysis** | Information flow analysis, compliance with privacy principles |
| **(e) Privacy Risk Management** | Identify threats, vulnerabilities, and risk mitigation measures |
| **(f) Summary of Assessment and Sign Off** | Findings summary, approval by DPO and management |

### PIA and System Development Lifecycle

- PIA begins at the **earliest possible stages** of a system initiative
- Continues **throughout development** and **after deployment**
- Opportunities to influence system design diminish over time — early PIA is more effective
- PIA embeds **Privacy by Design** into the development process

### PIA Review and Update Triggers

| Trigger | Action |
|---------|--------|
| New data processing activity | Conduct new PIA |
| Major system upgrade or change | Update existing PIA |
| New data sharing arrangement | Update PIA to cover new data flows |
| Significant security incident | Review and update PIA |
| Regulatory change | Review PIA for compliance |
| Periodic review (recommended: annually) | Scheduled PIA review |

### Child Privacy Impact Assessment

NPC Advisory 2024-03 mandates a **Child Privacy Impact Assessment** (CPIA) for products or services likely accessed by children. This is relevant for SIS modules accessible to students under 18.

---

## 12. Accountability and Governance

### DPO Qualifications and Responsibilities

#### Qualifications (NPC Circular 2022-04)

| Requirement | Detail |
|-------------|--------|
| **Employment** | Must be a full-time/organic employee; contract term of at least 2 years if contractual |
| **Knowledge** | Must be knowledgeable on relevant privacy/data protection policies and practices |
| **Understanding** | Must have adequate knowledge of the processing operations, information systems, data security, and data protection needs |
| **Independence** | Must be able to perform duties independently |

#### Responsibilities

- Oversee compliance with the DPA, its IRR, and NPC issuances
- Serve as point of contact for data subjects and the NPC
- Monitor compliance with privacy policies
- Ensure conduct of PIAs
- Advise on privacy-related matters
- Cultivate awareness of data privacy within the organization
- Manage data subject rights requests
- Coordinate breach response
- Interface with the NPC for registration, notifications, and compliance matters

### Privacy Management Program

A comprehensive program that must be codified into a **Privacy Manual** covering:

1. **Data inventory** — all processing activities, data flows, and systems
2. **Policies and procedures** — collection, use, storage, sharing, disposal
3. **Risk management** — ongoing risk assessment and mitigation
4. **Training** — regular privacy awareness training for all personnel
5. **Incident response** — breach response procedures
6. **Vendor management** — requirements for processors and third parties
7. **Rights management** — procedures for data subject requests
8. **Compliance monitoring** — regular audits and reviews

### Record of Processing Activities (ROPA)

Must document:
- Description of each processing activity
- Purpose of processing
- Categories of data subjects and personal data
- Categories of recipients
- Cross-border transfers (if any)
- Retention periods
- Security measures
- Legal basis for processing

### NPC Registration Requirements

#### Who Must Register (NPC Circular 2022-04)

Organizations must register if they:
- Employ at least **250 employees**, OR
- Process SPI of **1,000 or more individuals**, OR
- Process personal data which significantly impacts rights and freedoms

**Note:** Most HEIs will meet the 1,000 SPI threshold due to student enrollment numbers.

#### Registration Process

1. Register on the NPC Registration System (NPCRS)
2. Upload company registration documents
3. Register DPO details — generates a DPO Form
4. DPO Form must be signed by head of organization and **notarized**
5. Upload notarized DPO Form to NPCRS
6. NPC issues **Certificate of Registration** and **Seal of Registration**

#### Seal of Registration

- Valid for **1 year** from issuance, subject to renewal
- Must be displayed at **main entrance** of place of business or most conspicuous location
- Must be visible to all data subjects
- Deadline for registration: NPC has warned it will issue **show cause orders** for non-compliance (as of June 2024, referencing NPC Circular 2022-04)
- DPO must be registered within **90 days** of designation

### NPC Five Pillars of Compliance

The NPC's compliance framework, used in compliance checks:

| Pillar | Description |
|--------|-------------|
| **1. Appoint a DPO** | Designate and register DPO |
| **2. Conduct PIA** | Assess capabilities, threats, and risks |
| **3. Privacy Management Program** | Codify internal protocols into a Privacy Manual |
| **4. Data Protection Measures** | Implement organizational, physical, and technical security |
| **5. Breach Reporting** | Establish breach response protocols and comply with notification requirements |

### Regular Audits and Compliance Reviews

- NPC may conduct compliance checks at any time
- PICs should conduct **internal audits** periodically
- Review triggers: significant system changes, breach incidents, regulatory updates, annual review
- NPC compliance checks assess adherence to the Five Pillars

### PPM Certification (NPC Circular 2023-05)

Optional but encouraged:
- PIC/PIP must be certified **ISO/IEC 27001** (ISMS) AND **ISO/IEC 27701** (PIMS)
- Certification bodies must be accredited by the NPC
- Provides formal recognition of compliance

---

## Summary of Key NPC Issuances Affecting SIS

| Issuance | Subject | SIS Relevance |
|----------|---------|---------------|
| RA 10173 | Data Privacy Act | Foundation law |
| IRR (as amended) | Implementing rules | Detailed processing requirements |
| NPC Circular 16-03 | Breach management | Breach response procedures |
| NPC Circular 2020-03 | Data sharing agreements | Sharing student data with CHED, partners |
| NPC Circular 2022-01 | Administrative fines | Penalty framework |
| NPC Circular 2022-04 | DPO and DPS registration | Registration obligations |
| NPC Circular 2023-04 | Consent guidelines | Consent management for students |
| NPC Circular 2023-06 | Security of personal data | Technical and organizational security |
| NPC Advisory 2021-01 | Data subject rights | Rights implementation |
| NPC Advisory 2024-01 | Model contractual clauses | Cross-border transfers (cloud hosting) |
| NPC Advisory 2024-03 | Child-oriented transparency | Minor student protections |
| NPC Advisory 2024-04 | AI and personal data | Automated processing considerations |
| DPCES Advisory 2020-1 | Education sector | Online learning privacy requirements |
| NPC AO 2025-017 | Student record access | Access to student records |

---

## Sources

- [Republic Act 10173 — Data Privacy Act of 2012 (NPC)](https://privacy.gov.ph/data-privacy-act/)
- [Official Gazette — RA 10173 Full Text](https://www.officialgazette.gov.ph/2012/08/15/republic-act-no-10173/)
- [IRR of RA 10173 (as amended)](https://privacy.gov.ph/wp-content/uploads/2023/06/IRR_RA-10173-as-amended.pdf)
- [NPC Advisories & Circulars Page](https://privacy.gov.ph/pips-and-pics/advisories-circulars/)
- [NPC Circular 16-03 — Breach Management](https://privacy.gov.ph/wp-content/uploads/2022/01/sgd-npc-circular-16-03-personal-data-breach-management.pdf)
- [NPC Circular 2020-03 — Data Sharing Agreements](https://law.upd.edu.ph/wp-content/uploads/2021/05/NPC-Circular-No-2020-03.pdf)
- [NPC Circular 2022-01 — Administrative Fines](https://privacy.gov.ph/wp-content/uploads/2022/08/NPC-CIRCULAR-NO.-2022-01-GUIDELINES-ON-ADMINISTRATIVE-FINES-dated-08-AUGUST-2022-w-SGD.pdf)
- [NPC Circular 2023-04 — Consent Guidelines](https://privacy.gov.ph/wp-content/uploads/2023/11/NPC-Circular-No.-2023-04_Guidelines-on-Consent_07Nov2023.pdf)
- [NPC Circular 2023-06 — Security of Personal Data](https://privacy.gov.ph/wp-content/uploads/2024/03/NPC-Circular-Repeal-16-01-Signed.pdf)
- [NPC Advisory 2021-01 — Data Subject Rights](https://privacy.gov.ph/wp-content/uploads/2021/02/NPC-Advisory-2021-01-FINAL.pdf)
- [NPC Advisory 2024-01 — Model Contractual Clauses](https://bccslaw.com/npc-advisory-no-2024-01-model-contractual-clauses-for-cross-border-transfers-of-personal-data/)
- [NPC Advisory 2024-03 — Child-Oriented Transparency](https://privacy.gov.ph/wp-content/uploads/2024/12/FAQs-Advisory-on-Guidelines-on-Child-Oriented-Transparency.pdf)
- [NPC Advisory Opinion 2025-017 — Student Record Access](https://privacy.gov.ph/wp-content/uploads/2026/01/NPC-Advisory-Opinion-No.-2025-017_Redactedv2.pdf)
- [DPCES Education Sector Advisory 2020-1](https://privacy.gov.ph/wp-content/uploads/2023/05/DP-Council-Education-Sector-Advisory-No.-2020-1.pdf)
- [NPC Data Subject Rights Page](https://privacy.gov.ph/data-subject-rights/)
- [NPC Five Pillars of Compliance](https://privacy.gov.ph/5-pillars-of-compliance-3/)
- [NPC Breach Reporting Page](https://privacy.gov.ph/pips-and-pics/breach-reporting/)
- [NPC Enforcement Decisions](https://privacy.gov.ph/enforcement-decisions/)
- [NPC Advisory 2017-003 — PIA Methodology](https://privacy.gov.ph/wp-content/uploads/2022/01/NPC_AdvisoryNo.2017-03.pdf)
- [NPC PIA Guide](https://privacy.gov.ph/wp-content/uploads/2022/01/NPC_PIA_0618.pdf)
- [NPC Advisory Opinion 2017-024 — Retention Periods](https://privacy.gov.ph/wp-content/uploads/2022/01/NPC_AdvisoryOpinionNo._2017-024.pdf)
- [NPC Advisory Opinion 2022-014 — Recording Online Classes](https://privacy.gov.ph/wp-content/uploads/2022/08/Advisory-Opinion-No.-2022-014_Redacted.pdf)
- [IAPP Summary — Philippines DPA](https://iapp.org/news/a/summary-philippines-data-protection-act-and-implementing-regulations)
- [DLA Piper — Philippines Data Protection](https://www.dlapiperdataprotection.com/?t=law&c=PH)
- [Baker McKenzie — Philippines Security Requirements](https://resourcehub.bakermckenzie.com/en/resources/global-data-and-cyber-handbook/asia-pacific/philippines/topics/security-requirements-and-breach-notification)
- [CHED Memoranda on Student Records](https://www.lawyer-philippines.com/articles/ched-memoranda-on-student-records-management-retention-and-disposal-in-the-philippines)
- [Data Privacy for Student Grades — Respicio](https://www.respicio.ph/commentaries/data-privacy-for-student-grades-in-the-philippines)
- [NPC Education Sector Code of Conduct Initiative](https://privacy.gov.ph/npc-initiates-code-of-conduct-to-guide-schools-amid-shift-to-online-education/)
- [Thales — NPC Circular 2023-06 Compliance Brief](https://cpl.thalesgroup.com/compliance/apac/data-security-compliance-npc-circular-2023-06)
- [NPC Advisory 2025-01 — Data Sharing Agreement Clarification](https://privacy.gov.ph/wp-content/uploads/2025/07/SGD-2025-01-DSA-Clarification.pdf)
- [NPC DPO Registration FAQ](https://privacy.gov.ph/pips-and-pics/faqs/)
- [Liability for Violating Data Privacy Rights of Minors in Schools — Respicio](https://www.respicio.ph/commentaries/liability-for-violating-the-data-privacy-rights-of-minors-in-schools)
