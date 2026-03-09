# ADR-026: Financial Aid Modeling

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

Philippine universities administer multiple overlapping financial aid programs:

- **Free tuition (RA 10931):** Covers all Filipino students enrolled in SUCs and LUCs
- **TES (Tertiary Education Subsidy):** Up to PHP 20,000 tuition + PHP 40,000 living allowance for qualified students in private HEIs
- **DOST-SEI scholarships:** Merit-based scholarships administered by the Department of Science and Technology
- **PWD discount (RA 7277 / RA 10754):** Mandatory 20% discount for persons with disability
- **Solo parent dependent scholarship (RA 8972 / RA 11861):** Educational benefits for dependents of solo parents
- **Institutional scholarships:** University-funded programs with varying eligibility criteria

These programs can stack — a student may simultaneously benefit from free tuition and a living allowance subsidy — but stacking is not always permitted. Certain combinations are mutually exclusive (e.g., TES and full DOST scholarship), and some programs impose cumulative caps. UniFAST and COA require a complete audit trail of all award decisions and disbursements.

### Problems to Solve

1. No unified model for program definitions, eligibility rules, and per-student awards
2. Eligibility evaluation is manual and error-prone, leading to missed qualifiers or improper awards
3. Discount and subsidy application order is not standardized, producing inconsistent assessment amounts
4. Audit trail requirements for government compliance are unmet

## Decision

### 1. Two-Model Design

Financial aid is represented by two models:

- **`esmis.financial.aid.program`** — program definition (name, funding source, governing law, eligibility rules, per-term benefit amounts, stacking policy)
- **`esmis.financial.aid.award`** — per-student, per-term award record (program reference, student, term, status, approved amount, disbursement records)

### 2. Rule-Based Eligibility

Each `esmis.financial.aid.program` record stores eligibility criteria as Odoo domain expressions evaluated against the student record. Criteria include: citizenship, GWA threshold, household income bracket, PWD status flag, solo parent dependent flag, and prior baccalaureate degree check.

This approach makes eligibility rules inspectable, version-controlled, and testable without code changes.

### 3. Batch Eligibility Evaluation

Eligibility evaluation runs as a batch job per term using `queue_job`. The job evaluates all enrolled students against all active programs and produces candidate lists. Officers review and approve candidates before awards are created.

### 4. Discount and Subsidy Application Order

When computing a student's assessed fees, discounts and subsidies are applied in this order:

1. Free tuition (RA 10931) — applied first, may reduce tuition to zero
2. Government subsidies (TES, DOST-SEI) — applied to remaining balance
3. Institutional scholarships — applied after government programs
4. PWD discount (RA 7277 / RA 10754) and solo parent discount (RA 8972 / RA 11861) — applied last

This order is fixed by regulation and is not configurable.

### 5. Philippine-Specific Programs in a Dedicated Module

Philippine-specific program definitions, eligibility rule defaults, and RA references live in the `esmis_financial_aid_ph` module. The base `esmis_financial_aid` module contains the generic models and workflows, keeping the core portable.

### 6. Audit Trail for UniFAST and COA Compliance

All award state changes (draft → evaluated → approved → disbursed) and any modifications to approved amounts are recorded in an immutable audit log. The log captures the acting user, timestamp, previous state, and reason for change.

## Consequences

### Positive

- Flexible enough to model any present or future subsidy program without schema changes
- Rule-based eligibility criteria are testable in isolation and auditable by regulators
- Batch evaluation scales to large student populations without blocking the UI
- Application order enforcement eliminates inconsistent fee computation

### Negative

- Stacking rules and mutual exclusivity logic require careful testing across program combinations; edge cases will emerge in production
- Institutions with highly customized programs must configure eligibility domains correctly — misconfiguration may silently qualify or disqualify students

## Implementation Notes

- Eligibility rules are stored as Odoo domain expressions on `esmis.financial.aid.program.eligibility_domain` (type `Char`). Evaluation uses `self.env['esmis.student'].search(domain)`.
- Batch evaluation runs via `queue_job`; job failure does not affect existing approved awards.
- Award state machine: `draft` → `evaluated` → `approved` → `disbursed`. Disbursement records link to account journal entries.
- Stacking policy field on `esmis.financial.aid.program`: `stackable`, `exclusive`, or `capped` (with a `max_combined_amount` field).
- Philippine program defaults (TES amounts, PWD discount rate) are provided as data files in `esmis_financial_aid_ph/data/`.

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09
