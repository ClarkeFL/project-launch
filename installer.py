#!/usr/bin/env python3
"""
Installer for Project Launcher
Creates Start Menu shortcuts and installs the application properly on Windows.
"""

import os
import sys
import shutil
import subprocess
import ctypes
import platform
from pathlib import Path


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_install_dir():
    """Get the installation directory."""
    if platform.system() == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Programs" / "ProjectLauncher"
    elif platform.system() == "Darwin":
        return Path("/Applications")
    else:
        return Path.home() / ".local" / "bin"


def get_start_menu_dir():
    """Get the Start Menu programs directory."""
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def get_desktop_dir():
    """Get the Desktop directory."""
    return Path.home() / "Desktop"


def get_source_exe():
    """Get the path to the built executable."""
    script_dir = Path(__file__).parent
    exe_path = script_dir / "dist" / "ProjectLauncher.exe"
    if exe_path.exists():
        return exe_path
    return None


def create_shortcut(target_path, shortcut_path, description="", icon_path=None, working_dir=None):
    """Create a Windows shortcut (.lnk file)."""
    try:
        import winreg
        
        # Use PowerShell to create shortcut (most reliable method)
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Description = "{description}"
'''
        if working_dir:
            ps_script += f'$Shortcut.WorkingDirectory = "{working_dir}"\n'
        if icon_path:
            ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'
        
        ps_script += '$Shortcut.Save()'
        
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create shortcut: {e}")
        return False


def install_windows():
    """Install on Windows."""
    print("\n[*] Installing Project Launcher for Windows...")
    
    # Check for built executable
    source_exe = get_source_exe()
    if not source_exe:
        print("[ERROR] ProjectLauncher.exe not found in dist/ folder.")
        print("        Run 'python build.py' first to create the executable.")
        return False
    
    # Create installation directory
    install_dir = get_install_dir()
    print(f"[*] Installation directory: {install_dir}")
    
    try:
        install_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print("[ERROR] Permission denied. Try running as Administrator.")
        return False
    
    # Copy executable
    dest_exe = install_dir / "ProjectLauncher.exe"
    print(f"[*] Copying executable...")
    shutil.copy2(source_exe, dest_exe)
    print(f"[OK] Copied to {dest_exe}")
    
    # Create Start Menu shortcut
    start_menu_dir = get_start_menu_dir()
    start_menu_shortcut = start_menu_dir / "Project Launcher.lnk"
    
    print(f"[*] Creating Start Menu shortcut...")
    if create_shortcut(
        str(dest_exe),
        str(start_menu_shortcut),
        description="Launch your development projects with one click",
        working_dir=str(install_dir)
    ):
        print(f"[OK] Start Menu shortcut created")
    else:
        print("[WARNING] Could not create Start Menu shortcut")
    
    # Create Desktop shortcut (optional)
    desktop_shortcut = get_desktop_dir() / "Project Launcher.lnk"
    print(f"[*] Creating Desktop shortcut...")
    if create_shortcut(
        str(dest_exe),
        str(desktop_shortcut),
        description="Launch your development projects with one click",
        working_dir=str(install_dir)
    ):
        print(f"[OK] Desktop shortcut created")
    else:
        print("[WARNING] Could not create Desktop shortcut")
    
    # Create uninstaller script
    uninstaller_path = install_dir / "uninstall.bat"
    uninstaller_content = f'''@echo off
echo Uninstalling Project Launcher...
del "{start_menu_shortcut}" 2>nul
del "{desktop_shortcut}" 2>nul
rmdir /s /q "{install_dir}"
echo Project Launcher has been uninstalled.
pause
'''
    with open(uninstaller_path, "w") as f:
        f.write(uninstaller_content)
    print(f"[OK] Uninstaller created at {uninstaller_path}")
    
    return True


def install_macos():
    """Install on macOS."""
    print("\n[*] Installing Project Launcher for macOS...")
    
    script_dir = Path(__file__).parent
    app_path = script_dir / "dist" / "ProjectLauncher.app"
    
    if not app_path.exists():
        # Try standalone binary
        binary_path = script_dir / "dist" / "ProjectLauncher"
        if not binary_path.exists():
            print("[ERROR] ProjectLauncher.app not found in dist/ folder.")
            print("        Run 'python build.py' on macOS first.")
            return False
        
        # Copy binary to /usr/local/bin
        dest = Path("/usr/local/bin/project-launcher")
        print(f"[*] Copying to {dest}...")
        shutil.copy2(binary_path, dest)
        os.chmod(dest, 0o755)
        print("[OK] Installed to /usr/local/bin/project-launcher")
        return True
    
    # Copy .app to Applications
    dest = Path("/Applications/Project Launcher.app")
    if dest.exists():
        print("[*] Removing existing installation...")
        shutil.rmtree(dest)
    
    print("[*] Copying to Applications...")
    shutil.copytree(app_path, dest)
    print("[OK] Installed to /Applications/Project Launcher.app")
    
    return True


def install_linux():
    """Install on Linux."""
    print("\n[*] Installing Project Launcher for Linux...")
    
    script_dir = Path(__file__).parent
    binary_path = script_dir / "dist" / "project-launcher"
    
    if not binary_path.exists():
        print("[ERROR] project-launcher not found in dist/ folder.")
        print("        Run 'python build.py' on Linux first.")
        return False
    
    # Install to ~/.local/bin
    local_bin = Path.home() / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    
    dest = local_bin / "project-launcher"
    print(f"[*] Copying to {dest}...")
    shutil.copy2(binary_path, dest)
    os.chmod(dest, 0o755)
    print(f"[OK] Installed to {dest}")
    
    # Create .desktop file for application menu
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = applications_dir / "project-launcher.desktop"
    desktop_content = f'''[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch your development projects with one click
Exec={dest}
Terminal=false
Categories=Development;Utility;
'''
    
    with open(desktop_file, "w") as f:
        f.write(desktop_content)
    os.chmod(desktop_file, 0o755)
    print(f"[OK] Desktop entry created at {desktop_file}")
    
    # Check if ~/.local/bin is in PATH
    path = os.environ.get("PATH", "")
    if str(local_bin) not in path:
        print(f"\n[!] Add ~/.local/bin to your PATH if not already:")
        print(f'    export PATH="$PATH:{local_bin}"')
    
    return True


def print_banner():
    """Print installer banner."""
    print("""
============================================================
         PROJECT LAUNCHER - INSTALLER
============================================================
""")


def print_success_windows():
    """Print success message for Windows."""
    print("""
============================================================
         INSTALLATION COMPLETE!
============================================================

Project Launcher has been installed!

You can now:
  1. Search "Project Launcher" in Windows Start Menu
  2. Use the Desktop shortcut
  3. Run from: %LOCALAPPDATA%\\Programs\\ProjectLauncher

To uninstall:
  Run the uninstall.bat in the installation folder

""")


def main():
    print_banner()
    
    system = platform.system()
    
    if system == "Windows":
        success = install_windows()
        if success:
            print_success_windows()
    elif system == "Darwin":
        success = install_macos()
        if success:
            print("\n[OK] Installation complete! Find 'Project Launcher' in Applications or Spotlight.")
    else:
        success = install_linux()
        if success:
            print("\n[OK] Installation complete! Find 'Project Launcher' in your application menu.")
    
    if not success:
        print("\n[ERROR] Installation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
