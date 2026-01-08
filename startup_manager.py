"""
Startup Manager for Project Launcher
Thin wrapper that delegates to platform-specific handlers.

This module provides backward-compatible API while using the new
platform_handlers architecture internally.
"""

import sys
import platform
from pathlib import Path

from platform_handlers import get_platform_handler


def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()


def get_executable_path() -> Path:
    """Get the path to the running executable or script."""
    handler = get_platform_handler()
    return handler._get_executable_path()


def get_app_bundle_path() -> Path | None:
    """Get the .app bundle path on macOS, or None if not in a bundle."""
    if get_platform() != "Darwin" or not getattr(sys, 'frozen', False):
        return None
    
    exe_path = Path(sys.executable)
    parts = exe_path.parts
    for i, part in enumerate(parts):
        if part.endswith('.app'):
            return Path(*parts[:i+1])
    return None


def get_install_dir() -> Path:
    """Get the installation directory."""
    handler = get_platform_handler()
    return handler.get_install_dir()


def is_installed() -> bool:
    """Check if the application is running from the installed location."""
    exe_path = get_executable_path()
    install_dir = get_install_dir()
    
    try:
        exe_path.relative_to(install_dir)
        return True
    except ValueError:
        return False


def get_installed_exe_path() -> Path:
    """Get the path where the exe/app should be installed."""
    handler = get_platform_handler()
    return handler.get_installed_exe_path()


# =============================================================================
# Shortcuts
# =============================================================================

def create_desktop_shortcut() -> bool:
    """Create a desktop shortcut."""
    handler = get_platform_handler()
    return handler.create_desktop_shortcut()


def remove_desktop_shortcut() -> bool:
    """Remove desktop shortcut."""
    handler = get_platform_handler()
    return handler.remove_desktop_shortcut()


def has_desktop_shortcut() -> bool:
    """Check if desktop shortcut exists."""
    handler = get_platform_handler()
    return handler.has_desktop_shortcut()


def create_start_menu_shortcut() -> bool:
    """Create a Start Menu shortcut."""
    handler = get_platform_handler()
    return handler.create_start_menu_shortcut()


def remove_start_menu_shortcut() -> bool:
    """Remove Start Menu shortcut."""
    handler = get_platform_handler()
    return handler.remove_start_menu_shortcut()


def has_start_menu_shortcut() -> bool:
    """Check if Start Menu shortcut exists."""
    handler = get_platform_handler()
    return handler.has_start_menu_shortcut()


# =============================================================================
# Startup
# =============================================================================

def set_startup_enabled(enabled: bool) -> bool:
    """
    Enable or disable startup registration.
    
    Args:
        enabled: True to enable, False to disable
        
    Returns:
        True if successful, False otherwise
    """
    handler = get_platform_handler()
    return handler.set_startup_enabled(enabled)


def is_startup_enabled() -> bool:
    """
    Check if startup is currently enabled.
    
    Returns:
        True if enabled, False otherwise
    """
    handler = get_platform_handler()
    return handler.is_startup_enabled()


def get_startup_location() -> str:
    """
    Get the location where startup files are stored.
    
    Returns:
        Path string to the startup file/folder
    """
    handler = get_platform_handler()
    return handler.get_startup_location()


# =============================================================================
# Installation
# =============================================================================

def install_application(create_desktop: bool = True, create_start_menu: bool = True, 
                        create_startup: bool = True) -> dict:
    """
    Install the application to the standard location.
    
    Returns dict with:
        - success: bool
        - install_path: str (path where installed)
        - error: str (if failed)
    """
    handler = get_platform_handler()
    return handler.install_application(create_desktop, create_start_menu, create_startup)


def uninstall_application(remove_app: bool = False, remove_config: bool = False) -> dict:
    """
    Uninstall the application.
    
    Args:
        remove_app: Whether to remove the application files
        remove_config: Whether to remove config/data files
    
    Returns dict with:
        - success: bool
        - error: str (if failed)
    """
    handler = get_platform_handler()
    return handler.uninstall_application(remove_app, remove_config)


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print(f"Executable path: {get_executable_path()}")
    print(f"Install directory: {get_install_dir()}")
    print(f"Installed exe path: {get_installed_exe_path()}")
    print(f"Is installed: {is_installed()}")
    print(f"Startup enabled: {is_startup_enabled()}")
    print(f"Startup location: {get_startup_location()}")
    print(f"Desktop shortcut: {has_desktop_shortcut()}")
    print(f"Start Menu shortcut: {has_start_menu_shortcut()}")
