# Changelog

All notable changes to eSMIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

#### Foundation Modules — Phase 1A

- Base module (`esmis_base`) providing the shared configuration menu and common infrastructure every other module builds
  on
- Security module (`esmis_security`) with the three-tier group architecture — roles, functional privileges, data-scope
  groups — and cross-cutting mixins (56 tests)
- Consent module (`esmis_consent`) implementing RA 10173 per-partner, per-purpose consent with `esmis.consent`,
  `esmis.consent.scope` and a mixin models opt into (40 tests)
- Approval module (`esmis_approval`) with a reusable approval state machine, `esmis.approval.definition` and a mixin
  carrying `approval_state` (30 tests)

#### Student Profile Modules — Phase 1B

- Address module (`esmis_address`) with a structured `esmis.address` linked to `res.partner`, a computed `address_text`
  and address typing (21 tests)
- Student module (`esmis_student`) extending `res.partner` with universal student demographics, education history, and
  the `esmis.identifier` model that keeps government and institutional ID numbers off `res.partner` and out of the API
  surface. Identifiers are encrypted with AES-256-GCM and indexed by an HMAC-SHA256 blind index (89 tests)
- Philippine module (`esmis_ph`) holding every PH-specific extension in one place: the full PSGC hierarchy (region,
  province, city/municipality, barangay), PH address formatting, PH vocabularies and PH partner fields such as
  `middle_name_b4_marriage` (50 tests)
- Starter module (`esmis_starter_ph`) — the single `application=True` module and therefore the only entry in the Apps
  menu (ADR-018), aggregating the foundation into one installable product

#### Vocabulary System

- Vocabulary module (`esmis_vocabulary`) with `esmis.vocabulary` and `esmis.vocabulary.code` models
- 10 seed vocabularies: academic period type, blood type, civil status, degree type, disability type, document type,
  enrollment status, gender, grade remark, relationship type, scholarship type, student status, year level
- Security groups and ACLs for vocabulary management
- Tests for vocabulary CRUD, code management, system protection, and security

#### Documentation — Principles

- Naming conventions, access rights, module architecture, module visibility
- API design, performance and scalability, testing standards
- Approval workflows, error handling and logging, audit and compliance
- UI design, UI entity classification, UI performance, pretty URLs
- Odoo 19 compatibility guide
- Module descriptions guide
- Multi-campus architecture
- Government integrations (PhilSys, CHED HEMIS, eCAV, UniFAST, LMS, payments)
- Regulatory compliance (RA 10173, MORPHE, RA 10931, RA 10687, PWD, Solo Parent, PQF, microcredentials)
- Financial aid patterns (government, institutional, external, statutory discounts)
- Enrollment workflows (admission, pre-enrollment, add/drop, cross-enrollment)
- Grading and academic standing (Philippine grading systems, GWA, Latin honors)
- Student data lifecycle (admissions through alumni)
- Test data and PII handling rules
- Consent management (RA 10173)
- Data retention and disposal
- Data privacy and PII classification (authoritative reference)

#### Documentation — Architecture

- Architecture vision and integration patterns
- ADR-004: Access rights management
- ADR-007: Namespace URIs for identifiers
- ADR-009: Terminology system
- ADR-010: API v2 architecture
- ADR-011: Data classification system
- ADR-012: PII encryption strategy
- ADR-016: Foundation module strategy
- ADR-018: DMS security and storage enhancements
- ADR-020: Unified API audit log
- ADR-022: API v2 application-level authorization
- Data model registry and implementation plan
- Implementation roadmap and ERD diagrams

#### Documentation — Guides

- Module development guide (TDD workflow with Claude Code)
- Testing guide (writing, running, maintaining tests)
- Security audit guide (audit commands, fixing access rights)
- `esmis` CLI reference
- Claude Code for developers
- Claude Code sandbox (DevContainers)
- Government export guide (CHED HEMIS, eCAV, UniFAST)
- Multi-campus setup guide
- PhilSys integration guide
- Data breach response guide

#### Documentation — Research

- Philippine SIS regulatory research
- Government integration research
- Best practices research

#### Data Privacy Compliance (RA 10173)

- PII classification tiers and field inventory
- Consent management patterns and enforcement
- Data retention schedule and disposal procedures
- Breach response procedures and NPC notification guide
- Security scanning documentation

#### Infrastructure — Docker

- Multi-stage Dockerfile with Odoo 19 base
- `docker-compose.yml` for local development
- Production Docker Compose with Nginx, Redis, backup services
- Entrypoint script with health checks and configuration templating
- Development and production Python requirements
- `.env.production.example` with documented settings

#### Infrastructure — CI/CD

- GitHub Actions CI workflow (lint, test, build)
- Full CI workflow with matrix testing
- CodeQL code analysis workflow
- Pre-commit workflow
- Security scanning workflow (Trivy, Gitleaks, Semgrep)
- Dependabot configuration for Actions, pip, and npm

#### Infrastructure — Developer Tooling

- `esmis` CLI (build, start, stop, test, audit, lint, fix)
- Pre-commit hooks (ruff, prettier, eslint, pylint, mypy, semgrep)
- Claude Code agents (odoo-developer, code-reviewer, ux-expert, code-simplifier, verify-module)
- Claude Code commands (implement, verify-tests, analyze, expert-review, commit, pr)
- Claude Code rules (odoo-python, odoo-xml, security, testing, module-setup)
- DevContainer configuration for VS Code
- EditorConfig, ruff, isort, flake8, pylint configurations
- Makefile for common tasks
- Scripts: security audits (static + dynamic), module audits, environment caching, Odoo 19 cleanup

#### Infrastructure — Project Governance

- LICENSE (LGPL-3.0)
- COPYRIGHT file
- CONTRIBUTING.md
- CONTRIBUTORS.md
- Code of Conduct
- SECURITY.md (vulnerability reporting)
- Pull request template
- Issue templates (bug report, feature request)
- CODEOWNERS configuration script
- Gitleaks, Snyk, and Trivy ignore configurations

### Changed

- Renamed `tpl_*` namespace to `esmis_*` across the project
- Renumbered ADRs to eliminate gaps (001-015)
- Updated project documentation for Philippine SIS domain
- CI workflows skip on docs-only changes via `paths-ignore`

### Removed

- The public-export subsystem: `scripts/export_to_public.py`, `scripts/export_config.toml` and
  `scripts/tests/test_export_to_public.py`. It came from the project template this repository was generated from, where
  a private development repo published a curated slice of itself to a separate public one — stripping self-hosted
  runners and an internal Docker registry mirror on the way out. eSMIS2 is itself the public repository and has neither
  of those, so the transformations had nothing to act on. Its output manifest also excluded `docs/` entirely, generated
  a stub README over the real one, and deleted anything in the target it did not recognise, so running it could only
  produce something worse than the repository it ran in.

### Security

- Semgrep rules for Odoo-specific security patterns
- Gitleaks configuration for secret detection
- Trivy container scanning with ignore list
- Snyk dependency monitoring

### Dependencies

- Bumped `actions/checkout` from 4 to 6
- Bumped `actions/setup-python` from 5 to 6
- Bumped `codecov/codecov-action` from 4 to 5
- Bumped `docker/setup-buildx-action` from 3 to 4
- Bumped `github/codeql-action` from 3 to 4
- Bumped `fastapi` from 0.112.2 to 0.136.1
- Removed unused `git-aggregator` from Docker requirements
- Bumped `pillow` from 11.1.0 to 12.3.0 (clears all open advisories against 11.1.0)
- Updated `websocket-client` from ~=0.56 to ~=1.9
