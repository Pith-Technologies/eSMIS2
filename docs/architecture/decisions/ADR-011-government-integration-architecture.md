# ADR-005: Government Integration Architecture

## Status

**Accepted** - Implementation pending

**Date:** 2026-03-09
**Decision Owners:** Core Team

## Context

eSMIS must integrate with 10+ Philippine government systems as part of regulatory compliance for Higher Education Institutions (HEIs). These systems span academic reporting, financial obligations, and identity verification.

### Government Systems Inventory

| System | Agency | Purpose | Integration Type |
|--------|--------|---------|-----------------|
| CHED HEMIS | CHED | Higher education management information | Portal file upload |
| UniFAST | CHED / UNIFAST | Tertiary Education Subsidy (TES), SUC Leveling | Portal file upload |
| BIR | BIR | Tax withholding, BIR Form 2316, alphalist | Portal file upload (DAT/CSV) |
| SSS | SSS | Social Security System contributions | Portal file upload |
| GSIS | GSIS | Government Service Insurance (state universities) | Portal file upload |
| PhilHealth | PhilHealth | Health insurance contributions | Portal file upload |
| Pag-IBIG (HDMF) | HDMF | Housing fund contributions | Portal file upload |
| PhilSys | PSA | Philippine Identification System (student ID verification) | REST API |
| Payment gateways | Various | Online tuition and fee collection (PayMaya, GCash, DragonPay) | REST API |
| eGov PH Super App | DICT | Unified government services platform | REST API (targeted Q4 2025 — status uncertain) |

### Integration Reality

The majority of Philippine government systems in the HEI space are portal-based: agencies provide a prescribed file format (Excel, CSV, DAT), institutions prepare the file, and a staff member logs into the agency portal to upload it manually. Direct machine-to-machine APIs are the exception, not the rule.

Attempting to build API integrations for portal-based systems is not viable and introduces maintenance risk when portals are updated without notice. At the same time, payment collection and identity verification (PhilSys) require real-time API responses and cannot be handled by file exports.

## Decision

**Adopt a dual integration strategy based on the actual technical capability of each government system.**

### Strategy 1: API Integration (for systems with real APIs)

For **PhilSys** and **payment gateways** (PayMaya, GCash, DragonPay):

- Implement dedicated integration modules (e.g., `esmis_philsys`, `esmis_payment_gateway`)
- All API calls are asynchronous using `queue_job` to avoid blocking UI operations and to support retry on failure
- API credentials (keys, secrets, endpoint URLs) are stored in `ir.config_parameter`, never hardcoded in source
- Each integration module implements a standardised adapter interface so payment gateways can be swapped without changing the calling code
- Rate limiting and timeout handling are mandatory; no integration may call an external API synchronously in a `write()` or `create()` override

### Strategy 2: File Export (for portal-based systems)

For **CHED HEMIS, UniFAST, BIR, SSS, GSIS, PhilHealth, Pag-IBIG**:

- Implement wizard-based export modules (e.g., `esmis_ched_hemis_export`, `esmis_bir_export`)
- Each wizard validates data completeness and format compliance before generating the file
- Generated files match the exact prescribed format (column order, field lengths, encoding, delimiter) as published by the respective agency
- Validation errors are surfaced to the user in the wizard UI before download; staff must resolve errors before a file can be exported
- File format version is tracked in the wizard; when an agency updates its format, only the relevant export module is updated

### eGov PH Super App

The DICT's eGov PH Super App is targeting a unified API for government services. The timeline and scope remain uncertain. No integration will be built until an official, stable API specification is published and the platform is in general availability. This ADR will be updated when that occurs.

### Module Naming Convention

| Integration Type | Module Naming Pattern | Example |
|-----------------|----------------------|---------|
| API integration | `esmis_{system}` | `esmis_philsys`, `esmis_payment_gateway` |
| File export wizard | `esmis_{system}_export` | `esmis_ched_hemis_export`, `esmis_bir_export` |

## Consequences

### Positive

- The dual strategy accurately reflects what each government system actually supports today
- File export modules are fully testable: tests can assert on file content, column ordering, encoding, and field values without requiring network access
- File exports are more reliable than API calls for portal-based systems — no dependency on government API uptime
- `queue_job` retry logic for API integrations means transient government API outages do not cause data loss
- Credential management via `ir.config_parameter` keeps secrets out of source control and allows per-environment configuration

### Negative

- Portal-based file exports require a manual upload step by staff; this is an inherent limitation of the current government systems, not an eSMIS limitation
- When an agency updates its prescribed file format, the corresponding export module must be updated and redeployed; format change notifications from agencies are often short-notice
- The eGov PH Super App may eventually make some file export modules redundant; those modules will need to be deprecated at that time

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Agency changes file format without notice | HIGH | MEDIUM | Track agency bulletins; modular export design limits change scope to one module |
| API credentials committed to source | LOW | HIGH | `ir.config_parameter` storage enforced; pre-commit hook detects hardcoded secrets |
| queue_job retry storms on API outage | LOW | MEDIUM | Exponential backoff configured; max retry cap per job |
| PhilSys API downtime blocks enrollment | MEDIUM | HIGH | Enrollment proceeds with manual verification fallback; PhilSys match is advisory, not a hard gate |
| eGov PH API spec changes before GA | HIGH | LOW | No integration built until stable GA; watch-and-wait policy |

## Implementation Notes

1. **Export wizard structure**: Each `esmis_*_export` module provides a `TransientModel` wizard with: date range / period selection, a `validate()` method that returns user-facing error messages, and a `generate_file()` method that streams the file to the browser.
2. **API adapter pattern**: API integration modules implement an `_call_api()` method that is mockable in tests. Tests must not make real HTTP calls.
3. **Credentials**: All API keys and endpoint URLs go in `ir.config_parameter` with keys namespaced by module (e.g., `esmis_philsys.api_key`, `esmis_philsys.endpoint_url`). A setup wizard in each API module guides administrators through configuration.
4. **queue_job configuration**: API jobs use channel `root.government_api` with concurrency 2 to avoid hitting rate limits. Retry policy: max 5 retries with exponential backoff starting at 60 seconds.
5. **No PII in logs**: API call logs must not include student names, ID numbers, or financial amounts. Log job IDs and HTTP status codes only.
6. **Format version tracking**: Export wizards display the format version and effective date (e.g., "BIR Alphalist v7.3 — effective 2024-01-01") so operators can identify stale formats.

## References

- [CHED HEMIS Technical Specifications](https://ched.gov.ph/hemis/)
- [PhilSys Integration Guidelines — PSA](https://philsys.gov.ph/)
- [BIR e-Filing and Payment System](https://efps.bir.gov.ph/)
- ADR-008: Unified API Audit Log
- ADR-009: API V2 Application-Level Authorization

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09 **Next Review:** When eGov PH Super App reaches general availability or when a portal-based system publishes an API
