# eSMIS

<!-- TODO: Replace with actual logo -->
<!-- ![eSMIS Logo](docs/assets/logo.png) -->

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![Odoo: 19.0](https://img.shields.io/badge/Odoo-19.0-purple.svg)](https://www.odoo.com/)
[![Status: Pre-release](https://img.shields.io/badge/Status-Pre--release-orange.svg)]()

**eSMIS** (enhanced Student Management Information System) is a modular Student Information System for Philippine higher education institutions (HEIs), built on Odoo 19. It is designed from the ground up for Philippine regulatory compliance — including RA 10173 (Data Privacy Act), CHED MORPHE, and RA 10931 (Free Tuition Law) — with support for multi-campus deployments and government system integration.

## Key Features

- **Philippine regulatory compliance** — RA 10173, CHED MORPHE (CMO 40), RA 10931 (Free Tuition), RA 10687 (UniFAST), and accreditation standards (AACCUP/PACUCOA/PAASCU)
- **Multi-campus architecture** — leverages Odoo's multi-company model for campus isolation with centralized administration
- **Government system integration** — PhilSys identity verification, CHED HEMIS export, UniFAST/TES reporting, eCAV credential verification
- **Privacy by design** — PII encryption, per-purpose consent management, breach notification workflows, DPO tools (RA 10173)
- **Controlled vocabulary system** — institution-configurable terminology aligned with CHED and PQF standards
- **LMS integration** — LTI 1.3 and OneRoster support for Moodle and Canvas
- **Student self-service portal** — enrollment, grades, billing, and document requests
- **Full student lifecycle** — application, enrollment, scheduling, grading, billing, financial aid, graduation, and alumni tracking

## Current Status

eSMIS is in **pre-release / active development**. Phase 1 of the foundation layer is built: nine modules with 323 tests between them, covering vocabulary, security, consent, approvals, addresses, the student profile and the Philippine extensions. 77 documentation files establish the architecture, development principles and regulatory requirements. The project infrastructure (Docker dev environment, CLI tooling, CI/CD, linting) is production-ready.

No domain module — enrollment, curriculum, grading, scheduling, billing, financial aid — is written yet. The roadmap below marks what exists.

### Module Roadmap

| Phase | Modules | Status |
|-------|---------|--------|
| **Phase 1A: Foundation** | | |
| | `esmis_base` | ✅ Complete |
| | `esmis_vocabulary` | ✅ Complete |
| | `esmis_security` | ✅ Complete |
| | `esmis_consent` | ✅ Complete |
| | `esmis_approval` | ✅ Complete |
| **Phase 1B: Student Profile** | | |
| | `esmis_address` | ✅ Complete |
| | `esmis_student` | ✅ Complete |
| | `esmis_ph` | ✅ Complete |
| | `esmis_starter_ph` | ✅ Complete |
| **Phase 1C: Remaining Foundation** | | |
| | `esmis_academic_term` | 🔜 Next |
| **Phase 2: Core Academic** | | |
| | `esmis_curriculum` | 📋 Planned |
| | `esmis_scheduling` | 📋 Planned |
| | `esmis_faculty` | 📋 Planned |
| | `esmis_enrollment` | 📋 Planned |
| | `esmis_grading` | 📋 Planned |
| **Phase 3: Core Financial** | | |
| | `esmis_billing` | 📋 Planned |
| | `esmis_financial_aid` | 📋 Planned |
| **Phase 4: Extended Services** | | |
| | `esmis_documents` | 📋 Planned |
| | `esmis_reports` | 📋 Planned |
| | `esmis_student_services` | 📋 Planned |
| | `esmis_alumni` | 📋 Planned |
| **Phase 5: Portals & Integrations** | | |
| | `esmis_api` | 📋 Planned |
| | `esmis_student_portal` | 📋 Planned |
| | `esmis_lms_bridge` | 📋 Planned |
| | `esmis_philsys` | 📋 Planned |
| | `esmis_payment` | 📋 Planned |

A minimum viable SIS (Phases 1-3 plus `esmis_documents`) covers the full student lifecycle for a single-campus pilot deployment.

## Quick Start

### Prerequisites

- Docker and Docker Compose v2
- Git
- Python 3.9 or newer, for the `./esmis` CLI and the scripts. Odoo runs on its
  own interpreter inside the container, not this one

### Getting Started

```bash
git clone https://github.com/Pith-Technologies/eSMIS2.git
cd eSMIS2
./esmis build
./esmis start       # http://localhost:8069 (admin/admin)
```

Run `./esmis doctor` to verify your environment. See the [CLI Guide](docs/guides/esmis-cli.md) for all available commands.

## Architecture

Dependencies flow downward. Higher layers depend on lower ones, never the reverse.

```
Layer 4: PORTALS & INTEGRATIONS
    esmis_student_portal, esmis_api, esmis_lms_bridge, esmis_philsys, esmis_payment
        |
Layer 3: DOMAIN EXTENSIONS
    esmis_reports, esmis_documents, esmis_alumni, esmis_student_services
        |
Layer 2: DOMAIN CORE
    esmis_enrollment, esmis_curriculum, esmis_grading, esmis_scheduling,
    esmis_billing, esmis_financial_aid, esmis_faculty
        |
Layer 1: FOUNDATION
    esmis_security*, esmis_vocabulary*, esmis_consent*, esmis_approval*,
    esmis_address*, esmis_student*, esmis_ph*, esmis_starter_ph*,
    esmis_academic_term
        |
Layer 0: BASE
    esmis_base* -> base
```

`*` marks a module that exists today; everything else is planned. `esmis_base`
depends on `base` alone — the wider Odoo dependencies (`hr`, `account`,
`calendar`, `documents`) arrive with the Layer 2 modules that need them.

`esmis_address`, `esmis_ph` and `esmis_starter_ph` came out of Phase 1B, which
kept the Philippine extensions in one module rather than scattering `_ph`
modules across the foundation, and made `esmis_starter_ph` the only entry in
the Apps menu. See [Phase 1B Plan](docs/plans/phase-1b-plan.md) and
[ADR-018](docs/architecture/decisions/ADR-018-menu-architecture.md).

For details, see [Architecture Vision](docs/architecture/vision.md), [Integration Patterns](docs/architecture/integration-patterns.md), and [Architecture Decisions](docs/architecture/decisions/).

## Documentation

| Area | Location | Description |
|------|----------|-------------|
| Architecture & ADRs | [docs/architecture/](docs/architecture/) | System architecture, module map, and decision records |
| Development Principles | [docs/principles/](docs/principles/) | Naming, security, UI, regulatory compliance, data privacy |
| Developer Guides | [docs/guides/](docs/guides/) | CLI usage, module development, testing, Claude Code workflow |
| Research | [docs/research/](docs/research/) | Philippine SIS landscape, regulatory analysis, integration specs |

## Regulatory Compliance

eSMIS is built for the Philippine regulatory environment. Compliance is not an afterthought — it shapes the data model, security architecture, and module design.

| Regulation | Coverage |
|------------|----------|
| **RA 10173** (Data Privacy Act) | Consent management, DPO workflows, breach notification, PII encryption, audit logging |
| **CHED MORPHE** (CMO 40, s. 2008) | Student records structure, grading standards, retention policies |
| **RA 10931** (Free Tuition Law) | Citizenship verification, subsidy computation, CHED/UniFAST reporting |
| **RA 10687** (UniFAST Act) | Multi-source financial aid tracking and eligibility validation |
| **RA 7277/10754** (PWD Rights) | 20% tuition discount, accessibility compliance |
| **RA 8972/11861** (Solo Parent) | Scholarship eligibility determination |
| **RA 10968** (PQF Act) | Program-to-qualification framework mapping |
| **CMO 1, s. 2025** (Microcredentials) | Verifiable credential issuance |

See [Regulatory Compliance](docs/principles/regulatory-compliance.md) and [Government Integrations](docs/principles/government-integrations.md) for implementation details.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting changes, commit conventions, and the review process.

Module requests and feature proposals are encouraged — open an issue to start a discussion.

## License

This project is licensed under the [GNU Lesser General Public License v3 (LGPL-3)](LICENSE).

## Acknowledgments

- [Odoo](https://www.odoo.com/) and the [Odoo Community Association (OCA)](https://odoo-community.org/) for the framework and community ecosystem
- The [National Privacy Commission (NPC)](https://www.privacy.gov.ph/) for data privacy guidance and RA 10173 implementation advisories
- The [Commission on Higher Education (CHED)](https://ched.gov.ph/) for regulatory standards that inform this system's design
