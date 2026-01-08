"""
Startup Manager for Project Launcher
Handles cross-platform startup registration (Windows, macOS, Linux).
Uses Registry on Windows (no admin required).
"""

import os
import sys
import platform
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
# Windows Startup (Registry - no admin required)
# =============================================================================

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REGISTRY_VALUE_NAME = "ProjectLauncher"


def _get_windows_startup_folder() -> Path:
    """Get Windows startup folder path (for cleanup)."""
    startup = os.environ.get("APPDATA", "")
    if startup:
        return Path(startup) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _cleanup_legacy_startup() -> None:
    """Remove old startup methods (VBS files, Task Scheduler, etc.)."""
    import subprocess
    
    # Remove old VBS from Startup folder
    try:
        vbs_path = _get_windows_startup_folder() / "ProjectLauncher.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
    except Exception:
        pass
    
    # Remove old batch/vbs files from project directory
    try:
        working_dir = get_script_path().parent
        for old_file in ["startup_task.bat", "startup_silent.vbs"]:
            old_path = working_dir / old_file
            if old_path.exists():
                old_path.unlink()
    except Exception:
        pass
    
    # Remove any existing Task Scheduler entry (best effort, may fail without admin)
    try:
        subprocess.run(
            ["schtasks", "/delete", "/tn", "ProjectLauncher", "/f"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception:
        pass


def _enable_registry_startup() -> bool:
    """Create startup using Registry Run key (no admin required)."""
    try:
        import winreg
        
        script_path = get_script_path()
        python_exe = get_python_executable()
        
        # Use pythonw.exe (no console window) if available
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        if not Path(pythonw_exe).exists():
            pythonw_exe = python_exe
        
        # Create startup command - run Python directly
        startup_command = f'"{pythonw_exe}" "{script_path}" --auto'
        
        # Add to registry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, REGISTRY_VALUE_NAME, 0, winreg.REG_SZ, startup_command)
        winreg.CloseKey(key)
        
        return True
    except Exception as e:
        print(f"Registry startup setup failed: {e}")
        return False


def _is_registry_enabled() -> bool:
    """Check if Registry startup is enabled."""
    try:
        import winreg
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_READ
        )
        
        try:
            winreg.QueryValueEx(key, REGISTRY_VALUE_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def _remove_registry_startup() -> None:
    """Remove Registry startup entry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, REGISTRY_VALUE_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass


def _enable_windows_startup() -> bool:
    """Enable startup on Windows using Registry."""
    # Clean up any legacy startup methods
    _cleanup_legacy_startup()
    
    # Use Registry (works without admin)
    return _enable_registry_startup()


def _disable_windows_startup() -> bool:
    """Disable startup on Windows."""
    # Remove Registry entry
    _remove_registry_startup()
    
    # Clean up legacy files
    _cleanup_legacy_startup()
    
    return True


def _is_windows_startup_enabled() -> bool:
    """Check if Windows startup is enabled."""
    return _is_registry_enabled()


def _get_windows_startup_method() -> str:
    """Get which startup method is currently active."""
    if _is_registry_enabled():
        return "Registry (Windows Startup)"
    return "None"


# =============================================================================
# macOS Startup
# =============================================================================

def _get_macos_launch_agent_path() -> Path:
    """Get path to the macOS LaunchAgent plist."""
    return Path.home() / "Library" / "LaunchAgents" / "com.projectlauncher.plist"


def _enable_macos_startup() -> bool:
    """Enable startup on macOS using LaunchAgent."""
    try:
        import subprocess
        
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = get_script_path()
        python_exe = get_python_executable()
        working_dir = script_path.parent
        
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
        <string>--auto</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{working_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>LaunchOnlyOnce</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/projectlauncher.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/projectlauncher.err</string>
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
        import subprocess
        
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
        working_dir = script_path.parent
        
        # Create .desktop file
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch development projects
Exec="{python_exe}" "{script_path}" --auto
Path={working_dir}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Terminal=false
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
        return _get_windows_startup_method()
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
    print(f"Startup enabled: {is_startup_enabled()}")
    print(f"Startup method: {get_startup_location()}")
    
    # Test enabling/disabling
    print("\nTesting startup registration...")
    if not is_startup_enabled():
        print("Enabling startup...")
        set_startup_enabled(True)
        print(f"Startup enabled: {is_startup_enabled()}")
        print(f"Method: {get_startup_location()}")
    else:
        print("Startup already enabled.")
        print(f"Method: {get_startup_location()}")
