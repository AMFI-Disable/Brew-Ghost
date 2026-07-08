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

def analyze_ghosts(packages, metadata, history_path):
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

    # Precompile search patterns for efficiency
    pkg_chars = r"a-zA-Z0-9\-_\+\.@"
    pkg_patterns = {
        pkg: re.compile(rf"(?<![{pkg_chars}]){re.escape(pkg)}(?![{pkg_chars}])")
        for pkg in packages
    }

    remaining_packages = set(packages)
    
    # Analyze history
    for entry_timestamp, cmd_str in history_entries:
        if not remaining_packages:
            break
            
        found_in_entry = []
        for pkg in remaining_packages:
            if pkg in cmd_str:  # Quick substring optimization
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
    if history_entries:
        has_timestamps = any(ts is not None for ts, _ in history_entries)
        if not has_timestamps:
            print("Warning: Zsh history does not contain timestamps (EXTENDED_HISTORY is off).", file=sys.stderr)
            print("Ghost detection falls back to package installation times for unused commands.\n", file=sys.stderr)

    current_time = time.time()
    ghosts = []

    for pkg in packages:
        ts = last_active[pkg]
        days_idle = int((current_time - ts) / SECONDS_IN_A_DAY)
        # Cap days_idle at 0 to handle clock skew/timezone drift
        days_idle = max(0, days_idle)
        
        if days_idle > IDLE_THRESHOLD_DAYS:
            # Gather size info
            pkg_size = get_package_size(pkg, metadata.get(pkg, {}))
            ghosts.append({
                'name': pkg,
                'days_idle': days_idle,
                'size': pkg_size
            })

    # Sort ghosts by size descending for highest impact removal representation
    ghosts.sort(key=lambda g: g['size'], reverse=True)
    return ghosts

def print_help():
    """Print command line usage help."""
    help_text = """brew-ghost - A behavioral cleanup tool for Homebrew

Usage:
  brew-ghost [options]

Options:
  --exorcise   Safely purge packages that have been idle for over 90 days.
  -h, --help   Show this help message and exit.
"""
    print(help_text)

def main():
    # Handle basic arguments
    exorcise_mode = False
    for arg in sys.argv[1:]:
        if arg in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif arg == '--exorcise':
            exorcise_mode = True
        else:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            print_help()
            sys.exit(1)

    history_file = os.path.expanduser('~/.zsh_history')
    
    print("Searching for absolute freeloaders in your Cellar...\n")
    
    packages = get_installed_leaves()
    if not packages:
        print("No packages found in your Cellar! 🌟")
        sys.exit(0)
        
    metadata = get_packages_metadata(packages)
    ghosts = analyze_ghosts(packages, metadata, history_file)
    
    if not ghosts:
        print("No ghostly packages found in your Cellar! 🌟")
        sys.exit(0)

    # Render Table
    print(f"{'Formula':<14}{'Size':<10}{'Last Active':<15}{'Status':<12}")
    print("─" * 58)
    
    total_size = 0
    for g in ghosts:
        total_size += g['size']
        size_str = format_size(g['size'])
        last_active_str = f"{g['days_idle']} days ago"
        print(f"{g['name']:<14}{size_str:<10}{last_active_str:<15}{'Ghostly 👻':<12}")
        
    print("─" * 58)
    print(f"\nTotal potential space recovered: {format_size(total_size)}")

    if exorcise_mode:
        ghost_names = [g['name'] for g in ghosts]
        print(f"\nThe following packages will be uninstalled: {', '.join(ghost_names)}")
        try:
            confirm = input("Are you sure you want to exorcise these ghosts? (y/N): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)
            
        if confirm in ('y', 'yes'):
            print("\nExorcising ghosts...")
            for pkg_name in ghost_names:
                print(f"\nUninstalling {pkg_name}...")
                try:
                    subprocess.run(['brew', 'uninstall', pkg_name], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error during uninstall of {pkg_name}: {e}", file=sys.stderr)
            print("\nExorcism complete! Cellar is clean. 🧹✨")
        else:
            print("\nExorcism aborted. Ghosts remain in the Cellar.")
    else:
        print("Run `brew-ghost --exorcise` to safely purge these ghosts.")

if __name__ == '__main__':
    main()
