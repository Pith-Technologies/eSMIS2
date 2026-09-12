# Quickstart Guide

Get eSMIS running locally in under 10 minutes.

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool                              | Required | Notes                                                              |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| **Docker Desktop** (or Docker Engine + Docker Compose v2) | Yes | [Install Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Git**                           | Yes      | [Install Git](https://git-scm.com/downloads)                      |
| **Python 3.12+**                  | Yes      | For running scripts and linters locally. Odoo itself runs in Docker. |
| **pre-commit**                    | No       | Recommended. Runs linters automatically before each commit.        |

### Installing pre-commit (optional but recommended)

```bash
pip install pre-commit
cd eSMIS2
pre-commit install
```

Once installed, linters run automatically on every `git commit`. You can also run them manually at any time.

### Verify your environment

After cloning (see next section), you can check that everything is set up correctly:

```bash
./esmis doctor
```

This checks Docker, Docker Compose, Git, pre-commit, and port availability.

## Clone and Build

```bash
git clone https://github.com/Pith-Technologies/eSMIS2.git
cd eSMIS2
./esmis build
```

The `build` command creates the Docker image with Odoo 19 and all project dependencies. This takes a few minutes the first time. Subsequent builds are cached and much faster.

## Start the System

```bash
./esmis start
```

Once the logs show Odoo is ready, open your browser:

- **URL:** <http://localhost:8069>
- **Login:** `admin`
- **Password:** `admin`

You should see the Odoo backend with the eSMIS modules available.

## Explore What's Installed

The `esmis_vocabulary` module is the first foundation module and ships with the base demo profile. To see it in action:

1. Start with demo data if you have not already:

   ```bash
   ./esmis start --wipe --demo=base -y
   ```

2. Log in at <http://localhost:8069> with `admin` / `admin`.

3. Navigate to **Settings > Vocabularies**.

4. You will see 13 seed vocabularies, each with a set of predefined terms:

   | Vocabulary            | Example terms                          |
   | --------------------- | -------------------------------------- |
   | Academic Period Type  | Semester, Trimester, Quarter           |
   | Blood Type            | A+, B-, O+, AB-                        |
   | Civil Status          | Single, Married, Widowed               |
   | Degree Type           | Bachelor, Master, Doctorate            |
   | Disability Type       | Visual, Hearing, Mobility              |
   | Document Type         | Transcript, Diploma, Certificate       |
   | Enrollment Status     | Enrolled, Withdrawn, LOA               |
   | Gender                | Male, Female                           |
   | Grade Remark          | Passed, Failed, Incomplete             |
   | Relationship Type     | Parent, Guardian, Spouse               |
   | Scholarship Type      | Academic, Athletic, Government         |
   | Student Status        | Regular, Irregular, Transferee         |
   | Year Level            | 1st Year, 2nd Year, 3rd Year, 4th Year |

   These vocabularies provide institution-configurable terminology aligned with CHED and PQF standards. Institutions can add, rename, or deactivate terms to match their own conventions.

## Run Tests

Every module includes tests. Run them with:

```bash
./esmis test esmis_vocabulary
```

Tests run in an isolated Docker container with a temporary database, so they never affect your running dev instance. You can filter by tag:

```bash
./esmis test esmis_vocabulary --tags=post_install
```

## Development Workflow

Here is the typical workflow for making changes:

### 1. Create a branch

```bash
git checkout -b feat/my-new-feature
```

### 2. Make your changes

Edit models, views, security rules, or whatever your feature requires.

### 3. Run linters

```bash
# Lint only your changed files
pre-commit run --files esmis_vocabulary/models/vocabulary.py

# Or let the CLI auto-detect changed files
./esmis lint
```

### 4. Run tests

```bash
./esmis test esmis_vocabulary
```

### 5. Commit with conventional format

```bash
git add esmis_vocabulary/models/vocabulary.py
git commit -m "feat: add custom vocabulary validation"
```

We use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`. Imperative mood, present tense.

### 6. Submit a pull request

Push your branch and open a PR. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the full review process.

## Common Commands

Quick reference for the most useful `esmis` commands:

| Command                                | Alias          | Description                                    |
| -------------------------------------- | -------------- | ---------------------------------------------- |
| `./esmis build`                 | `b`            | Build the Docker image                         |
| `./esmis start`                 | `s`            | Start Odoo (port 8069)                         |
| `./esmis stop`                  | —              | Stop all containers                            |
| `./esmis restart`               | `r`            | Restart the Odoo container                     |
| `./esmis test <module>`         | `t <module>`   | Run module tests in isolation                  |
| `./esmis update`               | `u`            | Auto-detect and upgrade changed modules        |
| `./esmis logs -f`              | `l -f`         | Stream logs in real time                       |
| `./esmis shell`                | `sh`           | Open an interactive Odoo Python shell          |
| `./esmis sql`                  | —              | Open an interactive PostgreSQL shell           |
| `./esmis status`               | `st`           | Show running container status                  |
| `./esmis lint`                 | —              | Lint changed files                             |
| `./esmis doctor`               | —              | Verify prerequisites and environment           |
| `./esmis stop -v -y`           | —              | Stop and delete all data (clean reset)         |
| `./esmis start --wipe --demo=base` | —          | Fresh start with demo data                     |

For the full command reference, see the [CLI Guide](esmis-cli.md).

## Troubleshooting

### Docker is not running

**Symptom:** Commands fail with "Cannot connect to the Docker daemon" or similar.

**Fix:** Start Docker Desktop (or the Docker daemon if using Docker Engine). Then run `./esmis doctor` to verify.

### Port 8069 is already in use

**Symptom:** `./esmis start` fails because something else is using port 8069.

**Fix:**

```bash
# Check what is using the port
./esmis doctor

# Stop any existing eSMIS containers
./esmis stop

# If another application is using 8069, stop it or use the dev profile (dynamic port)
./esmis start --profile dev
```

### Module not found during tests or install

**Symptom:** Odoo cannot find a module you just created or modified.

**Fix:** Make sure your module directory is inside the project root, has a valid `__manifest__.py`, and has an `__init__.py`. If the module was just added, you may need to rebuild:

```bash
./esmis build
./esmis start --wipe --demo=base -y
```

### Module not updating after code changes

**Symptom:** You changed code but Odoo still shows old behavior.

**Fix:**

```bash
# Auto-detect and upgrade changed modules
./esmis update

# If that does not help, restart the container
./esmis restart
```

### Database errors or corrupted state

**Symptom:** Odoo shows unexpected errors, missing tables, or broken records.

**Fix:** Reset everything and start fresh:

```bash
./esmis stop -v -y       # Stop containers and delete all volumes (database + filestore)
./esmis start --demo=base  # Start with a clean database and demo data
```

### Tests fail but the dev instance works fine

**Symptom:** Tests report errors that you cannot reproduce in the browser.

**Fix:** Tests run in an isolated container with a temporary database. Common causes:

- Missing access rights in `ir.model.access.csv` (tests do not run as superuser)
- Missing demo data dependencies
- Test running with a user that lacks the required security group

Check the test output carefully and see the [Testing Guide](testing-guide.md) for patterns.

### Docker image seems stale

**Symptom:** New Python dependencies or Dockerfile changes are not picked up.

**Fix:** The CLI auto-detects when `Dockerfile` or `requirements.txt` change and prompts to rebuild. To force a full rebuild:

```bash
./esmis build --no-cache
```

## Next Steps

Once you have the system running, explore these resources:

- **[Module Development Guide](module-development.md)** — how to create and structure eSMIS modules
- **[Testing Guide](testing-guide.md)** — test patterns, coverage targets, and TDD workflow
- **[CLI Guide](esmis-cli.md)** — full reference for all `esmis` commands
- **[Architecture Vision](../architecture/vision.md)** — system architecture and module layers
- **[Implementation Roadmap](../architecture/implementation-roadmap.md)** — what is being built and in what order
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)** — commit conventions, PR process, and review guidelines
- **[Security Audit Guide](../runbooks/security-audit.md)** — auditing modules for access rights compliance
