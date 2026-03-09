# eSMIS Pre-Implementation Improvements Plan

Status: IN PROGRESS
Created: 2026-03-09

## Overview

Before building domain modules, we need to complete the project foundation so that contributors
can work efficiently and the project presents well as an open-source contribution.

## Steps (in dependency order)

### Phase A: Architecture & Specification (do first — everything else depends on these)

- [ ] A1. Create data model registry (`docs/architecture/data-model-registry.md`)
- [ ] A2. Create implementation roadmap (`docs/architecture/implementation-roadmap.md`)
- [ ] A3. Create Mermaid ERD for core models (`docs/architecture/erd.md`)
- [ ] A4. Fix ADR numbering gaps (renumber or create missing ADRs)

### Phase B: Seed Data & Foundation Code

- [ ] B1. Add seed vocabularies to `esmis_vocabulary` (academic terms, year levels, student
      statuses, enrollment statuses, grade remarks, degree types, document types, relationship
      types, disability types, scholarship types)
- [ ] B2. Define the `esmis_base` module decision — ADR for whether it should exist or if
      `esmis_vocabulary` + `esmis_security` suffice

### Phase C: Open-Source Readiness

- [ ] C1. Rewrite `README.md` (project description, badges, screenshots placeholder, quickstart,
      feature roadmap with status, contributing link)
- [ ] C2. Create `CHANGELOG.md`
- [ ] C3. Create `docs/guides/README.md` (guide index)
- [ ] C4. Update `CONTRIBUTING.md` with SIS-specific guidance (module proposals, vocabulary
      additions, country-specific modules, regulatory compliance in PRs)
- [ ] C5. Add "Module Request" issue template (`.github/ISSUE_TEMPLATE/module_request.md`)
- [ ] C6. Fix terminology inconsistencies across docs (campus vs company, identifier vs external
      ID)

### Phase D: Developer Experience

- [ ] D1. Add `quickstart` command to `odoo-project` or document a one-liner
- [ ] D2. Create example module tutorial (`docs/guides/tutorial-first-module.md`) using
      `esmis_academic_term` as the example

### Phase E: Strategic Documentation

- [ ] E1. Create compliance matrix page (`docs/architecture/compliance-matrix.md`)
- [ ] E2. Document internationalization strategy (`docs/architecture/decisions/ADR-016-internationalization-strategy.md`)
- [ ] E3. Create API specification outline (`docs/architecture/api-specification.md`)

## Execution Notes

- Each step gets committed individually
- Steps within a phase can often be parallelized
- Edwin reviews plan before implementation begins
