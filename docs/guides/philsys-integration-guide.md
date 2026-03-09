# PhilSys Integration Guide

How to configure and use Philippine National ID (PhilSys) verification in eSMIS.

## Onboarding as a Relying Party

Before PhilSys verification can go live, the institution must register with the Philippine Statistics Authority (PSA) as a Relying Party.

### Contact PSA

| Institution type | Contact |
|-----------------|---------|
| Private HEIs | fpsucd@psa.gov.ph |
| Government HEIs (SUCs) | gsucd@psa.gov.ph |

### Process

1. Complete the online application at https://everify.gov.ph.
2. Sign the NDA with PSA.
3. Receive the PhilSys Check Public Key and the API documentation from PSA.
4. Enter the public key and API credentials in eSMIS system parameters (see Configuration below).

---

## Offline QR Verification (PhilSys Check)

Offline verification reads and validates the QR code printed on the PhilID card. No network call to PSA is required.

### Steps

1. Student presents their PhilID card.
2. Operator scans the QR code using the device camera (via the eSMIS QR scanner widget).
3. eSMIS validates the EdDSA signature embedded in the QR data against the PSA public key stored in system parameters.
4. If the signature is valid, the system extracts the demographic payload:
   - Full name
   - Sex
   - Date of birth
   - PhilSys Card Number (PCN)
5. Extracted fields are offered for auto-population into the student record.
6. The PhilSys Number (PSN) is stored as an `esmis.identifier` record with the URI `urn:gov:ph:psa:philsys`.

### Signature validation failure

If the EdDSA signature does not match, the QR is rejected. Ask the student to present their physical card — do not manually enter the card data.

---

## Online Biometric Verification (eVerify)

Online verification confirms that the person presenting the card is its rightful holder. It requires a live network call to the PSA eVerify API.

### Steps

1. Student captures a selfie via the webcam widget in eSMIS.
2. eSMIS sends the selfie and PSN to the PSA eVerify endpoint.
3. The API returns a pass or fail authentication decision.
4. The result and timestamp are recorded on the student record.

### Async processing

The eVerify API call is handled via `queue_job` to prevent blocking the UI during network latency. The operator sees a "Verification pending" status that updates automatically when the job completes.

---

## Privacy Considerations

PhilSys data is subject to the Data Privacy Act of 2012 (RA 10173).

- **Minimal retention**: store only the PSN. Do not retain full biometric data (fingerprint templates, iris scans) in eSMIS.
- **Consent**: display and log a consent acknowledgment before initiating any PhilSys verification. Verification must not proceed without explicit consent.
- **Audit trail**: every verification attempt — successful or failed — is logged with operator, timestamp, and outcome.
- **Key rotation**: monitor PSA announcements. When PSA rotates the PhilSys Check Public Key, update `esmis.philsys.public_key` in system parameters before the old key expires. eSMIS will reject all QR verifications if the key is outdated.

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid QR signature | Card may be tampered or a photocopy | Reject; ask student to present the original PhilID |
| Expired card | PhilID validity period has lapsed | Flag the record for renewal; enrollment is allowed to proceed |
| eVerify timeout | PSA API unavailable or slow network | `queue_job` retries automatically; registrar can trigger a manual override |
| Biometric mismatch | Selfie does not match PSA's biometric on file | Escalate to admissions officer for manual identity verification |

Manual overrides are logged and require a reason. They are visible in the audit trail.

---

## Configuration

Set the following in **Settings → Technical → System Parameters**:

| Parameter key | Purpose |
|---------------|---------|
| `esmis.philsys.public_key` | EdDSA public key received from PSA (PEM format) |
| `esmis.philsys.everify_url` | PSA eVerify API base URL |
| `esmis.philsys.everify_api_key` | API key issued by PSA during Relying Party onboarding |

PhilSys verification can be enabled or disabled per campus via **Settings → Companies → [Campus] → PhilSys Verification**.

---

## Deep Dives

- `docs/principles/access-rights.md` — who can trigger verifications and view audit logs
- `docs/principles/error-handling.md` — logging rules, no PII in log messages
- `docs/principles/performance-scalability.md` — queue_job patterns for async API calls
