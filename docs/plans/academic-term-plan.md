# Build Plan: `esmis_academic_term`

Status: DRAFT — awaiting sign-off on the five decisions in section 3. Nothing
here has been built. Flip this to ACCEPTED on sign-off and to COMPLETE when the
module ships, as `phase-1-plan.md` and `phase-1b-plan.md` do.

Detailed implementation blueprint for the last foundation module. A developer
reading this plan should not need another document to build it; where it
contradicts an older spec, this plan wins and section 2 says why.

**Created:** 2026-09-12
**Phase:** 1C — Remaining Foundation, as allocated in `README.md`. This document
cites that label; it does not coin one. A plan is named for the work it does,
because a phase label is a roadmap property that moves — Phase 1B was invented
after the fact, and Phase 1 grew from four modules to nine.
**Branch:** `feat/esmis-academic-term`
**Prerequisite:** Phase 1A and 1B modules, all nine of which are built.

## 1. What this branch is for

`esmis_academic_term` is the tenth module and the last of the foundation layer.
Nine modules exist today (`esmis_base`, `esmis_vocabulary`, `esmis_security`,
`esmis_consent`, `esmis_approval`, `esmis_address`, `esmis_student`, `esmis_ph`,
`esmis_starter_ph`). This module is the one thing standing between Phase 1 and
Phase 2: `esmis_enrollment`, `esmis_scheduling`, `esmis_grading`, `esmis_faculty`
and `esmis_reports` all list it as a dependency, and `esmis.student.course.history`
already has a deferred `term_id` waiting for it (phase-1-plan Decision 3).

Nothing depends on it yet, which makes it cheap to get right and expensive to get
wrong: every field name chosen here is referenced by five unwritten modules.

## 2. The central finding: three specs disagree

`esmis_academic_term` is specified in three places, written at different times,
and no two agree:

- `docs/architecture/data-model-registry.md` — Layer 1 entry, field list only
- `docs/plans/phase-1-plan.md` §5 — the fullest spec: models, state machine, ACL
  matrix, record rules, acceptance criteria
- `docs/guides/tutorial-first-module.md` — 1,156 lines that build this exact
  module as a teaching example, and say outright that the real one comes later

This must be resolved before a line of code is written — otherwise the module
contradicts whichever document the next contributor happens to read.

| Concern | `data-model-registry.md` | `phase-1-plan.md` §5 | `tutorial-first-module.md` | Ruling |
|---|---|---|---|---|
| Term type (semester/trimester/summer) | absent | absent | `type_id` → vocabulary, required | **Tutorial.** `odoo-python.md` forbids static selections for classifications that follow an external standard; the `urn:esmis:vocabulary:academic-period-type` vocabulary already ships six codes in `esmis_vocabulary` and is currently referenced by nothing |
| Enrollment window field names | `enrollment_open_date` / `enrollment_close_date` | same | `enrollment_start` / `enrollment_end` | **Registry/phase-1.** Two of three sources agree, and `open`/`close` says what the dates mean |
| `add_drop_deadline` | yes | yes + constraint chain | absent | **Include.** It is a real CHED-relevant deadline and the constraint chain is specified |
| `state` machine | 5 states | 5 states + transition rules | absent | **Include.** Five modules will branch on it; adding it later means a migration |
| `is_current` | absent | absent | stored Boolean on both models | **Include as computed, not stored** — see D3 |
| `company_id` | plain field | `esmis.campus.aware` mixin | plain field | **Mixin.** It exists at `esmis_security/models/mixins/campus_aware.py` and carries the documented record-rule pattern |
| `mail.thread` | — | yes | no | **Yes**, matching `esmis.consent` |
| Security files | — | categories / privileges / groups / ACL / rules | single `security_groups.xml` | **phase-1-plan**, which matches `esmis_student/security/` on disk |
| Term data | demo only | demo only | `data/academic_term_data.xml` | **Demo only.** Terms are institution data, not seed data |
| Models per file | — | `academic_year.py` + `academic_term.py` | one file | **Two files**, per phase-1-plan |

Two further corrections the three specs all miss:

- **Dependencies.** phase-1-plan says `base`, `esmis_security`. `module-setup.md`
  requires every module to depend on `esmis_base`, and the vocabulary field pulls in
  `esmis_vocabulary`, and `mail.thread` pulls in `mail`. Correct set:
  `["esmis_base", "mail", "esmis_vocabulary", "esmis_security"]` — the same shape
  `esmis_student` uses.
- **Settings-admin inheritance.** `security.md` makes it REQUIRED that a module
  defining groups links its highest group into `base.group_system.implied_ids`.
  No spec mentions it; `esmis_student` does it. Without it, Settings admins lose
  access to terms.

## 3. Decisions needing sign-off

| # | Decision | Recommendation |
|---|---|---|
| **D1** | Adopt the reconciled spec in section 4 as the single source of truth, superseding the other three where they differ | **Yes.** Record the reconciliation in this document; update the registry and roadmap in the same PR rather than leaving three live specs |
| **D2** | `tutorial-first-module.md` teaches building this exact module and says "the real module will be built later". Once the module exists, the tutorial is 1,156 lines of near-duplicate code that will silently drift | **Rewrite the tutorial's code blocks to match the shipped module** and add a line pointing at the real source. Keeping a deliberately different teaching version is how a contributor learns the wrong `type_id` domain. Alternative, if the rewrite is too much for this PR: retarget the tutorial at a throwaway module name (`esmis_example_term`) — but do it in this PR either way, not later |
| **D3** | `is_current` as a stored Boolean (tutorial) invites two current terms per campus and a nightly job nobody wrote | **Computed, non-stored, from `date_start`/`date_end` vs today**, per campus. If a stored override is genuinely needed later, add it then with a constraint |
| **D4** | Does `esmis.academic.year` get a `company_id`? | **No.** Registry, phase-1-plan and tutorial all agree years are institution-wide; the campus variation lives on the term. This is the one thing all three specs agree on — do not revisit it mid-build |
| **D5** | Ship the state machine now, with no consumer? | **Yes.** Adding `state` after `esmis_enrollment` exists means a data migration across a live term table. The transition guard is ~20 lines |

If D2 is deferred, everything else still proceeds; it is the only item that can
be split into a follow-up PR without leaving the module incoherent.

## 4. Target design (reconciled)

### 4.1 Manifest

```python
{
    "name": "eSMIS Academic Term",
    "version": "19.0.1.0.0",
    "category": "eSMIS/Core",
    "summary": "Academic years and campus-scoped terms with enrollment windows",
    "author": "Pith Technologies",
    "website": "",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": [],
    "depends": ["esmis_base", "mail", "esmis_vocabulary", "esmis_security"],
    "data": [
        "security/categories.xml",
        "security/privileges.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "views/academic_year_views.xml",
        "views/academic_term_views.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/demo_academic_terms.xml"],
    "auto_install": False,
    "application": False,
    "installable": True,
}
```

### 4.2 `esmis.academic.year`

Institution-wide. `_inherit = ["mail.thread"]`, `_order = "date_start desc"`.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | required, e.g. "AY 2025-2026"; SQL `UNIQUE(name)` |
| `date_start` / `date_end` | Date | required |
| `term_ids` | One2many | `esmis.academic.term`, inverse `academic_year_id` |
| `is_current` | Boolean | computed, not stored — today falls inside the range |
| `active` | Boolean | default True |

Constraints: `date_end > date_start`; no two active years may overlap.
No `company_id`, no record rules (D4).

### 4.3 `esmis.academic.term`

`_inherit = ["esmis.campus.aware", "mail.thread"]`, `_order = "date_start desc"`.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | required |
| `academic_year_id` | Many2one | required, index, `ondelete="restrict"` |
| `type_id` | Many2one | `esmis.vocabulary.code`, required, `ondelete="restrict"`, domain `[('namespace_uri', '=', 'urn:esmis:vocabulary:academic-period-type')]` |
| `company_id` | Many2one | from `esmis.campus.aware` |
| `date_start` / `date_end` | Date | required |
| `enrollment_open_date` / `enrollment_close_date` | Datetime | optional |
| `add_drop_deadline` | Date | optional |
| `state` | Selection | `draft`/`enrollment_open`/`in_progress`/`grading`/`closed`, default `draft`, `tracking=True` |
| `is_current` | Boolean | computed, not stored |
| `active` | Boolean | default True |

Constraints, in this order:
1. `date_end > date_start`
2. `date_start >= academic_year_id.date_start` and `date_end <= academic_year_id.date_end`
3. `enrollment_open_date < enrollment_close_date` when both set
4. `enrollment_close_date <= add_drop_deadline` when both set
5. `add_drop_deadline <= date_end` when set
6. no two active terms at the same campus in the same year may overlap
7. SQL `UNIQUE(name, company_id)`

State machine — strictly forward, no backward transitions:

```
draft → enrollment_open → in_progress → grading → closed
```

One `action_*` method per transition, each raising `UserError` naming the current
state and the only legal next state. A generic `_ALLOWED_TRANSITIONS` dict keyed by
current state keeps the guard in one place.

### 4.4 Security

Following `esmis_student/security/` exactly:

- `categories.xml` — `category_esmis_academic_term`, "eSMIS / Academic Calendar"
- `privileges.xml` — `privilege_academic_calendar` (`res.groups.privilege`)
- `groups.xml` — `group_academic_term_viewer` → `officer` → `manager`, chained with
  `Command.link()` in `implied_ids`, plus the REQUIRED
  `base.group_system` `implied_ids` extension linking `group_academic_term_manager`
- `ir.model.access.csv` — `base.group_system` full CRUD row first for both models;
  `base.group_user` read-only on both (terms are reference data other modules read);
  officer 1,1,1,0; manager 1,1,1,1
- `record_rules.xml` — `<odoo noupdate="1">`, campus isolation on `esmis.academic.term`
  using the mixin's documented domain
  `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` for
  `base.group_user`, plus `[(1, '=', 1)]` for `group_academic_term_manager`.
  No rule on `esmis.academic.year`.

### 4.5 Views and menus

Per ADR-018, which allocates this module a slot by name:

```
eSMIS (esmis_base.menu_esmis_main)
└── Academic Terms   (seq 60)   menu_esmis_academic_term
    ├── Terms        (seq 10)   menu_esmis_academic_term_terms
    └── Academic Years (seq 20) menu_esmis_academic_term_years
```

`groups=` on every menuitem (`group_academic_term_viewer`). No Configuration
sub-menu — this module has nothing an officer configures; its vocabulary lives
under Settings → eSMIS and belongs to `esmis_vocabulary`.

Views: list + form for both models, search view on the term with a default
"Current year" filter, `statusbar` in the term form header with the four action
buttons, chatter on both forms. State must carry icon **and** colour
(`odoo-xml.md`): `draft` secondary/`fa-pencil`, `enrollment_open` info/`fa-unlock`,
`in_progress` primary/`fa-play`, `grading` warning/`fa-pencil-square-o`,
`closed` success/`fa-lock`.

### 4.6 Demo data

One year "AY 2025-2026" (2025-06-01 → 2026-05-31) and three terms on the main
campus: 1st Semester (Jun–Oct, `semester`), 2nd Semester (Nov–Mar, `semester`),
Summer 2026 (Apr–May, `summer`). Terms reference vocabulary codes by XML ID
(`esmis_vocabulary.code_academic_period_type_semester`). A second campus is NOT
created in demo data — the campus-isolation test creates its own, and demo data
that invents a campus confuses the starter module.

## 5. Build order

Each step is one commit. Tests first in every step, per the hard rule — the test
is written, run, and seen to fail before the model code exists.

| Step | Deliverable | Proves |
|---|---|---|
| 0 | Skeleton: `__init__.py`, `__manifest__.py`, `pyproject.toml` (whool), empty packages, `readme/DESCRIPTION.md` stub. Module installs empty | `./esmis test esmis_academic_term` reaches the "no tests of its own" path, not an install error |
| 1 | `test_academic_year.py` → `models/academic_year.py` | creation, date constraint, overlap constraint, `is_current`, `UNIQUE(name)` |
| 2 | `test_academic_term.py` → `models/academic_term.py` (fields, mixin, `type_id`) | creation, `type_id` domain rejects a code from another vocabulary, `company_id` defaults to `self.env.company` |
| 3 | Constraint tests → the six constraint methods | each constraint rejects its own violation and accepts the boundary case |
| 4 | `test_term_state_machine.py` → transitions | every legal hop succeeds; every illegal hop (including backward) raises `UserError` |
| 5 | `test_campus_isolation.py` → `security/*` | officer at campus B cannot read campus A's term; manager can; `base.group_user` can read years; officer cannot unlink |
| 6 | `views/*`, `menus.xml` | module installs with views; `./esmis start` renders the form and the statusbar |
| 7 | `demo/demo_academic_terms.xml` | demo install creates 1 year + 3 terms with correct `type_id` and dates inside the year |
| 8 | Paperwork (section 8) | — |

Steps 1–4 are pure model work and can be done in one sitting; step 5 is where the
defects historically live and deserves its own review pass.

### Agent routing

- Step 5 security design and review → `security-auditor`
- Steps 1–4 and 7 test authorship → `test-author`, then `odoo-developer` implements
- Step 6 form layout → `ux-expert`
- Final pass → `code-reviewer`, then `verify-module`
- `privacy-officer` is NOT needed: this module stores no PII. Terms are
  institutional configuration. Say so explicitly in the PR so the omission reads
  as a decision rather than an oversight.

## 6. File inventory

```
esmis_academic_term/
├── __init__.py
├── __manifest__.py
├── pyproject.toml                      # whool, copied from esmis_address
├── models/{__init__.py, academic_year.py, academic_term.py}
├── security/{categories.xml, privileges.xml, groups.xml,
│             ir.model.access.csv, record_rules.xml}
├── views/{academic_year_views.xml, academic_term_views.xml, menus.xml}
├── demo/demo_academic_terms.xml
├── tests/{__init__.py, test_academic_year.py, test_academic_term.py,
│          test_term_state_machine.py, test_campus_isolation.py}
└── readme/DESCRIPTION.md
```

Fifteen new files plus paperwork. No existing module is modified — the menu
attaches to `esmis_base.menu_esmis_main` by reference, which ADR-018 permits and
requires.

## 7. Verification

```sh
./esmis test esmis_academic_term          # must report tests run, 0 failed, 0 errors
./esmis audit-security                    # ACL/record-rule audit
./esmis audit-modules                     # project compliance
pre-commit run --files <changed files>    # 37 hooks incl. gitleaks, pylint_odoo, odoo-check-acl
```

Then `/verify-tests` (no test removed or weakened), and `./esmis start` to render
the term form and walk one term draft → closed by hand.

`docs/runbooks/security-audit.md` is the procedure behind the two audit commands
and gates module completion — follow it at step 5 rather than reading the raw
output cold. `docs/guides/module-development.md` (TDD workflow, manifest template,
directory layout) and `docs/guides/testing-guide.md` are the authorities for how
each step is carried out; this plan says what to build, they say how.

CI will pick the module up automatically — `scripts/detect_modules.py` builds the
matrix from changed files, so no list needs editing. Coverage must clear
`fail_under = 85` measured over the module alone.

## 8. Paperwork this PR must carry

| File | Change |
|---|---|
| `README.md` | module table: `esmis_academic_term` 🔜 Next → ✅ Complete; layer diagram: add the `*` marking it as built; the "nine modules" prose becomes ten |
| `CHANGELOG.md` | the module entry under `[Unreleased]`, with the test count. This plan's own entry is already there under "Documentation — Plans" |
| `docs/architecture/data-model-registry.md` | both models Planned → Implemented; add `type_id` and `is_current`; correct the enrollment field names |
| `docs/architecture/implementation-roadmap.md` | line 150 status, and the §"Order 3" spec block |
| `docs/plans/phase-1-plan.md` | §5 gains a pointer to this document as the superseding spec (do not silently rewrite history there) |
| `docs/guides/tutorial-first-module.md` | D2 |
| `docs/plans/academic-term-plan.md` | this file, status DRAFT → ACCEPTED, then COMPLETE when the module ships (the convention `phase-1-plan.md` and `phase-1b-plan.md` set) |
| `esmis_academic_term/readme/DESCRIPTION.md` | 25–60 lines, the seven sections `module-setup.md` requires (overview, Key Capabilities, Key Models, Configuration, UI Location, Security, Dependencies) — note the existing `esmis_address` DESCRIPTION predates that rule and is not the template to copy |

No new ADR. ADR-018 already allocates the menu and ADR-016 already settles the
foundation strategy; the field-set reconciliation belongs in this plan document.

## 9. Traps, each seen in this repository

1. **A module that ships test files but runs none fails the CLI** (`esmis`, since
   #35). The usual cause is a test file not imported in `tests/__init__.py`.
2. **`assertRaises` does not take a tuple** — one exception type per assertion.
3. **`with_context(tracking_disable=True)` in `setUpClass`**, or `mail.thread`
   turns every create into a message.
4. **Record rules do not apply to the superuser.** The isolation test must create
   real users with `group_ids` and `company_ids` set, as
   `esmis_student/tests/test_campus_isolation.py` does.
5. **The `base.group_system` CRUD row must be the first data row** of the ACL CSV,
   for both models.
6. **`base.group_user` needs read on both models** — this is reference data that
   `esmis_enrollment` will read from every enrollment form.
7. **Vocabulary lookups are ormcached** (`esmis.vocabulary.code._get_code_id`). In
   tests use `VocabCode.get_code("urn:esmis:vocabulary:academic-period-type", "semester")`
   rather than searching by hand.
8. **The vocabulary namespace is `urn:esmis:vocabulary:academic-period-type`** —
   note the `vocabulary:` segment. `urn:esmis:education-level` (no segment) is the
   older shape used elsewhere; copying that pattern silently yields an empty domain.
9. **`groups=` on every menuitem.** `esmis_student/views/menus.xml` omits it on
   leaf items; that is precedent, not permission.
10. **Two rules disagree on the Configuration sequence** — `odoo-xml.md` says 90 and
    a child of the app root, `module-setup.md` and ADR-018 say 99 inside the module's
    menu. Irrelevant here (no Configuration menu), but worth raising as a workspace
    fix so the next module does not have to decide.
11. **`testing.md` still says `./scripts/test_single_module.sh`** — the CLI was
    renamed to `./esmis test` in #32. A workspace-side rule fix, not a repo one.
12. **`docs/plans/` has no `README.md`** while `principles/`, `guides/`,
    `runbooks/`, `research/` and `decisions/` all do. The gap arrived with the
    split in #6/#7. This PR adds the fourth file to that directory and is the
    natural place to close it, if the directory's owner agrees.

## 10. Effort

Roughly one focused day: half a day for steps 1–4 (models and their tests are
mechanical once section 4 is settled), a couple of hours for step 5 (security,
where care pays), an hour for views, and an hour for paperwork. D2 adds two to
three hours if the tutorial is rewritten rather than retargeted.

The work is nearly all serial because each step's tests depend on the previous
step's model. The one thing that parallelises cleanly is the tutorial
reconciliation (D2), which touches no module file.
