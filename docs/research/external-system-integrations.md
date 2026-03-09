# External System Integrations Research

Research into external systems a Philippine university Student Information System should integrate with. Covers official APIs, data exchange formats, authentication requirements, and technical documentation.

---

## 1. PhilSys (Philippine Identification System / National ID) — RA 11055

**Managing Agency:** Philippine Statistics Authority (PSA)

### Available Services

PhilSys provides two primary authentication services under **NIDAS (National ID Authentication Services)**:

| Service | Description | Method |
|---------|-------------|--------|
| **National ID Check** | Validates the PhilID card by scanning the QR code against PSA's cryptographic infrastructure | QR code scan + EdDSA signature verification |
| **National ID eVerify** | Live server-side biometric comparison (selfie vs. reference image on file) | API call returning pass/fail decision |

### PhilSys Check — QR Code Verification

- Uses **Edwards-curve Digital Signature Algorithm (EdDSA)** for public-private key cryptography
- PSA digitally signs the demographic data in the PhilID QR code
- Relying parties use the PSA-distributed **public key** to verify authenticity offline or online
- Verification site: https://verify.philsys.gov.ph

**Data fields returned from QR scan:**
- Full name (first_name, middle_name, last_name, suffix)
- Sex
- Date of birth (dob)
- Place of birth
- PhilSys Card Number (PCN)
- Date of issuance
- Card status
- QR code status
- Low-resolution photo (ePhilID only)

### National ID eVerify — Biometric Verification

- Performs facial recognition (selfie-to-reference comparison)
- Also supports fingerprint scanning
- Returns pass/fail authentication decision to relying party
- Portal: https://everify.gov.ph

### Onboarding as a Relying Party

1. Contact PSA based on sector:
   - Government agencies/LGUs: gsucd@psa.gov.ph
   - Social protection: spucd@psa.gov.ph
   - Financial/private institutions: fpsucd@psa.gov.ph
2. Complete fully online application via https://everify.gov.ph
3. Execute a **Non-Disclosure Agreement (NDA)** before receiving public key and documentation
4. Request the **PhilSys Check Public Key** and API documentation via authorization letter template

### Integration Architecture Notes

- PhilSys Check can work **offline** once the public key is distributed
- eVerify requires **server-side API calls** (online only)
- As of September 2025, 87 relying parties onboarded across sectors
- PSN (PhilSys Number) is the persistent identifier; PCN is the card-specific number

### Technical Documentation

- PhilSys Check info: https://sites.google.com/view/philsys-check/home
- FOI request for API access: https://www.foi.gov.ph/requests/access-to-api-or-method-for-verifying-the-validity-of-philsys-id/
- eVerify onboarding: https://everify.gov.ph

---

## 2. CHED Data Systems

**Managing Agency:** Commission on Higher Education (CHED)

### CHED Digital Platform Ecosystem

CHED operates several interconnected digital platforms under **CHED One Touch** (https://onetouch.ched.gov.ph/):

| System | Purpose | URL |
|--------|---------|-----|
| **HEMIS** | Higher Education Management Information System — annual data collection | Regional CHED offices |
| **HEIDA** | Higher Education Institution Data Analytics | https://heida.ched.gov.ph/ |
| **eCAV** | Electronic Certification, Authentication, and Verification | https://ecav.ched.gov.ph/ |
| **SOAIS** | Student/institutional services | Via CHED One Touch |
| **ProgMES** | Program Monitoring and Evaluation System | Regional CHED offices |

### HEMIS — Annual Data Collection

**Data collection format:** Microsoft Excel (not Access)

**Required forms by institution type:**

**State Universities and Colleges (SUCs):**
- Form A — Institutional Profile
- Form B — Programs Offered, Enrollment Data, Graduate Data
- Form E1 — Faculty-related data
- Form E2 — Faculty and personnel data
- Research Extension Form — Research and extension activities
- Form GH — Allotment and expenditures
- Graduate List Form — Comprehensive list of graduates

**Private HEIs and Local Universities/Colleges (LUCs):**
- Form A — Institutional Profile
- Form BC — Programs Offered, Enrollment Data, Graduate Data
- Form E5 — Faculty Profile
- Graduate List Form

**Submission process:** Annual orientation workshops conducted by CHED Regional Offices for HEI Registrars, Records Officers, and HEMIS Coordinators.

**Integration method:** Currently file-based (Excel upload). No public REST API documented.

### eCAV — Full Implementation (April 2025)

- All CAV applications must be submitted via the eCAV web platform
- Real-time application status tracking
- Secure document upload
- Each issued eCAV includes a **unique QR code** for real-time authenticity verification
- QR code scannable by any device with a QR scanner

### Graduate Tracer Study (GTS)

**Data fields collected:**
- General information (contact details, demographics)
- Educational background (program, institution, year of graduation)
- Employment status and history
- Competencies learned in college
- Reasons for taking courses and jobs
- Job satisfaction factors

**Current state:** Data collection is largely survey-based. HEIs are often expected to conduct their own tracer studies and submit results to CHED. No standardized API.

### Technical Documentation

- CHED forms: https://ched.gov.ph/forms/
- HEIDA portal: https://heida.ched.gov.ph/
- eCAV portal: https://ecav.ched.gov.ph/

---

## 3. UniFAST / Free Tuition — RA 10931

**Managing Agency:** CHED-UniFAST (Unified Student Financial Assistance System for Tertiary Education)

### System Overview

UniFAST consolidates all government-funded Student Financial Assistance Programs (StuFAPs) — scholarships, grants-in-aid, student loans — into a single platform under RA 10687.

### TES (Tertiary Education Subsidy) Integration

**TES is school-based, not direct student application.** Key integration points:

| Step | Actor | Data Exchange |
|------|-------|---------------|
| MOA signing | HEI + CHED-UniFAST | Memorandum of Agreement required before portal access |
| Student application | HEI screens applicants | Student demographic data, enrollment data |
| Enrollment certification | HEI uploads | Certified CORS/COEs, list of enrolled student-applicants, applicable fees |
| Eligibility verification | UniFAST cross-references | Against Listahanan (DSWD poverty database) and 4Ps membership |
| Masterlist approval | CHED Regional Offices verify, UniFAST Board approves | Qualified grantees list |
| Subsidy disbursement | UniFAST | Up to PHP 20,000/year tuition (private HEIs), PHP 40,000/year living allowance |

### Data Fields Required from HEIs

- Student personal information (name, date of birth, address)
- Enrollment status and program
- Certified true copy of enrolled student-applicants list
- Certificate of Registration/Enrollment (CORS/COEs)
- Fee schedules charged by HEI
- Family income data (for ranking)

### Integration Method

- **Portal-based** — HEIs upload data through the TES Portal
- Requires valid MOA with CHED-UniFAST
- TES Focal Person at each HEI manages submissions
- No public API documented; upload format likely spreadsheet-based

### Technical Documentation

- UniFAST portal: https://unifast.gov.ph/
- CHED UniFAST page: https://ched.gov.ph/unifast/

---

## 4. DOST Scholarship System

**Managing Agency:** Department of Science and Technology — Science Education Institute (DOST-SEI)

### Scholarship Management

**Application system:** Online e-Application at https://ugs.science-scholarships.ph

**Scholar reporting requirements:**
- Grades and registration forms submitted every start and end of each semester/term
- Official Transcript of Records (TOR) or True Copy of Grades (TCG) signed by University Registrar or Dean
- Periodic Reports, Special Reports, Final Reports, and Yearly Reports
- Compliance with prescribed academic load based on program of study

### HEI Integration Points

| Data Point | Direction | Format |
|------------|-----------|--------|
| Scholar enrollment verification | HEI → DOST-SEI | Certified documents (likely PDF/scanned) |
| Grade reports | HEI → DOST-SEI | Certified TOR/TCG |
| Stipend/allowance disbursement | DOST-SEI → Scholar | Direct to student |
| Program of study compliance | HEI → DOST-SEI | Certified document |

### Integration Method

- **Document-based** — certified hard copies or scanned documents
- Helpdesk: https://helpdesk.sei.dost.gov.ph
- No public API documented for HEI system integration
- Potential for automated grade reporting if DOST-SEI develops API

### Graduate Tracer

- DOST-SEI maintains a separate tracer study form for scholar graduates
- Tracks employment outcomes relative to S&T fields

### Technical Documentation

- DOST-SEI website: https://www.sei.dost.gov.ph/
- Citizen's Charter: https://cc.sei.dost.gov.ph/citizens-charter/

---

## 5. LMS Integration

### Standards Overview

| Standard | Version | Purpose | Maintained By |
|----------|---------|---------|---------------|
| **LTI** | 1.3 (current) | Tool integration (launch, grade passback, deep linking) | 1EdTech (formerly IMS Global) |
| **OneRoster** | 1.2 | Roster/enrollment data exchange between SIS and LMS | 1EdTech |
| **LTI Advantage** | Extensions on 1.3 | Names & Roles Provisioning, Assignment & Grade Services, Deep Linking | 1EdTech |

### LTI 1.3 Technical Details

- **Security:** OAuth2, OpenID Connect, JSON Web Tokens (JWT)
- **Key services:**
  - **Deep Linking** — content selection and embedding
  - **Assignment and Grade Services (AGS)** — near real-time grade passback
  - **Names and Roles Provisioning Service (NRPS)** — automated roster sync from LMS to tools

### OneRoster Integration

- REST API or CSV file exchange
- Syncs: students, teachers, classes, enrollments, demographics
- Supports grade passback via OneRoster Gradebook API
- Google Classroom supports OneRoster for SIS integration (https://developers.google.com/workspace/classroom/sis-integrations/)

### Philippine University LMS Landscape

| Platform | Adoption | Notes |
|----------|----------|-------|
| **Moodle** | Widely used (SUCs, secondary schools) | Open-source, LTI Advantage Complete certified |
| **Google Classroom** | Widely used | LTI integration via Google Workspace LTI tools (compatible with Canvas, Schoology) |
| **Canvas** | Growing (e.g., University of the East) | Full LTI 1.3 support, OneRoster support |
| **UP UVLE** | UP System | Custom platform |

### Integration Architecture for SIS

```
SIS (eSMIS)
    ↕ OneRoster REST API (roster/enrollment sync)
    ↕ LTI 1.3 (launch, grade passback)
LMS (Moodle / Canvas / Google Classroom)
```

### Key Technical Resources

- LTI specification: https://www.imsglobal.org/lti-advantage-faq
- Moodle LTI docs: https://docs.moodle.org/501/en/LTI_and_Moodle
- Google Classroom SIS integration: https://developers.google.com/workspace/classroom/sis-integrations/
- OneRoster spec: https://www.imsglobal.org/activity/onerosterlis

---

## 6. Government Financial Systems

### 6.1 BIR (Bureau of Internal Revenue)

**Key forms for educational institutions:**

| Form | Purpose | Deadline |
|------|---------|----------|
| BIR Form 2316 | Certificate of Compensation Payment / Income Tax Withheld | Jan 31 (to employees), Feb 28 (to BIR) |
| BIR Form 1601-C | Monthly Remittance of Withholding Tax on Compensation | 10th of following month |
| BIR Form 1604-CF | Annual Information Return of Income Tax Withheld on Compensation | Jan 31 |

**Electronic systems:**
- **eFPS** (Electronic Filing and Payment System): https://efps.bir.gov.ph — web-based, 24/7 access
- **eBIRForms**: https://www.bir.gov.ph/ebirforms — offline form preparation, online submission
- **e-TIS mobile app**: Beta launched March 2025, planned employee self-download feature

**Integration method:**
- eFPS is web-portal based (no public API)
- Large taxpayers required to use eFPS (Revenue Regulations No. 9-2001)
- Selected large taxpayers piloting real-time digital payroll integration
- Electronic signatures on BIR Form 2316 permitted (RMC No. 29-2021)
- File generation (e.g., alphalist) follows BIR-prescribed CSV/DAT formats

### 6.2 DBM (Department of Budget and Management) — SUCs Only

**Key systems:**
- **SARO** (Special Allotment Release Order) — now tracked on blockchain (Polygon) since 2024
- **NCA** (Notice of Cash Allocation)
- Each SARO/NCA embedded with QR code for verification
- Blockchain verification site: https://blockchain.dbm.gov.ph/
- SARO Viewer documentation: https://docs.dbm.gov.ph/saro/saro/

**Integration method:** Document-based. SUCs receive SAROs and NCAs. No public API for budget system integration.

### 6.3 COA (Commission on Audit) — SUCs Only

**Key systems:**
- **eNGAS** (Enhanced Electronic New Government Accounting System) — government accounting
- **eBudget** v2.1 — budget management

**Integration method:** SUCs maintain their own eNGAS installations. COA auditors access records. No public API. Data exchange is file-based or through COA's own audit portals.

---

## 7. PhilHealth — Student/Employee Coverage

**Managing Agency:** Philippine Health Insurance Corporation

### Employer Reporting Systems

| System | Purpose |
|--------|---------|
| **EPRS** (Electronic Premium Remittance System v2.1) | Online premium contribution management |
| **ePOAF** (Electronic PhilHealth Online Access Form) | Employer registration for online services |

### Key Forms

| Form | Purpose | Frequency |
|------|---------|-----------|
| **ER1** | Employer Data Record | One-time registration |
| **ER2** | Report of Employee-Members | New hires |
| **ER3** | Employer Data Amendment | As needed |
| **RF-1** | Employer's Remittance Report | Monthly |

### EPRS Integration Details

- Web-based: https://eprs01.philhealth.gov.ph
- Features: online POR posting, employee management, employee tagging, transaction monitoring
- Employer representatives log in to manage employees and conduct transactions
- Portal for downloads: https://www.philhealth.gov.ph/downloads/

### Student Coverage

- Dependents (students under 21) covered under parent's PhilHealth
- Student coverage reporting is through the parent's employer, not the university directly
- University reports its own employees (faculty/staff) as employer

### Integration Method

- Portal-based (EPRS web interface)
- No public REST API documented
- File upload for bulk operations (format prescribed by PhilHealth)

### eGov PH Super App Migration

All three contribution agencies (SSS, PhilHealth, Pag-IBIG) are migrating to the **eGov PH Super App**, which will consolidate remittance and reporting in one API by Q4 2025. Portal: https://egov.ph

---

## 8. SSS / GSIS — Faculty/Staff HR Integration

### 8.1 SSS (Social Security System) — Private HEI Employees

**Electronic systems:**
- **My.SSS** — employer portal for contribution management
- **e-CS** (Electronic Collection System) — real-time posting of contributions
- **e-CL** (Electronic Contribution Collection List) — generate/review/edit employee contributions

**Key forms:**
- **R-3** — Contribution Collection List (monthly)
- **R-5** — Loan Payment Return
- Submission deadline: 10th day of following month (SSS Circular 2024-03)

**Integration method:**
- Portal-based via My.SSS
- Payment Reference Number (PRN) system for contribution payments
- Employers generate, review, and edit e-CL through portal
- No public REST API (eGov PH Super App consolidation planned)

### 8.2 GSIS (Government Service Insurance System) — SUC Employees

**Electronic systems:**
- **eBCS** (Electronic Billing and Collection System) — web-based contribution management
- **eGSISMO** (Electronic GSIS Member Online) — member self-service portal at https://gsismo.e.gov.ph/

**eBCS features:**
- Download GSIS billing statements
- Upload Electronic Remittance File (ERF)
- Review member account history
- Used by agency finance officers and ERF officers

**Key requirements:**
- Contributions deducted monthly from salary
- Remitted within first 10 days of following calendar month
- ERF contains list of members and monthly remittances (CSV format)

**Integration method:**
- Portal-based (eBCS web interface)
- ERF file upload (structured format)
- No public REST API documented

### 8.3 Pag-IBIG Fund (HDMF) — All Employees

**Electronic systems:**
- **Virtual Pag-IBIG** — employer portal for contribution management
- **eSRS** (Electronic Submission of Remittance Schedule)

**Integration method:**
- Remittance file in **CSV format**
- Upload to request Online Payment Instruction Number (OPIN)
- Portal: https://www.pagibigfundservices.com/virtualpagibig/

### eGov PH Super App — Unified Government Services

- **14 million+ users** as of July 2025
- **1,000+ government services** integrated
- Won UN award for digital government
- Planned unified API for SSS, PhilHealth, Pag-IBIG remittance by Q4 2025
- App available on iOS and Android

---

## 9. Payment Gateways

### Leading Philippine Payment Platforms

| Platform | Users/Reach | Developer Portal | Integration Type |
|----------|-------------|------------------|------------------|
| **PayMongo** | Major PH gateway | https://developers.paymongo.com/ | REST API |
| **Maya** (formerly PayMaya) | 47M users | https://developers.maya.ph/ | REST API |
| **Dragonpay** | Since 2010, bank/OTC channels | https://www.dragonpay.ph/developers/ | SOAP/XML or REST/JSON |
| **GCash** | 76M users | Via aggregators or Checkout.com | Via payment aggregator |
| **PayRex** | Newer entrant | https://www.payrex.com/ | REST API (unified) |

### PayMongo — Detailed API

**Authentication:** API keys (Secret + Public), Base64 encoded in Authorization header

**Integration models:**
1. **Checkout API** — hosted payment page (quickest integration)
2. **Payment Intent / Payment Method (PIPM)** — custom checkout flow

**Key concepts:**
- PaymentIntent = shopping cart/session (amount, currency, payment methods)
- Webhooks for async notifications (payment.paid, payment.failed)
- Webhook: HTTP POST to merchant's endpoint
- Supports: cards, e-wallets (GCash, Maya), online banking, OTC

**SDKs:** PHP, JavaScript, Python, Ruby

**Sandbox:** Available for testing

### Maya — Detailed API

**Authentication:** API key + colon, Base64 encoded, "Basic" auth header

**Products:**
- **Maya Checkout** — hosted payment page with multiple payment options
- **Maya Vault** — tokenized card storage for recurring payments
- **Pay with Maya** — express payment via Maya wallet/QR

**Sandbox endpoint:** `https://pg-sandbox.paymaya.com/checkout/v1/checkouts`

**SDKs:** PHP, Ruby, JavaScript, Node.JS, iOS, Android (all free)

### Dragonpay — Detailed API

**Integration models:**
1. **Name-value pair** — browser redirect with URL parameters
2. **SOAP/XML Web Service** — server-to-server, parameters not visible to end-users
3. **REST/JSON** — HTTP GET/POST with JSON payloads

**Key parameters:**
- txnid (unique transaction ID)
- amount, currency (ccy)
- description, email
- param1, param2 (custom, posted back on completion)

**SOAP endpoint:** `https://api.dragonpay.ph/DragonPayWebService/PaymentGatewayService.asmx`

**Channels:** Bank transfers, OTC payments, e-wallets

### Integration Recommendation for University SIS

A **payment aggregator** (PayMongo or PayRex) provides the simplest integration path:
- Single API for all payment methods (cards, GCash, Maya, bank transfer, OTC)
- Transaction fees typically 1.5-3.5%
- Webhook-based async payment confirmation
- Sandbox for testing

---

## 10. Philippine Academic Standards

### Transcript of Records (TOR) — Digital Format

**Legal basis:** RA 8792 (E-Commerce Act of 2000) recognizes electronic documents and electronic signatures as legal equivalents of paper.

### Philippine E-Transcript Hub (Pilot)

- Joint initiative of **CHED and DICT** (since 2023)
- HEIs issue **digitally signed PDFs with QR-code verification**
- Direct submission to DFA for apostille
- Paper TORs still required upon request
- Digital release reduces processing to 3-5 days

### CHED eCAV (Full Implementation April 2025)

- Each issued eCAV includes unique QR code for authenticity verification
- All CAV applications processed through eCAV web platform
- Real-time status tracking
- Portal: https://ecav.ched.gov.ph/

### Electronic Signatures

- **RA 8792** provides legal validity for e-signatures
- Defined as "any distinctive mark, characteristic, or sound in electronic form representing identity"
- Must be attached to or logically associated with an electronic document
- Intent to authenticate or approve required

### Digital Credential Standards

**CHED CMO No. 1, Series of 2025** — establishes national framework for microcredentials:
- All microcredentials mapped to **PQF Levels 5-8**
- Learning outcomes must be measurable and standardized
- Compatible with **Open Badges 3.0** and **W3C Verifiable Credentials**

**Philippine Qualifications Framework (PQF):**
- Describes levels of educational qualifications
- Sets standards for qualification outcomes
- Portal: https://pqf.gov.ph/

### Data Format Standards for TOR

No single mandated digital format exists. Current practices:
- PDF with digital signature and QR code (E-Transcript Hub)
- Paper-based with manual authentication (traditional)
- CHED eCAV for authentication/verification layer

---

## 11. Other Systems

### 11.1 Alumni Tracking Systems

- Typically custom-built per institution
- CHED Graduate Tracer Study provides a standardized survey framework
- Data collected: employment status, salary range, job relevance to degree, competency assessments
- No standardized API or data exchange format across institutions
- Integration point: SIS can export graduate data to feed alumni/tracer databases

### 11.2 OBE (Outcome-Based Education) Reporting

**Accrediting bodies in the Philippines:**

| Body | Scope |
|------|-------|
| **AACCUP** | State Universities and Colleges |
| **PAASCU** | Private schools, colleges, universities |
| **PACUCOA** | Private colleges and universities |
| **ACSCU-AAI** | Christian schools, colleges, universities |
| **ALCUCOA** | Local colleges and universities |
| **FAAP** | Federation/umbrella for all above |

**Accreditation levels:** I (initial) through IV (exemplary)

**OBE data requirements for accreditation:**
- Program outcomes mapped to institutional outcomes
- Course outcomes mapped to program outcomes
- Assessment evidence (rubrics, portfolios, exam results)
- Continuous improvement evidence
- Graduate employability data

**Integration point:** SIS should track and report student learning outcomes, assessment results, and program completion data aligned to PQF levels and institutional OBE frameworks.

### 11.3 Research Management Systems

- No Philippine-mandated standard
- Common systems: DSpace (institutional repositories), OJS (Open Journal Systems)
- CHED HEMIS Research Extension Form collects research activity data
- Potential SIS integration: link faculty/student research outputs to academic records

### 11.4 Library Systems

**Dominant ILS in Philippine universities: Koha (open-source)**

**Protocol support:**

| Protocol | Purpose |
|----------|---------|
| **Z39.50** | Bibliographic record search and retrieval |
| **SRU/SRW** | Modern successor to Z39.50 (XML-based) |
| **SIP2** | Self-checkout, RFID systems, security gates |
| **NCIP** | Interlibrary loan / resource sharing |
| **OAI-PMH** | Metadata harvesting |
| **REST API** | Koha's extensible REST API for custom integration |

**Cataloging standards:** MARC 21, UNIMARC, MARCXML, ISO 2709

**SIS integration points:**
- Patron management (student enrollment status synced to library system)
- Clearance verification (library holds/fines blocking enrollment)
- Single sign-on (SSO) for unified student access
- Koha REST API enables programmatic patron and circulation management

---

## Summary: Integration Readiness Matrix

| System | API Available | Integration Method | Maturity |
|--------|--------------|-------------------|----------|
| PhilSys Check | Yes (public key crypto) | QR verification, eVerify API | Production (87 relying parties) |
| PhilSys eVerify | Yes (biometric API) | REST API via onboarding | Production |
| CHED HEMIS | No public API | Excel file upload | Mature (annual) |
| CHED eCAV | No public API | Web portal | Production (April 2025) |
| UniFAST/TES | No public API | Portal upload (MOA required) | Production |
| DOST-SEI | No public API | Document-based | Legacy |
| LMS (Moodle/Canvas) | Yes (LTI 1.3, OneRoster) | REST API, OAuth2/JWT | Mature standard |
| BIR eFPS | No public API | Web portal, file generation | Production |
| DBM SARO | No public API | Blockchain verification | Production |
| COA eNGAS | No public API | Standalone installation | Legacy |
| PhilHealth EPRS | No public API | Web portal | Production |
| SSS My.SSS | No public API (eGov planned) | Web portal, PRN system | Production |
| GSIS eBCS | No public API | Web portal, ERF upload (CSV) | Production |
| Pag-IBIG eSRS | No public API (eGov planned) | Web portal, CSV upload | Production |
| PayMongo | Yes (REST) | REST API, webhooks | Production |
| Maya | Yes (REST) | REST API, SDK | Production |
| Dragonpay | Yes (SOAP/REST) | SOAP XML or REST JSON | Production |
| eGov PH Super App | Planned (Q4 2025) | Unified API for gov't services | In development |
| Koha Library | Yes (REST) | REST API, SIP2, Z39.50 | Mature |

---

## Key Architectural Recommendations

1. **PhilSys integration** should be prioritized — it provides foundational identity verification and is actively onboarding relying parties. Both offline (QR/EdDSA) and online (eVerify API) modes should be supported.

2. **Government agency integrations** (CHED, UniFAST, DOST-SEI, BIR, SSS, GSIS, PhilHealth, Pag-IBIG) are currently portal/file-based. The SIS should support **file export in prescribed formats** (Excel, CSV, DAT) rather than direct API integration. Watch the **eGov PH Super App** for future unified API.

3. **LMS integration** should follow **LTI 1.3 / LTI Advantage** and **OneRoster 1.2** standards. This covers 95%+ of LMS platforms used in Philippine universities.

4. **Payment integration** should use an **aggregator** (PayMongo recommended) for simplicity — single API covers cards, GCash, Maya, bank transfers, and OTC.

5. **Digital credentials** should align with **W3C Verifiable Credentials** and **Open Badges 3.0**, mapped to PQF levels, with QR-code verification compatible with CHED eCAV.

6. **Library integration** should use **Koha REST API** for patron sync and **SIP2** for self-service operations.

---

## Sources

### PhilSys / National ID
- [PhilSys Official Site](https://philsys.gov.ph/)
- [PSA Integrates National ID to PSAHelpline](https://psa.gov.ph/content/psa-integrates-national-id-psahelpline-identity-verification-enhanced-security)
- [PhilSys Check Info](https://sites.google.com/view/philsys-check/home)
- [NIDAS Overview — Kairos](https://www.kairos.com/post/national-id-authentication-services-nidas-what-it-is-how-it-works-and-where-kairos-fits)
- [56M National ID Authentications](https://philsys.gov.ph/56m-national-id-authentications-largest-use-cases-in-social-protection-financial-inclusion/)
- [PSA PhilSys Check Launch](https://psa.gov.ph/content/psa-unveils-philsys-check-philid-verification-system)
- [FOI Request for PhilSys API](https://www.foi.gov.ph/requests/access-to-api-or-method-for-verifying-the-validity-of-philsys-id/)
- [Philippines Digital ID Biometric Update](https://www.biometricupdate.com/202602/philippines-national-id-authentication-services-improve-social-protection-g2p-transactions)
- [National ID eVerify Portal](https://everify.gov.ph)

### CHED Systems
- [CHED Official Site](https://ched.gov.ph/)
- [HEMIS Orientation CHED Region 1](https://site.chedro1.com/chedro-spearheads-2024-hemis-orientation/)
- [HEMIS Data Collection CHED Region 11](https://ro11.ched.gov.ph/2024/10/25/online-orientation-for-the-annual-data-collection-of-hemis-for-sy-2024-2025/9581/uncategorized/)
- [HEIDA Portal](https://heida.ched.gov.ph/)
- [eCAV Portal](https://ecav.ched.gov.ph/)
- [CHED One Touch](https://onetouch.ched.gov.ph/)
- [eCAV Full Implementation Advisory](https://chedcar.com/2025/06/17/public-advisory-on-the-full-implementation-of-ched-electronic-certification-authentication-and-verification-ecav-web-application-system/)
- [CHED Microcredentials — Accredify](https://www.accredify.io/education/making-microcredentials-work-cheds-new-guidelines-mean-for-philippine-universities)

### UniFAST / TES
- [UniFAST Official](https://unifast.gov.ph/)
- [CHED UniFAST Page](https://ched.gov.ph/unifast/)
- [TES Program Overview — EduIsle](https://eduisle.com/tertiary-education-subsidy-2025-2026-unifast/)
- [UniFAST MC05-2023 Guidelines (PDF)](https://unifast.gov.ph/assets/pdf/guidelines/UniFAST_MC052023.pdf)

### DOST-SEI
- [DOST-SEI Official](https://www.sei.dost.gov.ph/)
- [DOST-SEI Helpdesk](https://helpdesk.sei.dost.gov.ph/)
- [DOST-SEI Citizen's Charter (PDF)](https://cc.sei.dost.gov.ph/citizens-charter/sei-pdf-citizens_charter-2025_First_Edition.pdf)

### LMS / EdTech Standards
- [LTI Fundamentals FAQ — 1EdTech](https://www.imsglobal.org/lti-fundamentals-faq)
- [Moodle LTI Documentation](https://docs.moodle.org/501/en/LTI_and_Moodle)
- [Google Classroom SIS Integration / OneRoster](https://developers.google.com/workspace/classroom/sis-integrations/validate-your-SIS)
- [LTI Assignment and Grade Services Spec](https://www.imsglobal.org/spec/lti-ags/v2p0)
- [Canvas in Filipino Classrooms — Instructure](https://www.instructure.com/en-au/resources/blog/three-insights-how-canvas-lms-transforming-filipino-classrooms)

### Government Financial Systems
- [BIR eFPS](https://efps.bir.gov.ph/)
- [BIR eBIRForms](https://www.bir.gov.ph/ebirforms)
- [BIR Forms List](https://www.bir.gov.ph/bir-forms)
- [DBM Blockchain SARO](https://blockchain.dbm.gov.ph/)
- [DBM SARO Viewer Docs](https://docs.dbm.gov.ph/saro/saro/)
- [COA Official](https://www.coa.gov.ph/)

### PhilHealth
- [PhilHealth EPRS v2.1 User Manual (PDF)](https://www.philhealth.gov.ph/downloads/employer/EPRS_v2.1_UserManual.pdf)
- [PhilHealth Downloads](https://www.philhealth.gov.ph/downloads/)
- [PhilHealth Employer Services](https://www.philhealth.gov.ph/partners/employers/)

### SSS / GSIS / Pag-IBIG
- [SSS Official](https://www.sss.gov.ph/)
- [SSS Pay Contributions](https://www.sss.gov.ph/pay-contribution/)
- [GSIS eBCS](https://www.gsis.gov.ph/ebcs/)
- [eGSISMO](https://gsismo.e.gov.ph/)
- [GSIS Contributions](https://www.gsis.gov.ph/active-members/contributions/)
- [Virtual Pag-IBIG](https://www.pagibigfundservices.com/virtualpagibig/)
- [eGov PH Super App — PIA](https://pia.gov.ph/news/egov-ph-super-app-the-future-of-govt-services-at-your-fingertips/)
- [eGov PH 14M Users](https://tribune.net.ph/2025/07/28/egov-ph-super-app-hits-14m-users-earns-un-award)

### Payment Gateways
- [PayMongo Developer Docs](https://developers.paymongo.com/)
- [Maya Developer Hub](https://developers.maya.ph/)
- [Maya Checkout API](https://developers.maya.ph/docs/maya-checkout)
- [Dragonpay Developers](https://www.dragonpay.ph/developers/)
- [Dragonpay PS API (PDF)](https://www.dragonpay.ph/wp-content/uploads/2014/05/Dragonpay-PS-API)
- [PayRex](https://www.payrex.com/)
- [PH Payment Gateway Comparison — HitPay](https://blog.hitpayapp.com/philippines-payment-gateway-comparison/)

### Academic Standards / Credentials
- [E-Commerce Act RA 8792 — Adobe](https://helpx.adobe.com/legal/esignatures/regulations/philippines.html)
- [E-Signatures Philippines — DocuSign](https://www.docusign.com/products/electronic-signature/legality/philippines)
- [Digital TOR Shift — Parchment](https://www.parchment.com/en-sea/blog/transcript-of-records-in-the-philippines/)
- [Philippine Qualifications Framework](https://pqf.gov.ph/)
- [PAASCU](https://paascu.org.ph/)

### Library Systems
- [Koha ILS](https://kohasupport.com/koha/)
- [Koha Standards — EIFL](https://www.eifl.net/resources/koha-worlds-first-free-and-open-source-integrated-library-management-system)
