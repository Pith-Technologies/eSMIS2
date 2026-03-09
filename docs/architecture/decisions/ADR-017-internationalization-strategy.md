# ADR-017: Internationalization Strategy

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

eSMIS is initially built for Philippine higher education institutions (HEIs), but as an
open-source project, other countries may want to adopt it. The architecture must support
country-specific variations in grading, regulations, government integrations, and academic
conventions without modifying base modules.

Country-varying concerns include:

| Concern | Philippine Example | Other-Country Example |
|---------|-------------------|-----------------------|
| Government identifiers | PhilSys National ID, LRN, TIN | Aadhaar (India), NIK (Indonesia) |
| Regulatory validations | RA 10173 consent, RA 10931 tuition checks | PDPA (Thailand), UU PDP (Indonesia) |
| Government export formats | CHED HEMIS, eCAV | DIKTI PDDIKTI (Indonesia) |
| Grading scales | 1.0–5.0 (1.0 = highest) | 0–100 percentage, A–F letter grades |
| Academic period types | Semester, trimester, summer | Quarter, block |
| Degree types | CHED-recognized program classifications | Country-specific qualification frameworks |
| Financial aid rules | RA 10931 free tuition, RA 10687 UniFAST | Country-specific scholarship programs |
| Data privacy regime | RA 10173 (Data Privacy Act), NPC circulars | GDPR (EU), PDPA (Thailand) |

### Why This Decision Matters

Without a clear internationalization strategy, one of two failure modes emerges:

1. **Philippine logic leaks into base modules.** Contributors add `if country == 'PH'`
   conditionals, making the codebase harder to maintain and hostile to non-Philippine adopters.
2. **Separate forks per country.** Each country maintains an independent fork, losing the
   benefits of shared development on enrollment, grading, scheduling, and other universal
   concerns.

The architecture must define where country-specific code lives, how it interacts with base
modules, and how conflicts between country variants are prevented.

## Decision

**Use a layered localization strategy with country modules extending country-neutral base
modules.**

### 1. Base Modules Are Country-Neutral

Core domain modules (`esmis_student`, `esmis_enrollment`, `esmis_grading`, `esmis_curriculum`,
`esmis_billing`, `esmis_scheduling`, `esmis_faculty`, `esmis_financial_aid`) contain no
country-specific logic. They define universal concepts — a student has enrollments, enrollments
reference courses, courses have grades — without assuming any particular country's conventions.

Where values vary by country (grading scales, academic period types, degree types, identifier
types), base modules use the vocabulary system (`esmis.vocabulary.code`) or configurable records
rather than hardcoded selections or constants.

### 2. Country Modules Extend Base

Country-specific functionality lives in `esmis_{feature}_{country}` modules (e.g.,
`esmis_grading_ph`, `esmis_student_ph`, `esmis_financial_aid_ph`). These modules use Odoo's
`_inherit` mechanism to extend base models with:

- **Government identifier types** — Philippine modules register PhilSys, LRN, and TIN as
  `esmis.identifier.type` records via data files.
- **Regulatory validations** — Philippine modules add consent checks (RA 10173), free tuition
  eligibility verification (RA 10931), and PWD/solo parent discount logic (RA 7277, RA 8972).
- **Government export formats** — CHED HEMIS export, eCAV integration, and UniFAST reporting
  live in Philippine modules only.
- **Grading scale defaults** — The Philippine 1.0–5.0 scale, GWA computation rules, INC
  resolution policies, and Latin honors thresholds ship as data files in `esmis_grading_ph`.
- **Country-specific fields** — Fields like `lrn` (Learner Reference Number) or
  `philsys_id` are added by country modules via `_inherit`, never in base.

### 3. Vocabulary-Driven Configuration

Grading scales, academic period types, degree types, student status codes, and other
country-varying classifications are vocabulary records (`esmis.vocabulary.code`), not hardcoded
`fields.Selection` choices or Python constants.

Country modules load country-specific vocabulary data via XML data files. This means:
- A Philippine deployment gets the CHED-recognized degree types.
- An Indonesian deployment could load DIKTI-recognized program types instead.
- Base modules reference vocabulary records by namespace URI, remaining agnostic to which
  country's values are loaded.

### 4. Mutual Exclusion via `excludes`

Country modules for the same feature declare mutual exclusion in their `__manifest__.py` using
the `excludes` key. For example:

```python
# esmis_grading_ph/__manifest__.py
{
    "name": "eSMIS Grading — Philippines",
    "depends": ["esmis_grading"],
    "excludes": ["esmis_grading_id", "esmis_grading_th"],
}
```

This prevents conflicting country localizations from being installed simultaneously. An
institution operates under one country's regulatory framework — mixing Philippine grading rules
with Indonesian ones would produce invalid results.

### 5. Language Support via Odoo i18n

UI translation uses Odoo's built-in internationalization system (PO files). Base modules ship
with English strings. Country modules include local language PO files where relevant (e.g.,
Filipino translations in `esmis_*_ph/i18n/tl.po`).

This separates two distinct concerns:
- **Localization** (country-specific business logic) — handled by country modules.
- **Translation** (UI language) — handled by PO files, orthogonal to localization.

A Philippine deployment might run the UI in English or Filipino. An Indonesian deployment might
run in Bahasa Indonesia. The translation layer is independent of which country module is
installed.

## Alternatives Considered

### Alternative A: Single Monolithic Module with Feature Flags

Put all country-specific logic in the base modules behind feature flags or system parameters
(e.g., `esmis.country = PH`).

**Pros:**
- Fewer modules to maintain
- All code in one place for each domain

**Cons:**
- Violates open/closed principle — adding a new country requires modifying base modules
- Conditional logic (`if country == 'PH'`) accumulates, making code harder to read and test
- Every deployment carries the code weight of every supported country
- Testing requires exercising every country path, even when only one applies
- Contributors must understand all countries' rules to avoid breaking unrelated country logic

**Decision:** Rejected — the maintenance burden grows multiplicatively with each new country.

### Alternative B: Separate Forks per Country

Each country maintains an independent fork of the entire eSMIS codebase.

**Pros:**
- Maximum freedom for each country's implementation
- No coordination overhead between country teams

**Cons:**
- Duplicates all shared logic (enrollment, scheduling, student management)
- Bug fixes and improvements must be manually ported between forks
- Community fragmentation — contributors cannot easily help across countries
- Defeats the purpose of an open-source project with shared governance

**Decision:** Rejected — the duplication cost makes this unsustainable beyond two countries.

## Consequences

### Positive

1. **Clean separation of concerns.** Base modules focus on universal SIS logic. Country modules
   focus on regulatory compliance and local conventions. Neither pollutes the other.
2. **Open to extension, closed to modification.** Adding support for a new country means
   creating new `esmis_*_{country}` modules — no changes to base modules required.
3. **Easier international contribution.** A contributor from Indonesia can build
   `esmis_grading_id` without needing to understand Philippine regulations, and without risk
   of breaking Philippine functionality.
4. **Vocabulary reuse.** The vocabulary system provides a uniform mechanism for country-varying
   classifications, reducing the amount of country-specific Python code needed.
5. **Testability.** Country modules can be tested independently. Base module tests verify
   country-neutral behavior. Country module tests verify country-specific behavior.

### Negative

1. **More modules to maintain.** Each country adds a set of `esmis_*_{country}` modules. For
   the Philippine localization alone, this means `esmis_student_ph`, `esmis_grading_ph`,
   `esmis_enrollment_ph`, `esmis_financial_aid_ph`, `esmis_billing_ph`, and integration modules
   (`esmis_philsys`, `esmis_hemis`, `esmis_ecav`).
2. **Base module design discipline.** Developers must resist the temptation to add "just this
   one Philippine thing" to a base module. Code review must enforce the country-neutral rule.
3. **Vocabulary data maintenance.** Each country's vocabulary data files must be kept accurate
   and up to date with regulatory changes. This is a documentation and governance challenge as
   much as a technical one.
4. **Cross-module coordination for country features.** A Philippine regulatory change might
   require updates across multiple `esmis_*_ph` modules. This is mitigated by keeping country
   modules focused and small.

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Philippine logic accidentally added to base modules | HIGH | MEDIUM | Code review checklist; lint rule flagging PH-specific imports in base modules |
| Country module `excludes` not maintained as new countries are added | MEDIUM | HIGH | CI check that all `esmis_*_{country}` modules for the same feature declare mutual exclusion |
| Vocabulary namespace collisions between countries | LOW | MEDIUM | Namespace URI convention includes country code (e.g., `urn:esmis:ph:grading-scale`) |
| Base module too generic to be useful without a country module | MEDIUM | MEDIUM | Ship Philippine modules as the reference implementation; document which country modules are needed for a functional deployment |

## Implementation Guidelines

### For Base Module Developers

- Use `esmis.vocabulary.code` for any value that could differ by country.
- Do not import or reference any `esmis_*_ph` module.
- Do not add fields, validations, or business logic specific to Philippine regulations.
- Provide hook methods (`_pre_*_hook()`, `_post_*_hook()`) where country modules may need to
  inject validation or computation logic.

### For Country Module Developers

- Follow the naming convention: `esmis_{feature}_{country_code}` (ISO 3166-1 alpha-2,
  lowercase).
- Use `_inherit` to extend base models — do not copy or redefine them.
- Load country-specific vocabulary data via XML data files in `data/`.
- Include `excludes` for all other known country variants of the same feature.
- Include PO files for local languages in `i18n/`.

### Module Naming Examples

| Base Module | Philippine Module | Indonesian Module |
|-------------|-------------------|-------------------|
| `esmis_grading` | `esmis_grading_ph` | `esmis_grading_id` |
| `esmis_student` | `esmis_student_ph` | `esmis_student_id` |
| `esmis_enrollment` | `esmis_enrollment_ph` | `esmis_enrollment_id` |
| `esmis_financial_aid` | `esmis_financial_aid_ph` | `esmis_financial_aid_id` |
| `esmis_billing` | `esmis_billing_ph` | `esmis_billing_id` |

## References

- [ADR-003: Vocabulary System](ADR-003-terminology-system.md) — vocabulary-driven configuration
- [ADR-011: Government Integration Architecture](ADR-011-government-integration-architecture.md) — country-specific integration patterns
- [ADR-012: Student Data Privacy — RA 10173](ADR-012-student-data-privacy-ra10173.md) — Philippine privacy compliance
- [ADR-015: Grading System Flexibility](ADR-015-grading-system-flexibility.md) — configurable grading scales
- [Odoo Python Rules](../../../.claude/rules/odoo-python.md) — country-specific code guidelines
- [Module Architecture Principles](../../principles/module-architecture.md)

---

**Document Version:** 1.0
**Last Updated:** 2026-03-09
