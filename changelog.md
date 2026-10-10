# Changelog

All notable changes, features, and release history for Brew-Ghost are documented in this file.

---

## [1.1.0] - Behavioral Engine Enhancements

### Added
- **Structured JSON Reporting**: Added support for structured output formats to enable scripting and piping into automated maintenance workflows.
- **Enhanced Cellar Metadata Parsing**: Improved directory footprint calculations across multi-versioned Cellar installations.

### Fixed
- **Memory String Formatting**: Cleaned up internal memory representations and unit formatting for gigabyte-scale package installations.
- **Safety Fallback Verification**: Hardened recent installation date checks to prevent false positive ghost detections for newly added packages.

---

## [1.0.0] - Initial Production Release

`brew-ghost` is a behavioral cleanup tool that identifies and purges unused Homebrew packages by analyzing terminal shell history.

### Added

#### Behavioral Shell Analysis
- **Shell History Cross-Referencing**: Analyzes `~/.zsh_history` to track the last executed timestamp of each top-level package.
- **Leaves Isolation**: Automatically gathers top-level packages using `brew leaves`, preserving dependency chains.

#### Safety Safeguards
- **Install Date Fallback**: Uses the original package installation timestamp if the command does not appear in shell history, protecting newly installed formulas.
- **Grace Period Protection**: Safeguards packages without extended history metadata by defaulting to file modification time.
- **Interactive Confirmation**: Prompts users for explicit approval (`[y/N]`) before any removals occur in `--exorcise` mode.

#### Reporting And Inspection
- **Terminal ASCII Reporting**: Clean formatted tables displaying package name, disk footprint, and idle duration.
- **Dry-Run Inspection**: Safe, default read-only scanning mode.
