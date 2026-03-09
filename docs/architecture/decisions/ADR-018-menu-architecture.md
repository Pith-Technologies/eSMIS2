# ADR-018: Menu Architecture

## Status

**Accepted**

**Date:** 2026-03-09

**Decision Owners:** Core Team

## Context

eSMIS needs a consistent, scalable menu structure across 15+ planned modules. As modules were
added incrementally, there was no shared convention for where configuration menus live, how
sequences are allocated, or when a module earns an independent top-level menu vs. nesting under
the main eSMIS app. This ADR establishes those conventions so all current and future modules
follow a single pattern.

## Design Principles

1. **`esmis_base` owns the structural scaffolding.** It defines the top-level "eSMIS" app menu
   (seq 80) and the Settings → eSMIS config menu. All other modules attach to this scaffolding;
   none may redefine it.

2. **Only `esmis_starter_ph` is `application=True`.** Domain modules are not standalone apps.
   Infrastructure modules (`esmis_security`, `esmis_vocabulary`) have no top-level menus at all.

3. **Academic workflow modules nest under the eSMIS main menu.** Modules that are part of the
   student lifecycle (student records, enrollment, curriculum, grading, scheduling, billing,
   financial aid) appear as children of `esmis_base.menu_esmis_main`.

4. **Cross-cutting modules get independent top-level menus.** Modules that serve a distinct
   audience or concern — billing, faculty, documents, alumni, consent, approvals, audit — own
   their own top-level menu entry with a dedicated sequence slot.

5. **Maximum 3 levels of nesting.** Top-level → section → item. A fourth level is a signal the
   section should become its own top-level menu.

6. **Configuration sits at seq 99 within each module's own menu** for domain-level configuration
   accessible to officers and managers. Superuser-only settings (technical knobs requiring
   `base.group_system`) go exclusively under Settings → eSMIS.

7. **Use "Registrar Office"** (not "Records Office") throughout all menu labels for the registrar
   audience.

## Decision

### Top-Level Menus

| Seq | Menu            | Owner              | Primary Audience          |
| --- | --------------- | ------------------ | ------------------------- |
| 80  | eSMIS           | `esmis_base`       | Registrar, Academic staff |
| 82  | eSMIS Accounting | `esmis_billing`   | Cashier, Accountant       |
| 84  | Faculty         | `esmis_faculty`    | Dean, HR                  |
| 86  | Documents       | `esmis_documents`  | Registrar Office          |
| 88  | Alumni          | `esmis_alumni`     | Alumni office             |
| 90  | Consent         | `esmis_consent`    | DPO, Compliance           |
| 92  | Approvals       | `esmis_approval`   | Approvers, Managers       |
| 94  | Audit Log       | `esmis_audit`      | DPO, Auditors             |

**Infrastructure modules with no top-level menus:**

- `esmis_security` — provides audit groups and record rules; the Audit Log menu belongs to
  `esmis_audit`, not here.
- `esmis_vocabulary` — configuration-only; its menus live under Settings → eSMIS.
- `esmis_starter_ph` — meta-package with no menus of its own.

### Complete Menu Trees

**eSMIS main (academic workflow):**

```
eSMIS (seq 80, esmis_base)                         [base.group_user]
├── Dashboard              (seq 1, future)
├── Students               (seq 10, esmis_student)
├── Enrollment             (seq 20, esmis_enrollment)
├── Curriculum             (seq 30, esmis_curriculum)
├── Scheduling             (seq 40, esmis_scheduling)
├── Grading                (seq 50, esmis_grading)
├── Academic Terms         (seq 60, esmis_academic_term)
└── Reports                (seq 70, esmis_reports)
```

**eSMIS Accounting (independent top-level):**

```
eSMIS Accounting (seq 82, esmis_billing)           [group_esmis_security_officer]
├── Assessments            (seq 10)
├── Payments               (seq 20)
├── Scholarships           (seq 30, esmis_financial_aid)
└── Configuration          (seq 99)                [group_esmis_security_manager]
    ├── Fee Structures     (seq 10)
    └── Aid Programs       (seq 20)
```

**Faculty (independent top-level):**

```
Faculty (seq 84, esmis_faculty)                    [group_esmis_security_officer]
├── Faculty Profiles       (seq 10)
├── Faculty Loading        (seq 20)
└── Configuration          (seq 99)                [group_esmis_security_manager]
    └── Designation Types  (seq 10)
```

**Documents (independent top-level):**

```
Documents (seq 86, esmis_documents)                [group_esmis_security_viewer]
├── Student Records        (seq 10)
└── Configuration          (seq 99)                [group_esmis_security_officer]
    └── Document Types     (seq 10)
```

**Alumni (independent top-level):**

```
Alumni (seq 88, esmis_alumni)                      [group_esmis_security_officer]
├── Alumni Records         (seq 10)
└── Configuration          (seq 99)                [group_esmis_security_manager]
    └── Alumni Programs    (seq 10)
```

**Consent (independent top-level):**

```
Consent (seq 90, esmis_consent)                    [group_esmis_security_viewer]
├── Consent Records        (seq 10)
└── Configuration          (seq 99)                [group_esmis_security_officer]
    └── Consent Scopes     (seq 10)
```

**Approvals (independent top-level):**

```
Approvals (seq 92, esmis_approval)                 [group_esmis_security_officer]
└── Configuration          (seq 99)                [group_esmis_security_manager]
    └── Approval Definitions (seq 10)
```

**Audit Log (independent top-level):**

```
Audit Log (seq 94, esmis_audit)                    [group_esmis_security_viewer]
├── Access Log             (seq 10)
└── Breach Log             (seq 20)
```

**Settings → eSMIS (superuser-only configuration):**

```
Settings > eSMIS (esmis_base.menu_esmis_root)      [base.group_system]
├── General Settings       (seq 10, res.config.settings, future)
├── Vocabularies           (seq 50, esmis_vocabulary)
│   ├── Vocabularies       (seq 10)
│   └── Codes              (seq 20)
└── Technical              (seq 90, future)
```

### XML ID Convention

| Menu Type                       | Pattern                               | Example                                           |
| ------------------------------- | ------------------------------------- | ------------------------------------------------- |
| eSMIS main menu                 | `menu_esmis_main`                     | `esmis_base.menu_esmis_main`                      |
| Settings → eSMIS                | `menu_esmis_root`                     | `esmis_base.menu_esmis_root`                      |
| eSMIS sub-menu (domain root)    | `menu_esmis_{domain}`                 | `esmis_student.menu_esmis_student`                |
| eSMIS sub-menu (item)           | `menu_esmis_{domain}_{item}`          | `esmis_student.menu_esmis_student_list`           |
| Independent top-level           | `menu_{domain}_root`                  | `esmis_consent.menu_consent_root`                 |
| Independent sub-menu (item)     | `menu_{domain}_{item}`                | `esmis_consent.menu_consent_records`              |
| Configuration parent            | `menu_{domain}_configuration`         | `esmis_consent.menu_consent_configuration`        |
| Configuration item              | `menu_{domain}_configuration_{feat}`  | `esmis_consent.menu_consent_configuration_scopes` |
| Settings config sub-menu        | `menu_esmis_configuration_{domain}`   | `esmis_vocabulary.menu_esmis_configuration_vocabularies` |

### Sequence Allocation

**Top-level sequences (global, reserved):**

| Seq | Menu             |
| --- | ---------------- |
| 80  | eSMIS            |
| 82  | eSMIS Accounting |
| 84  | Faculty          |
| 86  | Documents        |
| 88  | Alumni           |
| 90  | Consent          |
| 92  | Approvals        |
| 94  | Audit Log        |

**Under eSMIS main (academic workflow):**

| Seq | Section        |
| --- | -------------- |
| 1   | Dashboard      |
| 10  | Students       |
| 20  | Enrollment     |
| 30  | Curriculum     |
| 40  | Scheduling     |
| 50  | Grading        |
| 60  | Academic Terms |
| 70  | Reports        |

**Within any module's own menu:**

| Range  | Purpose                                      |
| ------ | -------------------------------------------- |
| 1–49   | Operational items (lists, forms, dashboards) |
| 50–79  | Reporting items                              |
| 99     | Configuration sub-menu (single, always last) |

**Settings → eSMIS:**

| Seq | Item             |
| --- | ---------------- |
| 10  | General Settings |
| 50  | Vocabularies     |
| 90  | Technical        |

### Security Group Assignments

| Menu                        | Minimum Group                         | Notes                                                       |
| --------------------------- | ------------------------------------- | ----------------------------------------------------------- |
| eSMIS (top-level)           | `base.group_user`                     | Shell only; children enforce their own groups               |
| eSMIS → Students            | `group_esmis_security_viewer`         |                                                             |
| eSMIS → Enrollment          | `group_esmis_security_officer`        |                                                             |
| eSMIS → Curriculum          | `group_esmis_security_officer`        |                                                             |
| eSMIS → Scheduling          | `group_esmis_security_officer`        |                                                             |
| eSMIS → Grading             | `group_esmis_security_officer`        | Grades are SPI; apply field-level access controls           |
| eSMIS → Academic Terms      | `group_esmis_security_officer`        |                                                             |
| eSMIS → Reports             | `group_esmis_security_viewer`         |                                                             |
| eSMIS Accounting (top)      | `group_esmis_security_officer`        |                                                             |
| eSMIS Accounting → Config   | `group_esmis_security_manager`        |                                                             |
| Faculty (top)               | `group_esmis_security_officer`        |                                                             |
| Faculty → Configuration     | `group_esmis_security_manager`        |                                                             |
| Documents (top)             | `group_esmis_security_viewer`         |                                                             |
| Documents → Configuration   | `group_esmis_security_officer`        |                                                             |
| Alumni (top)                | `group_esmis_security_officer`        |                                                             |
| Alumni → Configuration      | `group_esmis_security_manager`        |                                                             |
| Consent (top)               | `group_esmis_security_viewer`         | DPO needs read-only access to verify compliance             |
| Consent → Configuration     | `group_esmis_security_officer`        |                                                             |
| Approvals (top)             | `group_esmis_security_officer`        |                                                             |
| Approvals → Configuration   | `group_esmis_security_manager`        |                                                             |
| Audit Log (top)             | `group_esmis_security_viewer`         | Read-only for all non-superusers                            |
| Settings → eSMIS            | `base.group_system`                   | Superuser only; never expose to officers                    |

### Configuration Split

The configuration for each module is split into two locations depending on who needs access:

| Module              | Settings → eSMIS (superuser)            | Module → Configuration (officer/manager)                  |
| ------------------- | --------------------------------------- | --------------------------------------------------------- |
| `esmis_vocabulary`  | Vocabularies, Codes                     | —                                                         |
| `esmis_security`    | Security groups (via Odoo Settings)     | —                                                         |
| `esmis_consent`     | —                                       | Consent Scopes                                            |
| `esmis_approval`    | —                                       | Approval Definitions                                      |
| `esmis_student`     | —                                       | Student Categories, Identifier Types                      |
| `esmis_academic_term` | —                                     | Academic Terms, Periods                                   |
| `esmis_enrollment`  | —                                       | Enrollment Rules, Admission Types                         |
| `esmis_curriculum`  | —                                       | Program Types, Course Categories                          |
| `esmis_grading`     | —                                       | Grading Scales, Grade Equivalents                         |
| `esmis_scheduling`  | —                                       | Room Types, Schedule Templates                            |
| `esmis_billing`     | —                                       | Fee Structures, Payment Modes                             |
| `esmis_financial_aid` | —                                     | Aid Programs, Eligibility Rules                           |
| `esmis_faculty`     | —                                       | Designation Types, Loading Rules                          |
| `esmis_documents`   | —                                       | Document Types, Retention Policies                        |
| `esmis_alumni`      | —                                       | Alumni Programs, Tracking Rules                           |
| `esmis_audit`       | —                                       | — (audit log is read-only; no end-user config)            |
| `esmis_reports`     | —                                       | Report Templates, Export Formats                          |

**Rule:** If a configuration item requires `base.group_system` (superuser) to be meaningful or
safe, it belongs under Settings → eSMIS. Everything else that a registrar manager or DPO should
be able to configure without IT involvement belongs in the module's own Configuration sub-menu.

## Developer Guidelines

### Decision Tree: Where Does My Menu Go?

```
Is this module part of the academic workflow
(student lifecycle: admissions → enrollment → grading → records)?
  YES → Nest under esmis_base.menu_esmis_main
  NO →
    Does it serve a distinct audience or concern
    (billing, faculty, documents, alumni, consent, audit)?
      YES → Own independent top-level menu (application=False)
      NO (infrastructure, foundational config) →
        Settings → eSMIS only (base.group_system)
```

### Template: Nesting Under eSMIS Main

Use this pattern for academic workflow modules (e.g., `esmis_grading`):

```xml
<!-- views/menus.xml -->
<odoo>
  <!-- Section root under eSMIS main -->
  <menuitem
      id="menu_esmis_grading"
      name="Grading"
      parent="esmis_base.menu_esmis_main"
      sequence="50"
      groups="esmis_security.group_esmis_security_officer"
  />

  <!-- Operational items -->
  <menuitem
      id="menu_esmis_grading_list"
      name="Grade Sheets"
      parent="menu_esmis_grading"
      action="action_esmis_grade_sheet"
      sequence="10"
      groups="esmis_security.group_esmis_security_officer"
  />

  <!-- Configuration (always seq 99, always last) -->
  <menuitem
      id="menu_esmis_grading_configuration"
      name="Configuration"
      parent="menu_esmis_grading"
      sequence="99"
      groups="esmis_security.group_esmis_security_manager"
  />
  <menuitem
      id="menu_esmis_grading_configuration_scales"
      name="Grading Scales"
      parent="menu_esmis_grading_configuration"
      action="action_esmis_grading_scale"
      sequence="10"
      groups="esmis_security.group_esmis_security_manager"
  />
</odoo>
```

### Template: Independent Top-Level Menu

Use this pattern for cross-cutting modules (e.g., `esmis_consent`):

```xml
<!-- views/menus.xml -->
<odoo>
  <!-- Independent top-level -->
  <menuitem
      id="menu_consent_root"
      name="Consent"
      sequence="90"
      web_icon="esmis_consent,static/description/icon.png"
      groups="esmis_security.group_esmis_security_viewer"
  />

  <!-- Operational items -->
  <menuitem
      id="menu_consent_records"
      name="Consent Records"
      parent="menu_consent_root"
      action="action_esmis_consent_record"
      sequence="10"
      groups="esmis_security.group_esmis_security_viewer"
  />

  <!-- Configuration (always seq 99, always last) -->
  <menuitem
      id="menu_consent_configuration"
      name="Configuration"
      parent="menu_consent_root"
      sequence="99"
      groups="esmis_security.group_esmis_security_officer"
  />
  <menuitem
      id="menu_consent_configuration_scopes"
      name="Consent Scopes"
      parent="menu_consent_configuration"
      action="action_esmis_consent_scope"
      sequence="10"
      groups="esmis_security.group_esmis_security_officer"
  />
</odoo>
```

### Template: Settings → eSMIS

Use this pattern for superuser-only configuration (e.g., `esmis_vocabulary`):

```xml
<!-- views/menus.xml -->
<odoo>
  <!-- Child of esmis_base.menu_esmis_root (Settings > eSMIS) -->
  <menuitem
      id="menu_esmis_configuration_vocabularies"
      name="Vocabularies"
      parent="esmis_base.menu_esmis_root"
      sequence="50"
      groups="base.group_system"
  />
  <menuitem
      id="menu_esmis_configuration_vocabularies_list"
      name="Vocabularies"
      parent="menu_esmis_configuration_vocabularies"
      action="action_esmis_vocabulary"
      sequence="10"
      groups="base.group_system"
  />
  <menuitem
      id="menu_esmis_configuration_vocabularies_codes"
      name="Codes"
      parent="menu_esmis_configuration_vocabularies"
      action="action_esmis_vocabulary_code"
      sequence="20"
      groups="base.group_system"
  />
</odoo>
```

### Pre-Merge Checklist

Before merging any menu changes:

- [ ] XML IDs follow the naming convention table above
- [ ] Sequences match the allocated range for that menu's position
- [ ] `groups=` is set on every `<menuitem>` — no menu is unguarded
- [ ] Configuration items are at seq 99 and always the last child
- [ ] Superuser-only configuration is under Settings → eSMIS (`base.group_system`)
- [ ] Maximum 3 levels of nesting (top → section → item)
- [ ] Independent top-level menus have `web_icon` set
- [ ] No module modifies another module's `<menuitem>` definitions
- [ ] Menu labels use "Registrar Office" not "Records Office"

## Consequences

**Positive:**

- Consistent navigation experience across all modules — users can predict where to find things.
- Sequence gaps (e.g., 80, 82, 84...) leave room to insert new modules without renumbering.
- Clear separation of superuser config (Settings → eSMIS) from domain config (Module →
  Configuration) reduces the risk of accidental privilege escalation.
- The decision tree removes ambiguity for new module authors.

**Negative:**

- Modules already deployed with non-conforming menu structures will need a migration step to
  reassign parent menus and update sequences.
- Independent top-level menus increase the icon count in the home screen — this is intentional
  for audience separation but may feel cluttered on small deployments. Starter modules can address
  this by conditionally hiding menus via record rules scoped to installed modules.

## Alternatives Considered

**All config under Settings → eSMIS (previous approach):** Simpler for developers, but forces
non-superusers (registrar managers, DPOs) to navigate into Odoo's technical Settings area to
manage domain config. Rejected because it violates least-privilege and creates a confusing UX for
non-technical staff.

**Everything nested under one eSMIS top-level menu:** Keeps the home screen clean but results in
menus 4+ levels deep for configuration items and mixes audiences (cashiers and registrars share
the same top-level). Rejected because it violates the 3-level nesting rule and makes role-based
visibility harder to reason about.

## References

- [Module Architecture Principles](../../principles/module-architecture.md)
- [Module Visibility](../../principles/module-visibility.md)
- [Access Rights Management](ADR-001-access-rights-management.md)
- [Foundation Module Strategy](ADR-016-foundation-module-strategy.md)
