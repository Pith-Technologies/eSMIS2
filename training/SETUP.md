# Pre-Training Setup Guide

> **Author**: Edwin Gonzales **Last Updated**: March 4, 2026
>
> **Complete these steps before the training session.** Installation and downloads can take 30+ minutes depending on
> your internet speed. If you run into issues, contact your instructor ahead of time.

---

## What You Need

| Tool             | Required    | Purpose                                          |
| ---------------- | ----------- | ------------------------------------------------ |
| Docker Desktop   | Yes         | Runs Odoo and PostgreSQL in containers           |
| Git              | Yes         | Version control — tracks your changes            |
| Python 3.10+     | Yes         | Runs the `odoo-project` CLI and pre-commit hooks |
| pre-commit       | Yes         | Automated code quality checks on every commit    |
| Claude Code      | Yes         | AI-powered development assistant (CLI)           |
| A code editor    | Yes         | VS Code recommended (any editor works)           |
| A GitHub account | Recommended | To push your project after the training          |

---

## Step 1: Install Docker Desktop

Docker Desktop includes Docker Engine, Docker Compose, and a GUI for managing containers.

### Windows

1. **Check system requirements**:

   - Windows 10 version 2004+ or Windows 11
   - WSL 2 enabled (Docker Desktop will prompt you to install it)
   - Hardware virtualization enabled in BIOS/UEFI (usually on by default)

2. **Download** Docker Desktop from <https://www.docker.com/products/docker-desktop/>

3. **Run the installer** — accept the defaults. When prompted:

   - Select **"Use WSL 2 instead of Hyper-V"** (recommended)
   - Check **"Add shortcut to desktop"** if you like

4. **Restart your computer** when prompted

5. **Launch Docker Desktop** — it appears in your system tray. Wait for the status to show "Docker Desktop is running"

6. **If WSL 2 is not installed**, Docker Desktop will show a link. Follow it, or run in PowerShell (as Administrator):

   ```powershell
   wsl --install
   ```

   Then restart and launch Docker Desktop again.

7. **Verify** — open a terminal (PowerShell or Command Prompt):
   ```bash
   docker --version
   docker compose version
   ```
   Both should print version numbers without errors.

> **Troubleshooting (Windows)**:
>
> - "Hardware assisted virtualization and data execution protection must be enabled in the BIOS" → Restart, enter BIOS
>   (usually F2, F12, or Del during boot), enable Intel VT-x or AMD-V
> - "WSL 2 installation is incomplete" → Run `wsl --update` in PowerShell (as Administrator)
> - Docker Desktop stuck on "Starting..." → Restart Docker Desktop, or restart your computer

### macOS

1. **Download** Docker Desktop from <https://www.docker.com/products/docker-desktop/>

   - Choose **Apple Silicon** (M1/M2/M3/M4) or **Intel** based on your Mac

2. **Open the `.dmg`** and drag Docker to Applications

3. **Launch Docker Desktop** from Applications — grant permissions when prompted

4. **Wait** for the whale icon in the menu bar to show "Docker Desktop is running"

5. **Verify** — open Terminal:
   ```bash
   docker --version
   docker compose version
   ```

> **Troubleshooting (macOS)**:
>
> - "Docker Desktop requires macOS 12.0 or later" → Update macOS in System Settings → General → Software Update
> - Slow on Apple Silicon → Make sure you downloaded the Apple Silicon version, not Intel

### Linux

Docker Engine (no Desktop GUI needed):

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose-v2

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER
```

**Log out and log back in** for the group change to take effect.

Verify:

```bash
docker --version
docker compose version
```

> **Troubleshooting (Linux)**:
>
> - "permission denied" when running `docker` → You need to log out/in after `usermod`, or use `newgrp docker`
> - `docker compose` not found → Install `docker-compose-v2` package (not the old `docker-compose` Python package)

---

## Step 2: Install Git

### Windows

1. Download from <https://git-scm.com/download/win>
2. Run the installer — accept the defaults
3. Verify in a new terminal:
   ```bash
   git --version
   ```

> **Tip**: The installer includes "Git Bash", a Unix-like terminal for Windows. You can use it for the training if you
> prefer it over PowerShell.

### macOS

Git is included with the Xcode Command Line Tools:

```bash
xcode-select --install
```

Or install via Homebrew:

```bash
brew install git
```

Verify:

```bash
git --version
```

### Linux

```bash
# Ubuntu / Debian
sudo apt-get install git

# Fedora
sudo dnf install git
```

### Configure Git (all platforms)

Set your name and email (used in commit messages):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 3: Install Python

You need Python 3.10 or later. Check if you already have it:

```bash
python3 --version
```

If not installed or below 3.10:

### Windows

1. Download from <https://www.python.org/downloads/>
2. **Important**: Check **"Add python.exe to PATH"** during installation
3. Verify in a new terminal:
   ```bash
   python --version
   ```

> **Note**: On Windows, the command may be `python` instead of `python3`.

### macOS

```bash
brew install python@3.12
```

Or download from <https://www.python.org/downloads/>

### Linux

```bash
# Ubuntu / Debian
sudo apt-get install python3 python3-pip python3-venv
```

---

## Step 4: Install pre-commit

pre-commit runs code quality checks automatically before each `git commit`.

```bash
pip install pre-commit
```

Or if `pip` is not on your PATH:

```bash
python3 -m pip install pre-commit
```

Verify:

```bash
pre-commit --version
```

> **Note**: After cloning / unzipping the project during the training, you'll also run `pre-commit install` inside the
> project directory to activate the hooks. This step just installs the tool itself.

---

## Step 5: Install Claude Code

Claude Code is an AI-powered CLI that helps you write, review, and debug code. It's a core part of our development
workflow.

### Install via npm (all platforms)

Claude Code requires **Node.js 18+**. Check if you have it:

```bash
node --version
```

If not installed:

- **Windows**: Download from <https://nodejs.org/> (LTS version)
- **macOS**: `brew install node`
- **Linux**: `sudo apt-get install nodejs npm` (Ubuntu/Debian) or download from <https://nodejs.org/>

Then install Claude Code globally:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

### Configure the API Key

Your instructor will provide a shared **Anthropic API key** for the training. Set it as an environment variable so
Claude Code can authenticate.

**macOS / Linux:**

Add this line to your shell profile (`~/.zshrc`, `~/.bashrc`, or `~/.bash_profile`):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Then reload your shell:

```bash
source ~/.zshrc    # or ~/.bashrc
```

**Windows (PowerShell):**

Set it permanently for your user:

```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

Then **close and reopen** your terminal for the change to take effect.

**Windows (Command Prompt):**

```cmd
setx ANTHROPIC_API_KEY "sk-ant-..."
```

Then **close and reopen** your terminal.

> **Important**: Replace `sk-ant-...` with the actual key your instructor provides. Do not share this key outside the
> training session.

To verify the key is set:

```bash
echo $ANTHROPIC_API_KEY          # macOS / Linux
echo %ANTHROPIC_API_KEY%         # Windows Command Prompt
$env:ANTHROPIC_API_KEY           # Windows PowerShell
```

You should see the key value printed (starting with `sk-ant-`).

### First-Time Setup

Run `claude` once to complete the initial setup:

```bash
claude
```

This will prompt you to:

1. **Accept the terms** — review and accept the usage terms
2. **Choose a theme** — pick your preferred terminal color scheme

Claude Code will automatically use the `ANTHROPIC_API_KEY` environment variable for authentication. Once setup is
complete, type `/exit` to leave the interactive session.

### Verify Claude Code Works

```bash
claude --version
claude "What is 2 + 2?"
```

You should see a version number and then a response from Claude.

> **Troubleshooting**:
>
> - `command not found: claude` → Make sure Node.js `bin` directory is on your PATH. Try closing and reopening your
>   terminal.
> - `npm ERR! EACCES` on macOS/Linux → Use `sudo npm install -g @anthropic-ai/claude-code` or fix npm permissions:
>   <https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally>
> - `Error: Invalid API key` → Verify the environment variable is set correctly (see "Configure the API Key" above).
>   Make sure you opened a **new** terminal after setting it.
> - `Error: 401 Unauthorized` → The API key may have been rotated. Ask your instructor for the current key.

---

## Step 6: Install a Code Editor

Any editor works. We recommend **Visual Studio Code**:

1. Download from <https://code.visualstudio.com/>
2. Install these extensions (optional but helpful):
   - **Python** (Microsoft) — syntax highlighting, linting
   - **XML Tools** — XML formatting and navigation

---

## Step 7: Verify Everything

Open a terminal and run each of these. All should succeed:

```bash
docker --version           # Docker version 24.x or later
docker compose version     # Docker Compose version v2.x
git --version              # git version 2.x
python3 --version          # Python 3.10+
pre-commit --version       # pre-commit 3.x or later
claude --version           # Claude Code (any version)
```

**Expected output** (version numbers will vary):

```
Docker version 27.5.1, build 9f9e405
Docker Compose version v2.32.4
git version 2.47.1
Python 3.12.8
pre-commit 4.1.0
1.0.16 (Claude Code)
```

If any command fails, revisit the installation step for that tool.

### Final check — Docker is actually running

```bash
docker info > /dev/null 2>&1 && echo "Docker is running" || echo "Docker is NOT running - start Docker Desktop"
```

If Docker is not running, launch Docker Desktop and wait for it to finish starting.

---

## What to Bring to the Training

- Your laptop with all tools installed and verified
- The ZIP file provided by your instructor (you'll receive this separately)
- This guide for reference if anything needs troubleshooting

**You're all set! See you at the training.**
