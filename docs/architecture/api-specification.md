# eSMIS External API Specification

**Status:** Planned
**Module:** `esmis_api` (Layer 4)
**Last Updated:** 2026-03-09

This document specifies the external REST API that eSMIS exposes to integrating systems. It is
detailed enough to derive a full OpenAPI specification but is not one itself. All endpoints listed
here are **Planned** unless otherwise noted.

**Governing documents:**

- [ADR-004: API V2 Architecture](decisions/ADR-004-api-v2-architecture.md)
- [ADR-009: Application-Level Authorization](decisions/ADR-009-api-v2-application-level-authorization.md)
- [ADR-008: Unified API Audit Log](decisions/ADR-008-unified-api-audit-log.md)
- [API Design Principles](../principles/api-design.md)
- [Government Integrations](../principles/government-integrations.md)

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication and Authorization](#2-authentication-and-authorization)
3. [Common Patterns](#3-common-patterns)
4. [Endpoint Groups](#4-endpoint-groups)
5. [Webhook Events](#5-webhook-events)
6. [PII Handling in API](#6-pii-handling-in-api)
7. [Government API Integrations (Outbound)](#7-government-api-integrations-outbound)
8. [LTI 1.3 Specification](#8-lti-13-specification)

---

## 1. API Overview

| Attribute           | Value                                          |
| ------------------- | ---------------------------------------------- |
| Base URL            | `https://{host}/api/v1/esmis`                  |
| Protocol            | HTTPS (TLS 1.2+, required)                     |
| Format              | JSON (`application/json`)                      |
| Authentication      | OAuth 2.0 (primary), API key (simple)          |
| Versioning          | Path-based (`/api/v1/`, `/api/v2/`)            |
| Identifier strategy | Stable identifiers only; no internal DB IDs    |
| Architecture        | Enhanced Odoo (FastAPI routers, not microservice) |
| Deprecation policy  | 6-month compatibility period for major versions |

**Response headers (all responses):**

| Header                  | Example                                  |
| ----------------------- | ---------------------------------------- |
| `X-API-Version`         | `1.0.0`                                  |
| `X-Request-Id`          | `req_abc123def456`                       |
| `X-RateLimit-Limit`     | `1000`                                   |
| `X-RateLimit-Remaining` | `994`                                    |
| `X-RateLimit-Reset`     | `1709942400`                             |
| `X-Deprecation-Notice`  | (present only for deprecated endpoints)  |

**Capability discovery:**

```
GET /api/v1/esmis/metadata
```

Returns a FHIR-inspired CapabilityStatement listing all available resources, supported
interactions, search parameters, and installed extensions. Per ADR-004, this enables clients
to discover what the API offers at runtime.

---

## 2. Authentication and Authorization

### 2.1 OAuth 2.0 Client Credentials Flow (Primary)

For machine-to-machine integrations. Per ADR-009, API clients are not Odoo users; they
authenticate via OAuth 2.0 and receive JWT tokens.

**Token request:**

```
POST /api/v1/esmis/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}
```

**Token response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "students:read enrollments:read grades:read"
}
```

| Property       | Description                                    |
| -------------- | ---------------------------------------------- |
| Token type     | JWT (RS256 signed)                             |
| Expiry         | 1 hour (configurable per client)               |
| Secret hashing | Scrypt (per ADR-004)                           |
| Refresh tokens | Not issued; re-authenticate on expiry          |

**Using the token:**

```
Authorization: Bearer {access_token}
```

### 2.2 API Key (Simple Integrations)

For internal tools or simple integrations that do not require OAuth flows.

```
X-API-Key: {api_key}
```

API keys carry the same scope restrictions as OAuth clients. They are registered via the
`esmis.api.client` model with `auth_method = 'api_key'`.

### 2.3 Scope-Based Authorization

Per ADR-009, authorization is enforced at the application level (not via Odoo record rules).
Each API client has explicit scopes stored in `esmis.api.client.scope`.

**Scope format:** `{resource}:{action}`

| Resource         | Actions                  |
| ---------------- | ------------------------ |
| `students`       | `read`, `search`, `write` |
| `enrollments`    | `read`, `search`, `write` |
| `grades`         | `read`, `search`, `write` |
| `curriculum`     | `read`, `search`         |
| `academic_terms` | `read`, `search`         |
| `financial`      | `read`, `search`         |
| `financial_aid`  | `read`, `search`, `write` |
| `documents`      | `read`, `search`, `write` |
| `gov_exports`    | `read`, `search`         |
| `lms`            | `read`, `write`          |
| `webhooks`       | `manage`                 |

Every endpoint checks `api_client.has_scope(resource, action)` before processing. Scope
enforcement is explicit in each router and covered by dedicated tests per ADR-009.

### 2.4 Consent Layer

For endpoints returning student PII, a consent check runs after scope enforcement:

1. Verify the student has an active `esmis.consent` record for the relevant purpose
2. Check whether the requesting organization (`api_client.partner_id`) is an authorized recipient
3. Filter response fields to only those covered by the consent scope (`esmis.consent.scope`)

If no applicable consent exists, the response contains only the stable identifier (no PII).

---

## 3. Common Patterns

### 3.1 Stable Identifiers

All resources are addressed by stable external identifiers, never by internal database IDs.
This follows the Stable Identifier Rule from the API Design Principles and ADR-004.

Students, for example, are identified by their `student_number` or government identifiers
(`esmis.identifier` records such as PhilSys PSN, LRN, or TIN).

```json
{
  "identifier": [
    {"system": "urn:ph:esmis:student-number", "value": "2025-00001"},
    {"system": "urn:ph:deped:lrn", "value": "123456789012"}
  ]
}
```

Path parameters use the student number: `/api/v1/esmis/students/2025-00001`

### 3.2 Pagination

All list endpoints return paginated results using cursor-based pagination.

**Request parameters:**

| Parameter | Type    | Default | Description                   |
| --------- | ------- | ------- | ----------------------------- |
| `limit`   | integer | 20      | Items per page (max 100)      |
| `cursor`  | string  | —       | Opaque cursor from prior page |

**Response envelope:**

```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "has_more": true,
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "total_count": 1523
  }
}
```

`total_count` is omitted when the query cost would be excessive (documented per endpoint).

### 3.3 Filtering

List endpoints support filtering via query parameters. Filter names match field names.

```
GET /api/v1/esmis/students?program_code=BSCS&academic_standing=good_standing&year_level=3
```

**Operators (suffix convention):**

| Suffix       | Example                           | Meaning                |
| ------------ | --------------------------------- | ---------------------- |
| (none)       | `?state=enrolled`                 | Exact match            |
| `__gt`       | `?gwa__gt=1.5`                    | Greater than           |
| `__gte`      | `?gwa__gte=1.0`                   | Greater than or equal  |
| `__lt`       | `?year_level__lt=4`               | Less than              |
| `__lte`      | `?gwa__lte=3.0`                   | Less than or equal     |
| `__in`       | `?state__in=enrolled,active`      | In list                |
| `__contains` | `?name__contains=Garcia`          | Substring match        |

### 3.4 Field Selection

Clients can request a subset of fields using the `_fields` parameter, reducing response size
and avoiding exposure of unnecessary data.

```
GET /api/v1/esmis/students/2025-00001?_fields=identifier,given_name,family_name,program_code
```

### 3.5 Error Responses

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters.",
    "details": [
      {
        "field": "term_id",
        "issue": "Term '2025-3S' does not exist.",
        "code": "INVALID_REFERENCE"
      }
    ],
    "request_id": "req_abc123def456"
  }
}
```

**Standard error codes:**

| HTTP Status | Code                  | Description                              |
| ----------- | --------------------- | ---------------------------------------- |
| 400         | `VALIDATION_ERROR`    | Invalid request parameters               |
| 401         | `AUTHENTICATION_ERROR`| Missing or invalid credentials           |
| 403         | `SCOPE_DENIED`        | Client lacks required scope              |
| 403         | `CONSENT_REQUIRED`    | No active consent for this data subject  |
| 404         | `NOT_FOUND`           | Resource does not exist                  |
| 409         | `CONFLICT`            | State conflict (e.g., duplicate add)     |
| 422         | `BUSINESS_RULE_ERROR` | Business rule violated (e.g., prereq)    |
| 429         | `RATE_LIMITED`        | Rate limit exceeded                      |
| 500         | `INTERNAL_ERROR`      | Server error (no PII in message)         |

Error messages never contain PII (student names, IDs, grades). They reference stable
identifiers at most.

### 3.6 Rate Limiting

| Client tier | Requests/hour | Burst (per second) |
| ----------- | ------------- | ------------------- |
| Standard    | 1,000         | 10                  |
| Partner     | 10,000        | 50                  |
| Internal    | 100,000       | 200                 |

Rate limit tier is configured per `esmis.api.client`. When exceeded, the API returns HTTP 429
with `Retry-After` header.

> **Note:** Rate limiting middleware is defined but not yet enforced (per ADR-004
> implementation status). This is a Phase 3 deliverable.

### 3.7 Bundle/Batch Operations

Per ADR-004, the API supports FHIR-inspired bundle transactions for atomic multi-resource
operations.

```
POST /api/v1/esmis/$batch
```

**Transaction mode** (all-or-nothing):

```json
{
  "type": "transaction",
  "entries": [
    {"method": "POST", "url": "enrollments", "body": {...}, "ref": "urn:uuid:temp-1"},
    {"method": "POST", "url": "enrollment-lines", "body": {"enrollment_ref": "urn:uuid:temp-1", ...}}
  ]
}
```

**Batch mode** (independent, best-effort): Each entry succeeds or fails independently.

---

## 4. Endpoint Groups

### 4.1 Students

**Resource:** `esmis.student` (backed by `res.partner` + `esmis.identifier`)
**Module:** `esmis_student`

| Method | Path                                          | Description                          | Scope              |
| ------ | --------------------------------------------- | ------------------------------------ | ------------------ |
| GET    | `/students`                                   | Search students (paginated)          | `students:search`  |
| GET    | `/students/{student_number}`                  | Get student profile                  | `students:read`    |
| POST   | `/students`                                   | Create student record                | `students:write`   |
| PATCH  | `/students/{student_number}`                  | Update student profile               | `students:write`   |
| GET    | `/students/{student_number}/identifiers`      | List student identifiers             | `students:read`    |
| GET    | `/students/{student_number}/enrollment-history`| Enrollment history across all terms | `enrollments:read` |

**Search parameters:**

| Parameter          | Type   | Description                            |
| ------------------ | ------ | -------------------------------------- |
| `program_code`     | string | CHED program code                      |
| `campus`           | string | Campus code (`company_id` external ID) |
| `state`            | string | Student state (enrolled, active, etc.) |
| `academic_standing`| string | Academic standing                      |
| `year_level`       | int    | Year level                             |
| `name`             | string | Partial name match (given or family)   |

**Response (single student):**

```json
{
  "identifier": [
    {"system": "urn:ph:esmis:student-number", "value": "2025-00001"},
    {"system": "urn:ph:deped:lrn", "value": "123456789012"}
  ],
  "given_name": "Maria",
  "family_name": "Santos",
  "program": {
    "code": "BSCS",
    "name": "Bachelor of Science in Computer Science"
  },
  "campus": "main",
  "year_level": 3,
  "state": "enrolled",
  "academic_standing": "good_standing",
  "gwa": 1.45
}
```

> **PII note:** `given_name`, `family_name`, and government identifiers are consent-filtered.
> Clients without applicable consent receive only the student number and program.

### 4.2 Enrollment

**Resource:** `esmis.enrollment`, `esmis.enrollment.line`, `esmis.enrollment.change`
**Module:** `esmis_enrollment`

| Method | Path                                                 | Description                        | Scope                |
| ------ | ---------------------------------------------------- | ---------------------------------- | -------------------- |
| GET    | `/enrollments`                                       | Search enrollments                 | `enrollments:search` |
| GET    | `/enrollments/{enrollment_ref}`                      | Get enrollment with lines          | `enrollments:read`   |
| GET    | `/students/{student_number}/enrollments`             | Student's enrollments by term      | `enrollments:read`   |
| GET    | `/students/{student_number}/enrollments/current`     | Current term enrollment            | `enrollments:read`   |
| POST   | `/enrollments`                                       | Create enrollment (cart stage)     | `enrollments:write`  |
| POST   | `/enrollments/{enrollment_ref}/lines`                | Add course to enrollment           | `enrollments:write`  |
| DELETE | `/enrollments/{enrollment_ref}/lines/{line_ref}`     | Drop course from enrollment        | `enrollments:write`  |
| POST   | `/enrollments/{enrollment_ref}/submit`               | Submit enrollment for validation   | `enrollments:write`  |

**Enrollment reference format:** `{term_code}-{student_number}` (e.g., `2025-1S-2025-00001`)

**Search parameters:**

| Parameter        | Type   | Description              |
| ---------------- | ------ | ------------------------ |
| `term_code`      | string | Academic term code       |
| `student_number` | string | Student number           |
| `state`          | string | Enrollment state         |
| `campus`         | string | Campus code              |
| `program_code`   | string | CHED program code        |

**Response (enrollment with lines):**

```json
{
  "ref": "2025-1S-2025-00001",
  "student_number": "2025-00001",
  "term": {"code": "2025-1S", "name": "1st Semester 2025-2026"},
  "state": "enrolled",
  "campus": "main",
  "lines": [
    {
      "ref": "2025-1S-2025-00001-CS101",
      "course": {"code": "CS 101", "name": "Introduction to Computing"},
      "section": "CS101-A",
      "units": 3.0,
      "state": "confirmed"
    }
  ],
  "total_units": 21.0,
  "is_cross_enrolled": false
}
```

### 4.3 Grades

**Resource:** `esmis.grade`
**Module:** `esmis_grading`

| Method | Path                                                     | Description                             | Scope            |
| ------ | -------------------------------------------------------- | --------------------------------------- | ---------------- |
| GET    | `/students/{student_number}/grades`                      | All grades for student (by term)        | `grades:read`    |
| GET    | `/students/{student_number}/grades/current`              | Current term grades                     | `grades:read`    |
| GET    | `/students/{student_number}/gwa`                         | Cumulative and per-term GWA             | `grades:read`    |
| POST   | `/sections/{section_ref}/grades`                         | Submit grades for a section (faculty)   | `grades:write`   |
| PATCH  | `/sections/{section_ref}/grades/{student_number}`        | Update a single grade                   | `grades:write`   |
| POST   | `/sections/{section_ref}/grades/submit`                  | Submit section grades for approval      | `grades:write`   |
| GET    | `/sections/{section_ref}/grades`                         | List grades for a section               | `grades:search`  |

**Grades are SPI (Sensitive Personal Information)** per NPC advisory. The following
restrictions apply:

- Grade values are never returned in student list endpoints
- The `grades:read` scope requires the client to have a specific consent purpose (`consent_enrollment` or `consent_ched_reporting`)
- All grade reads are audit-logged with the requesting client, purpose, and timestamp

**Search parameters (student grades):**

| Parameter   | Type   | Description              |
| ----------- | ------ | ------------------------ |
| `term_code` | string | Filter by academic term  |
| `state`     | string | Grade state (draft, approved, locked) |

**Response (student grades):**

```json
{
  "student_number": "2025-00001",
  "term": {"code": "2025-1S", "name": "1st Semester 2025-2026"},
  "grades": [
    {
      "course": {"code": "CS 101", "name": "Introduction to Computing"},
      "section": "CS101-A",
      "final_grade": 1.25,
      "units": 3.0,
      "state": "approved",
      "is_incomplete": false,
      "source": "manual"
    }
  ],
  "term_gwa": 1.45,
  "cumulative_gwa": 1.52
}
```

**Grade submission (faculty):**

```json
{
  "grades": [
    {"student_number": "2025-00001", "final_grade": 1.25},
    {"student_number": "2025-00002", "final_grade": 2.0},
    {"student_number": "2025-00003", "final_grade": null, "is_incomplete": true, "resolution_deadline": "2026-06-30"}
  ]
}
```

### 4.4 Curriculum

**Resource:** `esmis.program`, `esmis.course`, `esmis.curriculum`
**Module:** `esmis_curriculum`

| Method | Path                                            | Description                          | Scope               |
| ------ | ----------------------------------------------- | ------------------------------------ | ------------------- |
| GET    | `/programs`                                     | List academic programs               | `curriculum:search`  |
| GET    | `/programs/{program_code}`                      | Get program details                  | `curriculum:read`    |
| GET    | `/programs/{program_code}/curricula`             | List curriculum versions             | `curriculum:read`    |
| GET    | `/programs/{program_code}/curricula/{version}`   | Get curriculum with course list      | `curriculum:read`    |
| GET    | `/courses`                                      | Search courses                       | `curriculum:search`  |
| GET    | `/courses/{course_code}`                        | Get course details and prerequisites | `curriculum:read`    |
| GET    | `/courses/{course_code}/prerequisites`          | Get prerequisite graph               | `curriculum:read`    |

**Response (program):**

```json
{
  "code": "BSCS",
  "name": "Bachelor of Science in Computer Science",
  "degree_type": "bachelor",
  "pqf_level": 6,
  "college": "College of Computing",
  "current_curriculum": {
    "version": "2024",
    "effective_year": "AY 2024-2025",
    "total_units": 160.0
  }
}
```

### 4.5 Academic Terms

**Resource:** `esmis.academic.year`, `esmis.academic.term`
**Module:** `esmis_academic_term`

| Method | Path                                        | Description                    | Scope                  |
| ------ | ------------------------------------------- | ------------------------------ | ---------------------- |
| GET    | `/academic-years`                           | List academic years            | `academic_terms:search`|
| GET    | `/academic-years/{year_code}`               | Get academic year with terms   | `academic_terms:read`  |
| GET    | `/terms`                                    | List terms (filterable)        | `academic_terms:search`|
| GET    | `/terms/{term_code}`                        | Get term details               | `academic_terms:read`  |
| GET    | `/terms/current`                            | Get the current active term    | `academic_terms:read`  |

**Search parameters (terms):**

| Parameter | Type   | Description                        |
| --------- | ------ | ---------------------------------- |
| `campus`  | string | Campus code                        |
| `state`   | string | Term state (enrollment_open, etc.) |
| `year`    | string | Academic year code                 |

**Response (term):**

```json
{
  "code": "2025-1S",
  "name": "1st Semester 2025-2026",
  "academic_year": "AY 2025-2026",
  "campus": "main",
  "date_start": "2025-08-12",
  "date_end": "2025-12-15",
  "enrollment_open_date": "2025-07-01T08:00:00+08:00",
  "enrollment_close_date": "2025-08-10T17:00:00+08:00",
  "add_drop_deadline": "2025-09-01",
  "state": "in_progress"
}
```

### 4.6 Financial

**Resource:** `esmis.financial.assessment`, `esmis.fee.schedule`, `esmis.payment`
**Modules:** `esmis_billing`, `esmis_payment`

| Method | Path                                                       | Description                         | Scope              |
| ------ | ---------------------------------------------------------- | ----------------------------------- | ------------------ |
| GET    | `/students/{student_number}/assessment`                    | Current term financial assessment   | `financial:read`   |
| GET    | `/students/{student_number}/assessment/{term_code}`        | Assessment for a specific term      | `financial:read`   |
| GET    | `/students/{student_number}/payments`                      | Payment history                     | `financial:read`   |
| GET    | `/students/{student_number}/balance`                       | Outstanding balance                 | `financial:read`   |
| GET    | `/fee-schedules`                                           | List fee schedules                  | `financial:search` |
| GET    | `/fee-schedules/{schedule_ref}`                            | Get fee schedule details            | `financial:read`   |

**Response (assessment):**

```json
{
  "student_number": "2025-00001",
  "term": {"code": "2025-1S"},
  "tuition": 21000.00,
  "miscellaneous_fees": 5500.00,
  "financial_aid_applied": -21000.00,
  "total_assessed": 5500.00,
  "total_paid": 5500.00,
  "balance": 0.00,
  "currency": "PHP",
  "state": "paid"
}
```

> **Note:** Payment endpoint does not expose bank account numbers or payment gateway
> references. Those are Tier 3 fields and are excluded from all API responses.

### 4.7 Financial Aid

**Resource:** `esmis.financial.aid.program`, `esmis.financial.aid.award`, `esmis.financial.aid.application`
**Module:** `esmis_financial_aid`

| Method | Path                                                         | Description                             | Scope                  |
| ------ | ------------------------------------------------------------ | --------------------------------------- | ---------------------- |
| GET    | `/financial-aid/programs`                                    | List available aid programs             | `financial_aid:search` |
| GET    | `/financial-aid/programs/{program_ref}`                      | Get aid program details                 | `financial_aid:read`   |
| GET    | `/students/{student_number}/financial-aid`                   | List student's aid awards               | `financial_aid:read`   |
| GET    | `/students/{student_number}/financial-aid/eligibility`       | Check eligibility for all aid programs  | `financial_aid:read`   |
| POST   | `/students/{student_number}/financial-aid/applications`      | Submit financial aid application        | `financial_aid:write`  |
| GET    | `/students/{student_number}/financial-aid/applications`      | List student's applications             | `financial_aid:read`   |
| GET    | `/students/{student_number}/financial-aid/applications/{ref}`| Get application details                 | `financial_aid:read`   |

**Eligibility response:**

```json
{
  "student_number": "2025-00001",
  "term": {"code": "2025-1S"},
  "eligibility": [
    {
      "program": {"ref": "TES", "name": "Tertiary Education Subsidy"},
      "eligible": true,
      "basis": "Filipino citizen, enrolled in SUC, no prior bachelor's degree",
      "precedence": 1
    },
    {
      "program": {"ref": "PWD-DISCOUNT", "name": "PWD 20% Tuition Discount"},
      "eligible": true,
      "basis": "Valid PWD ID on file (RA 7277/10754)",
      "precedence": 2
    }
  ],
  "note": "Free tuition (TES) applied first per RA 10931. PWD discount applies to remaining fees."
}
```

> **Business rule:** Free tuition eligibility (RA 10931) takes precedence over all other
> subsidies. The API reflects the same stacking order enforced by `esmis_financial_aid`.

### 4.8 Documents

**Resource:** `esmis.document.request`, `esmis.document`
**Module:** `esmis_documents`

| Method | Path                                                          | Description                     | Scope              |
| ------ | ------------------------------------------------------------- | ------------------------------- | ------------------ |
| POST   | `/students/{student_number}/document-requests`                | Request a document (TOR, etc.) | `documents:write`  |
| GET    | `/students/{student_number}/document-requests`                | List document requests          | `documents:read`   |
| GET    | `/students/{student_number}/document-requests/{request_ref}`  | Get request status              | `documents:read`   |
| GET    | `/documents/{document_ref}`                                   | Get document metadata           | `documents:read`   |
| GET    | `/documents/{document_ref}/download`                          | Download generated document     | `documents:read`   |
| GET    | `/documents/verify/{qr_token}`                                | Verify document via QR token    | (public, no auth)  |

**Document request:**

```json
{
  "document_type": "tor",
  "purpose": "Employment application",
  "copies": 2
}
```

**Document request response:**

```json
{
  "ref": "DR-2026-00042",
  "student_number": "2025-00001",
  "document_type": "tor",
  "state": "processing",
  "requested_date": "2026-03-09T10:00:00+08:00",
  "estimated_release": "2026-03-16"
}
```

**Document types:** `tor` (Transcript of Records), `diploma`, `certification`, `clearance`,
`coe` (Certificate of Enrollment)

> The `/documents/verify/{qr_token}` endpoint is public and unauthenticated. It returns a
> minimal verification response (valid/invalid, document type, issuance date) without exposing
> student PII.

### 4.9 Government Exports

**Module:** `esmis_hemis_export` (HEMIS), `esmis_documents` (eCAV)

| Method | Path                                       | Description                             | Scope               |
| ------ | ------------------------------------------ | --------------------------------------- | -------------------- |
| GET    | `/gov/hemis/forms`                         | List HEMIS forms for an academic year   | `gov_exports:read`   |
| POST   | `/gov/hemis/forms/generate`                | Generate HEMIS export files             | `gov_exports:write`  |
| GET    | `/gov/hemis/forms/{form_ref}/download`     | Download generated HEMIS Excel file     | `gov_exports:read`   |
| GET    | `/gov/hemis/forms/{form_ref}/validation`   | Get data validation results             | `gov_exports:read`   |
| POST   | `/gov/ecav/export`                         | Generate eCAV credential export         | `gov_exports:write`  |
| GET    | `/gov/ecav/export/{export_ref}/download`   | Download eCAV export file               | `gov_exports:read`   |

**HEMIS generation request:**

```json
{
  "academic_year": "AY 2025-2026",
  "institution_type": "suc",
  "forms": ["form_a", "form_b", "form_e1", "form_e2", "graduate_list"]
}
```

> **Important:** These endpoints trigger file generation, not direct government submission.
> The registrar downloads the files and uploads them to CHED portals manually. There is no
> public CHED API. See [Government Integrations](../principles/government-integrations.md).

### 4.10 LMS Integration

**Module:** `esmis_lms_bridge`

These endpoints serve two purposes: (1) LTI 1.3 tool launch protocol and (2) OneRoster 1.2
roster/grade sync. See [Section 8](#8-lti-13-specification) for full LTI details.

| Method | Path                                          | Description                                | Scope         |
| ------ | --------------------------------------------- | ------------------------------------------ | ------------- |
| POST   | `/lms/lti/login`                              | LTI 1.3 OIDC login initiation             | (LTI protocol)|
| POST   | `/lms/lti/launch`                             | LTI 1.3 resource link launch              | (LTI protocol)|
| GET    | `/lms/lti/jwks`                               | eSMIS public key set (JWKS)                | (public)      |
| GET    | `/lms/oneroster/classes`                       | OneRoster: list classes (sections)         | `lms:read`    |
| GET    | `/lms/oneroster/classes/{class_id}/students`   | OneRoster: students in a class             | `lms:read`    |
| GET    | `/lms/oneroster/classes/{class_id}/teachers`   | OneRoster: teachers in a class             | `lms:read`    |
| GET    | `/lms/oneroster/enrollments`                   | OneRoster: all enrollments                 | `lms:read`    |
| PUT    | `/lms/oneroster/classes/{class_id}/results`    | OneRoster: grade passback for a class      | `lms:write`   |
| GET    | `/lms/oneroster/students/{student_id}/results` | OneRoster: grades for a student            | `lms:read`    |

**OneRoster search parameters:**

| Parameter   | Type   | Description                  |
| ----------- | ------ | ---------------------------- |
| `term_code` | string | Academic term code           |
| `campus`    | string | Campus code                  |
| `status`    | string | `active`, `tobedeleted`      |
| `since`     | string | Delta sync (ISO 8601 date)   |

> **Architecture note:** eSMIS is the **Platform** (data source) and the LMS is the **Tool**.
> Roster sync is implemented as a scheduled action (not real-time webhook) to avoid tight
> coupling per the government integrations principle.

---

## 5. Webhook Events

eSMIS can notify external systems about events via outbound webhooks. Webhook subscriptions
are managed per API client.

### 5.1 Webhook Management

| Method | Path                         | Description                | Scope              |
| ------ | ---------------------------- | -------------------------- | ------------------ |
| POST   | `/webhooks`                  | Register a webhook         | `webhooks:manage`  |
| GET    | `/webhooks`                  | List registered webhooks   | `webhooks:manage`  |
| PATCH  | `/webhooks/{webhook_id}`     | Update webhook URL/events  | `webhooks:manage`  |
| DELETE | `/webhooks/{webhook_id}`     | Remove a webhook           | `webhooks:manage`  |

**Webhook registration:**

```json
{
  "url": "https://partner.example.com/hooks/esmis",
  "events": ["enrollment.created", "grade.posted", "payment.received"],
  "secret": "whsec_..."
}
```

### 5.2 Event Types

| Event                  | Trigger                                           | Payload includes                       |
| ---------------------- | ------------------------------------------------- | -------------------------------------- |
| `enrollment.created`   | Enrollment reaches `enrolled` state               | student_number, term, program, units   |
| `enrollment.dropped`   | Enrollment cancelled or all lines dropped         | student_number, term, reason           |
| `grade.posted`         | Grade approved by registrar                       | student_number, course_code, term      |
| `grade.changed`        | Approved grade is modified (grade change workflow) | student_number, course_code, term, old_grade, new_grade |
| `payment.received`     | Payment confirmed by gateway webhook              | student_number, amount, term           |
| `payment.refunded`     | Refund processed                                  | student_number, amount, term           |
| `document.ready`       | Requested document is ready for release           | request_ref, document_type             |
| `student.status_changed`| Student state transition (e.g., enrolled to LOA) | student_number, old_state, new_state   |

### 5.3 Webhook Delivery

**Format:**

```
POST {registered_url}
Content-Type: application/json
X-Webhook-Signature: sha256={hmac_hex}
X-Webhook-Event: enrollment.created
X-Webhook-Id: evt_abc123def456
X-Webhook-Timestamp: 1709942400
```

```json
{
  "event": "enrollment.created",
  "timestamp": "2026-03-09T10:00:00+08:00",
  "data": {
    "student_number": "2025-00001",
    "term": "2025-1S",
    "program_code": "BSCS",
    "total_units": 21.0
  }
}
```

**Delivery guarantees:**

- At-least-once delivery (subscribers must handle duplicates using `X-Webhook-Id`)
- Retry on non-2xx response: 1 min, 5 min, 30 min, 2 hours, 24 hours
- Webhook disabled after 7 consecutive days of failures
- Signature: HMAC-SHA256 of `{timestamp}.{body}` using the registered secret

**PII in webhooks:** Webhook payloads contain stable identifiers only (student number, course
code). No names, grades, or government IDs are included in webhook payloads. The subscriber
must call the API to retrieve full details, which enforces consent checks.

---

## 6. PII Handling in API

Per RA 10173 (Data Privacy Act of 2012) and NPC advisories, the API enforces strict controls
on personally identifiable information.

### 6.1 Data Classification Tiers

| Tier   | Examples                                    | API behavior                            |
| ------ | ------------------------------------------- | --------------------------------------- |
| Tier 1 | Religion, ethnicity, IP membership          | Returned only with specific consent     |
| Tier 2 | Name, birthdate, address, contact info      | Consent-filtered per purpose            |
| Tier 3 | Grades (SPI), government IDs, health data, bank account | Never in list endpoints; detail endpoints only with consent + audit; encrypted at rest |

### 6.2 Tier 3 Fields: Exclusion from List Endpoints

List/search endpoints (`GET /students`, `GET /enrollments`) never include Tier 3 fields.
These fields are available only on detail endpoints (`GET /students/{id}`) and only when:

1. The API client has the required scope
2. An active consent exists for the relevant purpose
3. The access is audit-logged

### 6.3 Field Masking

When a client has scope to access a resource but consent does not cover a specific field, that
field is masked in the response:

```json
{
  "given_name": "Maria",
  "family_name": "Santos",
  "birth_date": "****-**-**",
  "phone": "****"
}
```

The masked value is a fixed placeholder, not a partial reveal.

### 6.4 Audit Logging

Every API request that reads or modifies PII is logged to `esmis.api.audit.log` (per ADR-008):

| Field                | Description                                |
| -------------------- | ------------------------------------------ |
| `api_client_id`      | Which client accessed the data             |
| `request_id`         | Correlation ID for the request             |
| `ip_address`         | Client IP address                          |
| `operation`          | `read`, `search`, `create`, `update`, etc. |
| `resource_type`      | Resource accessed (students, grades, etc.) |
| `resource_identifier`| Stable identifier (never DB ID)            |
| `consent_id`         | Linked consent record (if applicable)      |
| `fields_returned`    | Which fields were included in the response |
| `status`             | `success`, `access_denied`, etc.           |

This supports GDPR Article 30 (records of processing) and RA 10173 data subject access
requests.

### 6.5 No PII in Error Messages or Logs

Error responses and server logs never contain student names, grades, government IDs, or other
PII. They reference record IDs or stable identifiers only.

---

## 7. Government API Integrations (Outbound)

These are APIs that eSMIS calls as a client, not APIs that eSMIS exposes.

### 7.1 PhilSys eVerify (PSA)

| Attribute     | Value                                      |
| ------------- | ------------------------------------------ |
| Module        | `esmis_philsys`                            |
| Direction     | Outbound (eSMIS calls PSA)                 |
| Protocol      | REST API over HTTPS                        |
| Auth          | API credentials from PSA (after NDA)       |
| Purpose       | Live biometric identity verification       |

**Flow:**

1. Student presents at registration desk
2. eSMIS captures a live selfie
3. eSMIS posts the selfie to PSA eVerify endpoint
4. PSA returns pass/fail (no biometric data stored in eSMIS)
5. eSMIS records the verification result in `esmis.philsys.verification`

**Offline alternative (PhilSys Check):** QR code on PhilID is verified using EdDSA signature
with PSA's public key. No network call required.

**Credentials:** Stored in `ir.config_parameter`:
- `esmis_philsys.psa_public_key`
- `esmis_philsys.everify_api_key`
- `esmis_philsys.everify_endpoint_url`

### 7.2 Payment Gateways (PayMongo, Maya, Dragonpay)

| Attribute     | Value                                      |
| ------------- | ------------------------------------------ |
| Module        | `esmis_payment`                            |
| Direction     | Bidirectional (outbound + inbound webhooks)|
| Protocol      | REST API + webhooks                        |
| Auth          | API keys (per gateway)                     |

**Outbound (eSMIS to gateway):**

1. eSMIS creates a PaymentIntent/Checkout via REST API
2. Gateway returns a checkout URL for the student
3. Student pays on the gateway's hosted page

**Inbound (gateway to eSMIS — webhooks):**

1. Gateway POSTs payment confirmation to eSMIS webhook endpoint
2. eSMIS verifies webhook signature
3. eSMIS processes event asynchronously via `queue_job`
4. Payment record updated, official receipt issued

**Webhook endpoints (incoming, not exposed via `/api/v1/esmis/`):**

| Path                                    | Gateway   |
| --------------------------------------- | --------- |
| `/esmis/payment/webhook/paymongo`       | PayMongo  |
| `/esmis/payment/webhook/maya`           | Maya      |
| `/esmis/payment/webhook/dragonpay`      | Dragonpay |

These are Odoo HTTP controllers (not FastAPI routers), authenticated by webhook signature
verification only.

**Credentials:** Stored in `ir.config_parameter`:
- `esmis_payment.{gateway}_secret_key`
- `esmis_payment.{gateway}_webhook_secret`

---

## 8. LTI 1.3 Specification

eSMIS acts as the **LTI Platform** (Tool Consumer). The LMS (Moodle, Canvas, Google
Classroom) acts as the **Tool** (Tool Provider).

### 8.1 Protocol Overview

| Component      | Standard           | Purpose                              |
| -------------- | ------------------ | ------------------------------------ |
| Authentication | OIDC + OAuth 2.0   | Secure tool launch                   |
| Token format   | JWT (RS256)        | Claims carry user context            |
| Key exchange   | JWKS               | Public key discovery                 |
| Grade passback | AGS (LTI Advantage)| LMS sends grades back to eSMIS       |
| Roster sync    | NRPS / OneRoster   | eSMIS provides class rosters to LMS  |

### 8.2 Launch Flow

1. **Login initiation** (`POST /lms/lti/login`): LMS sends OIDC login request
2. **Authentication redirect**: eSMIS redirects to LMS authorize endpoint with login hint
3. **Launch** (`POST /lms/lti/launch`): LMS POSTs signed JWT with user claims
4. **Validation**: eSMIS validates JWT signature against LMS JWKS, nonce, deployment

### 8.3 Claims in Launch JWT

| Claim                                    | Description                         |
| ---------------------------------------- | ----------------------------------- |
| `sub`                                    | Student number (stable identifier)  |
| `given_name`, `family_name`              | Student name                        |
| `email`                                  | Institutional email                 |
| `https://purl.imsglobal.org/spec/lti/claim/roles` | LTI roles (Learner, Instructor) |
| `https://purl.imsglobal.org/spec/lti/claim/context` | Course/section context      |
| `https://purl.imsglobal.org/spec/lti/claim/resource_link` | Specific resource link  |

### 8.4 Assignment and Grade Services (AGS)

The LMS calls back to eSMIS to submit grades:

| Method | Path                                                    | Description                 |
| ------ | ------------------------------------------------------- | --------------------------- |
| GET    | `/lms/lti/ags/{context_id}/lineitems`                   | List grade line items       |
| POST   | `/lms/lti/ags/{context_id}/lineitems`                   | Create a line item          |
| PUT    | `/lms/lti/ags/{context_id}/lineitems/{id}/scores`       | Submit a score              |
| GET    | `/lms/lti/ags/{context_id}/lineitems/{id}/results`      | Read results                |

Grades submitted via AGS are recorded in `esmis.grade` with `source = 'lms'` and enter the
standard approval workflow (faculty submit, registrar approve).

### 8.5 Platform Registration

Each LMS connection is registered in `esmis.lms.platform`:

| Setting            | Description                            |
| ------------------ | -------------------------------------- |
| `platform_type`    | `moodle`, `canvas`, `google_classroom` |
| `base_url`         | LMS base URL                           |
| `client_id`        | LTI client ID                          |
| `lti_private_key`  | RSA private key for JWT signing        |
| `company_id`       | Campus (supports multi-campus)         |

Multiple LMS platforms can be registered (one per campus, or multiple per campus).

### 8.6 JWKS Endpoint

```
GET /lms/lti/jwks
```

Returns the eSMIS public key set for LMS tools to verify signed JWTs.

---

## Appendix A: Implementation Phases

| Phase | Endpoints                                          | Dependencies                       |
| ----- | -------------------------------------------------- | ---------------------------------- |
| 1     | OAuth, metadata, students, academic terms          | `esmis_api`, `esmis_student`, `esmis_academic_term` |
| 2     | Enrollment, curriculum, grades                     | `esmis_enrollment`, `esmis_curriculum`, `esmis_grading` |
| 3     | Financial, financial aid, documents                | `esmis_billing`, `esmis_financial_aid`, `esmis_documents` |
| 4     | LMS (LTI + OneRoster), webhooks                    | `esmis_lms_bridge`                 |
| 5     | Government exports, payment gateway webhooks       | `esmis_hemis_export`, `esmis_payment` |

## Appendix B: Performance Targets

Per ADR-004:

| Operation                  | Target Latency (p95) | Throughput     |
| -------------------------- | -------------------- | -------------- |
| Single resource read       | < 100ms              | 1,000 req/s    |
| Search (100 results)       | < 500ms              | 200 req/s      |
| Batch create (100 records) | < 2s                 | 50 req/s       |
| Capability statement       | < 50ms               | 5,000 req/s    |

## Appendix C: Related Documents

| Document | Relevance |
| -------- | --------- |
| [ADR-004: API V2 Architecture](decisions/ADR-004-api-v2-architecture.md) | Core architecture, FHIR-inspired patterns, bundle transactions |
| [ADR-008: Unified API Audit Log](decisions/ADR-008-unified-api-audit-log.md) | Audit log model and integration points |
| [ADR-009: Application-Level Authorization](decisions/ADR-009-api-v2-application-level-authorization.md) | Scope enforcement, consent filtering, sudo pattern |
| [API Design Principles](../principles/api-design.md) | Stable identifiers, versioning, field filtering |
| [Government Integrations](../principles/government-integrations.md) | PhilSys, CHED, UniFAST, LMS, payment gateway details |
| [Data Model Registry](data-model-registry.md) | All `esmis.*` model specifications |
