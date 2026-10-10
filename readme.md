# 👻 Brew-Ghost

<div align="center">

**Exorcise The Freeloaders In Your Homebrew Cellar**  
*Behavioral shell-history analyzer that safely identifies and purges abandoned packages idle for over 90 days.*

[![Platform: macOS & Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-blue.svg?style=flat-square&logo=apple)](https://apple.com)
[![Shell: Bash / Zsh](https://img.shields.io/badge/Shell-Bash%20%2F%20Zsh-orange.svg?style=flat-square&logo=gnubash)](https://gnu.org)
[![Tap: AMFI-Disable/tap](https://img.shields.io/badge/Tap-AMFI--Disable%2Ftap-blue.svg?style=flat-square&logo=homebrew)](https://brew.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](license)
[![Privacy: Zero Telemetry](https://img.shields.io/badge/Privacy-Zero%20Telemetry%20%2F%20100%25%20Local-purple.svg?style=flat-square)](#-how-it-works)

</div>

---

## 🚀 Installation

Install `Brew-Ghost` using the official Homebrew Tap:

```bash
# 1. Tap the repository
brew tap AMFI-Disable/tap

# 2. Install Brew-Ghost
brew install AMFI-Disable/tap/brew-ghost
```

---

## 🛠 Usage

Once installed, you can scan your Cellar by running:

```bash
# Scan and identify ghost packages (read-only mode)
brew-ghost
```

### Exorcising Ghosts (Cleanup)

To safely purge the identified ghosts, use the `--exorcise` flag:

```bash
# Purge packages idle for more than 90 days
brew-ghost --exorcise
```

You will be presented with the list of packages to remove and prompted for confirmation `[y/N]` before any actions are taken.

---

## 🧠 How It Works

`Brew-Ghost` follows a multi-phase behavioral analysis:

1. **Inventory Gathering**: Runs `brew leaves` to identify all top-level user-installed packages (ignoring dependent library packages).
2. **Behavioral Shell Analysis**: Scans `~/.zsh_history` from newest to oldest to track the most recent execution timestamp of each package name.
3. **Safety Fallbacks**:
   - If a package is never found in your history, its "last active" date falls back to its **original installation date**. This prevents newly installed packages from being flagged as ghosts.
   - If Zsh history lacks timestamps (e.g., if `EXTENDED_HISTORY` is disabled), commands in history default to the history file's modification time (essentially "today") to protect you from accidental uninstalls.
4. **Metadata Resolution**: Queries `brew info --json=v2` (with direct Cellar directory size calculations as a fallback) to retrieve exact disk footprints.
5. **ASCII Reporting**: Outputs a beautifully formatted table detailing name, size, and days idle.

---

## ⚠️ Getting Accurate Results

For `Brew-Ghost` to compute exact active days, your Zsh shell must write execution timestamps to the history file.

Add the following to your `~/.zshrc` to enable this:

```zsh
# Enable extended history timestamps (format: : <epoch>:<elapsed>;<command>)
setopt EXTENDED_HISTORY
```

> [!NOTE]
> If `EXTENDED_HISTORY` is off, `Brew-Ghost` will warn you and fall back to treating any package name found in your history as active "today" to prevent false uninstallation flags.

---

## 📄 License And Open Source

Licensed under the [MIT License](license). Copyright (c) 2026 AMFI-Disable.
