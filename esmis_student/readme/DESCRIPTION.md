# eSMIS Student

Universal student demographics and lifecycle management built on `res.partner`.

## Purpose

Extends Odoo's standard contact model (`res.partner`) with all student-specific
fields required for Philippine Higher Education Institution (HEI) student records.
Provides the foundational student data layer that all other eSMIS domain modules
depend on.

## Key Features

- **Structured name fields** — `last_name`, `first_name`, `middle_name` with
  locale-aware display name formatting (extensible by country modules).
- **Demographic fields** — birthdate, birthplace, age (computed), gender (ISO 5218),
  civil status, nationality, blood type, disability type (RA 7277/10754), indigenous
  peoples flag (RA 8371).
- **Student lifecycle state machine** — enforces valid transitions across the full
  student lifecycle: Applicant → Admitted → Enrolled → Active → Graduated → Alumni,
  with branches for Leave of Absence, Dismissed, Transferred Out, and Denied.
- **Guardian requirement** — automatically enforces that students under 18 have a
  `guardian_id` set, per RA 10173 requirements for minor consent.
- **Encrypted identifiers** (`esmis.identifier`) — stores government and institutional
  IDs (PhilSys, LRN, TIN, SSS, etc.) encrypted with AES-256-GCM. Supports blind-index
  search via HMAC-SHA256 without decrypting all rows.
- **Education history** (`esmis.education.history`) — tracks institutions attended
  per education level with year and honors information.
- **Campus isolation** — record rules on `res.partner`, `esmis.identifier`, and
  `esmis.education.history` isolate records by `company_id` (campus).
- **Three-tier registrar hierarchy** — Viewer, Officer, Manager groups with implied
  permissions. Student Self group for portal access.

## Encryption Key Setup

Identifier values are encrypted at rest. For production:

```bash
export ESMIS_ENCRYPTION_KEY=$(python3 -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())")
```

If the environment variable is not set, the module auto-generates a key and stores it
in `ir.config_parameter`. **Always use the environment variable in production.**

## Data Privacy (RA 10173)

- Student name, birthdate, and guardian information are classified as PII.
- Encrypted identifiers are classified as Sensitive Personal Information (SPI).
- Consent management is handled by the `esmis_consent` module.
- No PII is written to log files or exception messages.

## Dependencies

- `esmis_base` — root menus and base infrastructure
- `esmis_vocabulary` — vocabulary codes for gender, civil status, blood type, etc.
- `esmis_security` — PII-aware mixin, campus-aware mixin
- `esmis_consent` — consent mixin for RA 10173 compliance
- `esmis_address` — structured address records for students
- `mail` — activity and tracking support
