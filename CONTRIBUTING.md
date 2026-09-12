# Contributing to eSMIS

Thank you for your interest in contributing to the Student Management Information System for Philippine higher education
institutions!

## Prerequisites

|        |                                                                                                                        |
| ------ | ---------------------------------------------------------------------------------------------------------------------- |
| Docker | Compose v2. Odoo and PostgreSQL both run in containers                                                                 |
| Python | 3.9 or newer, for the `./esmis` CLI and the scripts. Odoo's own interpreter lives in the container and is not this one |
| Git    | any recent version                                                                                                     |

Python 3.11 adds `tomllib`. On an older interpreter the optional `~/.esmis.toml` config is skipped with a notice, and
`pip install tomli` restores it. Nothing else needs it.

`./esmis doctor` checks all of the above and names anything missing.

## Getting Started

1. Read the [Development Principles](docs/principles/README.md)
2. Review the [Architecture](docs/architecture/) and [ADRs](docs/architecture/decisions/)
3. Check open issues in this repository
4. Set up your local environment (see the [Quickstart](docs/guides/quickstart.md) and
   [CLI Guide](docs/guides/esmis-cli.md) for commands)

## Module Proposals

All new `esmis_*` modules go through a proposal process before implementation.

### Steps

1. **File a Module Request issue** describing the module's purpose, which layer it belongs to (see the
   [module dependency graph](docs/architecture/implementation-roadmap.md)), and what problems it solves.
2. **Create an ADR** if the module involves architectural decisions (new integrations, data model changes, cross-module
   dependencies). Place it in `docs/architecture/decisions/` following the existing numbering convention.
3. **Get team review** before writing code. The issue should be approved and the ADR accepted. This prevents wasted
   effort on modules that overlap with existing plans or violate architectural constraints.
4. **Reference the dependency graph** in your implementation. Modules must respect the layer hierarchy:
   - Layer 1 (Foundation) modules depend only on Layer 0 (Odoo Core)
   - Layer 2 (Domain Core) modules depend on Layer 1
   - Layer 3 (Domain Extensions) depend on Layer 2
   - Layer 4 (Portals & Integrations) depend on Layer 3

See [Module Architecture](docs/principles/module-architecture.md) and
[Module Visibility](docs/principles/module-visibility.md) for naming and manifest rules.

## Adding Vocabularies

Vocabularies live in `esmis_vocabulary/data/` as XML data files. Follow the established pattern:

### Vocabulary Record

```xml
<odoo noupdate="1">
    <record id="vocab_your_vocabulary" model="esmis.vocabulary">
        <field name="name">Human-Readable Name</field>
        <field name="namespace_uri">urn:tpl:vocab:your-vocabulary</field>
        <field name="description">Clear description of what this vocabulary covers.</field>
        <field name="is_system" eval="True"/>
        <field name="domain">academic</field>
    </record>
</odoo>
```

### Vocabulary Codes

```xml
<record id="code_your_vocab_first_value" model="esmis.vocabulary.code">
    <field name="vocabulary_id" ref="vocab_your_vocabulary"/>
    <field name="code">VALUE_CODE</field>
    <field name="display">Human-Readable Display Text</field>
    <field name="sequence">10</field>
</record>
```

### Rules

- Use `noupdate="1"` so user customizations are preserved on upgrade.
- Set `is_system` to `True` for system-managed vocabularies that users should not delete.
- Provide a real `namespace_uri` using the `urn:tpl:vocab:` prefix (see
  [ADR-002](docs/architecture/decisions/ADR-002-namespace-uris-for-identifiers.md) and
  [ADR-003](docs/architecture/decisions/ADR-003-terminology-system.md)).
- Include human-readable `display` text and a `description` on the vocabulary itself.
- Use `sequence` values in increments of 10 to allow future insertions.
- Add the new XML file to the `data` list in `esmis_vocabulary/__manifest__.py`.

## Country-Specific Modules

eSMIS is built for Philippine HEIs first, but the architecture supports other countries.

### Naming Convention

Use `esmis_{feature}_{country_code}` for country-specific modules:

- `esmis_grading_ph` -- Philippine grading scales (1.0-5.0, INC, DRP)
- `esmis_grading_id` -- Indonesian grading scales
- `esmis_billing_ph` -- Philippine billing with BIR compliance

### Guidelines

- **Use `_inherit` to extend base models** with country-specific fields and methods. The base module (e.g.,
  `esmis_grading`) defines the shared interface; the country module adds localized behavior.
- **Never add country-specific logic to base modules.** If you find yourself writing `if country == 'PH':` in a base
  module, that logic belongs in a country module instead.
- **Use `excludes` in the manifest** for mutually exclusive country modules. This prevents installing two conflicting
  country variants simultaneously:

```python
{
    "name": "eSMIS Grading - Philippines",
    "excludes": ["esmis_grading_id", "esmis_grading_vn"],
}
```

- **Keep vocabularies country-aware.** Country-specific code lists (e.g., Philippine civil status values from PSA)
  belong in the country module, not the base vocabulary data.

## Regulatory Compliance in PRs

Reviewers check every PR against RA 10173 (Data Privacy Act) and related regulations. Prepare for these checks:

### PII Classification

Every new field that stores personal data must be classified using the
[4-tier model](docs/architecture/decisions/ADR-005-data-classification-system.md):

| Tier | Category        | Examples                              | Requirements                       |
| ---- | --------------- | ------------------------------------- | ---------------------------------- |
| 0    | Public          | Institution name, program title       | Standard access control            |
| 1    | Internal        | Enrollment status, section assignment | Role-based access                  |
| 2    | Confidential    | Home address, contact number          | Consent + role-based access        |
| 3    | Sensitive (SPI) | Grades, national ID, medical records  | Consent + encryption + audit + MFA |

### Checklist for PR Authors

- [ ] New fields with personal data have a PII tier classification
- [ ] Consent management is implemented for fields requiring student data processing (Tier 2+)
- [ ] No PII appears in `_logger` calls, exception messages, or user-facing error strings
- [ ] No PII in XML IDs (use codes or sequence numbers, not names)
- [ ] Sensitive fields use `groups=` attribute to restrict access
- [ ] Tier 3 (SPI) field access is audit-logged
- [ ] Tests verify access control and consent enforcement for new PII fields
- [ ] MFA consideration documented for views accessing Tier 3 data

See [Data Privacy and PII](docs/principles/data-privacy-and-pii.md),
[Consent Management](docs/principles/consent-management.md), and
[ADR-012](docs/architecture/decisions/ADR-012-student-data-privacy-ra10173.md) for details.

## Code Standards

Detailed standards are in `docs/principles/`. Here is a summary of what every contributor should know:

### Naming Conventions

All modules use `esmis_*` technical names and `esmis.*` model names. See
[Naming Conventions](docs/principles/naming-conventions.md).

### Odoo 19 Compatibility

Use the Odoo 19 API (Command tuples, `@api.depends`, etc.). See
[Odoo 19 Compatibility](docs/principles/odoo19-compatibility.md).

### Error Handling and PII Protection

- No `print()` -- use `_logger`
- No bare `except:` clauses
- No `cr.commit()` in loops
- No PII in log messages or exceptions -- log record IDs instead

See [Error Handling](docs/principles/error-handling.md) and [Test Data PII](docs/principles/test-data-pii.md).

### Testing Requirements

- Tests are required for all new functionality
- Tests must run under appropriate user roles, not just admin
- Access control and consent enforcement must have dedicated tests
- Government export formats must be tested against agency specifications

See [Testing](docs/principles/testing.md).

### Access Rights

- Every model needs an entry in `ir.model.access.csv`
- Related models need ACLs too (e.g., if `esmis.order` has an ACL, `esmis.order.line` likely needs one)
- Fix ACL issues properly -- do not bypass with `sudo()`

See [Access Rights](docs/principles/access-rights.md).

## Development Workflow

### Test-Driven Development

We practice TDD:

1. **Write a failing test** that describes the expected behavior
2. **Write the minimum code** to make the test pass
3. **Refactor** while keeping tests green
4. When fixing bugs, **write a failing test that reproduces the bug first**

### Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) in imperative mood, present tense:

```
{type}({scope}): {description}

{body}
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

Examples:

- `feat(enrollment): add pre-enrollment validation for free tuition eligibility`
- `fix(grading): prevent grade posting without consent verification`
- `docs(privacy): add RA 10173 consent flow diagrams`

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the principles and TDD workflow
3. Write/update tests -- verify they pass with `./esmis test <module>`
4. Run linters: `pre-commit run --files <changed_files>`
5. Submit a PR using the template
6. Address reviewer feedback, especially regulatory compliance checks

### Running Tests and Linters

```bash
./esmis test <module_name>                    # Run module tests
./esmis test <module> --tags=post_install     # Filter by tag
pre-commit run ruff --files <changed_files>          # Lint Python
pre-commit run ruff-format --files <changed_files>   # Format Python
pre-commit run prettier --files <changed_files>      # Format XML/MD/JSON
./esmis audit-security                        # Security/ACL audit
```

## Community

- [Code of Conduct](code_of_conduct.md)
- [Security Policy](SECURITY.md)
- [Vulnerability Disclosure](vulnerability_disclosure_policy.md)

## Documentation

| Document                                                                                   | Purpose                           |
| ------------------------------------------------------------------------------------------ | --------------------------------- |
| [docs/principles/](docs/principles/)                                                       | Development standards             |
| [docs/architecture/](docs/architecture/)                                                   | Architecture decisions            |
| [docs/architecture/decisions/](docs/architecture/decisions/)                               | ADRs for significant decisions    |
| [docs/architecture/implementation-roadmap.md](docs/architecture/implementation-roadmap.md) | Module dependency graph & roadmap |

## Questions?

Open an issue or reach out to the maintainers.
