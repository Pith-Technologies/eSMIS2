# Multi-Campus Setup Guide

How to configure eSMIS when an institution operates more than one campus.

Each campus is modeled as a separate Odoo company. Data isolation, user access, and reporting scope are all controlled through the standard Odoo multi-company mechanisms.

---

## Creating Campus Companies

1. Go to **Settings → Companies → Create**.
2. Enter the campus name. Use a consistent convention, for example:
   - "University of X - Main Campus"
   - "University of X - Satellite Campus"
3. Set the address, contact details, and logo for the campus.
4. Configure the chart of accounts — either create a campus-specific chart or link to a shared one.

Repeat for each campus.

---

## User Assignment

Each user is granted access to one or more companies.

1. Go to **Settings → Users → [User]**.
2. Under **Allowed Companies**, add every campus the user may access.
3. Set **Default Company** to the user's primary campus.

| User type | Allowed companies |
|-----------|-------------------|
| Campus staff (registrar, admissions, finance) | Their campus only |
| System administrators | All campuses |
| VP Academic Affairs / President / CHED Reporter | All campuses (system-wide groups — see below) |

When a user switches the active company in the top bar, all records and menus reflect that campus.

---

## Security Group Setup

eSMIS uses two categories of groups for multi-campus deployments.

### Campus-scoped groups

Groups such as Registrar, Admissions Officer, and Campus Finance are scoped to the user's active company via `company_id` record rules. A user in these groups can only see and edit records belonging to their current company.

### System-wide groups

Groups such as VP Academic Affairs, President, and CHED Reporter bypass company isolation. Users in these groups see records across all campuses. Assign these groups with care.

Group inheritance follows Odoo's standard `implied_ids` pattern — a higher-level group automatically includes the permissions of lower-level groups in the same domain.

---

## Academic Configuration Per Campus

Some academic data is configured separately for each campus.

| Configuration | Scope |
|---------------|-------|
| Academic calendar dates (enrollment open/close, grading deadlines) | Per campus |
| Fee schedules (tuition, miscellaneous fees) | Per campus |
| Room and facility catalog | Per campus |
| Faculty assignments | Per campus (secondary assignment to another campus is allowed) |

To configure these, switch to the target campus using the company switcher, then navigate to the relevant menu.

---

## Shared Academic Data

Some academic data is shared across all campuses. These records carry no `company_id` and are visible system-wide regardless of the active company.

| Data | Shared |
|------|--------|
| Course catalog | Yes |
| Curriculum definitions | Yes |
| Grading system templates (campus may override defaults) | Yes |
| Vocabulary codes | Yes |

Do not set a `company_id` on these models. Adding company scoping to shared data will break cross-campus curriculum consistency.

---

## Testing a Multi-Campus Setup

After configuration, verify isolation and aggregation before going live.

### Create test users

Create at least three users:

- One user assigned only to Campus A
- One user assigned only to Campus B
- One system administrator assigned to all campuses

### Isolation checks

| Scenario | Expected result |
|----------|----------------|
| Campus A user views enrollment records | Sees only Campus A records |
| Campus A user switches to Campus B | Campus B records not visible (no access) |
| System admin views enrollment records | Sees records from all campuses |

### Aggregation checks

| Scenario | Expected result |
|----------|----------------|
| HEMIS export run by CHED Reporter | Aggregates data from all campuses into a single submission file |
| Financial consolidation report | Consolidates per Odoo multi-company accounting rules |

Run these checks against real test data, not just empty companies.

---

## Deep Dives

- `docs/principles/access-rights.md` — record rules, company_id scoping, system-wide groups
- `docs/principles/module-architecture.md` — which models carry company_id and which are shared
- `docs/guides/government-export-guide.md` — how HEMIS export aggregates multi-campus data
