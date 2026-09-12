---
name: Module Request
about: Propose a new eSMIS module
title: "[Module] esmis_"
labels: "module-request"
assignees: ""
---

## Module Name

`esmis_` (must follow `esmis_*` naming convention)

## Architecture Layer

<!-- Select one. See docs/architecture/implementation-roadmap.md for layer definitions. -->

- [ ] Layer 1: Foundation (core data, shared services)
- [ ] Layer 2: Domain Core (enrollment, curriculum, grading, scheduling, billing, financial aid, faculty)
- [ ] Layer 3: Domain Extensions (reports, documents, alumni, student services)
- [ ] Layer 4: Portals & Integrations (student portal, API, LMS bridge, PhilSys, payment)

## Problem Statement

<!-- What problem does this module solve? Who is affected? -->

## Key Models

<!-- List the primary Odoo models this module will introduce. -->

| Model                  | Purpose |
| ---------------------- | ------- |
| `esmis.example`        |         |
| `esmis.example.line`   |         |

## Key Features

<!-- Describe the main features this module provides. -->

-
-
-

## Dependencies

<!-- List existing eSMIS modules and Odoo core modules this depends on. -->

### eSMIS Modules

-

### Odoo Core Modules

-

## Regulatory Requirements

<!-- Which Philippine regulations does this module address? Check all that apply. -->

- [ ] RA 10173 (Data Privacy Act)
- [ ] CHED MORPHE / CMOs (specify: )
- [ ] RA 10931 (Free Tuition Law)
- [ ] RA 10687 (UniFAST)
- [ ] RA 7277 / RA 10754 (PWD Rights)
- [ ] RA 8972 / RA 11861 (Solo Parent)
- [ ] RA 10968 (PQF Act)
- [ ] CMO 1, s. 2025 (Microcredentials)
- [ ] Other (specify: )
- [ ] None

## PII and Data Privacy Considerations

<!-- Does this module handle PII or SPI? What consent and access controls are needed? -->

## Acceptance Criteria

<!-- What must be true for this module to be considered complete? -->

- [ ] Models created with proper naming (`esmis.*`)
- [ ] Security groups and ACLs defined in `security/`
- [ ] Unit tests with adequate coverage
- [ ] Demo data that creates complete, consistent records
- [ ] `readme/DESCRIPTION.md` written
- [ ] `__manifest__.py` with correct `application` and `auto_install` settings
- [ ] No PII in log messages
- [ ] Consent management for models with student PII (if applicable)
- [ ] Multi-campus record rules isolate by `company_id` (if applicable)
- [ ] Government export formats tested against agency specs (if applicable)
-

## Additional Context

<!-- Mockups, diagrams, references to ADRs, research docs, or external specs. -->
