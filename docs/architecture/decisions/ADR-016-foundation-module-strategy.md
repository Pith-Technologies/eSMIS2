# ADR-016: Foundation Module Strategy

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

Layer 1 (Foundation) of the eSMIS architecture contains four modules that every higher-layer
module depends on:

| Module               | Purpose                                                   | Models | Complexity |
|----------------------|-----------------------------------------------------------|--------|------------|
| `esmis_vocabulary`   | Controlled code lists / terminology system                | 3      | M          |
| `esmis_security`     | Security groups, PII mixins, audit logging, consent, DPO  | 10+    | XL         |
| `esmis_academic_term`| Academic year and term/semester definitions                | 2      | S          |
| `esmis_student`      | Student profiles, `res.partner` extensions, identifiers   | 4      | L          |

The question is whether these four modules should remain separate, or whether some subset
should be consolidated into a single `esmis_base` module.

### Why This Decision Matters

Foundation modules are the most depended-upon code in the system. The dependency graph shows
that `esmis_security` alone is a dependency of every module in Layers 2–4 (all 16+ modules).
Getting the granularity wrong here has cascading consequences: too coarse means unnecessary
coupling and slower iteration; too fine means dependency sprawl and installation complexity.

### Current Dependency Structure

From the implementation roadmap, the foundation dependency chain is:

```
esmis_vocabulary  →  base
esmis_security    →  base, esmis_vocabulary
esmis_academic_term → base, esmis_security
esmis_student     →  base, esmis_vocabulary, esmis_security
```

The `esmis_security` module is particularly large. It owns:
- Security groups, privileges, and the three-tier access architecture (ADR-001)
- 26 domain categories for `ir.module.category`
- Cross-cutting mixins: `esmis.approval.mixin`, `esmis.consent.mixin`, `esmis.pii.aware`,
  `esmis.campus.aware`, `esmis.retention.aware`
- Privacy/compliance models: `esmis.consent`, `esmis.consent.scope`, `esmis.data.breach`,
  `esmis.data.subject.request`, `esmis.disposal.review`, `esmis.retention.schedule`
- Audit infrastructure: `esmis.audit.rule`, `esmis.audit.log`, `esmis.pii.access.log`
- Approval definitions: `esmis.approval.definition`

## Decision

**We will keep the foundation as four separate modules (Option A).**

The foundation layer consists of:
1. **`esmis_vocabulary`** — vocabulary/terminology system (no student domain knowledge)
2. **`esmis_security`** — security groups, PII mixins, audit logging, consent management
3. **`esmis_academic_term`** — academic year/term management
4. **`esmis_student`** — student profiles, `res.partner` extensions, identifiers

No `esmis_base` module will be created.

### Rationale

1. **Clear domain boundaries.** Each module has a well-defined responsibility:
   - `esmis_vocabulary` is a generic code-list system with no student or academic knowledge.
   - `esmis_security` is infrastructure: groups, mixins, audit, and compliance tooling. It
     does not know what a student or a term is.
   - `esmis_academic_term` models calendar/scheduling concepts (years, semesters, enrollment
     windows) — a clean domain separate from student identity.
   - `esmis_student` is the first domain module — it knows what a student is, links to
     `res.partner`, and manages identifiers.

2. **Avoids the "base module" anti-pattern.** An `esmis_base` module would inevitably become
   a dumping ground for code that "doesn't fit elsewhere." This is a well-documented problem
   in Odoo ecosystems — large base modules accumulate unrelated functionality, become hard to
   test, and create unnecessary upgrade risk.

3. **Independent testability.** Each module can be tested in isolation:
   - `esmis_vocabulary` tests need only `base`.
   - `esmis_security` tests need `base` + `esmis_vocabulary`.
   - `esmis_academic_term` tests need `base` + `esmis_security`.
   - `esmis_student` tests need `base` + `esmis_vocabulary` + `esmis_security`.
   A monolithic base module would force all tests to load everything.

4. **Parallel development.** Four separate modules means up to four contributors can work on
   foundation code simultaneously with minimal merge conflicts.

5. **Odoo's module system favors small, focused modules.** The Odoo framework is designed
   around fine-grained modules with explicit dependencies. Module installation, upgrade, and
   uninstallation all work at the module level — smaller modules give administrators more
   control and reduce upgrade risk.

6. **Selective installation remains possible.** While most deployments will install all four
   foundation modules, keeping them separate preserves the option of lightweight setups
   (e.g., a vocabulary-only configuration for testing terminology before rolling out the
   full SIS).

## Alternatives Considered

### Alternative: `esmis_base` Consolidation (Option B)

Merge security groups, `res.partner` extensions, and shared mixins into a single `esmis_base`
module. Keep `esmis_vocabulary` separate (no student domain knowledge) and
`esmis_academic_term` separate (clean domain boundary). `esmis_student` would depend on
`esmis_base` instead of `esmis_security`.

**Pros:**
- Fewer modules to install and manage at the foundation layer
- Single dependency for upper-layer modules instead of listing `esmis_security` +
  `esmis_student` separately
- Reduced boilerplate in `__manifest__.py` dependency lists

**Cons:**
- Merges infrastructure (`esmis_security`) with domain logic (`esmis_student`), blurring
  the line between "what secures the system" and "what the system is about"
- `esmis_security` already has 10+ models and 5 mixins — adding student models would make
  it even larger (14+ models), harder to review, and slower to test
- Creates a coupling where changes to student profile fields trigger reinstallation of
  security infrastructure (and vice versa)
- Sets a precedent for future "just add it to base" decisions, leading to gradual bloat
- Makes it harder for external contributors to understand module boundaries
- The "fewer dependencies to list" benefit is marginal — Odoo handles transitive
  dependencies automatically

**Decision:** Rejected — the costs of coupling outweigh the convenience of consolidation.

## Consequences

### Positive

1. **Stable interfaces.** Each module's API surface is small and well-defined. Changes to
   audit logging don't risk breaking student profile logic.
2. **Faster CI.** Module-level test suites run independently and in parallel. The vocabulary
   test suite doesn't need to load security infrastructure.
3. **Clear ownership.** Code review assignments are straightforward — security changes stay
   in `esmis_security`, student model changes stay in `esmis_student`.
4. **Upgrade safety.** A bugfix to consent management (`esmis_security`) can be deployed
   without touching `esmis_student` or `esmis_academic_term`.
5. **Documentation clarity.** The four-module foundation maps directly to the architecture
   diagram in `CLAUDE.md`, making it easy for contributors to orient themselves.

### Negative

1. **More modules to track.** Four foundation modules instead of two or three means more
   `__manifest__.py` files, more `ir.model.access.csv` files, and more test directories to
   maintain.
2. **Dependency lists are slightly longer.** Upper-layer modules must list both
   `esmis_security` and `esmis_student` as dependencies (rather than a single `esmis_base`).
   This is mitigated by Odoo's transitive dependency resolution.
3. **Cross-module coordination needed.** If a change spans security and student concerns
   (e.g., adding a PII field to the student model), it requires coordinated changes across
   two modules. This is by design — the separation forces explicit consideration of both
   security and domain implications.

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `esmis_security` grows too large on its own | MEDIUM | MEDIUM | Monitor model count; extract `esmis_audit` or `esmis_consent` if it exceeds ~15 models |
| Circular dependency between foundation modules | LOW | HIGH | Enforce strict layering: vocabulary → security → term/student (never reverse) |
| Contributors unsure which foundation module owns a concern | LOW | LOW | Data model registry and module architecture docs are authoritative |

## References

- [ADR-001: Access Rights Management](ADR-001-access-rights-management.md) — defines
  `esmis_security` scope
- [Data Model Registry](../data-model-registry.md) — authoritative model-to-module mapping
- [Implementation Roadmap](../implementation-roadmap.md) — Phase 1 build order
- [Module Architecture Principles](../../principles/module-architecture.md)

---

**Document Version:** 1.0
**Last Updated:** 2026-03-09
