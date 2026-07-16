# 👻 brew-ghost

> Exorcise the absolute freeloaders in your Cellar.

`brew-ghost` is a behavioral cleanup tool that identifies and purges "ghost" Homebrew packages—top-level formulas that you installed but haven't actually executed or used in over 90 days. It does this by cross-referencing your intentionally installed leaves against your terminal shell history.

---

## 🚀 Installation

Install `brew-ghost` using your custom Homebrew Tap:

```bash
# 1. Tap the repository
brew tap amfi-disable/tap

# 2. Install brew-ghost
brew install amfi-disable/tap/brew-ghost
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

`brew-ghost` follows a multi-phase behavioral analysis:

1. **Inventory Gathering**: Runs `brew leaves` to identify all top-level user-installed packages (ignoring dependent library packages).
2. **Behavioral Shell Analysis**: Scans `~/.zsh_history` from newest to oldest to track the most recent execution timestamp of each package name.
3. **Safety Fallbacks**:
   - If a package is never found in your history, its "last active" date falls back to its **original installation date**. This prevents newly installed packages from being flagged as ghosts.
   - If Zsh history lacks timestamps (e.g., if `EXTENDED_HISTORY` is disabled), commands in history default to the history file's modification time (essentially "today") to protect you from accidental uninstalls.
4. **Metadata Resolution**: Queries `brew info --json=v2` (with direct Cellar directory size calculations as a fallback) to retrieve exact disk footprints.
5. **ASCII Reporting**: Outputs a beautifully formatted table detailing name, size, and days idle.

---

## ⚠️ Getting Accurate Results

For `brew-ghost` to compute exact active days, your Zsh shell must write execution timestamps to the history file. 

Add the following to your `~/.zshrc` to enable this:

```zsh
# Enable extended history timestamps (format: : <epoch>:<elapsed>;<command>)
setopt EXTENDED_HISTORY
```

> [!NOTE]
> If `EXTENDED_HISTORY` is off, `brew-ghost` will warn you and fall back to treating any package name found in your history as active "today" to prevent false uninstallation flags.
