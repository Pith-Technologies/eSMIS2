# ADR-027: LMS Integration Standards

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

CHED CMO No. 4, s. 2020 requires Philippine HEIs to support flexible learning arrangements. As a result, universities operate one or more Learning Management Systems (LMS) in parallel with their student information system. The most common platforms in Philippine HEIs are:

- **Moodle** — most widely deployed, particularly in SUCs and LUCs
- **Canvas** — growing adoption in private HEIs
- **Google Classroom** — common in institutions without dedicated LMS infrastructure

Two integration needs arise from this landscape:

1. **Enrollment roster synchronization:** The SIS is the system of record for course enrollment. LMS platforms must receive accurate, up-to-date class rosters at the start of each term and reflect adds/drops in real time.
2. **Grade passback:** Faculty record grades in the LMS during the term. Final grades (and in some cases component grades) must flow back to the SIS for official recording.

Without a standards-based integration layer, each LMS requires a bespoke connector, creating maintenance burden and vendor lock-in.

### Additional Requirement

Learning modality per section must be tracked to comply with CMO No. 4 reporting requirements and to drive appropriate workflows (e.g., online sections may not require room assignment).

## Decision

### 1. LTI 1.3 for Tool Launches and Grade Passback

The system implements the **LTI 1.3** (Learning Tools Interoperability) specification as a tool provider. LTI 1.3 covers:

- Authenticated tool launch from the LMS into SIS-hosted tools
- **Assignment and Grade Services (AGS)** for grade passback from LMS to SIS

LTI 1.3 is supported by Moodle 3.8+, Canvas, and Brightspace. Google Classroom does not implement LTI 1.3; Google Classroom integration falls back to OneRoster (see below) for roster sync and requires manual grade entry.

### 2. OneRoster 1.2 for Enrollment and Roster Synchronization

The system exposes a **OneRoster 1.2** REST API for LMS consumption. The LMS polls (or subscribes via delta) to receive:

- Course and class (section) records
- Enrollment records (student-to-class, teacher-to-class)
- Add/drop changes as incremental updates

OneRoster is supported by Moodle (via plugin), Canvas natively, and Google Classroom (via third-party connector).

### 3. Learning Modality Tracking on Sections

`esmis.section` gains a `learning_modality` selection field with vocabulary-coded values:

| Code | Label |
|------|-------|
| `face_to_face` | Face-to-Face |
| `online` | Fully Online |
| `blended` | Blended / Hybrid |
| `asynchronous` | Asynchronous Distance Learning |

Vocabulary codes are defined in `esmis_vocabulary` to allow institution-specific extensions without schema changes.

### 4. Grade Passback Flow

LTI AGS grade passback writes incoming grade data to `esmis.grade` with state `draft`. Faculty must review and submit; a registrar approves before the grade is locked. This preserves the existing grade approval workflow and prevents LMS data from directly mutating official grade records.

### 5. Dedicated Integration Module

All LMS integration code lives in `esmis_lms_bridge`, positioned at Layer 4 (Integrations) in the module architecture. This module has no reverse dependencies — it depends on domain modules but nothing depends on it, ensuring the core SIS operates normally without the LMS bridge installed.

### 6. Authentication

- **LTI 1.3:** OAuth 2.0 authorization code flow with JWT (RS256) for all messages. Platform (LMS) public keys fetched from the LMS JWKS endpoint at launch time.
- **OneRoster:** API key + secret (HMAC-SHA256) per the OneRoster 1.2 security specification. Keys are scoped per LMS instance and stored encrypted.

## Consequences

### Positive

- Standards-based approach eliminates vendor lock-in; any LTI 1.3 or OneRoster 1.2 compliant LMS can integrate without custom code
- Grade passback feeds into the existing draft → approved → locked workflow, preserving data integrity
- Modality tracking on sections enables CMO No. 4 compliance reporting without additional data collection

### Negative

- LTI 1.3 implementation is non-trivial; JWT validation, JWKS rotation, and deep-link message handling require careful security review
- LMS platforms vary in their fidelity to the standards; testing against each target LMS is required and edge cases will differ
- Google Classroom's lack of LTI 1.3 support means it receives reduced integration depth (roster sync only, no automated grade passback)

## Implementation Notes

- LTI 1.3 tool provider endpoint is implemented in `esmis_lms_bridge/controllers/lti.py`. The launch URL, JWKS URI, and AGS callback URL are configurable per LMS instance via `esmis.lms.platform` records.
- OneRoster REST API is exposed at `/api/oneroster/v1p2/` and requires a valid API key header (`X-OneRoster-Key`).
- `learning_modality` field on `esmis.section` uses `fields.Selection` with a fallback default of `face_to_face` for backward compatibility with existing section records.
- Grade passback creates `esmis.grade` records with `source = 'lms'` for traceability; faculty can see which grades originated from LMS passback.
- OneRoster delta sync uses a `last_modified` cursor stored per LMS platform record to avoid full-roster retransmission on each sync.

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09
