export const siteConfig = {
  "title": "Brew-Ghost",
  "repoUrl": "https://github.com/AMFI-Disable/Brew-Ghost",
  "category": "CLI & Developer Tool",
  "accent": "#FBC02D",
  "tagline": "Behavioral Homebrew cleanup CLI that analyzes Bash/Zsh shell history to safely identify and purge packages idle for over 90 days.",
  "primaryCta": {
    "label": "Install via Homebrew",
    "href": "#quick-start"
  },
  "secondaryCta": {
    "label": "View on GitHub",
    "href": "https://github.com/AMFI-Disable/Brew-Ghost"
  },
  "quickCmd": "brew tap AMFI-Disable/tap && brew install brew-ghost",
  "features": [
    {
      "title": "90-Day Behavioral Audit",
      "desc": "Cross-references installed Homebrew formulae against your actual Bash/Zsh command history timestamps."
    },
    {
      "title": "Read-Only Scan by Default",
      "desc": "Running brew-ghost inspects your cellar safely without uninstalling a single package."
    },
    {
      "title": "Dependency-Aware Exorcise",
      "desc": "Protects active dependencies and lets you confirm or exclude packages before purging."
    },
    {
      "title": "Zero External Dependencies",
      "desc": "Lightweight Python script distributed cleanly via the official AMFI-Disable/tap Homebrew tap."
    }
  ],
  "steps": [
    {
      "title": "Parse Shell History",
      "desc": "Reads extended Bash/Zsh history timestamps to build a per-binary last-used map."
    },
    {
      "title": "Map Homebrew Cellar",
      "desc": "Matches installed formulae and their executables against observed usage over the past 90 days."
    },
    {
      "title": "Safe Interactive Purge",
      "desc": "Reports idle 'ghost' packages with reclamation estimates and optional guided removal."
    }
  ],
  "installCmds": [
    {
      "label": "Homebrew Tap (Recommended)",
      "cmd": "brew tap AMFI-Disable/tap && brew install brew-ghost"
    },
    {
      "label": "Run Read-Only Scan",
      "cmd": "brew-ghost --dry-run"
    }
  ],
  "requirements": [
    "macOS or Linux with Homebrew",
    "Bash or Zsh extended history enabled",
    "Python 3.10+"
  ],
  "hubName": "AMFI Terminal",
  "hubHash": "terminal",
  "previewTabs": [
    {
      "tab": "90-Day Audit",
      "title": "Shell History Correlation",
      "body": "Cross-references installed Homebrew formulae against extended Bash/Zsh history timestamps."
    },
    {
      "tab": "Read-Only Scan",
      "title": "Safe Default Mode",
      "body": "Running brew-ghost --dry-run reports idle packages and disk savings without uninstalling anything."
    },
    {
      "tab": "Guided Exorcise",
      "title": "Dependency-Aware Purge",
      "body": "Protects active dependencies and lets you confirm or exclude packages before removal."
    }
  ]
} as const;
