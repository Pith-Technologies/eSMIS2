# ADR-023: Multi-Campus Architecture

## Status

**Accepted** - Implementation pending

**Date:** 2026-03-09
**Decision Owners:** Core Team

## Context

Philippine universities are commonly multi-campus systems. The UP System has 8 constituent universities, DLSU operates multiple campuses, and similar structures exist across many private and state universities. Each campus may have independent academic calendars, fee schedules, room inventories, and enrollment quotas, while the parent institution must produce consolidated reports for CHED, accreditation bodies (AACCUP, PAASCU, PACUCOA), and internal governance.

### Problems to Solve

1. **Campus isolation**: Students, faculty, rooms, sections, and fees must be scoped per campus to prevent data leakage between campuses
2. **Consolidated reporting**: CHED HEMIS, FASTECH, and institutional dashboards require system-wide aggregation across campuses
3. **Shared master data**: Curriculum, course catalog, grading system templates, and vocabulary data must be maintained once and reused across campuses to avoid drift
4. **Financial separation**: Each campus may be a separate cost center or legal entity with its own chart of accounts

### Options Evaluated

- Custom multi-tenancy schema (separate databases per campus)
- Single database with campus discriminator column and manual filtering
- Odoo's native multi-company architecture (`res.company` per campus)

## Decision

**Use Odoo's native multi-company architecture with one `res.company` record per campus.**

### Core Principles

1. **One company per campus**: Each campus is represented as a `res.company` record. The parent institution (e.g., "UP System") is the root company.
2. **Shared academic master data**: Curriculum plans, course catalog entries, grading system templates, and vocabulary terms are not company-scoped. They are defined once at the system level and referenced by all campuses.
3. **Campus-scoped transactional data**: Sections, room assignments, enrollment records, fee schedules, grade sheets, and disciplinary records carry `company_id` and are filtered per campus by default record rules.
4. **System-level users for reporting**: Users with CHED reporting or system administration roles receive cross-company access. This is granted via group membership, not by bypassing record rules with `sudo()`.
5. **No custom multi-tenancy code**: The architecture relies entirely on Odoo's built-in company switching, financial consolidation, and inter-company transaction mechanisms.

### Data Scoping Rules

| Data Type | Scoping | Rationale |
|-----------|---------|-----------|
| `res.company` (campus) | Root-level | One per campus |
| Curriculum / course catalog | System-wide | Maintained centrally, reused across campuses |
| Grading system templates | System-wide | Uniform grading scales defined once |
| Vocabulary / code tables | System-wide | Shared controlled vocabularies |
| Academic sections | Campus-scoped | Sections belong to a campus offering |
| Room inventory | Campus-scoped | Physical rooms are per campus |
| Enrollment records | Campus-scoped | Student enrolled at a specific campus |
| Fee schedules | Campus-scoped | Tuition and fees may differ per campus |
| Grade sheets | Campus-scoped | Grades issued by the campus section |
| Payroll / HR | Campus-scoped | Employees are assigned to a campus |
| Chart of accounts | Campus-scoped | Financial separation per Odoo's standard |

### Standard Model Pattern

Every new domain model that holds campus-scoped data must include the following field and a corresponding record rule:

```python
company_id = fields.Many2one(
    'res.company',
    string='Campus',
    required=True,
    default=lambda self: self.env.company,
)
```

The record rule restricts visibility to the user's active company:

```xml
<record id="rule_{model}_company" model="ir.rule">
    <field name="name">Campus isolation: {Model}</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">
        [('company_id', 'in', company_ids)]
    </field>
</record>
```

### Inter-Campus Enrollment

When a student from one campus takes a course at another campus (cross-enrollment, common in the UP System), a dedicated cross-enrollment workflow creates linked enrollment records in both campuses. The requesting campus holds the student record; the hosting campus holds the section enrollment. A cross-campus coordinator user with access to both companies manages the handoff.

## Consequences

### Positive

- Leverages Odoo's tested multi-company infrastructure with no custom multi-tenancy code to maintain
- Native financial consolidation reports work without modification
- Campus switching in the UI uses Odoo's standard company selector
- Inter-company invoicing and cost allocation use Odoo's built-in inter-company rules
- CHED system-level users can run consolidated reports using Odoo's standard `allowed_company_ids` mechanism

### Negative

- Cross-campus queries must explicitly include company filtering; ad-hoc SQL reports must be reviewed for missing filters
- Inter-campus enrollment requires a dedicated workflow module (`esmis_cross_enrollment`) rather than a simple section assignment
- Shared master data and campus-scoped data must be clearly distinguished in every module — ambiguity here causes isolation failures
- System administrators must understand Odoo's multi-company rules to correctly configure user company access

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Developer forgets `company_id` on new model | MEDIUM | HIGH | Module audit script checks for missing `company_id` on transactional models |
| Shared master data accidentally scoped | LOW | MEDIUM | Code review checklist; architect approval for any `company_id` on master data models |
| Cross-campus query returns all campuses | MEDIUM | HIGH | Record rule tests in CI; integration tests assert campus isolation |
| User assigned to wrong campus | LOW | MEDIUM | Onboarding checklist; company assignment reviewed by IT admin role |

## Implementation Notes

1. Every new transactional model adds `company_id` with the default lambda and a company record rule as shown above.
2. System-level reporting users (CHED coordinator, system admin) are added to the `esmis_security.group_system_admin` group, which carries `res.groups` `share` = False and explicit multi-company access.
3. Shared master data models (curriculum, course catalog, grading templates) explicitly omit `company_id` and omit company record rules. This is a deliberate design choice, not an oversight.
4. The `esmis_cross_enrollment` module, when implemented, must use `with_company()` context manager to create enrollment records in the hosting campus.
5. Module audit tooling (`./odoo-project audit-modules`) will be extended to flag transactional models missing `company_id`.

## References

- [Odoo 19 Multi-Company Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/multicompany.html)
- ADR-004: Access Rights Management Architecture
- ADR-011: Data Classification System

---

**Document Version:** 1.0 **Last Updated:** 2026-03-09 **Next Review:** After first multi-campus pilot deployment
