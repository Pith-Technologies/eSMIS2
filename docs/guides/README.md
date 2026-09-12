# eSMIS Guides

This directory contains practical how-to guides for working with eSMIS. While [principles](../principles/) describe _what_ standards to follow, these guides describe _how_ to accomplish specific tasks.

## Guide Documents

| Guide                                                       | Description                                                                    |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------ |
| [Module Development](module-development.md)                 | Create, structure, and ship a new module from scratch using TDD and Claude Code |
| [Testing Guide](testing-guide.md)                           | Write, run, and maintain tests for project modules                             |
| [Security Audit Guide](security-audit-guide.md)             | Audit, understand, and fix access rights issues in modules                     |
| [esmis CLI](esmis-cli.md)                     | Developer CLI for running, testing, and managing the project locally            |
| [Government Export Guide](government-export-guide.md)       | Generate and submit government-mandated reports (CHED HEMIS, eCAV, UniFAST)    |
| [Multi-Campus Setup](multi-campus-setup-guide.md)           | Configure eSMIS for institutions with multiple campuses                        |
| [PhilSys Integration](philsys-integration-guide.md)         | Configure and use Philippine National ID (PhilSys) verification                |
| [Data Breach Response](breach-response-guide.md)            | Step-by-step procedure for responding to a personal data breach                |
| [Claude Code Sandbox](claude-code-sandbox.md)               | Run Claude Code safely using DevContainers                                     |

## How to Use These Guides

1. **New Development**: Follow the [Module Development](module-development.md) guide when creating new modules
2. **Testing**: Refer to the [Testing Guide](testing-guide.md) for test patterns and running tests
3. **Security**: Use the [Security Audit Guide](security-audit-guide.md) before declaring a module complete
4. **Deployment**: Consult the [Multi-Campus Setup](multi-campus-setup-guide.md) for multi-campus configurations
5. **Compliance**: Follow the [Government Export Guide](government-export-guide.md) and [Data Breach Response](breach-response-guide.md) for regulatory workflows

## Relationship to Other Documentation

- [Principles](../principles/) — Standards and conventions that guides implement
- [Architecture Decisions](../architecture/decisions/) — ADRs that inform guide recommendations
- [Research](../research/) — Background research behind guide content
