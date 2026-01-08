#!/usr/bin/env python3
"""
Project Launcher - Release Script
Automates version bump, commit, and tag creation.

Usage:
    python release.py           # Interactive mode (prompts for version)
    python release.py 0.0.3     # Direct version
    python release.py --dry-run # Interactive + dry run
"""

import sys
import re
import subprocess
from pathlib import Path


def get_current_version():
    """Read current version from update_checker.py."""
    update_checker = Path(__file__).parent / "update_checker.py"
    content = update_checker.read_text()
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return None


def suggest_next_version(current: str | None) -> dict:
    """Suggest next patch, minor, and major versions."""
    if not current:
        return {"patch": "0.0.1", "minor": "0.1.0", "major": "1.0.0"}
    
    parts = current.split('.')
    if len(parts) != 3:
        return {"patch": "0.0.1", "minor": "0.1.0", "major": "1.0.0"}
    
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return {
            "patch": f"{major}.{minor}.{patch + 1}",
            "minor": f"{major}.{minor + 1}.0",
            "major": f"{major + 1}.0.0"
        }
    except ValueError:
        return {"patch": "0.0.1", "minor": "0.1.0", "major": "1.0.0"}


def update_version(new_version: str) -> bool:
    """Update VERSION in update_checker.py."""
    update_checker = Path(__file__).parent / "update_checker.py"
    content = update_checker.read_text()
    
    # Replace VERSION = "x.x.x" with new version
    new_content = re.sub(
        r'(VERSION\s*=\s*["\'])([^"\']+)(["\'])',
        f'\\g<1>{new_version}\\g<3>',
        content
    )
    
    if new_content == content:
        print("[ERROR] Could not find VERSION in update_checker.py")
        return False
    
    update_checker.write_text(new_content)
    return True


def run_command(cmd: str, dry_run: bool = False) -> bool:
    """Run a shell command."""
    print(f"  $ {cmd}")
    if dry_run:
        print("    (dry-run, skipped)")
        return True
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [ERROR] {result.stderr.strip()}")
        return False
    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            print(f"    {line}")
    return True


def main():
    dry_run = '--dry-run' in sys.argv
    
    # Get current version
    current_version = get_current_version()
    suggestions = suggest_next_version(current_version)
    
    print()
    print("=" * 50)
    print("  PROJECT LAUNCHER - RELEASE")
    print("=" * 50)
    print()
    print(f"  Current version: {current_version or 'unknown'}")
    print()
    print("  Suggested versions:")
    print(f"    patch: {suggestions['patch']}")
    print(f"    minor: {suggestions['minor']}")
    print(f"    major: {suggestions['major']}")
    print()
    
    # Check if version was provided as argument
    new_version = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            new_version = arg.lstrip('v')
            break
    
    # If no version provided, prompt for it
    if not new_version:
        try:
            user_input = input("  Enter new version (or patch/minor/major): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  Cancelled.")
            sys.exit(0)
        
        if not user_input:
            print("  No version entered. Exiting.")
            sys.exit(0)
        
        # Handle shortcuts
        if user_input in suggestions:
            new_version = suggestions[user_input]
        else:
            new_version = user_input.lstrip('v')
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"\n[ERROR] Invalid version format: {new_version}")
        print("Expected format: X.Y.Z (e.g., 0.0.3)")
        sys.exit(1)
    
    print()
    print(f"  New version:     {new_version}")
    if dry_run:
        print("  Mode:            DRY RUN")
    print()
    
    if current_version == new_version:
        print("[ERROR] New version is same as current version")
        sys.exit(1)
    
    # Confirm
    try:
        confirm = input(f"  Release v{new_version}? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n  Cancelled.")
        sys.exit(0)
    
    if confirm not in ('y', 'yes'):
        print("  Cancelled.")
        sys.exit(0)
    
    print()
    
    # Step 1: Update version in update_checker.py
    print("[1/4] Updating version in update_checker.py...")
    if not dry_run:
        if not update_version(new_version):
            sys.exit(1)
    print("    Done")
    print()
    
    # Step 2: Git add
    print("[2/4] Staging changes...")
    if not run_command("git add update_checker.py", dry_run):
        sys.exit(1)
    print()
    
    # Step 3: Git commit
    print("[3/4] Creating commit...")
    if not run_command(f'git commit -m "Release v{new_version}"', dry_run):
        sys.exit(1)
    print()
    
    # Step 4: Create and push tag
    print("[4/4] Creating and pushing tag...")
    if not run_command(f"git tag v{new_version}", dry_run):
        sys.exit(1)
    if not run_command("git push", dry_run):
        sys.exit(1)
    if not run_command("git push --tags", dry_run):
        sys.exit(1)
    print()
    
    print("=" * 50)
    print("  RELEASE COMPLETE!")
    print("=" * 50)
    print()
    print(f"  Version v{new_version} has been released.")
    print()
    print("  GitHub Actions will now build installers for:")
    print(f"    - Windows (ProjectLauncher-Setup-{new_version}.exe)")
    print(f"    - macOS (ProjectLauncher-Installer-{new_version}.dmg)")
    print(f"    - Linux (project-launcher-installer-{new_version})")
    print()
    print(f"  Watch progress: https://github.com/ClarkeFL/project-launch/actions")
    print(f"  Release page:   https://github.com/ClarkeFL/project-launch/releases/tag/v{new_version}")
    print()


if __name__ == "__main__":
    main()
