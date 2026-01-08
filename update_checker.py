#!/usr/bin/env python3
"""
Project Launcher - Update Checker
Checks GitHub releases for new versions.
"""

import urllib.request
import json
import threading
import webbrowser
from typing import Optional, Callable, Tuple

# Current version - UPDATE THIS ON EACH RELEASE
VERSION = "0.0.12"

# GitHub repository info
GITHUB_REPO = "ClarkeFL/project-launch"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string like 'v0.0.2' or '0.0.2' into tuple of ints."""
    # Remove 'v' prefix if present
    version_str = version_str.lstrip('v')
    try:
        return tuple(int(x) for x in version_str.split('.'))
    except ValueError:
        return (0, 0, 0)


def compare_versions(current: str, latest: str) -> int:
    """
    Compare two version strings.
    Returns: -1 if current < latest, 0 if equal, 1 if current > latest
    """
    current_tuple = parse_version(current)
    latest_tuple = parse_version(latest)
    
    if current_tuple < latest_tuple:
        return -1
    elif current_tuple > latest_tuple:
        return 1
    return 0


def check_for_updates() -> Optional[dict]:
    """
    Check GitHub for latest release.
    Returns dict with version info if update available, None otherwise.
    """
    try:
        request = urllib.request.Request(
            RELEASES_URL,
            headers={
                'User-Agent': 'ProjectLauncher-UpdateChecker',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            latest_version = data.get('tag_name', '')
            
            if compare_versions(VERSION, latest_version) < 0:
                return {
                    'current_version': VERSION,
                    'latest_version': latest_version,
                    'release_name': data.get('name', ''),
                    'release_notes': data.get('body', ''),
                    'download_url': data.get('html_url', DOWNLOAD_URL),
                    'published_at': data.get('published_at', '')
                }
            
            return None
            
    except Exception as e:
        print(f"Update check failed: {e}")
        return None


def check_for_updates_async(callback: Callable[[Optional[dict]], None]) -> None:
    """
    Check for updates in background thread.
    Calls callback with result when done.
    """
    def _check():
        result = check_for_updates()
        callback(result)
    
    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def open_download_page(url: str = None) -> None:
    """Open the download page in default browser."""
    webbrowser.open(url or DOWNLOAD_URL)


def get_current_version() -> str:
    """Return the current version string."""
    return VERSION


if __name__ == "__main__":
    # Test the update checker
    print(f"Current version: {VERSION}")
    print("Checking for updates...")
    
    result = check_for_updates()
    
    if result:
        print(f"\nUpdate available!")
        print(f"  Current: {result['current_version']}")
        print(f"  Latest:  {result['latest_version']}")
        print(f"  Download: {result['download_url']}")
    else:
        print("You're running the latest version!")
