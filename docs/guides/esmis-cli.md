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

## One stack for every worktree

`docker-compose.yml` pins the Compose project name to `esmis2`, so every git worktree of this repository uses the same
containers, network and volumes: one database (`esmis2_postgres_data`) and one filestore (`esmis2_odoo_data`). Local
users, configuration and data survive creating a new worktree or switching between worktrees. Starting from scratch
happens only when you ask for it: `./esmis resetdb`, `./esmis stop -v` or `./esmis start --wipe`, each behind a
confirmation, and each one deletes the data every worktree uses.

The addons are bind-mounted from the worktree you run the command in, so the running Odoo serves the code of whichever
worktree last ran `./esmis start`. Two worktrees cannot run the stack at the same time, and nothing tells the others
apart except that path:

```bash
./esmis status            # Shared stack 'esmis2' is serving: /path/to/worktree (branch feat/x)
./esmis start             # prints "Serving code from: ..." once it is up
```

### Switching worktrees

1. Run `./esmis start` in the worktree you are moving to. It warns that the stack is serving another worktree, then
   recreates the Odoo container with this worktree's code. The database container keeps running and the data is kept.
2. If the two worktrees differ in their module set or module versions, upgrade the changed modules yourself. Nothing
   upgrades on its own. `./esmis update` (click-odoo-update, checksum based) refuses to run while Odoo serves a
   different worktree, or when it cannot tell. To upgrade a named module instead, run `./esmis status` first, because
   the raw command does not check and runs inside whatever the container serves:

   ```bash
   docker compose --profile ui exec odoo-app odoo -d odoo -u <module> --stop-after-init --no-http
   # dev profile: docker compose --profile dev exec odoo-dev ...
   ./esmis restart
   ```
3. A module that exists only in the worktree you left stays installed in the database with no code behind it.
   Uninstall it before switching, or reset the database, if that gets in the way.

Test databases are unaffected: `./esmis test` still creates a throwaway `test_<module>_<random>` database against the
shared PostgreSQL and drops it afterwards.

To run a deliberately separate stack, set `COMPOSE_PROJECT_NAME` for every command, and remember that it moves ports
and volumes with it:

```bash
COMPOSE_PROJECT_NAME=esmis2-spike ./esmis start
```

### Moving data from an old per-worktree stack

Before the project name was pinned, Compose named the project after the worktree directory, so each worktree had its
own pair of volumes: `<dir>_postgres_data` and `<dir>_odoo_data`, where `<dir>` is the directory name lowercased with
anything Compose does not accept removed (`19.0` became `190`; `feat-esmis-academic-term` stayed as it was). Those
volumes, and the old projects' stopped containers, were not deleted. Either start fresh or copy one old project's data
into the shared stack, once. `./esmis stop` only ever touches the `esmis2` project, so the old ones are yours to stop
and remove by name.

**Start fresh.** `./esmis start` creates the shared volumes empty and initialises the database. Remove each old project
when you no longer want it (`down -v` deletes its containers, network and volumes):

```bash
docker volume ls                                  # find the old <dir>_postgres_data / <dir>_odoo_data pairs
docker compose -p 190 down -v                     # for each old project you are done with
```

**Copy an old project's data.** The old and new stacks run the same PostgreSQL image, so a cluster that is stopped can
be copied file for file. A running one cannot: stop the old project first. The shared volumes must not exist yet, or
must hold nothing you want.

```bash
./esmis stop                                      # the shared stack must not be running
docker compose -p 190 down                        # the old project too; without -v its volumes stay
docker ps -a --filter label=com.docker.compose.project=190   # must print no containers
docker volume ls --filter name=esmis2_            # must print nothing; `./esmis stop -v -y` clears an unwanted pair
docker compose --profile ui create                # creates the shared volumes empty and labelled, starts nothing
docker run --rm -v 190_postgres_data:/from -v esmis2_postgres_data:/to alpine cp -a /from/. /to/
docker run --rm -v 190_odoo_data:/from -v esmis2_odoo_data:/to alpine cp -a /from/. /to/
./esmis start                                     # check your users, settings and data are there
docker compose -p 190 down -v                     # once satisfied
```

Replace `190` with the name of the project you are copying from. Let Compose create the shared volumes, as above,
rather than `docker volume create`: a volume Compose did not create works but draws a warning on every later `up`.
Copy one project only: merging two old databases into one is not a file copy, and the shared stack holds one database.

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
| `--wipe`      | Delete all data (database + filestore, shared by every worktree) before starting |
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
| `-v, --volumes` | Also remove Docker volumes (destructive; the volumes are shared by every worktree) |
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

Shows which worktree the shared stack is serving, then the Docker containers.

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

### Odoo shows another worktree's code, or `update` refuses to run

The stack is shared and serves the worktree that last started it. `./esmis status` names that worktree; `./esmis start`
in the worktree you want switches it, keeping the data. See [One stack for every worktree](#one-stack-for-every-worktree).

### A new worktree starts empty

It should not: every worktree shares one database and filestore. If a worktree does start empty, check that
`docker-compose.yml` still carries `name: esmis2` and that `COMPOSE_PROJECT_NAME` is not set in your shell.

### Database connection issues

```bash
./esmis doctor                # check Docker daemon is running
./esmis status                # check container states
./esmis logs db               # check database logs
```
