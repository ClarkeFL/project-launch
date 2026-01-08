"""
Startup Manager for Project Launcher
Handles cross-platform startup registration and shortcut creation.
Uses Startup Folder on Windows (no registry, no admin required).
"""

import os
import sys
import platform
import shutil
from pathlib import Path


def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()


def get_executable_path() -> Path:
    """Get the path to the running executable or script."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable)
    else:
        # Running as script
        return Path(__file__).parent / "project_launcher.py"


def get_install_dir() -> Path:
    """Get the installation directory."""
    if get_platform() == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ProjectLauncher"
    elif get_platform() == "Darwin":
        return Path.home() / "Applications" / "ProjectLauncher"
    else:  # Linux
        return Path.home() / ".local" / "share" / "ProjectLauncher"


def is_installed() -> bool:
    """Check if the application is running from the installed location."""
    exe_path = get_executable_path()
    install_dir = get_install_dir()
    
    try:
        # Check if current exe is inside the install directory
        exe_path.relative_to(install_dir)
        return True
    except ValueError:
        return False


def get_installed_exe_path() -> Path:
    """Get the path where the exe should be installed."""
    install_dir = get_install_dir()
    if get_platform() == "Windows":
        return install_dir / "ProjectLauncher.exe"
    elif get_platform() == "Darwin":
        return install_dir / "ProjectLauncher"
    else:  # Linux
        return install_dir / "project-launcher"


# =============================================================================
# Windows Shortcuts (using win32com or PowerShell fallback)
# =============================================================================

def _get_windows_startup_folder() -> Path:
    """Get Windows startup folder path."""
    startup = os.environ.get("APPDATA", "")
    if startup:
        return Path(startup) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _get_windows_desktop_folder() -> Path:
    """Get Windows desktop folder path."""
    return Path.home() / "Desktop"


def _get_windows_start_menu_folder() -> Path:
    """Get Windows Start Menu programs folder path."""
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def _create_windows_shortcut(shortcut_path: Path, target_path: Path, description: str = "", icon_path: Path | None = None) -> bool:
    """Create a Windows .lnk shortcut file."""
    try:
        # Try using win32com first (most reliable)
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(target_path)
            shortcut.WorkingDirectory = str(target_path.parent)
            shortcut.Description = description
            if icon_path and icon_path.exists():
                shortcut.IconLocation = str(icon_path)
            shortcut.save()
            return True
        except ImportError:
            pass
        
        # Fallback: Use PowerShell to create shortcut
        import subprocess
        
        ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.WorkingDirectory = "{target_path.parent}"
$Shortcut.Description = "{description}"
$Shortcut.Save()
'''
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


def _remove_windows_shortcut(shortcut_path: Path) -> bool:
    """Remove a Windows shortcut file."""
    try:
        if shortcut_path.exists():
            shortcut_path.unlink()
        return True
    except Exception as e:
        print(f"Error removing shortcut: {e}")
        return False


def _cleanup_legacy_windows_startup() -> None:
    """Remove old startup methods (Registry, VBS files, Task Scheduler)."""
    # Remove old VBS from Startup folder
    try:
        vbs_path = _get_windows_startup_folder() / "ProjectLauncher.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
    except Exception:
        pass
    
    # Remove Registry entry if exists
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, "ProjectLauncher")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Remove Task Scheduler entry (best effort)
    try:
        import subprocess
        subprocess.run(
            ["schtasks", "/delete", "/tn", "ProjectLauncher", "/f"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
    except Exception:
        pass


# =============================================================================
# Windows Startup (Startup Folder - no registry, no admin)
# =============================================================================

def _enable_windows_startup() -> bool:
    """Enable startup on Windows using Startup Folder shortcut."""
    # Clean up any legacy startup methods first
    _cleanup_legacy_windows_startup()
    
    exe_path = get_executable_path()
    if not exe_path.exists():
        return False
    
    startup_folder = _get_windows_startup_folder()
    startup_folder.mkdir(parents=True, exist_ok=True)
    
    shortcut_path = startup_folder / "ProjectLauncher.lnk"
    return _create_windows_shortcut(shortcut_path, exe_path, "Project Launcher - Launch your projects")


def _disable_windows_startup() -> bool:
    """Disable startup on Windows."""
    # Clean up legacy methods
    _cleanup_legacy_windows_startup()
    
    # Remove startup folder shortcut
    shortcut_path = _get_windows_startup_folder() / "ProjectLauncher.lnk"
    return _remove_windows_shortcut(shortcut_path)


def _is_windows_startup_enabled() -> bool:
    """Check if Windows startup is enabled (shortcut exists in Startup folder)."""
    shortcut_path = _get_windows_startup_folder() / "ProjectLauncher.lnk"
    return shortcut_path.exists()


# =============================================================================
# Windows Desktop & Start Menu Shortcuts
# =============================================================================

def create_desktop_shortcut() -> bool:
    """Create a desktop shortcut (Windows only for now)."""
    if get_platform() != "Windows":
        return False
    
    exe_path = get_executable_path()
    if not exe_path.exists():
        return False
    
    desktop = _get_windows_desktop_folder()
    shortcut_path = desktop / "Project Launcher.lnk"
    return _create_windows_shortcut(shortcut_path, exe_path, "Project Launcher")


def remove_desktop_shortcut() -> bool:
    """Remove desktop shortcut."""
    if get_platform() != "Windows":
        return False
    
    shortcut_path = _get_windows_desktop_folder() / "Project Launcher.lnk"
    return _remove_windows_shortcut(shortcut_path)


def has_desktop_shortcut() -> bool:
    """Check if desktop shortcut exists."""
    if get_platform() != "Windows":
        return False
    
    shortcut_path = _get_windows_desktop_folder() / "Project Launcher.lnk"
    return shortcut_path.exists()


def create_start_menu_shortcut() -> bool:
    """Create a Start Menu shortcut (Windows only for now)."""
    if get_platform() != "Windows":
        return False
    
    exe_path = get_executable_path()
    if not exe_path.exists():
        return False
    
    start_menu = _get_windows_start_menu_folder()
    start_menu.mkdir(parents=True, exist_ok=True)
    
    shortcut_path = start_menu / "Project Launcher.lnk"
    return _create_windows_shortcut(shortcut_path, exe_path, "Project Launcher")


def remove_start_menu_shortcut() -> bool:
    """Remove Start Menu shortcut."""
    if get_platform() != "Windows":
        return False
    
    shortcut_path = _get_windows_start_menu_folder() / "Project Launcher.lnk"
    return _remove_windows_shortcut(shortcut_path)


def has_start_menu_shortcut() -> bool:
    """Check if Start Menu shortcut exists."""
    if get_platform() != "Windows":
        return False
    
    shortcut_path = _get_windows_start_menu_folder() / "Project Launcher.lnk"
    return shortcut_path.exists()


# =============================================================================
# Installation Functions
# =============================================================================

def install_application(create_desktop: bool = True, create_start_menu: bool = True, create_startup: bool = True) -> dict:
    """
    Install the application to the standard location.
    
    Returns dict with:
        - success: bool
        - install_path: str (path where installed)
        - error: str (if failed)
    """
    result = {"success": False, "install_path": "", "error": ""}
    
    try:
        current_exe = get_executable_path()
        install_dir = get_install_dir()
        target_exe = get_installed_exe_path()
        
        # Check if already installed at target location
        if is_installed():
            result["success"] = True
            result["install_path"] = str(target_exe)
            
            # Still create shortcuts if requested
            if create_desktop:
                create_desktop_shortcut()
            if create_start_menu:
                create_start_menu_shortcut()
            if create_startup:
                set_startup_enabled(True)
            
            return result
        
        # Create install directory
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable to install location
        shutil.copy2(current_exe, target_exe)
        
        # Make executable on Unix
        if get_platform() != "Windows":
            os.chmod(target_exe, 0o755)
        
        # Copy assets if they exist (for icons)
        current_dir = current_exe.parent
        assets_dir = current_dir / "assets"
        if assets_dir.exists():
            target_assets = install_dir / "assets"
            if target_assets.exists():
                shutil.rmtree(target_assets)
            shutil.copytree(assets_dir, target_assets)
        
        result["success"] = True
        result["install_path"] = str(target_exe)
        
        # Create shortcuts
        if create_desktop:
            create_desktop_shortcut()
        if create_start_menu:
            create_start_menu_shortcut()
        if create_startup:
            set_startup_enabled(True)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def uninstall_application() -> dict:
    """
    Uninstall the application.
    
    Returns dict with:
        - success: bool
        - error: str (if failed)
    """
    result = {"success": False, "error": ""}
    
    try:
        # Remove all shortcuts
        remove_desktop_shortcut()
        remove_start_menu_shortcut()
        set_startup_enabled(False)
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


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
        
        exe_path = get_executable_path()
        working_dir = exe_path.parent
        
        # Create LaunchAgent plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.projectlauncher</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
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
        
        exe_path = get_executable_path()
        working_dir = exe_path.parent
        
        # Create .desktop file
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch development projects
Exec="{exe_path}" --auto
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
        return str(_get_windows_startup_folder() / "ProjectLauncher.lnk")
    elif system == "Darwin":
        return str(_get_macos_launch_agent_path())
    else:  # Linux
        return str(_get_linux_autostart_path())


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print(f"Executable path: {get_executable_path()}")
    print(f"Install directory: {get_install_dir()}")
    print(f"Is installed: {is_installed()}")
    print(f"Startup enabled: {is_startup_enabled()}")
    print(f"Startup location: {get_startup_location()}")
    print(f"Desktop shortcut: {has_desktop_shortcut()}")
    print(f"Start Menu shortcut: {has_start_menu_shortcut()}")
