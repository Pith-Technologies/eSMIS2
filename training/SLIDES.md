# Developer Training — Slide Outline

> **Author**: Edwin Gonzales **Last Updated**: March 4, 2026
>
> Structured outline for building a presentation deck. Each section lists slides with speaker notes / key talking
> points. Timing estimates are per-section; adjust to audience pace.

---

## Section 1: Odoo 19 Overview (~10 slides)

### Slide 1-1: What Is Odoo?

- Open-source ERP / business application platform
- Modular: install only what you need
- Python backend, PostgreSQL database, JS/OWL frontend
- Huge ecosystem: 30k+ community modules

### Slide 1-2: What's New in Odoo 19

- **Command API** replaces tuple syntax for One2many / Many2many writes
  - Old: `(0, 0, {...})`, `(4, id, 0)`, `(6, 0, [ids])`
  - New: `Command.create({...})`, `Command.link(id)`, `Command.set([ids])`
- `privilege_id` field on `res.groups` — links functional groups to a `res.groups.privilege` record (used alongside
  `category_id`, not a replacement)
- `group_expand` signature changed to 2 parameters: `(self, stages, domain)`
- XPath `hasclass()` function — use instead of `@class="..."` selectors
- Upgraded JS framework (OWL 2.x)

### Slide 1-3: Module Architecture — Bird's Eye

- Addons path: directories that Odoo scans for modules
- Each module = one directory with `__manifest__.py`
- Module = self-contained feature unit (models + views + security + tests)

### Slide 1-4: Module Directory Structure

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py
├── views/
├── security/
│   └── ir.model.access.csv
├── data/
├── demo/
├── tests/
│   └── __init__.py
└── readme/
    └── DESCRIPTION.md
```

### Slide 1-5: `__manifest__.py` — Module Metadata

- `name`, `version`, `category`, `depends`, `data`, `license`
- `application` flag: creates a top-level menu entry
- `auto_install`: installs automatically when all `depends` are present
- Version format: `19.0.1.0.0`

### Slide 1-6: The ORM — Object-Relational Mapping

- Python classes → database tables
- `_name` = table identity (e.g. `"my.model"` → `my_model`)
- `_inherit` = extend an existing model
- `_description` = human-readable label

### Slide 1-7: Field Types

| Type                | Example       | Notes                            |
| ------------------- | ------------- | -------------------------------- |
| `Char`              | Name, code    | `required`, `index`, `translate` |
| `Text` / `Html`     | Description   | Rich text with `Html`            |
| `Integer` / `Float` | Quantities    | `digits` for precision           |
| `Boolean`           | Flags         | Convention: `is_*`, `has_*`      |
| `Date` / `Datetime` | Timestamps    |                                  |
| `Selection`         | State machine | Fixed choices                    |
| `Many2one`          | FK reference  | `comodel_name`, `ondelete`       |
| `One2many`          | Reverse FK    | `inverse_name`                   |
| `Many2many`         | Join table    |                                  |

### Slide 1-8: Computed Fields & Decorators

- `@api.depends('field')` — recompute when dependency changes
- `@api.constrains('field')` — validate on write
- `@api.onchange('field')` — UI-only live feedback
- `@api.model` — class-level method (no `self` recordset)

### Slide 1-9: CRUD & Business Methods

- `create(vals_list)` — insert records
- `write(vals)` — update records
- `unlink()` — delete records
- `search(domain)` / `browse(ids)` — read records
- Custom action methods: `action_confirm()`, `action_cancel()`

### Slide 1-10: Inheritance Patterns

- **Classical inheritance** (`_inherit` without `_name`): extend existing model in-place
- **Prototype inheritance** (`_inherit` + `_name`): copy model definition into new table
- **Delegation** (`_inherits`): composition — link to parent record via FK
- Most common in practice: classical (`_inherit = "res.partner"`)

### Slide 1-11: Views — How Users See Your Models

- Models define _data_; views define _presentation_
- Views are XML records stored in the database — not templates on disk
- Odoo resolves the "best" view for a model automatically (inheritance, priority)
- Three view types you'll use constantly: **form**, **list**, **search**

| View Type   | Purpose                       | Key Element                       |
| ----------- | ----------------------------- | --------------------------------- |
| Form        | Create / edit a single record | `<form>`, `<sheet>`, `<notebook>` |
| List (tree) | Browse multiple records       | `<list>`, `<field>` columns       |
| Search      | Filter and group the list     | `<search>`, `<filter>`, `<group>` |

Other view types: kanban, calendar, pivot, graph, gantt, map, activity

### Slide 1-12: Anatomy of a Form View

```xml
<form>
    <header>
        <!-- Status bar + action buttons -->
        <button name="action_confirm" string="Confirm" type="object"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <group>
            <group string="Left Column">
                <field name="code"/>
            </group>
            <group string="Right Column">
                <field name="date"/>
            </group>
        </group>
        <notebook>
            <page string="Details">
                <field name="description"/>
            </page>
        </notebook>
    </sheet>
</form>
```

- `<header>` — status bar and action buttons only (minimal)
- `<sheet>` — the white card area; all editable content goes here
- `<group>` nesting — two `<group>` inside a `<group>` = two-column layout
- `<notebook>` + `<page>` — tabbed sections for organizing fields

---

## Section 1B: Python for Odoo Developers (~8 slides)

### Slide 1B-1: Why Python?

- Odoo is built on Python — backend, ORM, business logic, tests, CLI tools
- Python handles: model definitions, controllers, wizards, cron jobs, migrations
- JS/OWL handles: frontend UI components (not covered in this training)
- Everything you write today is Python (+ XML for views and data)

### Slide 1B-2: Python Concepts Odoo Relies On

| Concept               | How Odoo Uses It                                                 |
| --------------------- | ---------------------------------------------------------------- |
| Classes & inheritance | Every model is a class; `_inherit` maps to Python MRO            |
| Decorators            | `@api.depends`, `@api.constrains`, `@api.onchange`, `@api.model` |
| Context managers      | `with self.assertRaises(...)`, `with self.env.cr.savepoint()`    |
| List comprehensions   | Filtering records, building vals lists                           |
| Dunder methods        | `__init__.py` for package imports, `_name` / `_inherit` for ORM  |
| `*args` / `**kwargs`  | Controller routes, method overrides                              |

### Slide 1B-3: Classes & Inheritance in Odoo

```python
# Every Odoo model is a Python class
class Course(models.Model):
    _name = "sis.course"          # DB table identity
    _description = "Course"       # Human label

# Extending an existing model — Python MRO handles method resolution
class ResPartner(models.Model):
    _inherit = "res.partner"      # No new table — extends in place
    is_student = fields.Boolean()
```

- `models.Model` = persistent (stored in DB)
- `models.TransientModel` = temporary (wizards, cleaned up automatically)
- `models.AbstractModel` = no table, mixin only

### Slide 1B-4: Decorators That Matter

```python
@api.depends("enrollment_ids.state")
def _compute_completed_count(self):
    """Recomputes when dependency changes — cached until then."""

@api.constrains("student_number")
def _check_student_number(self):
    """Runs on write — raises ValidationError if invalid."""

@api.onchange("is_student")
def _onchange_is_student(self):
    """UI-only — sets defaults live in the form, not saved yet."""
```

- Decorators = metadata telling the ORM _when_ to call your method
- `@api.depends` → computed fields (stored or virtual)
- `@api.constrains` → validation (server-side, on save)
- `@api.onchange` → UI responsiveness (client-side feel, server-side logic)

### Slide 1B-5: `self` Is a Recordset

```python
def action_enroll(self):
    # self can be ONE record or MANY — always iterate
    for record in self:
        if record.state != "draft":
            raise UserError(_("Cannot enroll from state %s.") % record.state)
        record.state = "enrolled"
```

- `self` is not a single object — it's a **recordset** (0, 1, or many records)
- `self.ensure_one()` — asserts exactly one record (raises if not)
- Always loop with `for record in self:` for multi-record safety
- `self.filtered(lambda r: r.state == 'draft')` — filter without looping

### Slide 1B-6: Context, Environment & `sudo()`

```python
self.env                         # Current environment
self.env.user                    # Current user
self.env.company                 # Current company
self.env.context                 # Dict of context flags
self.with_context(key=value)     # New env with extra context
self.sudo()                      # Bypass access rights (use sparingly!)
self.with_user(user)             # Switch to another user's permissions
```

- `env` carries: user, company, database cursor, context flags
- `sudo()` is powerful but dangerous — bypasses all ACLs
- In tests: use `with_user()` to verify security works for each role
- Context flags: `tracking_disable=True` (skip mail), `default_*` (form defaults)

### Slide 1B-7: Domains — Odoo's Query Language

```python
# Domains are lists of (field, operator, value) tuples
[("is_student", "=", True)]
[("state", "in", ["draft", "enrolled"])]
[("enrollment_date", ">=", "2026-01-01")]

# Boolean operators prefix the conditions they combine
["&", ("is_student", "=", True), ("program", "!=", False)]
["|", ("state", "=", "completed"), ("state", "=", "dropped")]
```

- Used in: `search()`, view filters, record rules, field domains
- Implicit `&` (AND) between conditions
- Operators: `=`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `not in`, `like`, `ilike`, `child_of`
- `"&"`, `"|"`, `"!"` for boolean logic (Polish notation)

### Slide 1B-8: Testing with `unittest` + Odoo

```python
from odoo.tests.common import TransactionCase

class TestCourse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Course = cls.env["sis.course"]

    def test_create_course(self):
        course = self.Course.create({"name": "CS101", "code": "CS101"})
        self.assertEqual(course.name, "CS101")

    def test_duplicate_rejected(self):
        self.Course.create({"name": "CS101", "code": "CS101"})
        with self.assertRaises(Exception):
            self.Course.create({"name": "CS102", "code": "CS101"})
```

- `TransactionCase` — each test runs in a transaction, rolled back after
- `HttpCase` — for testing web controllers (starts real HTTP server)
- `setUpClass` creates shared test data (runs once per class)
- Standard `unittest` assertions: `assertEqual`, `assertTrue`, `assertRaises`

### Slide 1B-9: Why Tests Matter

- **Odoo modules are deeply interconnected** — a change in one model can break views, security, workflows, and other
  modules that depend on it
- Without tests, you only find out something is broken when a user reports it in production
- With tests, you find out **in seconds**, before the code leaves your machine

| Without Tests                 | With Tests                                         |
| ----------------------------- | -------------------------------------------------- |
| "It works on my screen"       | Proof it works — on every screen, every time       |
| Afraid to refactor            | Refactor with confidence — tests catch regressions |
| Manual QA after every change  | Automated verification in seconds                  |
| Bugs found by users           | Bugs found by developers                           |
| Hours debugging in production | Minutes debugging locally                          |

- **TDD (Test-Driven Development)** — write the test _first_, then the code
  - Forces you to think about _what_ before _how_
  - The test is both specification and verification
  - In this lab, every phase writes tests before implementation
- Tests are not extra work — they are **insurance** that pays for itself on the first bug they catch

---

## Section 2: Development Environment (~12 slides)

### Slide 2-1: What Is Docker?

- A tool that packages applications into **containers** — lightweight, isolated environments
- A container bundles the app + its dependencies + its configuration into one unit
- "Works on my machine" → "Works in the container" (same everywhere)
- Not a VM — containers share the host OS kernel, so they start in seconds

```
┌──────────────────────────────────┐
│  Your Machine (Host OS)          │
│  ┌────────────┐ ┌────────────┐  │
│  │ Container  │ │ Container  │  │
│  │  Odoo 19   │ │ PostgreSQL │  │
│  │  Python    │ │  18        │  │
│  │  deps      │ │            │  │
│  └────────────┘ └────────────┘  │
│         Shared OS Kernel         │
└──────────────────────────────────┘
```

### Slide 2-2: Docker Key Concepts

| Concept            | What It Is                                   | Analogy                           |
| ------------------ | -------------------------------------------- | --------------------------------- |
| **Image**          | Read-only blueprint                          | A recipe                          |
| **Container**      | Running instance of an image                 | A dish cooked from the recipe     |
| **Dockerfile**     | Instructions to build an image               | The recipe card                   |
| **Volume**         | Persistent storage outside the container     | A fridge — data survives restarts |
| **Network**        | Communication channel between containers     | A kitchen intercom                |
| **Docker Compose** | Define multi-container apps in one YAML file | A meal plan                       |

- `docker compose up` — start all services defined in `docker-compose.yml`
- `docker compose down` — stop and remove containers
- Our `./odoo-project` CLI wraps these commands for convenience

### Slide 2-3: Project Architecture Diagram

```
┌──────────────────────────────────────────┐
│  Host Machine                            │
│                                          │
│  ┌─────────────┐    ┌─────────────────┐  │
│  │ odoo-app    │    │ db              │  │
│  │ (ui profile)│◄──►│ PostgreSQL 18   │  │
│  │ Port 8069   │    │ (PostGIS)       │  │
│  └─────────────┘    └─────────────────┘  │
│  ┌─────────────┐    ┌─────────────────┐  │
│  │ odoo-dev    │    │ test            │  │
│  │ (dev profile│    │ (one-off)       │  │
│  │  dynamic pt)│    │ isolated tests  │  │
│  └─────────────┘    └─────────────────┘  │
│                                          │
│  Volumes: postgres_data, odoo_data       │
│  Network: odoo-net (bridge)              │
└──────────────────────────────────────────┘
```

### Slide 2-4: Docker Compose Services

| Service    | Profile   | Port         | Purpose                    |
| ---------- | --------- | ------------ | -------------------------- |
| `db`       | (always)  | —            | PostgreSQL 18 with PostGIS |
| `odoo-app` | `ui`      | 8069 (fixed) | Stable UI development      |
| `odoo-dev` | `dev`     | dynamic      | Dev with auto-reload       |
| `test`     | (one-off) | —            | Isolated test runner       |

- Your custom modules are mounted read-only into the container
- Database persists in a Docker volume

### Slide 2-5: The `odoo-project` CLI

- Single entry point for all development tasks
- Python-based, cross-platform (macOS, Linux, Windows WSL)
- Wraps Docker Compose commands with project conventions
- Tab completion via `./odoo-project activate`
- Command aliases: `t` = test, `s` = start, `b` = build, `l` = logs

### Slide 2-6: Essential CLI Commands

```bash
./odoo-project doctor          # Check prerequisites
./odoo-project build           # Build Docker image
./odoo-project start           # Start (http://localhost:8069)
./odoo-project stop            # Stop services
./odoo-project stop -v -y      # Stop + delete volumes (clean slate)
./odoo-project test my_module  # Run tests (isolated container)
./odoo-project logs -f         # Follow live logs
./odoo-project shell           # Interactive Odoo shell
```

### Slide 2-7: More CLI Commands

```bash
./odoo-project resetdb --demo=base  # Fresh DB with demo data
./odoo-project update               # Upgrade changed modules
./odoo-project lint                  # Run linters (changed files)
./odoo-project sql "SELECT 1"       # Run SQL directly
./odoo-project url -o               # Open Odoo in browser
./odoo-project status               # Show running containers
```

### Slide 2-8: What Are Pre-Commit Hooks?

- **Pre-commit** is a framework for managing git hook scripts
- Hooks run **automatically** before each `git commit` — if they fail, the commit is blocked
- Purpose: catch problems _before_ they enter the codebase, not after

```
You run: git commit -m "feat: add student model"
            │
            ▼
  ┌─────────────────────┐
  │  Pre-commit hooks    │
  │  ✓ Linter (ruff)    │
  │  ✓ Formatter (ruff)  │
  │  ✓ XML (prettier)   │
  │  ✗ Syntax error!    │ ← Blocks the commit
  └─────────────────────┘
            │
            ▼
  Fix the issue, then commit again
```

- Configured in `.pre-commit-config.yaml` at the project root
- Install once: `pre-commit install` (runs automatically after that)

### Slide 2-9: Our Pre-Commit Hooks

| Hook                | Language      | What It Checks                                            |
| ------------------- | ------------- | --------------------------------------------------------- |
| **ruff**            | Python        | Linting — unused imports, bad patterns, style issues      |
| **ruff-format**     | Python        | Formatting — consistent indentation, line length, spacing |
| **prettier**        | XML, MD, JSON | Formatting — consistent markup and data files             |
| Custom Odoo linters | Python/XML    | Project-specific rules (naming, security patterns)        |

- Run manually on specific files: `pre-commit run --files path/to/file.py`
- Run all hooks on all files: `pre-commit run --all-files`
- Or use the CLI shortcut: `./odoo-project lint`
- Auto-fix most issues: `./odoo-project fix-lint <module>`

### Slide 2-10: What Is GitHub?

- **Git** = version control system (tracks changes to files locally)
- **GitHub** = cloud platform that hosts Git repositories and adds collaboration tools
- Key GitHub features we use:

| Feature                 | Purpose                                 |
| ----------------------- | --------------------------------------- |
| **Repositories**        | Central home for project code           |
| **Branches**            | Isolated lines of development           |
| **Pull Requests (PRs)** | Propose changes, get code review, merge |
| **Issues**              | Track bugs, features, tasks             |
| **Actions (CI/CD)**     | Automated testing on every push         |

### Slide 2-11: GitHub Workflow

```
main ──────●──────────────●──────── (stable, always deployable)
            \            / merge PR
             \          /
  feature ────●────●────●           (your work branch)
              ↑    ↑    ↑
           commit commit commit
```

1. **Branch** from `main`: `git checkout -b feat/add-student-model`
2. **Commit** changes incrementally (conventional commits)
3. **Push** to GitHub: `git push -u origin feat/add-student-model`
4. **Open a PR** — reviewers check the code, CI runs tests
5. **Merge** into `main` after approval
6. **Delete** the feature branch (it served its purpose)

### Slide 2-12: Conventional Commits

| Prefix      | When to Use                           | Example                                       |
| ----------- | ------------------------------------- | --------------------------------------------- |
| `feat:`     | New feature                           | `feat: add student model`                     |
| `fix:`      | Bug fix                               | `fix: validate student number on save`        |
| `test:`     | Adding tests                          | `test: add enrollment state transition tests` |
| `docs:`     | Documentation                         | `docs: update README with setup steps`        |
| `refactor:` | Code restructure (no behavior change) | `refactor: extract enrollment validation`     |
| `chore:`    | Maintenance                           | `chore: update Docker base image`             |

- Imperative mood, present tense: "add student model" not "added student model"
- Subject line explains the _why_ — the diff shows the _what_
- Pre-commit hooks enforce code quality before the commit goes through

### Slide 2-13: Configuration File

`~/.odoo-project.toml` — personal defaults:

```toml
default_profile = "dev"     # dev or ui
default_demo = "base"       # demo profile
default_db = "odoo"         # database name
```

---

## Section 3: Claude Code Integration (~17 slides)

### Slide 3-1: What Is Claude Code?

- AI-powered CLI for software engineering
- Understands your entire project context
- Reads files, writes code, runs commands
- Not a chatbot — a development partner with tool access

### Slide 3-2: Project Configuration Layers

```
CLAUDE.md                    ← Always loaded (project rules)
.claude/rules/*.md           ← Auto-loaded by file path
.claude/agents/*.md          ← Specialized subagents
.claude/commands/*.md        ← Slash commands (/implement, /commit)
.claude/settings.json        ← Team-shared permissions
.claude/settings.local.json  ← Personal permissions (not committed)
```

### Slide 3-3: Path-Scoped Rules

Rules auto-load when you edit matching files — no manual activation:

| Rule File         | Triggers On                   | Covers                                  |
| ----------------- | ----------------------------- | --------------------------------------- |
| `odoo-python.md`  | `models/*.py`, `wizard/*.py`  | Naming, Command API, error handling     |
| `odoo-xml.md`     | `views/*.xml`, `data/*.xml`   | View syntax, form layout, accessibility |
| `security.md`     | `security/*`                  | ACLs, groups, record rules              |
| `testing.md`      | `tests/*.py`                  | Coverage targets, test patterns         |
| `module-setup.md` | `__manifest__.py`, `readme/*` | Visibility, architecture                |

### Slide 3-4: What Are Agents?

- An **agent** is a specialized Claude Code instance with a focused role and specific tool access
- Think of them as **team members** — each has expertise, responsibilities, and boundaries
- Defined in `.claude/agents/*.md` — a markdown file that describes the agent's persona, knowledge, and rules
- Claude Code launches agents as **subprocesses** — they work independently and report back

```
You (the developer)
  │
  ├── ask Claude Code to implement a feature
  │
  └── Claude Code orchestrates agents:
        ├── @odoo-developer  → writes the code
        ├── @code-reviewer   → reviews for security & quality
        ├── @ux-expert       → checks form layouts
        └── @verify-module   → runs tests, confirms it works
```

### Slide 3-5: Our Project Agents

| Agent              | Model  | Tools                   | Role                                                              |
| ------------------ | ------ | ----------------------- | ----------------------------------------------------------------- |
| `@odoo-developer`  | Sonnet | Read, Write, Edit, Bash | The builder — writes models, views, security, tests               |
| `@code-reviewer`   | Opus   | Read, Grep, Glob, Bash  | The reviewer — checks quality, security, Odoo 19 compliance       |
| `@ux-expert`       | Opus   | Read, Glob, Grep        | The designer — validates form layouts, UX patterns                |
| `@code-simplifier` | Sonnet | Read, Edit, Glob, Grep  | The cleaner — reduces complexity after implementation             |
| `@verify-module`   | Sonnet | Read, Bash, Glob, Grep  | The tester — installs module, runs tests, scans for anti-patterns |

Key differences:

- **Sonnet** agents (faster, cheaper) → implementation and verification tasks
- **Opus** agents (deeper reasoning) → review and design tasks
- **Tool access varies** — `@code-reviewer` cannot write files (read-only review), `@odoo-developer` has full access

### Slide 3-6: Agent Anatomy — What's in the File?

Each `.claude/agents/*.md` file has three parts:

```markdown
---
name: odoo-developer # How you reference it
description: Expert Odoo 19 developer... # When Claude should use it
tools: Read, Write, Edit, Glob, Grep, Bash # What it can do
model: sonnet # Which AI model powers it
---

You are an expert Odoo 19 developer. # Persona / system prompt

## Required Reading Before Any Code Changes # Rules and constraints

- naming-conventions.md
- access-rights.md ...

## Development Standards # Detailed instructions

- Use `_logger` not `print()`
- Every model needs ACLs ...
```

- The **frontmatter** (between `---`) configures capabilities
- The **body** is the agent's knowledge — project rules, checklists, patterns
- Agents inherit project context (`CLAUDE.md`, rules) but get their own focused instructions

### Slide 3-7: How Agents Work Together — `/implement`

The `/implement` command orchestrates multiple agents in phases:

```
Phase 1: Analyze
  └── Claude reads the plan, breaks into tasks

Phase 2: Implement
  ├── @odoo-developer → writes models, security, views
  └── @ux-expert      → reviews UI (runs in parallel)

Phase 3: Self-Verify
  └── Claude runs linters and tests, fixes failures

Phase 4: Simplify
  └── @code-simplifier → cleans up the code

Phase 5: Expert Review (all in parallel)
  ├── @code-reviewer  → security, naming, compliance
  ├── @ux-expert      → UI patterns (if views changed)
  └── @verify-module  → end-to-end installation test

Phase 6: Final Verification
  └── Claude reruns tests, confirms clean state
```

- Agents that don't depend on each other run **in parallel** (Phase 5)
- Critical/important issues from review are fixed before completion
- The whole cycle is automated — you start it and review the result

### Slide 3-8: How Agents Work Together — `/expert-review`

The `/expert-review` command launches 3 agents in parallel:

```
/expert-review
  │
  ├── @code-reviewer   → "Are there security gaps? Naming violations?
  │                       Odoo 19 anti-patterns?"
  │
  ├── @ux-expert       → "Do forms follow the project layout conventions?
  │                       Are there accessibility issues?"
  │
  └── @verify-module   → "Does the module install? Do all tests pass?
                          Any print() or bare except: in the code?"
```

Output is a consolidated report:

- **Critical** issues → must fix before merge
- **Important** issues → should fix
- **Suggestions** → nice to have

### Slide 3-9: Agent Best Practices

**When to use agents:**

- `/implement` for any feature touching >2 files — agents handle the full TDD cycle
- `/expert-review` before every PR — catches issues you might miss
- `/verify-tests` after any subagent work — confirms no tests were weakened

**How to get the best results:**

- **Plan before implementing** — agents follow plans much better than vague instructions
- **Be specific about what you want** — "add a `student_number` field to `res.partner` with a uniqueness constraint"
  beats "add a field"
- **Review agent output** — agents are good but not infallible; read the code they produce
- **Fix critical review findings** — don't ignore `@code-reviewer` warnings about missing ACLs or security gaps

**What agents can't do:**

- Make architectural decisions for you — use Plan mode for that
- Replace understanding — you need to know _what_ you're building; agents help with _how_
- Guarantee correctness — always run tests (`./odoo-project test`) as the final verification

### Slide 3-10: Slash Commands

| Command          | When           | What It Does                               |
| ---------------- | -------------- | ------------------------------------------ |
| `/implement`     | After planning | Full TDD workflow with subagents           |
| `/verify-tests`  | After changes  | Check test integrity (catch removed tests) |
| `/commit`        | Before commit  | Conventional commit with staged changes    |
| `/pr`            | After commit   | Create GitHub Pull Request                 |
| `/expert-review` | For review     | Parallel review from 3 perspectives        |
| `/analyze`       | Debugging      | Deep analysis without code changes         |

### Slide 3-11: Why Plan Before You Build?

- Code is expensive to change — a wrong direction costs hours of rework
- Plans are cheap to change — a wrong sentence costs seconds to fix
- **Without a plan**: Claude jumps straight to code, may solve the wrong problem, touch the wrong files, or miss edge
  cases
- **With a plan**: Claude researches first, proposes an approach, you review and correct _before_ any code is written

| Scenario                  | Without Plan                                                                     | With Plan                                                                             |
| ------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| "Add enrollment tracking" | Claude guesses the model structure, writes code, you find it's wrong, start over | Claude proposes models + fields + relations, you adjust, then one-shot implementation |
| "Fix the security error"  | Claude patches the symptom, breaks something else                                | Claude analyzes the root cause, identifies all affected files, fixes correctly        |
| "Add a portal page"       | Claude creates controllers + templates, misses record rules                      | Plan includes controller, templates, AND security — nothing forgotten                 |

- Plans also survive **context compression** — if a conversation gets long, Claude's earlier research may be lost, but a
  written plan persists as a file
- Rule of thumb: **if it touches more than 2 files, plan first**

### Slide 3-12: Plan Mode — How It Works

Enter Plan mode: press **Shift+Tab twice** (or type `plan` in the prompt)

```
┌─────────────────────────────────────────────────┐
│  PLAN MODE                                      │
│                                                 │
│  Claude CAN:                                    │
│    ✓ Read files (Glob, Grep, Read)              │
│    ✓ Search the codebase                        │
│    ✓ Analyze existing code                      │
│    ✓ Propose an implementation approach         │
│                                                 │
│  Claude CANNOT:                                 │
│    ✗ Write or edit files                        │
│    ✗ Run commands                               │
│    ✗ Make any changes to the codebase           │
│                                                 │
│  Exit: Shift+Tab twice (or approve the plan)    │
└─────────────────────────────────────────────────┘
```

- Plan mode is **read-only** — Claude explores but can't break anything
- You stay in control — review, adjust, and approve before implementation starts
- Plans are written to a file so you can annotate them with inline comments

### Slide 3-13: Anatomy of a Good Plan

A plan Claude produces typically includes:

```markdown
## Context

What we're building and why.

## Files Modified

| File                                        | Action | What Changes                 |
| ------------------------------------------- | ------ | ---------------------------- |
| sis_student/models/res_partner.py           | Edit   | Add enrollment_ids field     |
| sis_enrollment/models/enrollment.py         | Create | New model with state machine |
| sis_enrollment/security/ir.model.access.csv | Create | ACLs for 3-tier access       |

## Implementation Steps

1. Write tests for enrollment model
2. Create sis.enrollment model with state machine
3. Add security groups and ACLs
4. Create form and list views
5. Add menu under SIS root

## Design Decisions

- Use Many2one to res.partner (not a new student model)
- State machine: draft → enrolled → completed / dropped
- SQL constraint for unique (student, course) pairs

## Open Questions

- Should we add a portal view? (deferred to Phase 4)
```

**What makes a plan good:**

- **File paths** are explicit — you know exactly what will be touched
- **Steps are ordered** — dependencies are clear
- **Trade-offs are stated** — you can challenge decisions before code exists
- **Questions are surfaced** — ambiguity is resolved before implementation, not during

### Slide 3-14: Plan Mode in Practice

**Example workflow:**

```
You:    "I want to add a course prerequisites feature — courses
         that must be completed before enrolling in another course."

         [Enter Plan mode: Shift+Tab twice]

Claude: Researches sis_course model, sis_enrollment model,
        existing views, security setup...

Claude: Proposes plan:
        - Add self-referential M2M on sis.course (prerequisite_ids)
        - Add validation in sis.enrollment.action_enroll()
        - Update course form view with prerequisites tab
        - Add tests for prerequisite enforcement

You:    "Looks good, but also show prerequisites on the portal
         detail page."

Claude: Updates plan to include portal template changes.

You:    [Approve plan → Exit plan mode]

Claude: Implements exactly what was agreed.
```

**Tips for working with plans:**

- **Ask Claude to write the plan to a file** — this makes it persistent and reviewable
- **Annotate with inline comments** — Claude will address your notes
- **Iterate** — a good plan may take 2-3 rounds; that's faster than rewriting code
- **Don't skip planning for "simple" features** — many "simple" features turn out to touch security, views, and tests

### Slide 3-15: The TDD Workflow with Claude Code

```
1. Plan mode (Shift+Tab twice)     → Design approach
2. /implement                       → Write tests first, then code
3. /verify-tests                    → Confirm no tests removed/weakened
4. /expert-review                   → Security + UX + verification
5. /commit                          → Conventional commit
6. /pr                              → Open Pull Request
```

Planning is step 1 for a reason — everything downstream depends on it.

### Slide 3-16: Working with Claude Code — Tips

- **Be specific**: "Add a `student_number` field to `res.partner`" > "add a field"
- **Plan first**: Use Plan mode for anything touching >2 files
- **Trust but verify**: Always run tests after AI-generated code
- **Read the rules**: `.claude/rules/` files are summaries; deep dives in `docs/principles/`
- **Iterate**: Claude Code handles multi-step workflows — use `/implement` for full cycles

### Slide 3-17: Demo — Live Claude Code Session

- Live demo: create a simple model using Claude Code
- Show Plan mode → `/implement` → `/verify-tests` → `/commit`
- Highlight how rules auto-load based on file being edited

---

## Section 4: Template Architecture (~6 slides)

### Slide 4-1: Module Layers

```
Layer 3 ── DOMAIN EXTENSIONS  (sis_reports, sis_api)
               ↓
Layer 2 ── DOMAIN CORE        (sis_student, sis_course, sis_enrollment)
               ↓
Layer 1 ── FOUNDATION         (sis_security, sis_vocabulary)
               ↓
Layer 0 ── ODOO CORE          (base, hr, stock, account, portal)
```

- Dependencies flow **downward** only — never upward or circular
- Foundation modules are shared infrastructure
- Domain modules implement business logic
- Extensions add cross-cutting features (reports, APIs)

### Slide 4-2: Naming Conventions

| Element          | Pattern                       | Example                        |
| ---------------- | ----------------------------- | ------------------------------ |
| Module directory | `{prefix}_{domain}`           | `sis_student`                  |
| Python model     | `{prefix}.{domain}`           | `sis.course`                   |
| Boolean fields   | `is_*` / `has_*`              | `is_student`, `has_enrollment` |
| Many2one fields  | `{model}_id`                  | `course_id`, `student_id`      |
| One2many / M2M   | `{model}_ids`                 | `enrollment_ids`               |
| Date fields      | `*_date`                      | `enrollment_date`              |
| XML IDs          | descriptive, no abbreviations | `menu_sis_configuration`       |

### Slide 4-3: The `init` Command — Bootstrapping

```bash
./odoo-project init sis "Student Information System"
```

This transforms the template:

| From                   | To                           |
| ---------------------- | ---------------------------- |
| `esmis_vocabulary/`      | `sis_vocabulary/`            |
| `esmis.vocabulary`       | `sis.vocabulary`             |
| `model_esmis_vocabulary` | `model_sis_vocabulary`       |
| `eSMIS`            | `Student Information System` |

- Renames directories, updates all references in `.py`, `.xml`, `.csv`, `.md`
- Run once — then build your own modules on top

### Slide 4-4: The Vocabulary Pattern

**Problem**: `fields.Selection` is hard-coded — can't change options without code changes.

**Solution**: `sis.vocabulary.code` — a managed code list in the database.

```python
# Instead of:
gender = fields.Selection([("male", "Male"), ("female", "Female")])

# Use:
gender_id = fields.Many2one(
    "sis.vocabulary.code",
    domain="[('namespace_uri', '=', 'urn:iso:std:iso:5218')]",
)
```

- Vocabularies group codes by `namespace_uri` (e.g., `urn:iso:std:iso:5218` for ISO Gender)
- Admins can manage codes through the UI
- System vocabularies are protected from modification

### Slide 4-5: Three-Tier Security Model

```
Tier 1 ── ROLES (composite, cross-domain)
              Example: "Field Officer" — bundles privileges from multiple domains
              ↑
Tier 2 ── FUNCTIONAL PRIVILEGES (per domain)
              viewer → officer → manager
              ↑
Tier 3 ── BASE PERMISSIONS (technical, granular)
              read, write, create, delete
```

- **Viewer**: read-only access
- **Officer**: create, read, write (no delete)
- **Manager**: full CRUD + admin functions
- **Admin** (`base.group_system`): unrestricted — every model must grant this

### Slide 4-6: Security Implementation

Three layers to configure per module:

1. **Groups** (`security/security_groups.xml`)

   - Define viewer, officer, manager groups
   - Use `privilege_id` (Odoo 19) for privilege hierarchy
   - Groups imply each other: manager → officer → viewer

2. **ACLs** (`security/ir.model.access.csv`)

   - First row: `base.group_system` with full CRUD
   - Then: viewer (read), officer (read/write/create), manager (full CRUD)

3. **Record Rules** (optional, for row-level filtering)
   - e.g., "users can only see records in their company"

---

## Section 5: Hands-On Preview (~4 slides)

### Slide 5-1: What We're Building

**Student Information System (SIS)** — 4 modules + portal:

1. **`sis_student`** — Student records (extends `res.partner`)
2. **`sis_course`** — Course catalog (standalone model)
3. **`sis_enrollment`** — Student-course links with state machine
4. **`sis_portal`** — Web frontend for students to view enrollments

### Slide 5-2: Module Dependency Graph

```
     sis_portal
     ├── portal (Odoo)
     └── sis_enrollment
         ├── sis_student
         │   ├── sis_vocabulary
         │   └── base (Odoo)
         └── sis_course
             └── base (Odoo)
```

### Slide 5-3: What You'll Learn

| Phase | Module           | Key Patterns                                             |
| ----- | ---------------- | -------------------------------------------------------- |
| 0     | (setup)          | `init`, `doctor`, `start`                                |
| 1     | `sis_student`    | Inherit & extend, vocabulary fields, three-tier security |
| 2     | `sis_course`     | Standalone model, CRUD, views                            |
| 3     | `sis_enrollment` | State machine, M2O relations, SQL constraints            |
| 4     | `sis_portal`     | Controllers, QWeb templates, portal security             |

### Slide 5-4: Expected Outcome

- 4 installed modules with passing tests
- Student records extending contacts
- Course catalog with list/form views
- Enrollment with draft → enrolled → completed/dropped flow
- Web portal at `/my/enrollments` for logged-in students
- All secured with three-tier access control

**Let's get started!**
