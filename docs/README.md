# Project Documentation

Documentation for eSMIS, a Student Management Information System for Philippine
higher education institutions, built on Odoo 19. Modules use `esmis_*` naming and
the system is built to comply with RA 10173 (Data Privacy Act), CHED regulations
and RA 10931 (Free Tuition Law).

## Directory Structure

```
docs/
├── architecture/        # Architecture decisions and project vision
│   └── decisions/       # ADRs (Architecture Decision Records)
├── principles/          # Development standards and guidelines
├── guides/              # Developer guides
├── research/            # Regulatory and domain research behind the principles
└── security/            # Security scanning docs
```

## Quick Links

| Need to... | Go to... |
|------------|----------|
| See the project architecture vision | [architecture/vision.md](architecture/vision.md) |
| Understand module integration patterns | [architecture/integration-patterns.md](architecture/integration-patterns.md) |
| Read coding principles | [principles/](principles/) |
| Check an ADR | [architecture/decisions/](architecture/decisions/) |
| Use the developer CLI | [guides/odoo-project-cli.md](guides/odoo-project-cli.md) |
| Create a new module | [guides/module-development.md](guides/module-development.md) |
| Write and run tests | [guides/testing-guide.md](guides/testing-guide.md) |
| Use Claude Code effectively | [guides/claude-code-for-developers.md](guides/claude-code-for-developers.md) |
| Run security audits | [guides/security-audit-guide.md](guides/security-audit-guide.md) |
| Run Claude Code in sandbox | [guides/claude-code-sandbox.md](guides/claude-code-sandbox.md) |

## Getting Started

1. Review [Architecture Vision](architecture/vision.md) — project architecture and module approach
2. Read [Development Principles](principles/README.md) — how we build
3. Check [Module Development Guide](guides/module-development.md) — building your first module

## Key Architecture Documents

- [Architecture Vision](architecture/vision.md) — Module map and implementation approach
- [Module Integration Patterns](architecture/integration-patterns.md) — Mapping domain concepts to Odoo modules
