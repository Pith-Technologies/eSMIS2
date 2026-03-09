# Changelog

All notable changes to eSMIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

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
- `odoo-project` CLI reference
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

- `odoo-project` CLI (build, start, stop, test, audit, lint, fix)
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
- Bumped `fastapi` from 0.112.2 to 0.135.1
- Bumped `git-aggregator` from 4.0 to 4.1
- Bumped `pillow` from 11.1.0 to 12.1.1
- Updated `websocket-client` from ~=0.56 to ~=1.9
