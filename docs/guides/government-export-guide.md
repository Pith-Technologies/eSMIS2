# Government Export Guide

How to generate and submit government-mandated reports from eSMIS.

## CHED HEMIS Export

HEMIS is the Higher Education Management Information System. Data is submitted annually to the CHED Regional Office.

### Forms by institution type

**SUC (State Universities and Colleges)**

| Form | Contents |
|------|----------|
| Form A | Institutional profile |
| Form B | Programs, enrollment, and graduates |
| Form E1 / E2 | Faculty data |
| Research Extension | Research and extension activities |
| Form GH | Allotment and expenditure |
| Graduate List | Names and program details of all graduates |

**Private HEIs**

| Form | Contents |
|------|----------|
| Form A | Institutional profile |
| Form BC | Programs, enrollment, and graduates |
| Form E5 | Faculty data |
| Graduate List | Names and program details of all graduates |

### Steps

1. Navigate to **Reports → HEMIS Export**.
2. Select the academic year.
3. Select the forms to include.
4. Click **Validate** — the system checks completeness before allowing download.
5. Click **Download Excel** to get the submission-ready file.

### Validation checks

The system verifies the following before generating the export:

- All active programs have enrollment data for every year level.
- All faculty records have qualifications entered.
- Enrollment headcounts match the sum of individual year-level counts.

### Common errors

**Missing program data** — A program is active but has no enrollment records for the selected year. Check the program's enrollment entries under Academic Records.

**Faculty without qualifications** — One or more faculty members have no highest educational attainment recorded. Go to HR → Faculty and complete the qualification fields.

**Enrollment count mismatches** — The program-level total does not match the year-level breakdown. Recheck the enrollment records for the affected program and year level.

---

## CHED eCAV Export

eCAV is CHED's credential authentication and verification system. Each credential carries a QR code that can be verified against the eCAV portal.

### Steps

1. Navigate to **Documents → eCAV Export**.
2. Select the student.
3. Click **Generate Credential Data** — the system produces the structured data payload.
4. Log in to the eCAV portal and upload the payload.

### QR code format

The QR code embedded in the credential must conform to the eCAV verification schema. eSMIS generates the payload in the required format; do not alter it before uploading.

---

## UniFAST / TES Export

The Tertiary Education Subsidy (TES) is administered by UniFAST. The export produces the eligible student list for upload to the TES Portal.

### Prerequisites

- MOA between the institution and CHED-UniFAST must be signed and on file.
- A TES Focal Person must be assigned in **Settings → UniFAST Configuration**.

### Steps

1. Navigate to **Financial Aid → TES Export**.
2. Select the term.
3. Click **Generate Eligible Student List**.
4. Click **Validate** — the system runs the eligibility checks listed below.
5. Click **Download** to get the file.
6. Log in to the TES Portal and upload the file.

### Validation checks

| Check | Detail |
|-------|--------|
| Citizenship | Student must be a Filipino citizen |
| No prior degree | Student must not hold an existing baccalaureate degree |
| Retention compliance | Student must meet the institution's retention policy |
| Fee schedule | A current fee schedule must be attached to the student's enrollment |

Students already present in the Listahanan or 4Ps database are flagged for review. The system does not automatically exclude them — the TES Focal Person must confirm eligibility.

---

## DOST-SEI Scholar Reports

DOST-SEI requires a grade report each semester and an official TOR for all scholars.

### Steps

1. Navigate to **Financial Aid → DOST Reports**.
2. Select the scholars to include.
3. Click **Generate Grade Report** — produces the semester grade summary.
4. Click **Print Certified TOR** — generates the official transcript for submission.

### Requirements

- Grades must be finalized for the selected semester before generating the report.
- Academic load must comply with DOST-SEI minimum unit load requirements.
- The TOR must carry the Registrar's official signature and dry seal before submission.

---

## BIR Alphalist (Faculty and Staff)

The BIR Alphalist is the annual withholding tax summary. It includes Form 2316 for every employee.

### Steps

1. Navigate to **HR → Payroll → BIR Reports**.
2. Click **Generate Alphalist**.
3. Click **Export** to download in the BIR-prescribed format.

The export file conforms to the current BIR data entry guidelines. Import it directly into the BIR RELIEF software or the eBIR Forms system.

---

## Government Contribution Files

eSMIS generates contribution remittance files for SSS, GSIS, PhilHealth, and Pag-IBIG.

### Export formats

| Agency | Format |
|--------|--------|
| SSS | CSV (R-3 format) |
| GSIS | ERF (Electronic Remittance File) |
| PhilHealth | RF-1 format |
| Pag-IBIG | CSV |

### Steps

1. Navigate to **HR → Contributions**.
2. Select the agency.
3. Select the contribution period.
4. Click **Generate**.
5. Click **Download** to get the remittance file.

Upload each file to the corresponding agency portal (My.SSS, GSIS e-Card, PhilHealth e-Services, Virtual Pag-IBIG).

---

## Deep Dives

- `docs/principles/module-architecture.md` — how reporting modules fit into the layer structure
- `docs/principles/access-rights.md` — who can generate and download government reports
- `docs/principles/performance-scalability.md` — large export batches and queue_job usage
