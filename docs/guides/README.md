# eSMIS Guides

Practical how-to guides for building eSMIS. Where [principles](../principles)
describe _what_ standards to follow, these describe _how_ to accomplish a task.

Guides are read to learn. Procedures you follow under pressure, often against a
regulatory deadline, live in [runbooks](../runbooks) instead.

## Guide Documents

| Guide | Description |
| --- | --- |
| [Module Development](module-development.md) | Create, structure and ship a new module from scratch using TDD and Claude Code |
| [Tutorial: Your First Module](tutorial-first-module.md) | Worked example building `esmis_academic_term` step by step |
| [Testing Guide](testing-guide.md) | Write, run and maintain tests for project modules |
| [esmis CLI](esmis-cli.md) | Developer CLI for running, testing and managing the project locally |
| [PhilSys Integration](philsys-integration-guide.md) | Configure and use Philippine National ID (PhilSys) verification |
| [Security Scanning](security-scanning.md) | How the scanning pipeline is configured and what it checks |
| [Claude Code Sandbox](claude-code-sandbox.md) | Run Claude Code safely using DevContainers |

## How to Use These Guides

1. **Learning the codebase**: start with [Tutorial: Your First Module](tutorial-first-module.md), then [Module Development](module-development.md)
2. **Testing**: refer to the [Testing Guide](testing-guide.md) for test patterns and how to run them
3. **Before declaring a module complete**: run the [security audit runbook](../runbooks/security-audit.md)

## Relationship to Other Documentation

- [Principles](../principles) — standards and conventions that guides implement
- [Runbooks](../runbooks) — operational procedures, followed rather than read
- [Architecture Decisions](../architecture/decisions) — ADRs that inform guide recommendations
- [Research](../research) — background research behind guide content
