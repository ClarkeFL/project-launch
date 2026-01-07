"""
Startup Manager for Project Launcher
Handles cross-platform startup registration (Windows, macOS, Linux).
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()


def get_script_path() -> Path:
    """Get the path to the main launcher script."""
    return Path(__file__).parent / "project_launcher.py"


def get_python_executable() -> str:
    """Get the Python executable path."""
    return sys.executable


# =============================================================================
# Windows Startup
# =============================================================================

def _get_windows_startup_folder() -> Path:
    """Get Windows startup folder path."""
    startup = os.environ.get("APPDATA", "")
    if startup:
        return Path(startup) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _get_windows_shortcut_path() -> Path:
    """Get path to the Windows shortcut."""
    return _get_windows_startup_folder() / "ProjectLauncher.vbs"


def _enable_windows_startup() -> bool:
    """Enable startup on Windows using VBS script (more reliable than shortcuts)."""
    try:
        startup_folder = _get_windows_startup_folder()
        startup_folder.mkdir(parents=True, exist_ok=True)
        
        script_path = get_script_path()
        python_exe = get_python_executable()
        
        # Create a VBS script that launches Python without showing a console window
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{python_exe}"" ""{script_path}""", 0, False
'''
        
        vbs_path = _get_windows_shortcut_path()
        with open(vbs_path, "w") as f:
            f.write(vbs_content)
        
        return True
    except Exception as e:
        print(f"Error enabling Windows startup: {e}")
        return False


def _disable_windows_startup() -> bool:
    """Disable startup on Windows."""
    try:
        vbs_path = _get_windows_shortcut_path()
        if vbs_path.exists():
            vbs_path.unlink()
        return True
    except Exception as e:
        print(f"Error disabling Windows startup: {e}")
        return False


def _is_windows_startup_enabled() -> bool:
    """Check if Windows startup is enabled."""
    return _get_windows_shortcut_path().exists()


# =============================================================================
# macOS Startup
# =============================================================================

def _get_macos_launch_agent_path() -> Path:
    """Get path to the macOS LaunchAgent plist."""
    return Path.home() / "Library" / "LaunchAgents" / "com.projectlauncher.plist"


def _enable_macos_startup() -> bool:
    """Enable startup on macOS using LaunchAgent."""
    try:
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = get_script_path()
        python_exe = get_python_executable()
        
        # Create LaunchAgent plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.projectlauncher</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>LaunchOnlyOnce</key>
    <true/>
</dict>
</plist>
'''
        
        plist_path = _get_macos_launch_agent_path()
        with open(plist_path, "w") as f:
            f.write(plist_content)
        
        # Load the LaunchAgent
        subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
        
        return True
    except Exception as e:
        print(f"Error enabling macOS startup: {e}")
        return False


def _disable_macos_startup() -> bool:
    """Disable startup on macOS."""
    try:
        plist_path = _get_macos_launch_agent_path()
        
        if plist_path.exists():
            # Unload the LaunchAgent
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink()
        
        return True
    except Exception as e:
        print(f"Error disabling macOS startup: {e}")
        return False


def _is_macos_startup_enabled() -> bool:
    """Check if macOS startup is enabled."""
    return _get_macos_launch_agent_path().exists()


# =============================================================================
# Linux Startup
# =============================================================================

def _get_linux_autostart_path() -> Path:
    """Get path to the Linux autostart .desktop file."""
    config_home = os.environ.get("XDG_CONFIG_HOME", "")
    if not config_home:
        config_home = Path.home() / ".config"
    else:
        config_home = Path(config_home)
    
    return config_home / "autostart" / "project-launcher.desktop"


def _enable_linux_startup() -> bool:
    """Enable startup on Linux using XDG autostart."""
    try:
        autostart_dir = _get_linux_autostart_path().parent
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = get_script_path()
        python_exe = get_python_executable()
        
        # Create .desktop file
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch development projects
Exec={python_exe} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
        
        desktop_path = _get_linux_autostart_path()
        with open(desktop_path, "w") as f:
            f.write(desktop_content)
        
        # Make it executable
        os.chmod(desktop_path, 0o755)
        
        return True
    except Exception as e:
        print(f"Error enabling Linux startup: {e}")
        return False


def _disable_linux_startup() -> bool:
    """Disable startup on Linux."""
    try:
        desktop_path = _get_linux_autostart_path()
        if desktop_path.exists():
            desktop_path.unlink()
        return True
    except Exception as e:
        print(f"Error disabling Linux startup: {e}")
        return False


def _is_linux_startup_enabled() -> bool:
    """Check if Linux startup is enabled."""
    return _get_linux_autostart_path().exists()


# =============================================================================
# Public API
# =============================================================================

def set_startup_enabled(enabled: bool) -> bool:
    """
    Enable or disable startup registration.
    
    Args:
        enabled: True to enable, False to disable
        
    Returns:
        True if successful, False otherwise
    """
    system = get_platform()
    
    if system == "Windows":
        if enabled:
            return _enable_windows_startup()
        else:
            return _disable_windows_startup()
    elif system == "Darwin":
        if enabled:
            return _enable_macos_startup()
        else:
            return _disable_macos_startup()
    else:  # Linux
        if enabled:
            return _enable_linux_startup()
        else:
            return _disable_linux_startup()


def is_startup_enabled() -> bool:
    """
    Check if startup is currently enabled.
    
    Returns:
        True if enabled, False otherwise
    """
    system = get_platform()
    
    if system == "Windows":
        return _is_windows_startup_enabled()
    elif system == "Darwin":
        return _is_macos_startup_enabled()
    else:  # Linux
        return _is_linux_startup_enabled()


def get_startup_location() -> str:
    """
    Get the location where startup files are stored.
    
    Returns:
        Path string to the startup file/folder
    """
    system = get_platform()
    
    if system == "Windows":
        return str(_get_windows_shortcut_path())
    elif system == "Darwin":
        return str(_get_macos_launch_agent_path())
    else:  # Linux
        return str(_get_linux_autostart_path())


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print(f"Script path: {get_script_path()}")
    print(f"Python executable: {get_python_executable()}")
    print(f"Startup location: {get_startup_location()}")
    print(f"Startup enabled: {is_startup_enabled()}")
    
    # Test enabling/disabling
    print("\nTesting startup registration...")
    if not is_startup_enabled():
        print("Enabling startup...")
        set_startup_enabled(True)
        print(f"Startup enabled: {is_startup_enabled()}")
    else:
        print("Startup already enabled.")
