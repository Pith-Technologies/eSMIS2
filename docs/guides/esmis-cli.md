# esmis CLI

Developer CLI for running, testing, and managing your Odoo project locally with Docker.

## Prerequisites

Run `./esmis doctor` to verify your environment:

- **Docker** and **Docker Compose v2** (required)
- **Git** (optional, used by `lint`)
- **pre-commit** (optional, used by `lint`)
- **argcomplete** (optional, enables tab completion)

## Quick Start

```bash
# 1. Check prerequisites
./esmis doctor

# 2. Build the Docker image
./esmis build

# 3. Start Odoo
./esmis start

# 4. Open http://localhost:8069 (admin / admin)

# 5. Run tests
./esmis test esmis_vocabulary

# 6. Stop everything
./esmis stop
```

### init — Initialize from template

Replaces the `tpl` placeholder prefix and `eSMIS` name throughout the codebase, then renames `esmis_*` directories to match your project.

```bash
./esmis init eh EHealth             # replace esmis -> eh, eSMIS -> EHealth
./esmis init --dry-run eh EHealth   # preview changes without modifying files
./esmis init myapp "My App"         # any lowercase prefix works
```

| Option          | Description                                      |
|-----------------|--------------------------------------------------|
| `prefix`        | Your project prefix (lowercase, e.g., `eh`)      |
| `project_name`  | Your project display name (e.g., `EHealth`)       |
| `--dry-run, -n` | Show what would change without modifying files    |

What gets replaced:

| Pattern      | Example                              |
|--------------|--------------------------------------|
| `esmis_` → `{prefix}_` | `esmis_vocabulary` → `eh_vocabulary` |
| `esmis.` → `{prefix}.` | `esmis.vocabulary` → `eh.vocabulary` |
| `esmis/` → `{prefix}/` | `esmis/Core` → `eh/Core`            |
| `esmis ` → `{prefix} ` | `esmis Vocabulary` → `eh Vocabulary` |
| `eSMIS` → name   | `eSMIS` → `EHealth`           |

Binary files and `.git/` are always skipped.

## Commands

Every command has a short alias shown in parentheses.

### test (t) — Run module tests

Runs tests in an isolated container that does not affect your running dev instance.

```bash
./esmis test esmis_vocabulary
./esmis t esmis_vocabulary                     # alias
./esmis test esmis_vocabulary --tags=post_install
./esmis test esmis_vocabulary --local           # force local mode (no Docker)
./esmis test esmis_vocabulary --docker           # force Docker mode
```

| Option     | Description                        |
|------------|------------------------------------|
| `--tags`   | Test tags filter (e.g. `post_install`) |
| `--local`  | Force local mode (uses local venv) |
| `--docker` | Force Docker mode                  |

### start (s) — Start Odoo

Starts the Odoo development server. Defaults to the **ui** profile on port 8069.

```bash
./esmis start                     # default: ui profile, port 8069
./esmis s                         # alias
./esmis start --profile dev       # dynamic port, auto-reload enabled
./esmis start --demo=base         # install base demo data on start
./esmis start --wipe              # wipe all data first (fresh DB)
./esmis start --wipe --demo=base  # fresh start with demo data
./esmis start --no-build          # skip Docker image freshness check
./esmis start -y                  # auto-confirm prompts (rebuild, etc.)
```

| Option        | Description                                              |
|---------------|----------------------------------------------------------|
| `--profile`   | `ui` (fixed port 8069, default) or `dev` (dynamic port) |
| `--demo`      | Demo data profile to install (see [Demo Profiles](#demo-profiles)) |
| `--wipe`      | Delete all data (database + filestore) before starting   |
| `--no-watch`  | Disable auto-reload (dev profile enables it by default)  |
| `--no-build`  | Skip Docker image freshness check                        |
| `-y, --yes`   | Skip confirmation prompts                                |

### stop — Stop all services

Stops all Docker containers across all profiles.

```bash
./esmis stop
./esmis stop -v           # also remove volumes (deletes DB data)
./esmis stop -y           # skip confirmation prompt
./esmis stop -v -y        # remove volumes without confirmation
```

| Option        | Description                       |
|---------------|-----------------------------------|
| `-v, --volumes` | Also remove Docker volumes (destructive) |
| `-y, --yes`     | Skip confirmation prompt           |

### restart (r) — Restart Odoo

Auto-detects which profile is running and restarts the Odoo container.

```bash
./esmis restart
./esmis r                 # alias
```

### resetdb — Reset database

Drops and recreates the database. Use with `start` to initialize with modules.

```bash
./esmis resetdb -y                          # reset with defaults
./esmis resetdb --demo=base -y              # reset with demo profile
./esmis resetdb --db=mydb -y                # reset a named database
./esmis resetdb --demo=base start           # reset then start (chained)
```

| Option     | Description                                            |
|------------|--------------------------------------------------------|
| `--demo`   | Demo profile to install after reset                    |
| `--db`     | Database name (default: `odoo`)                        |
| `-y, --yes` | Skip confirmation prompt                             |

### update (u) — Update modules

Uses `click-odoo-update` to auto-detect changed modules based on file checksums.

```bash
./esmis update
./esmis u                      # alias
./esmis update --db=mydb       # target a specific database
```

| Option | Description                     |
|--------|---------------------------------|
| `--db` | Database name (default: `odoo`) |

### build (b) — Build Docker images

Builds the Docker image for the specified profile.

```bash
./esmis build
./esmis b                      # alias
./esmis build --no-cache       # full rebuild without cache
./esmis build --profile dev    # build dev profile image
```

| Option       | Description                       |
|--------------|-----------------------------------|
| `--profile`  | `ui` (default) or `dev`           |
| `--no-cache` | Build without using Docker cache  |

### logs (l) — View logs

Shows container logs. Auto-detects the running Odoo service.

```bash
./esmis logs
./esmis l                      # alias
./esmis logs -f                # follow (stream) logs
./esmis logs --tail 50         # last 50 lines
./esmis logs db                # show database logs
```

| Option        | Description                        |
|---------------|------------------------------------|
| `-f, --follow` | Stream logs in real time          |
| `--tail`       | Number of lines (default: 100)   |
| `service`      | Service name (`db`, `odoo-app`, etc.) |

### shell (sh) — Open Odoo shell

Opens an interactive Odoo Python shell connected to the running instance.

```bash
./esmis shell
./esmis sh                     # alias
./esmis shell --db             # open PostgreSQL shell instead
./esmis shell -d mydb          # connect to a specific database
```

| Option          | Description                              |
|-----------------|------------------------------------------|
| `--db`          | Open PostgreSQL shell instead of Odoo shell |
| `-d, --database` | Database name (default: `odoo`)         |

### sql — Run SQL queries

Opens an interactive PostgreSQL shell or executes a query directly.

```bash
./esmis sql                                           # interactive psql
./esmis sql "SELECT name FROM esmis_vocabulary"         # run a query
./esmis sql -f scripts/report.sql                     # run SQL from file
./esmis sql -d mydb "SELECT 1"                        # target specific DB
```

| Option          | Description                     |
|-----------------|---------------------------------|
| `query`         | SQL query to execute (optional) |
| `-d, --database` | Database name (default: `odoo`) |
| `-f, --file`    | SQL file to execute             |

### url — Show server URL

Displays the URL of the running Odoo instance.

```bash
./esmis url
./esmis url --open             # open in default browser
```

| Option      | Description             |
|-------------|-------------------------|
| `-o, --open` | Open URL in browser    |

### lint — Run linters

Runs `ruff`, `ruff-format`, and `prettier` via pre-commit on specified files.

```bash
./esmis lint                                   # lint changed files (git diff)
./esmis lint esmis_vocabulary/models/*.py        # lint specific files
```

| Option  | Description                                      |
|---------|--------------------------------------------------|
| `files` | Files to lint (default: git changed files)       |

### status (st) — Show service status

Shows running Docker containers.

```bash
./esmis status
./esmis st                     # alias
```

### doctor — Check prerequisites

Verifies that all required and optional tools are installed.

```bash
./esmis doctor
```

Checks: Docker, Docker Compose, Docker daemon, Git, pre-commit, argcomplete, config file, port 8069.

### activate — Enable tab completion

Outputs a shell script that enables tab completion for commands and module names.

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
eval "$(./esmis activate)"
```

Requires `argcomplete` (`pip install argcomplete`).

### fix-odoo19 — Fix Odoo 19 compatibility

Applies automatic fixes for Odoo 19 Command API tuples in Python files.

```bash
./esmis fix-odoo19                        # fix all modules
./esmis fix-odoo19 esmis_vocabulary          # fix specific module
./esmis fix-odoo19 --dry-run               # preview changes
```

| Option          | Description                                    |
|-----------------|------------------------------------------------|
| `modules`       | Modules to fix (default: all)                  |
| `--dry-run, -n` | Preview changes without applying               |

### fix-lint — Fix linting issues

Runs ruff, pylint, and prettier across module files and optionally invokes an AI agent for remaining issues.

```bash
./esmis fix-lint esmis_vocabulary            # fix specific module
./esmis fix-lint                           # fix all modules
./esmis fix-lint esmis_vocabulary --lint-only # linters only, no AI
```

| Option        | Description                                      |
|---------------|--------------------------------------------------|
| `modules`     | Modules to fix (default: all)                    |
| `--lint-only` | Only run linters, skip AI fixing                 |

### fix-security — Fix security compliance

Applies mechanical fixes for Odoo 19 security issues (tuple syntax, field renames) and optionally invokes an AI agent for complex issues.

```bash
./esmis fix-security esmis_vocabulary        # fix specific module
./esmis fix-security --all                 # fix all modules with issues
./esmis fix-security --dry-run esmis_api     # preview changes
./esmis fix-security --mechanical-only esmis_api  # no AI
```

| Option              | Description                                      |
|---------------------|--------------------------------------------------|
| `modules`           | Modules to fix                                   |
| `--all`             | Fix all modules with issues                      |
| `--dry-run, -n`     | Show what would be fixed                         |
| `--mechanical-only` | Only apply mechanical fixes (no AI agent)        |

### audit-security — Audit security compliance

Audits modules for access rights compliance using the Python security audit script.

```bash
./esmis audit-security                     # audit all modules
./esmis audit-security esmis_vocabulary      # audit specific module
./esmis audit-security --report            # generate markdown report
./esmis audit-security --json              # output as JSON
```

| Option     | Description                          |
|------------|--------------------------------------|
| `modules`  | Modules to audit (default: all)      |
| `--report` | Generate markdown report             |
| `--json`   | Output as JSON                       |

### audit-modules — Audit module compliance

Audits modules against project principles using an AI agent (requires `cursor-agent` or `claude`).

```bash
./esmis audit-modules                      # audit all modules
./esmis audit-modules esmis_vocabulary       # audit specific module
./esmis audit-modules --fix                # auto-fix simple issues
./esmis audit-modules --fix --commit       # fix and commit
```

| Option    | Description                                    |
|-----------|------------------------------------------------|
| `modules` | Modules to audit (default: all)                |
| `--fix`   | Auto-fix clear, mechanical issues              |
| `--commit` | Auto-commit fixes after each module           |
| `--model` | AI model to use (default: `composer-1`)        |

## Demo Profiles

Demo profiles are predefined sets of modules to install:

| Profile | Modules Installed  |
|---------|--------------------|
| `base`  | `esmis_vocabulary`   |

Use with `start` or `resetdb`:

```bash
./esmis start --demo=base
./esmis resetdb --demo=base -y
```

## Command Chaining

Commands can be chained in a single invocation. Options apply to the preceding command.

```bash
./esmis resetdb --demo=base start         # reset DB, then start
./esmis stop start --wipe                  # stop, then wipe and start
./esmis resetdb --demo=base start --wipe   # reset, then wipe and start
```

## Dry Run Mode

Add `--dry-run` (or `-n`) to see what commands would be executed without running them.

```bash
./esmis --dry-run start
./esmis -n stop -v
```

## Configuration

Defaults can be customized via `~/.esmis.toml`:

```toml
default_demo = "base"       # auto-install demo on start
default_profile = "ui"      # "ui" or "dev"
default_db = "odoo"          # database name
```

Create the file:

```bash
echo 'default_profile = "ui"' > ~/.esmis.toml
```

## Common Workflows

### Fresh start with demo data

```bash
./esmis start --wipe --demo=base -y
```

### Daily development

```bash
./esmis start                # start Odoo
# ... make code changes ...
./esmis update               # auto-detect and upgrade changed modules
./esmis test esmis_vocabulary   # run tests
./esmis lint                  # lint changed files
```

### Debugging a module

```bash
./esmis start
./esmis shell                 # open Odoo shell
>>> env['esmis.vocabulary'].search([])

./esmis sql "SELECT * FROM esmis_vocabulary"
./esmis logs -f               # watch logs in real time
```

### Quick test cycle

```bash
./esmis test esmis_vocabulary
./esmis test esmis_vocabulary --tags=post_install
```

### Complete reset

```bash
./esmis stop -v -y            # stop and delete all data
./esmis build --no-cache      # full rebuild
./esmis start --demo=base     # fresh start with demo
```

## Troubleshooting

### Port 8069 already in use

```bash
./esmis doctor                # will show port status
./esmis stop                  # stop any running containers
```

### Docker image seems stale

The CLI auto-detects when `Dockerfile` or `requirements.txt` change and prompts to rebuild. To force:

```bash
./esmis build --no-cache
```

### Tests fail but dev instance works

Tests run in an isolated container with a temporary database. Check:

```bash
./esmis test esmis_vocabulary   # re-run tests
./esmis logs                  # check logs for errors
```

### Module not updating after code changes

```bash
./esmis update                # auto-detect and upgrade changed modules
./esmis restart               # restart if update doesn't pick up changes
```

### Database connection issues

```bash
./esmis doctor                # check Docker daemon is running
./esmis status                # check container states
./esmis logs db               # check database logs
```
