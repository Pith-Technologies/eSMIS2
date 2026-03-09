# Government & External System Integration Principles

Standards for integrating eSMIS with Philippine government systems, LMS platforms, payment gateways, and campus subsystems.

## Core Principles

1. **File-based exports for government systems without APIs** — Most Philippine government systems (CHED HEMIS, UniFAST, DOST-SEI, BIR, SSS, GSIS, PhilHealth, Pag-IBIG) have no public REST API. Generate prescribed file formats (Excel, CSV, DAT, ERF) for manual portal upload.
2. **Webhook-based async for payment gateways** — PayMongo, Maya, and Dragonpay confirm payments asynchronously. Never poll; handle confirmations via incoming webhooks.
3. **Standards-based for LMS** — Use LTI 1.3 and OneRoster 1.2. These cover 95%+ of LMS platforms in Philippine universities and avoid vendor lock-in.
4. **Retry and queue for API calls** — All outbound API calls (PhilSys eVerify, LMS, payment gateways, Koha) must be queued via `queue_job`. Never call external APIs synchronously in a web request if the result is not immediately user-blocking.
5. **Credentials in system parameters only** — Never store API keys, PSA public keys, webhook secrets, or OAuth tokens in source code. Use `ir.config_parameter` (Odoo system parameters) exclusively.

---

## 1. PhilSys (Philippine Identification System — RA 11055)

**Managing Agency:** Philippine Statistics Authority (PSA)
**Implementation Module:** `esmis_philsys`

### System Overview

PhilSys provides identity verification through **NIDAS (National ID Authentication Services)**. There are two distinct modes that must both be supported:

| Mode | Description | Connectivity |
|------|-------------|--------------|
| **PhilSys Check** (QR verification) | Validates the PhilID card by verifying the PSA-signed QR code using EdDSA public key cryptography | Offline capable once public key is distributed |
| **National ID eVerify** | Live biometric comparison (selfie vs. reference image), returns pass/fail | Online only (REST API) |

### Data Fields Returned

From a PhilSys Check QR scan (both modes share this demographic data):

| Field | Notes |
|-------|-------|
| `first_name`, `middle_name`, `last_name`, `suffix` | Full legal name |
| `sex` | As registered |
| `date_of_birth` | DOB |
| `place_of_birth` | As registered |
| `pcn` | PhilSys Card Number (card-specific; PSN is the persistent person ID) |
| `date_of_issuance` | Card issue date |
| `card_status` | Active, suspended, etc. |
| `qr_code_status` | Valid/invalid |
| `photo` | Low-resolution (ePhilID only) |

### Integration Method

**PhilSys Check (Offline QR Verification):**
- PSA signs demographic data embedded in the QR code using **EdDSA (Edwards-curve Digital Signature Algorithm)**
- eSMIS verifies the signature against the PSA-distributed public key without requiring a network call
- The public key must be stored in `ir.config_parameter` as `esmis_philsys.psa_public_key`
- Parse and verify QR payload on-device; no data leaves the institution during this step

**eVerify (Online Biometric):**
- REST API call to PSA's eVerify endpoint
- Submits a live selfie; PSA returns a pass/fail decision
- No raw biometric data is stored in eSMIS — only the verification result and timestamp

### Authentication

| Mode | Auth Mechanism |
|------|----------------|
| PhilSys Check | PSA-distributed EdDSA public key (obtained after NDA execution) |
| eVerify | API credentials issued after relying party onboarding at https://everify.gov.ph |

Store all credentials in system parameters:
- `esmis_philsys.psa_public_key`
- `esmis_philsys.everify_api_key`
- `esmis_philsys.everify_endpoint_url`

### Onboarding as a Relying Party

1. Contact PSA at the appropriate sector email (educational institutions: coordinate with CHED for guidance)
2. Complete the online application at https://everify.gov.ph
3. Execute the **Non-Disclosure Agreement (NDA)** — required before receiving the public key and API documentation
4. Obtain the PhilSys Check Public Key and API documentation via authorization letter template

### Error Handling

```python
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

def verify_philsys_qr(self, qr_payload):
    try:
        result = self._verify_eddsa_signature(qr_payload)
    except InvalidSignatureError:
        raise UserError(_(
            "The PhilID QR code could not be verified. "
            "The card may be tampered with or the public key may be outdated. "
            "Please contact the Registrar's Office."
        ))
    except Exception:
        _logger.exception("PhilSys QR verification failed for enrollment_id=%s", self.id)
        raise UserError(_("ID verification failed due to a system error. Please try again."))
    return result
```

- Log failures with enrollment/session ID only — never log the QR payload or any biometric data
- A failed eVerify call must not silently fall back to a lower assurance level without user consent and audit trail

### Testing Approach

- Unit test EdDSA signature verification using PSA-provided test vectors (obtained during onboarding)
- Mock the eVerify HTTP endpoint for integration tests — never call PSA's production API from automated tests
- Test both the success path and signature failure path
- Test that no PII appears in log output on failure

---

## 2. CHED HEMIS (Higher Education Management Information System)

**Managing Agency:** Commission on Higher Education (CHED)
**Implementation Module:** `esmis_hemis_export` or `esmis_reporting_ph`

### System Overview

HEMIS is CHED's annual data collection system. There is no public REST API. HEIs submit data as Microsoft Excel files through CHED Regional Offices during annual orientation periods.

### Required Forms by Institution Type

**State Universities and Colleges (SUCs):**

| Form | Content |
|------|---------|
| Form A | Institutional profile |
| Form B | Programs offered, enrollment data, graduate data |
| Form E1 | Faculty-related data |
| Form E2 | Faculty and personnel data |
| Research Extension Form | Research and extension activities |
| Form GH | Allotment and expenditures |
| Graduate List Form | Comprehensive list of graduates |

**Private HEIs and Local Universities/Colleges (LUCs):**

| Form | Content |
|------|---------|
| Form A | Institutional profile |
| Form BC | Programs offered, enrollment data, graduate data |
| Form E5 | Faculty profile |
| Graduate List Form | Comprehensive list of graduates |

### Integration Method

- **File export only** — generate Excel files matching CHED's prescribed templates
- Use `openpyxl` to write to CHED's exact column layout; do not invent an intermediate format
- Generated files are downloaded from eSMIS; the registrar uploads them manually to the CHED portal
- Provide a dedicated wizard in `esmis_hemis_export` that selects academic year and institution type, then produces a ZIP of all required forms

### Authentication

No API authentication. The registrar logs into the CHED Regional Office portal with their own CHED credentials.

### Error Handling

- Validate completeness of source data before generating files (missing programs, null enrollment counts, etc.)
- Surface validation errors to the user with field-level guidance before the export runs — a partially complete Excel submitted to CHED causes manual correction overhead
- Log the export event (academic year, institution, user, timestamp) to the audit trail via `esmis_audit`

### Testing Approach

- Generate test exports using factory data and assert that column headers, sheet names, and row counts match the CHED template specification
- Test with both SUC and private HEI institution types
- Test that missing required data raises a `UserError` before file generation begins

---

## 3. CHED eCAV (Electronic Certification, Authentication, and Verification)

**Managing Agency:** Commission on Higher Education (CHED)
**Implementation Module:** `esmis_documents` (with eCAV export feature)

### System Overview

eCAV is CHED's web platform for credential authentication. Full implementation was mandated in April 2025. Each issued eCAV contains a unique QR code for real-time authenticity verification. There is no public API — HEIs export credential data for manual upload to the eCAV portal.

### Integration Method

- eSMIS exports student credential data (transcript summary, graduation details, program information) in the format expected by the eCAV portal
- The QR codes embedded in printed/digital credentials issued by the university must be formatted to be scannable and compatible with eCAV's verification flow
- The registrar uploads exported data through https://ecav.ched.gov.ph/

### Authentication

No API authentication. Registrar uses institutional eCAV portal credentials.

### Error Handling

- Validate that all required credential fields are populated before export
- Flag records where graduation status or program approval is incomplete, as these will be rejected by CHED
- Log all credential export events to the audit trail (which student records were included, who initiated the export, when)

### Testing Approach

- Test credential export output against the eCAV-prescribed format
- Test that incomplete records are caught before export
- Test QR code generation for proper encoding

---

## 4. UniFAST / TES (RA 10931, RA 10687)

**Managing Agency:** CHED-UniFAST (Unified Student Financial Assistance System for Tertiary Education)
**Implementation Module:** `esmis_financial_aid_ph`

### System Overview

UniFAST consolidates all government-funded Student Financial Assistance Programs (StuFAPs). The Tertiary Education Subsidy (TES) is school-based — HEIs screen applicants and submit data through the TES Portal. A valid **Memorandum of Agreement (MOA)** with CHED-UniFAST is required before portal access is granted.

### Data Fields Required from HEIs

| Field | Purpose |
|-------|---------|
| Student personal information (name, DOB, address) | Identity matching |
| Enrollment status and program | Eligibility confirmation |
| Certified list of enrolled student-applicants | Masterlist submission |
| Certificate of Registration / Enrollment (CORS/COE) | Documentary requirement |
| Fee schedules | Subsidy calculation |
| Family income data | Ranking for eligibility |

UniFAST cross-references submitted data against:
- **Listahanan** (DSWD poverty database)
- **4Ps** (Pantawid Pamilyang Pilipino Program membership)

### Integration Method

- **Portal-based file upload** — HEIs upload data through the TES Portal (https://unifast.gov.ph/)
- Provide export wizards in `esmis_financial_aid_ph` that generate the prescribed spreadsheet format
- The TES Focal Person at each HEI manages submissions; eSMIS should track which students have been submitted and their submission status

### Authentication

No API authentication. TES Focal Person uses their own UniFAST portal credentials.

### Error Handling

- Validate that submitted students meet minimum eligibility criteria (enrolled, correct program, income data present) before generating the upload file
- Track submission state per student (`not_submitted`, `submitted`, `approved`, `rejected`) in eSMIS so the institution has a local record independent of the UniFAST portal
- Raise a `UserError` if a student is flagged for submission but their enrollment is not yet confirmed

### Testing Approach

- Test export file generation against the UniFAST-prescribed template
- Test student eligibility validation logic
- Test submission state transitions

---

## 5. DOST-SEI Scholarships

**Managing Agency:** Department of Science and Technology — Science Education Institute (DOST-SEI)
**Implementation Module:** `esmis_financial_aid_ph`

### System Overview

DOST-SEI manages scholarship programs for science and technology students. Integration is entirely document-based — no public API exists. HEIs provide certified hard copies or scanned documents.

### HEI Integration Points

| Data | Direction | Format |
|------|-----------|--------|
| Scholar enrollment verification | HEI to DOST-SEI | Certified document (PDF/scanned) |
| Grade reports (every semester) | HEI to DOST-SEI | Certified TOR or True Copy of Grades (TCG) signed by Registrar or Dean |
| Academic load compliance | HEI to DOST-SEI | Certified document |
| Stipend/allowance disbursement | DOST-SEI to scholar | Direct to student |

### Integration Method

- eSMIS generates grade reports and enrollment certifications for DOST scholars in the prescribed format
- Track which scholars have submitted their semester requirements and flag overdue submissions
- When DOST-SEI eventually publishes an API, the data model in `esmis_financial_aid_ph` should need no structural changes — only a new transport layer

### Authentication

No API authentication. Document submission is handled by the Registrar or Dean's office.

### Error Handling

- Alert scholarship coordinators when a DOST scholar's grade submission deadline is approaching (configurable lead time)
- Flag scholars whose academic load falls below the DOST-SEI prescribed minimum so the coordinator can act before the semester reporting deadline

### Testing Approach

- Test grade report generation for DOST scholars
- Test deadline alerting logic with mocked dates
- Test academic load compliance validation

---

## 6. LMS Integration (Moodle, Canvas, Google Classroom)

**Implementation Module:** `esmis_lms_bridge`

### System Overview

LMS integration uses two open standards maintained by 1EdTech (formerly IMS Global):

| Standard | Version | Purpose |
|----------|---------|---------|
| **LTI** | 1.3 (current) | Tool launch, grade passback, deep linking |
| **LTI Advantage** | Extensions on 1.3 | AGS, NRPS, Deep Linking |
| **OneRoster** | 1.2 | Roster and enrollment data exchange |

### LTI 1.3 Technical Details

- **Authentication:** OAuth 2.0 + OpenID Connect (OIDC), JSON Web Tokens (JWT)
- **Key services:**
  - **Deep Linking** — content selection and embedding from LMS into external tools
  - **Assignment and Grade Services (AGS)** — near real-time grade passback from LMS to eSMIS
  - **Names and Roles Provisioning Service (NRPS)** — automated roster sync from LMS to tools

### OneRoster 1.2 Technical Details

- REST API or CSV file exchange
- Syncs: students, teachers, classes, enrollments, demographics
- Grade passback via OneRoster Gradebook API
- Google Classroom supports OneRoster for SIS integration

### Integration Architecture

```
eSMIS (esmis_lms_bridge)
    ↕  OneRoster 1.2 REST API   — enrollment/roster sync
    ↕  LTI 1.3 + AGS            — grade passback
LMS (Moodle / Canvas / Google Classroom)
```

### Authentication

| Protocol | Credentials |
|----------|-------------|
| LTI 1.3 launch | RSA key pair; LMS registers eSMIS as a platform (client_id, deployment_id) |
| OneRoster REST | OAuth 2.0 client credentials (client_id, client_secret) |

Store in system parameters:
- `esmis_lms_bridge.lti_private_key`
- `esmis_lms_bridge.lms_client_id`
- `esmis_lms_bridge.lms_client_secret`
- `esmis_lms_bridge.lms_base_url`

Support multiple LMS configurations (an institution may use more than one platform).

### Error Handling

```python
def sync_enrollment_to_lms(self, enrollment):
    try:
        self._oneroster_post_enrollment(enrollment)
    except requests.Timeout:
        _logger.warning(
            "LMS enrollment sync timed out for enrollment_id=%s, will retry", enrollment.id
        )
        enrollment.with_delay(max_retries=3, eta=300).sync_enrollment_to_lms()
    except requests.HTTPError as e:
        _logger.error(
            "LMS enrollment sync failed for enrollment_id=%s: HTTP %s",
            enrollment.id, e.response.status_code
        )
        raise
```

- Use `queue_job` (`with_delay()`) for all LMS sync operations — never block a web request
- Exponential backoff on retries: 5 min, 15 min, 60 min
- A failed grade passback must not silently drop — surface failed sync records in a reconciliation view

### Testing Approach

- Unit test LTI 1.3 JWT construction and OIDC flow validation
- Mock OneRoster API endpoints for enrollment sync integration tests
- Test grade passback round-trip with a mock AGS endpoint
- Test retry behavior on timeout and on HTTP 5xx responses
- Never call a live LMS from automated tests

---

## 7. Payment Gateways (PayMongo, Maya, Dragonpay)

**Implementation Module:** `esmis_payment`

### System Overview

| Gateway | Integration Type | Reach |
|---------|-----------------|-------|
| **PayMongo** | REST API + webhooks | Cards, GCash, Maya, bank transfer, OTC |
| **Maya** | REST API + webhooks | 47M users; Maya wallet, QR, cards |
| **Dragonpay** | SOAP/XML or REST/JSON | Bank transfers, OTC channels |

**Recommendation:** Use PayMongo as the primary gateway for broadest payment method coverage under a single API. Dragonpay is valuable for OTC-heavy student populations without bank accounts.

### Integration Method

**Payment flow:**
1. eSMIS creates a PaymentIntent via REST API → receives a checkout URL
2. Student completes payment on the gateway's hosted page
3. Gateway sends a webhook POST to eSMIS confirming payment
4. eSMIS marks the fee record as paid and issues an official receipt

Never poll the gateway for payment status. All confirmation is webhook-driven.

### Authentication

| Gateway | Auth Mechanism |
|---------|----------------|
| PayMongo | Secret API key (Base64-encoded in Authorization header) |
| Maya | API key + colon, Base64-encoded, "Basic" auth |
| Dragonpay | Merchant ID + password |

Store in system parameters:
- `esmis_payment.paymongo_secret_key`
- `esmis_payment.paymongo_webhook_secret`
- `esmis_payment.maya_secret_key`
- `esmis_payment.maya_webhook_secret`
- `esmis_payment.dragonpay_merchant_id`
- `esmis_payment.dragonpay_password`

Use sandbox credentials for non-production environments; gate sandbox vs. production via a system parameter flag.

### Webhook Handling

```python
@route('/esmis/payment/webhook/paymongo', type='json', auth='none', csrf=False)
def handle_paymongo_webhook(self, **kwargs):
    payload = request.get_data(as_text=True)
    signature = request.httprequest.headers.get('Paymongo-Signature')
    if not self._verify_webhook_signature(payload, signature):
        _logger.warning("PayMongo webhook received with invalid signature")
        return Response(status=400)
    event = json.loads(payload)
    self.env['esmis.payment.event'].sudo().with_delay().process_gateway_event(event)
    return Response(status=200)
```

- Always verify the webhook signature before processing
- Respond with HTTP 200 immediately; process the event asynchronously via `queue_job`
- Implement idempotency — a webhook may be delivered more than once; check if the payment event was already processed before applying it

### Error Handling

- On gateway API error (checkout creation fails): raise `UserError` so the student can retry
- On webhook processing failure: log the raw event payload for manual reconciliation; alert finance staff
- Maintain a `esmis.payment.event` log of all incoming webhook payloads for audit purposes

### Testing Approach

- Use sandbox API keys (all three gateways provide them) for integration tests
- Test webhook signature verification — both valid and tampered payloads
- Test idempotency: simulate the same webhook delivered twice
- Test the full checkout creation → webhook confirmation flow against sandbox endpoints
- Never use production API keys in tests

---

## 8. Government Contribution Systems (BIR, SSS, GSIS, PhilHealth, Pag-IBIG)

**Scope:** HR/Payroll (faculty and staff) — not student-facing
**Implementation:** Via Odoo HR/Payroll modules (standard + eSMIS customization as needed)

### System Overview

All Philippine government contribution agencies currently operate portal-based systems with no public REST API. File generation in prescribed formats is the integration strategy.

| Agency | System | File Format | Deadline |
|--------|--------|-------------|----------|
| **BIR** | eFPS / eBIRForms | CSV/DAT (alphalist), XML | Monthly (1601-C by 10th), Annual (1604-CF Jan 31) |
| **SSS** | My.SSS / e-CS / e-CL | R-3 contribution list format | 10th of following month |
| **GSIS** | eBCS | ERF (Electronic Remittance File, CSV) | 10th of following month |
| **PhilHealth** | EPRS v2.1 | RF-1 prescribed format | Monthly |
| **Pag-IBIG** | Virtual Pag-IBIG / eSRS | CSV | Monthly |

### Integration Method

- Generate agency-prescribed export files from payroll computation data
- Staff upload files manually to agency portals
- eSMIS tracks submission status per period and agency to support compliance monitoring

### eGov PH Super App — Future Unified API

SSS, PhilHealth, and Pag-IBIG are consolidating into the **eGov PH Super App** (https://egov.ph). A unified API for remittance and reporting is planned for Q4 2025. The data model in eSMIS should be structured so that swapping from file upload to API call requires only adding a new transport layer.

### Authentication

No API authentication for current portal-based systems. Future eGov PH API credentials should be stored in system parameters when available.

### Error Handling

- Validate payroll data completeness before generating contribution files (all employees have TIN, SSS/GSIS/PhilHealth/HDMF numbers)
- Raise `UserError` for missing mandatory identifiers — do not generate a partial file
- Log generation events (period, agency, file checksum, generating user) to the audit trail

### Testing Approach

- Test file generation output against BIR, SSS, GSIS, PhilHealth, and Pag-IBIG prescribed formats
- Test validation logic for missing employee identifiers
- Test deadline alerting logic

---

## 9. Library System (Koha)

**Implementation Module:** `esmis_library_bridge`

### System Overview

Koha is the dominant Integrated Library System (ILS) in Philippine universities. Two integration protocols are relevant:

| Protocol | Purpose |
|----------|---------|
| **Koha REST API** | Patron management, circulation data |
| **SIP2** | Self-service kiosks, RFID systems, security gates |

### Integration Points

| Flow | Direction | Trigger |
|------|-----------|---------|
| Create library patron | eSMIS to Koha | New student enrollment confirmed |
| Update patron status | eSMIS to Koha | Enrollment status changes (leave of absence, graduation, dropout) |
| Clearance check | Koha to eSMIS | During enrollment or document request — check for outstanding fines/holds |
| Block enrollment | Koha result to eSMIS | Outstanding fines or unreturned items prevent enrollment confirmation |

### Authentication

- **Koha REST API:** OAuth 2.0 or API key (depends on Koha version and configuration)
- **SIP2:** Username and password over TCP connection

Store in system parameters:
- `esmis_library_bridge.koha_base_url`
- `esmis_library_bridge.koha_client_id`
- `esmis_library_bridge.koha_client_secret`
- `esmis_library_bridge.sip2_host`
- `esmis_library_bridge.sip2_port`
- `esmis_library_bridge.sip2_username`
- `esmis_library_bridge.sip2_password`

### Patron Sync

```python
def sync_patron_to_library(self, student):
    """Push enrollment status change to Koha."""
    payload = {
        "cardnumber": student.student_number,
        "surname": student.last_name,
        "firstname": student.first_name,
        "categorycode": self._map_patron_category(student),
        "branchcode": self._get_home_branch(),
        "dateexpiry": self._compute_expiry_date(student),
    }
    try:
        self._koha_api_put(f"/api/v1/patrons/{student.library_patron_id}", payload)
    except requests.HTTPError as e:
        _logger.error(
            "Koha patron sync failed for student_id=%s: HTTP %s",
            student.id, e.response.status_code
        )
        raise UserError(_("Library system sync failed. Please contact IT support."))
```

### Clearance Check

- Clearance checks block enrollment confirmation if the student has outstanding fines or unreturned items
- The check is synchronous (user is waiting for a result) but must have a timeout — if Koha is unreachable, log a warning and allow the enrollment to proceed with a pending clearance flag for manual review
- Do not hard-block enrollment on Koha connectivity failure; surface a warning to the registrar instead

### Error Handling

- Log Koha sync failures with `student_id` only — never log patron names or library borrowing history
- Use `queue_job` for non-blocking patron updates triggered by enrollment events
- Clearance check failures due to connectivity must not silently pass — they must set a `library_clearance_pending` flag and alert the registrar

### Testing Approach

- Mock Koha REST API endpoints for patron sync integration tests
- Test clearance check with both clean and flagged patron states
- Test timeout behavior — Koha unreachable should set `library_clearance_pending`, not hard-block
- Never call a live Koha instance from automated tests

---

## Architectural Patterns Reference

### Credential Storage Pattern

```python
# Always retrieve credentials from system parameters at call time
def _get_paymongo_key(self):
    param = self.env['ir.config_parameter'].sudo()
    key = param.get_param('esmis_payment.paymongo_secret_key')
    if not key:
        raise UserError(_(
            "PayMongo API key is not configured. "
            "Go to Settings > Technical > System Parameters."
        ))
    return key
```

### Queue Job Pattern for External Calls

```python
from odoo.addons.queue_job.job import job

class EsmisLmsBridge(models.Model):
    _name = 'esmis.lms.bridge'

    @job(retry_pattern={1: 5 * 60, 2: 15 * 60, 3: 60 * 60})
    def sync_enrollment_to_lms(self, enrollment_id):
        enrollment = self.env['esmis.enrollment'].browse(enrollment_id)
        self._oneroster_post_enrollment(enrollment)
```

### File Export Pattern for Government Systems

```python
class HemisExportWizard(models.TransientModel):
    _name = 'esmis.hemis.export.wizard'

    def action_export(self):
        self._validate_data_completeness()  # Raise UserError before touching openpyxl
        workbook = self._build_form_a()
        # ... build remaining forms
        return self._create_download_response(workbook)

    def _validate_data_completeness(self):
        missing = self._collect_missing_fields()
        if missing:
            raise UserError(_(
                "Cannot generate HEMIS export. The following data is missing:\n%s",
                "\n".join(missing)
            ))
```

---

## Integration Readiness Matrix

| System | API Available | Method | Priority |
|--------|:-------------:|--------|----------|
| PhilSys Check (QR / EdDSA) | Yes | Public key cryptography, offline capable | High |
| PhilSys eVerify (biometric) | Yes | REST API (onboarding via PSA NDA) | Medium |
| CHED HEMIS | No | Excel file export, manual portal upload | High |
| CHED eCAV | No | Credential data export, manual portal upload | High |
| UniFAST / TES | No | Spreadsheet file upload (MOA required) | High |
| DOST-SEI Scholarships | No | Document generation (PDF/certified reports) | Medium |
| LMS — Moodle | Yes (LTI 1.3, OneRoster 1.2) | REST API, OAuth2/JWT | High |
| LMS — Canvas | Yes (LTI 1.3, OneRoster 1.2) | REST API, OAuth2/JWT | High |
| LMS — Google Classroom | Yes (OneRoster 1.2) | REST API, OAuth2 | Medium |
| PayMongo | Yes (REST) | REST API + webhooks | High |
| Maya | Yes (REST) | REST API + webhooks | Medium |
| Dragonpay | Yes (SOAP/REST) | REST JSON or SOAP XML | Medium |
| eGov PH Super App | Planned Q4 2025 | Unified REST API (watch for release) | Future |
| BIR eFPS / eBIRForms | No | File generation (CSV/DAT), portal upload | High |
| SSS My.SSS | No | File generation, portal upload | High |
| GSIS eBCS | No | ERF file (CSV), portal upload | High (SUC only) |
| PhilHealth EPRS | No | RF-1 file, portal upload | High |
| Pag-IBIG Virtual Pag-IBIG | No | CSV file, portal upload | High |
| Koha Library | Yes (REST, SIP2) | REST API + SIP2 | Medium |

---

**See also:** [API Design](api-design.md), [Error Handling](error-handling.md), [Performance & Scalability](performance-scalability.md), [Audit & Compliance](audit-compliance.md)
