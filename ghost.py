#!/usr/bin/env python3
"""
ghost.py - Core engine of the brew-ghost utility.
Identifies and purges "ghost" Homebrew packages (packages not used in > 90 days).
"""

import sys
import os
import re
import subprocess
import json
import time

import datetime

CONFIG_DIR = os.path.expanduser('~/.config/brew-ghost')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

def get_formula_executables(pkg, pkg_metadata):
    """Retrieve list of executable names installed by the formula in its bin directory."""
    executables = {pkg}
    cellar = get_cellar_path()
    version = pkg_metadata.get('version')
    linked_keg = pkg_metadata.get('linked_keg')
    
    version_dir = version or linked_keg
    if version_dir:
        bin_dir = os.path.join(cellar, pkg, version_dir, 'bin')
        if os.path.isdir(bin_dir):
            try:
                for entry in os.listdir(bin_dir):
                    entry_path = os.path.join(bin_dir, entry)
                    if os.path.isfile(entry_path) and os.access(entry_path, os.X_OK):
                        executables.add(entry)
            except OSError:
                pass
    return list(executables)

# Threshold for marking a package as a ghost (in days)
IDLE_THRESHOLD_DAYS = 90
SECONDS_IN_A_DAY = 86400

def get_installed_leaves():
    """Run `brew leaves` to get top-level packages installed by the user."""
    try:
        res = subprocess.run(['brew', 'leaves'], capture_output=True, text=True, check=True)
        packages = [line.strip() for line in res.stdout.split('\n') if line.strip()]
        return packages
    except subprocess.SubprocessError as e:
        print(f"Error executing `brew leaves`: {e}", file=sys.stderr)
        sys.exit(1)

def get_packages_metadata(packages):
    """Run `brew info --json=v2` to get metadata for all specified packages."""
    metadata = {}
    if not packages:
        return metadata

    # Attempt to query all packages in a single bulk call for speed
    try:
        cmd = ['brew', 'info', '--json=v2'] + packages
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        
        for formula in data.get('formulae', []):
            name = formula.get('name')
            installed_list = formula.get('installed', [])
            if installed_list:
                installed = installed_list[0]
                metadata[name] = {
                    'version': installed.get('version'),
                    'install_time': installed.get('time') or 0,
                    'size': installed.get('size'),
                    'linked_keg': formula.get('linked_keg')
                }
    except Exception:
        # Fall back to querying packages individually if the bulk call fails
        for pkg in packages:
            try:
                cmd = ['brew', 'info', '--json=v2', pkg]
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(res.stdout)
                formulae = data.get('formulae', [])
                if formulae:
                    formula = formulae[0]
                    installed_list = formula.get('installed', [])
                    if installed_list:
                        installed = installed_list[0]
                        metadata[pkg] = {
                            'version': installed.get('version'),
                            'install_time': installed.get('time') or 0,
                            'size': installed.get('size'),
                            'linked_keg': formula.get('linked_keg')
                        }
            except Exception:
                metadata[pkg] = {
                    'version': None,
                    'install_time': 0,
                    'size': None,
                    'linked_keg': None
                }
    return metadata

_cellar_cache = None
def get_cellar_path():
    """Retrieve the Homebrew Cellar path dynamically, caching the result."""
    global _cellar_cache
    if _cellar_cache is not None:
        return _cellar_cache
    try:
        res = subprocess.run(['brew', '--cellar'], capture_output=True, text=True, check=True)
        _cellar_cache = res.stdout.strip()
        return _cellar_cache
    except Exception:
        if os.path.exists('/opt/homebrew/Cellar'):
            _cellar_cache = '/opt/homebrew/Cellar'
        elif os.path.exists('/usr/local/Cellar'):
            _cellar_cache = '/usr/local/Cellar'
        else:
            _cellar_cache = '/opt/homebrew/Cellar'
        return _cellar_cache

def calculate_directory_size(path):
    """Calculate total size of files under the given directory in bytes."""
    total_size = 0
    if not os.path.isdir(path):
        return 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.islink(file_path):
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass
    return total_size

def get_package_size(pkg, pkg_metadata):
    """Get size of the package, falling back to directory calculation if size key is missing."""
    size = pkg_metadata.get('size')
    if size is not None:
        return int(size)

    cellar = get_cellar_path()
    version = pkg_metadata.get('version')
    linked_keg = pkg_metadata.get('linked_keg')
    
    version_dir = version or linked_keg
    if version_dir:
        pkg_dir = os.path.join(cellar, pkg, version_dir)
        if os.path.isdir(pkg_dir):
            return calculate_directory_size(pkg_dir)

    pkg_root = os.path.join(cellar, pkg)
    if os.path.isdir(pkg_root):
        total = 0
        try:
            for entry in os.listdir(pkg_root):
                entry_path = os.path.join(pkg_root, entry)
                if os.path.isdir(entry_path) and not os.path.islink(entry_path):
                    total += calculate_directory_size(entry_path)
            return total
        except OSError:
            pass
            
    return 0

def parse_zsh_history(history_path):
    """Parse Zsh history file into (timestamp, command) tuples."""
    history_entries = []
    if not os.path.exists(history_path):
        return history_entries
        
    pattern = re.compile(r'^:\s*(\d+):\d+;(.*)$')
    
    try:
        with open(history_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        current_timestamp = None
        current_cmd = []
        
        for line in lines:
            line = line.rstrip('\r\n')
            match = pattern.match(line)
            if match:
                if current_timestamp is not None:
                    history_entries.append((current_timestamp, "\n".join(current_cmd)))
                current_timestamp = int(match.group(1))
                current_cmd = [match.group(2)]
            else:
                if current_timestamp is not None:
                    current_cmd.append(line)
                else:
                    # Handle raw history formats without timestamps
                    history_entries.append((None, line))
                    
        if current_timestamp is not None:
            history_entries.append((current_timestamp, "\n".join(current_cmd)))
            
    except Exception:
        pass
        
    return history_entries

def format_size(bytes_size):
    """Format bytes into readable MB or GB strings."""
    if bytes_size is None or bytes_size == 0:
        return "0 MB"
    mb = bytes_size / (1024 * 1024)
    if mb >= 1024:
        gb = mb / 1024
        return f"{gb:.1f} GB"
    # Match layout specifications (e.g. integer MB or rounded floats)
    if mb >= 10:
        return f"{int(round(mb))} MB"
    return f"{mb:.1f} MB"

def analyze_ghosts(packages, metadata, history_path, threshold_days=90):
    """Correlate shell history and install times to find ghost packages."""
    history_entries = parse_zsh_history(history_path)
    # Reverse so we search newest to oldest
    history_entries.reverse()

    # Track last active timestamp. Fallback is the package installation time.
    last_active = {}
    for pkg in packages:
        val = metadata.get(pkg, {}).get('install_time')
        last_active[pkg] = val if val is not None else 0

    # File modification time for fallback when extended history is missing
    history_mtime = int(os.path.getmtime(history_path)) if os.path.exists(history_path) else int(time.time())

    # Precompile search patterns and cache executables for efficiency
    pkg_chars = r"a-zA-Z0-9\-_\+\.@"
    pkg_patterns = {}
    pkg_executables = {}
    for pkg in packages:
        execs = get_formula_executables(pkg, metadata.get(pkg, {}))
        pkg_executables[pkg] = execs
        pattern_str = "|".join(re.escape(e) for e in execs)
        pkg_patterns[pkg] = re.compile(rf"(?<![{pkg_chars}])(?:{pattern_str})(?![{pkg_chars}])")

    remaining_packages = set(packages)
    
    # Analyze history
    for entry_timestamp, cmd_str in history_entries:
        if not remaining_packages:
            break
            
        found_in_entry = []
        for pkg in remaining_packages:
            if any(e in cmd_str for e in pkg_executables[pkg]):  # Quick substring optimization
                if pkg_patterns[pkg].search(cmd_str):
                    # If extended history timestamp is missing, use history file mtime
                    ts = entry_timestamp if entry_timestamp is not None else history_mtime
                    # Only update if the found time is newer than what we currently have
                    if ts > last_active[pkg]:
                        last_active[pkg] = ts
                    found_in_entry.append(pkg)
                    
        # Remove found packages from active search set to speed up lookup
        for pkg in found_in_entry:
            remaining_packages.remove(pkg)

    # Check for warning condition: Zsh history exists, but has no timestamps
    has_history_timestamps = True
    if history_entries:
        has_timestamps = any(ts is not None for ts, _ in history_entries)
        if not has_timestamps:
            has_history_timestamps = False

    current_time = time.time()
    ghosts = []

    for pkg in packages:
        ts = last_active[pkg]
        days_idle = int((current_time - ts) / SECONDS_IN_A_DAY)
        # Cap days_idle at 0 to handle clock skew/timezone drift
        days_idle = max(0, days_idle)
        
        if days_idle > threshold_days:
            # Gather size info
            pkg_size = get_package_size(pkg, metadata.get(pkg, {}))
            ghosts.append({
                'name': pkg,
                'days_idle': days_idle,
                'size': pkg_size
            })

    # Sort ghosts by size descending for highest impact removal representation
    ghosts.sort(key=lambda g: g['size'], reverse=True)
    return ghosts, has_history_timestamps

class Color:
    # Check if stdout is a tty to decide if we should use colors
    ENABLED = sys.stdout.isatty()
    
    # ANSI Codes
    RESET = "\033[0m" if ENABLED else ""
    BOLD = "\033[1m" if ENABLED else ""
    DIM = "\033[2m" if ENABLED else ""
    
    RED = "\033[31m" if ENABLED else ""
    GREEN = "\033[32m" if ENABLED else ""
    YELLOW = "\033[33m" if ENABLED else ""
    BLUE = "\033[34m" if ENABLED else ""
    MAGENTA = "\033[35m" if ENABLED else ""
    CYAN = "\033[36m" if ENABLED else ""
    WHITE = "\033[37m" if ENABLED else ""
    GRAY = "\033[90m" if ENABLED else ""
    
    # Semantic colors
    HEADER = BOLD + CYAN
    SEPARATOR = GRAY
    ROW_NAME = YELLOW
    ROW_IDLE = RED
    SPACE = BOLD + GREEN
    SUCCESS = BOLD + GREEN
    WARN = BOLD + YELLOW

def print_help():
    """Print command line usage help."""
    help_text = f"""brew-ghost - A behavioral cleanup tool for Homebrew

Usage:
  brew-ghost [options]

Options:
  -d, --days <days>  Configure the threshold of inactivity to flag a ghost (1 to 180 days). Default is 90.
  --exorcise         Safely purge packages that have been idle for over the specified threshold.
  -h, --help         Show this help message and exit.
"""
    print(help_text)

def main():
    # Handle basic arguments
    exorcise_mode = False
    config = load_config()
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif arg == '--exorcise':
            exorcise_mode = True
            i += 1
        elif arg in ('-d', '--days'):
            if i + 1 >= len(args):
                print(f"{Color.RED}Error: --days requires an integer value between 1 and 180.{Color.RESET}", file=sys.stderr)
                sys.exit(1)
            val_str = args[i+1]
            try:
                val = int(val_str)
                if val < 1 or val > 180:
                    raise ValueError()
                config['days_threshold'] = val
                save_config(config)
                print(f"{Color.SUCCESS}Settings updated: Inactivity threshold set to {val} days.{Color.RESET}")
                sys.exit(0)
            except ValueError:
                print(f"{Color.RED}Error: Invalid days value '{val_str}'. Must be an integer between 1 and 180.{Color.RESET}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"{Color.RED}Unknown argument: {arg}{Color.RESET}", file=sys.stderr)
            print_help()
            sys.exit(1)

    idle_threshold_days = config.get('days_threshold', 90)
    history_file = os.path.expanduser('~/.zsh_history')
    
    print("Searching for absolute freeloaders in your Cellar...\n")
    
    packages = get_installed_leaves()
    if not packages:
        print(f"{Color.SUCCESS}No packages found in your Cellar! 🌟{Color.RESET}")
        sys.exit(0)
        
    metadata = get_packages_metadata(packages)
    ghosts, has_history_timestamps = analyze_ghosts(packages, metadata, history_file, idle_threshold_days)
    
    # Handle warning prompt for extended history
    if not has_history_timestamps:
        current_time = int(time.time())
        mute_until = config.get('extended_history_mute_until', 0)
        
        # Only prompt if not configured yet AND mute duration has expired
        if not config.get('extended_history_configured') and current_time >= mute_until:
            print(f"{Color.WARN}Warning: Zsh history does not contain timestamps (EXTENDED_HISTORY is off).{Color.RESET}", file=sys.stderr)
            print("Ghost detection falls back to package installation times for unused commands.\n", file=sys.stderr)
            
            # Check if stdin is a tty to ask the user
            if sys.stdin.isatty() and sys.stdout.isatty():
                try:
                    confirm = input(f"Would you like to enable extended history in ~/.zshrc automatically? (y/N): ").strip().lower()
                    if confirm in ('y', 'yes'):
                        zshrc_path = os.path.expanduser('~/.zshrc')
                        with open(zshrc_path, 'a') as f:
                            f.write("\n# Enable extended history timestamps for brew-ghost\nsetopt EXTENDED_HISTORY\n")
                        print(f"\n{Color.SUCCESS}Extended history has been enabled in ~/.zshrc! 🎉{Color.RESET}")
                        print(f"Please open a new terminal session or run '{Color.BOLD}source ~/.zshrc{Color.RESET}' to apply changes.\n")
                        config['extended_history_configured'] = True
                        save_config(config)
                    else:
                        # Mute for 7 days
                        config['extended_history_mute_until'] = current_time + (7 * 24 * 3600)
                        save_config(config)
                        mute_date = datetime.datetime.fromtimestamp(config['extended_history_mute_until']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"\nExtended history prompt muted for 7 days (until {mute_date}).\n")
                except (KeyboardInterrupt, EOFError):
                    print()
        else:
            # If muted or configured, just log the warning without prompting
            print(f"{Color.WARN}Warning: Zsh history does not contain timestamps (EXTENDED_HISTORY is off).{Color.RESET}", file=sys.stderr)
            print("Ghost detection falls back to package installation times for unused commands.\n", file=sys.stderr)
    
    if not ghosts:
        print(f"{Color.SUCCESS}No ghostly packages found in your Cellar! 🌟{Color.RESET}")
        sys.exit(0)

    # Render Table
    print(f"{Color.HEADER}{'Formula':<14}{'Size':<10}{'Last Active':<15}{'Status':<12}{Color.RESET}")
    print(f"{Color.SEPARATOR}{'─' * 58}{Color.RESET}")
    
    total_size = 0
    for g in ghosts:
        total_size += g['size']
        size_str = format_size(g['size'])
        last_active_str = f"{g['days_idle']} days ago"
        print(f"{Color.ROW_NAME}{g['name']:<14}{Color.RESET}{size_str:<10}{Color.ROW_IDLE}{last_active_str:<15}{Color.ROW_IDLE}{'Ghostly 👻':<12}{Color.RESET}")
        
    print(f"{Color.SEPARATOR}{'─' * 58}{Color.RESET}")
    print(f"\nTotal potential space recovered: {Color.SPACE}{format_size(total_size)}{Color.RESET}")

    if exorcise_mode:
        ghost_names = [g['name'] for g in ghosts]
        print(f"\nThe following packages will be uninstalled: {Color.WARN}{', '.join(ghost_names)}{Color.RESET}")
        try:
            confirm = input(f"{Color.BOLD}Are you sure you want to exorcise these ghosts? (y/N): {Color.RESET}").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)
            
        if confirm in ('y', 'yes'):
            print(f"\n{Color.BOLD}Exorcising ghosts...{Color.RESET}")
            for pkg_name in ghost_names:
                print(f"\nUninstalling {Color.ROW_NAME}{pkg_name}{Color.RESET}...")
                try:
                    subprocess.run(['brew', 'uninstall', pkg_name], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"{Color.RED}Error during uninstall of {pkg_name}: {e}{Color.RESET}", file=sys.stderr)
            print(f"\n{Color.SUCCESS}Exorcism complete! Cellar is clean. 🧹✨{Color.RESET}")
        else:
            print("\nExorcism aborted. Ghosts remain in the Cellar.")
    else:
        print(f"Run {Color.BOLD}brew-ghost --exorcise{Color.RESET} to safely purge these ghosts.")

if __name__ == '__main__':
    main()
