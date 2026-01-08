#!/usr/bin/env python3
"""
Project Launcher - Self-Extracting Installer Builder
Builds a single installer file for Windows (.exe), macOS (.app), or Linux.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

from update_checker import VERSION


def get_platform():
    """Get current platform."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "linux"


def create_installer_script():
    """Create the cross-platform installer script that will be bundled."""
    
    installer_code = '''#!/usr/bin/env python3
"""
Project Launcher - Installer
Cross-platform installer that runs when user executes the installer.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_bundle_dir():
    """Get the directory where bundled files are located."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_install_dir():
    """Get the installation directory for each platform."""
    system = platform.system()
    if system == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Programs" / "ProjectLauncher"
    elif system == "Darwin":
        return Path.home() / "Applications" / "ProjectLauncher"
    else:
        return Path.home() / ".local" / "share" / "ProjectLauncher"


def get_bin_dir():
    """Get the bin directory for executables (Linux/macOS)."""
    return Path.home() / ".local" / "bin"


def get_desktop_dir():
    """Get the Desktop directory."""
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Desktop"
    elif system == "Linux":
        # Try XDG first
        xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
        if xdg_desktop:
            return Path(xdg_desktop)
        return Path.home() / "Desktop"
    else:
        return Path.home() / "Desktop"


# ============================================================================
# Windows Installation
# ============================================================================

def get_start_menu_dir():
    """Get the Windows Start Menu programs directory."""
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"



def create_windows_shortcut(target_path, shortcut_path, description="", icon_path=None, working_dir=None):
    """Create a Windows shortcut (.lnk file)."""
    try:
        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Description = "{description}"
"""
        if working_dir:
            ps_script += f'$Shortcut.WorkingDirectory = "{working_dir}"\\n'
        if icon_path:
            ps_script += f'$Shortcut.IconLocation = "{icon_path}"\\n'
        
        ps_script += '$Shortcut.Save()'
        
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False


def show_windows_message(title, message, style=0):
    """Show a Windows message box."""
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, style)


def install_windows():
    """Install on Windows."""
    import ctypes
    
    print("Installing Project Launcher for Windows...")
    
    bundle_dir = get_bundle_dir()
    source_exe = bundle_dir / "ProjectLauncher.exe"
    
    if not source_exe.exists():
        show_windows_message("Error", "Application files not found in installer.", 16)
        return False
    
    # Create installation directory
    install_dir = get_install_dir()
    
    try:
        install_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        show_windows_message("Error", "Permission denied. Try running as Administrator.", 16)
        return False
    
    # Copy executable
    dest_exe = install_dir / "ProjectLauncher.exe"
    print(f"Installing to {dest_exe}...")
    shutil.copy2(source_exe, dest_exe)
    
    # Copy icon if available
    icon_src = bundle_dir / "icon.ico"
    if icon_src.exists():
        shutil.copy2(icon_src, install_dir / "icon.ico")
    
    # Create Start Menu shortcut
    start_menu_dir = get_start_menu_dir()
    start_menu_shortcut = start_menu_dir / "Project Launcher.lnk"
    
    print("Creating Start Menu shortcut...")
    create_windows_shortcut(
        str(dest_exe),
        str(start_menu_shortcut),
        description="Launch your development projects with one click",
        working_dir=str(install_dir),
        icon_path=str(dest_exe) + ",0"
    )
    
    # Create Desktop shortcut
    desktop_shortcut = get_desktop_dir() / "Project Launcher.lnk"
    print("Creating Desktop shortcut...")
    create_windows_shortcut(
        str(dest_exe),
        str(desktop_shortcut),
        description="Launch your development projects with one click",
        working_dir=str(install_dir),
        icon_path=str(dest_exe) + ",0"
    )
    
    # Create Start Menu folder for app group
    start_menu_folder = start_menu_dir / "Project Launcher"
    start_menu_folder.mkdir(parents=True, exist_ok=True)
    
    # Move app shortcut to folder
    start_menu_app_shortcut = start_menu_folder / "Project Launcher.lnk"
    if start_menu_shortcut.exists():
        shutil.move(str(start_menu_shortcut), str(start_menu_app_shortcut))
    
    # Create uninstaller batch file
    uninstaller_path = install_dir / "uninstall.bat"
    uninstall_shortcut = start_menu_folder / "Uninstall Project Launcher.lnk"
    
    # Registry key for Add/Remove Programs
    reg_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ProjectLauncher"
    
    # Startup registry key (for fallback cleanup)
    startup_reg_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    
    uninstaller_content = f"""@echo off
echo Uninstalling Project Launcher...
taskkill /F /IM ProjectLauncher.exe 2>nul
del "{start_menu_app_shortcut}" 2>nul
del "{uninstall_shortcut}" 2>nul
rmdir "{start_menu_folder}" 2>nul
del "{desktop_shortcut}" 2>nul
REM Remove Task Scheduler startup entry
schtasks /delete /tn "ProjectLauncherStartup" /f 2>nul
REM Remove registry startup entry (fallback)
reg delete "HKCU\\{startup_reg_key}" /v "ProjectLauncher" /f 2>nul
REM Remove Add/Remove Programs entry
reg delete "HKCU\\{reg_key}" /f 2>nul
timeout /t 2 /nobreak >nul
cd /d "%TEMP%"
rmdir /s /q "{install_dir}"
echo Project Launcher has been uninstalled.
pause
"""
    with open(uninstaller_path, "w") as f:
        f.write(uninstaller_content)
    
    # Create Start Menu shortcut for uninstaller
    print("Creating uninstaller shortcut...")
    create_windows_shortcut(
        str(uninstaller_path),
        str(uninstall_shortcut),
        description="Uninstall Project Launcher",
        working_dir=str(install_dir)
    )
    
    # Register in Windows Add/Remove Programs
    print("Registering in Add/Remove Programs...")
    icon_path = install_dir / "icon.ico"
    reg_script = f"""
$regPath = "HKCU:\\{reg_key}"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "DisplayName" -Value "Project Launcher"
Set-ItemProperty -Path $regPath -Name "DisplayVersion" -Value "0.0.1"
Set-ItemProperty -Path $regPath -Name "Publisher" -Value "Project Launcher"
Set-ItemProperty -Path $regPath -Name "InstallLocation" -Value "{install_dir}"
Set-ItemProperty -Path $regPath -Name "UninstallString" -Value "{uninstaller_path}"
Set-ItemProperty -Path $regPath -Name "DisplayIcon" -Value "{icon_path if icon_path.exists() else dest_exe}"
Set-ItemProperty -Path $regPath -Name "NoModify" -Value 1 -Type DWord
Set-ItemProperty -Path $regPath -Name "NoRepair" -Value 1 -Type DWord
"""
    try:
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", reg_script],
            capture_output=True,
            check=True
        )
    except Exception as e:
        print(f"Note: Could not register in Add/Remove Programs: {{e}}")
    
    # Success message
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "Project Launcher has been installed successfully!\\n\\n"
        "- Desktop shortcut created\\n"
        "- Start Menu shortcuts created\\n"
        "- Enable auto-start from Settings after launch\\n"
        "- Added to Add/Remove Programs\\n\\n"
        "Would you like to launch it now?",
        "Installation Complete",
        36  # MB_YESNO + MB_ICONQUESTION
    )
    
    if result == 6:  # IDYES
        subprocess.Popen([str(dest_exe)], cwd=str(install_dir))
    
    return True


# ============================================================================
# macOS Installation
# ============================================================================

def install_macos():
    """Install on macOS."""
    print("Installing Project Launcher for macOS...")
    
    bundle_dir = get_bundle_dir()
    
    # Look for the app or binary
    source_app = bundle_dir / "ProjectLauncher.app"
    source_binary = bundle_dir / "ProjectLauncher"
    
    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)
    
    if source_app.exists():
        # Copy .app bundle
        dest_app = Path.home() / "Applications" / "Project Launcher.app"
        if dest_app.exists():
            shutil.rmtree(dest_app)
        shutil.copytree(source_app, dest_app)
        print(f"Installed to {dest_app}")
        
        # Create symlink in /usr/local/bin (optional)
        bin_link = Path("/usr/local/bin/project-launcher")
        try:
            if bin_link.exists():
                bin_link.unlink()
            bin_link.symlink_to(dest_app / "Contents" / "MacOS" / "ProjectLauncher")
        except PermissionError:
            print("Note: Could not create /usr/local/bin symlink (needs sudo)")
        
        launch_path = str(dest_app)
        
    elif source_binary.exists():
        # Copy standalone binary
        dest_binary = install_dir / "ProjectLauncher"
        shutil.copy2(source_binary, dest_binary)
        os.chmod(dest_binary, 0o755)
        
        # Create symlink in ~/.local/bin
        bin_dir = get_bin_dir()
        bin_dir.mkdir(parents=True, exist_ok=True)
        bin_link = bin_dir / "project-launcher"
        if bin_link.exists():
            bin_link.unlink()
        bin_link.symlink_to(dest_binary)
        
        launch_path = str(dest_binary)
        print(f"Installed to {dest_binary}")
    else:
        print("Error: Application files not found in installer.")
        return False
    
    # Copy icon
    icon_src = bundle_dir / "icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, install_dir / "icon.png")
    
    # Create Launch Agent for auto-start
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    
    plist_path = launch_agents_dir / "com.projectlauncher.plist"
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.projectlauncher</string>
    <key>ProgramArguments</key>
    <array>
        <string>{launch_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>LaunchOnlyOnce</key>
    <true/>
</dict>
</plist>
"""
    with open(plist_path, "w") as f:
        f.write(plist_content)
    
    # Load the launch agent
    subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
    
    # Create uninstaller script
    uninstaller_path = install_dir / "uninstall.sh"
    uninstaller_content = f"""#!/bin/bash
echo "Uninstalling Project Launcher..."
launchctl unload "{plist_path}" 2>/dev/null
rm -f "{plist_path}"
rm -rf "$HOME/Applications/Project Launcher.app"
rm -f "$HOME/.local/bin/project-launcher"
rm -f /usr/local/bin/project-launcher 2>/dev/null
rm -f "$HOME/.local/share/applications/project-launcher-uninstall.desktop"
rm -rf "{install_dir}"
echo "Project Launcher has been uninstalled."
"""
    with open(uninstaller_path, "w") as f:
        f.write(uninstaller_content)
    os.chmod(uninstaller_path, 0o755)
    
    # Create .desktop file for uninstaller in Applications
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    
    uninstall_desktop = applications_dir / "project-launcher-uninstall.desktop"
    icon_path = install_dir / "icon.png"
    uninstall_desktop_content = f"""[Desktop Entry]
Type=Application
Name=Uninstall Project Launcher
Comment=Remove Project Launcher from your system
Exec=bash "{uninstaller_path}"
Icon={icon_path}
Terminal=true
Categories=Utility;
"""
    with open(uninstall_desktop, "w") as f:
        f.write(uninstall_desktop_content)
    os.chmod(uninstall_desktop, 0o755)
    
    print("\\nInstallation complete!")
    print("- App installed to ~/Applications or ~/.local/share/ProjectLauncher")
    print("- Will auto-start on login")
    print("- Find it in Spotlight by searching 'Project Launcher'")
    print("- Uninstaller available in Applications menu")
    
    # Ask to launch
    response = input("\\nWould you like to launch it now? [Y/n]: ").strip().lower()
    if response != 'n':
        subprocess.Popen([launch_path])
    
    return True


# ============================================================================
# Linux Installation
# ============================================================================

def install_linux():
    """Install on Linux."""
    print("Installing Project Launcher for Linux...")
    
    bundle_dir = get_bundle_dir()
    source_binary = bundle_dir / "project-launcher"
    
    if not source_binary.exists():
        # Try alternate name
        source_binary = bundle_dir / "ProjectLauncher"
    
    if not source_binary.exists():
        print("Error: Application files not found in installer.")
        return False
    
    # Install to ~/.local/share/ProjectLauncher
    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)
    
    dest_binary = install_dir / "project-launcher"
    shutil.copy2(source_binary, dest_binary)
    os.chmod(dest_binary, 0o755)
    print(f"Installed to {dest_binary}")
    
    # Create symlink in ~/.local/bin
    bin_dir = get_bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)
    bin_link = bin_dir / "project-launcher"
    if bin_link.exists():
        bin_link.unlink()
    bin_link.symlink_to(dest_binary)
    print(f"Created symlink at {bin_link}")
    
    # Copy icon
    icon_src = bundle_dir / "icon.png"
    icon_dest = install_dir / "icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, icon_dest)
    
    # Create .desktop file for application menu
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = applications_dir / "project-launcher.desktop"
    desktop_content = f"""[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch your development projects with one click
Exec={dest_binary}
Icon={icon_dest}
Terminal=false
Categories=Development;Utility;
StartupNotify=true
"""
    with open(desktop_file, "w") as f:
        f.write(desktop_content)
    os.chmod(desktop_file, 0o755)
    print(f"Created desktop entry at {desktop_file}")
    
    # Create autostart entry
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    
    autostart_file = autostart_dir / "project-launcher.desktop"
    shutil.copy2(desktop_file, autostart_file)
    print(f"Created autostart entry")
    
    # Create uninstaller script
    uninstaller_path = install_dir / "uninstall.sh"
    uninstall_desktop = applications_dir / "project-launcher-uninstall.desktop"
    uninstaller_content = f"""#!/bin/bash
echo "Uninstalling Project Launcher..."
rm -f "{desktop_file}"
rm -f "{uninstall_desktop}"
rm -f "{autostart_file}"
rm -f "{bin_link}"
rm -rf "{install_dir}"
echo "Project Launcher has been uninstalled."
"""
    with open(uninstaller_path, "w") as f:
        f.write(uninstaller_content)
    os.chmod(uninstaller_path, 0o755)
    
    # Create .desktop file for uninstaller in Applications menu
    uninstall_desktop_content = f"""[Desktop Entry]
Type=Application
Name=Uninstall Project Launcher
Comment=Remove Project Launcher from your system
Exec=bash "{uninstaller_path}"
Icon={icon_dest}
Terminal=true
Categories=Utility;
"""
    with open(uninstall_desktop, "w") as f:
        f.write(uninstall_desktop_content)
    os.chmod(uninstall_desktop, 0o755)
    print(f"Created uninstaller entry in applications menu")
    
    print("\\nInstallation complete!")
    print("- Binary installed to ~/.local/share/ProjectLauncher")
    print("- Symlink created at ~/.local/bin/project-launcher")
    print("- Desktop entry created (find in application menu)")
    print("- Will auto-start on login")
    print("- Uninstaller available in application menu")
    
    # Check PATH
    path = os.environ.get("PATH", "")
    if str(bin_dir) not in path:
        print(f"\\nNote: Add ~/.local/bin to your PATH if not already:")
        print(f'  export PATH="$PATH:{bin_dir}"')
    
    # Ask to launch
    response = input("\\nWould you like to launch it now? [Y/n]: ").strip().lower()
    if response != 'n':
        subprocess.Popen([str(dest_binary)])
    
    return True


# ============================================================================
# Main
# ============================================================================

def main():
    system = platform.system()
    
    print("=" * 50)
    print("   Project Launcher - Installer")
    print("=" * 50)
    print()
    
    if system == "Windows":
        success = install_windows()
    elif system == "Darwin":
        success = install_macos()
    else:
        success = install_linux()
    
    if not success:
        print("\\nInstallation failed.")
        if system == "Windows":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "Installation failed. Please try again.",
                "Error",
                16
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    return installer_code


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.absolute()


def build_installer_windows(root, temp_dir):
    """Build Windows installer."""
    print("[*] Building Windows installer...")
    
    app_exe = root / "dist" / "ProjectLauncher.exe"
    if not app_exe.exists():
        print("[*] App not built yet, building now...")
        subprocess.check_call([sys.executable, str(root / "build.py")])
        app_exe = root / "dist" / "ProjectLauncher.exe"
    
    # Copy files to temp
    shutil.copy2(app_exe, temp_dir / "ProjectLauncher.exe")
    
    icon_path = root / "assets" / "icon.ico"
    if icon_path.exists():
        shutil.copy2(icon_path, temp_dir / "icon.ico")
    
    # Build installer with version in name
    installer_name = f"ProjectLauncher-Setup-{VERSION}"
    installer_script = temp_dir / "installer_main.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={installer_name}",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}" if icon_path.exists() else "",
        "--add-data", f"{temp_dir / 'ProjectLauncher.exe'};.",
        "--add-data", f"{temp_dir / 'icon.ico'};." if (temp_dir / "icon.ico").exists() else "",
        "--uac-admin",
        str(installer_script)
    ]
    cmd = [c for c in cmd if c]
    
    subprocess.check_call(cmd, cwd=root)
    
    return root / "dist" / f"{installer_name}.exe"


def build_installer_macos(root, temp_dir):
    """Build macOS installer as .dmg disk image."""
    print("[*] Building macOS installer...")
    
    # Look for app or binary
    app_path = root / "dist" / "ProjectLauncher.app"
    binary_path = root / "dist" / "ProjectLauncher"
    
    if not app_path.exists() and not binary_path.exists():
        print("[*] App not built yet, building now...")
        subprocess.check_call([sys.executable, str(root / "build.py")])
        # Re-check paths after build
        app_path = root / "dist" / "ProjectLauncher.app"
        binary_path = root / "dist" / "ProjectLauncher"
    
    # Copy files to temp
    add_data_app = None
    if app_path.exists():
        shutil.copytree(app_path, temp_dir / "ProjectLauncher.app")
        add_data_app = f"{temp_dir / 'ProjectLauncher.app'}:."
    elif binary_path.exists():
        shutil.copy2(binary_path, temp_dir / "ProjectLauncher")
        add_data_app = f"{temp_dir / 'ProjectLauncher'}:."
    else:
        raise RuntimeError("Build completed but no app or binary found in dist/")
    
    icon_path = root / "assets" / "icon.png"
    if icon_path.exists():
        shutil.copy2(icon_path, temp_dir / "icon.png")
    
    icns_path = root / "assets" / "icon.icns"
    
    # Build installer with version in name
    installer_name = f"ProjectLauncher-Installer-{VERSION}"
    installer_script = temp_dir / "installer_main.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={installer_name}",
        "--onefile",
    ]
    
    if icns_path.exists():
        cmd.append(f"--icon={icns_path}")
    
    cmd.extend([
        "--add-data", add_data_app,
        "--add-data", f"{temp_dir / 'icon.png'}:." if (temp_dir / "icon.png").exists() else "",
        str(installer_script)
    ])
    cmd = [c for c in cmd if c]
    
    subprocess.check_call(cmd, cwd=root)
    
    installer_binary = root / "dist" / installer_name
    
    # Create .dmg disk image for proper macOS distribution
    dmg_name = f"{installer_name}.dmg"
    dmg_path = root / "dist" / dmg_name
    
    print("[*] Creating .dmg disk image...")
    try:
        # Create a temporary directory for DMG contents
        dmg_temp = temp_dir / "dmg_contents"
        dmg_temp.mkdir(exist_ok=True)
        
        # Copy installer to DMG contents
        shutil.copy2(installer_binary, dmg_temp / installer_name)
        
        # Make it executable
        os.chmod(dmg_temp / installer_name, 0o755)
        
        # Create README for the DMG
        readme_content = """# Project Launcher Installer

## Installation Instructions

1. Double-click the "ProjectLauncher-Installer" file
2. If macOS blocks it, right-click and select "Open"
3. Follow the on-screen prompts

The installer will:
- Install Project Launcher to ~/Applications
- Set up auto-start at login
- Create an uninstaller

## Troubleshooting

If you see "App is damaged" or cannot open:
1. Open Terminal
2. Run: xattr -cr /path/to/ProjectLauncher-Installer
3. Try opening again
"""
        with open(dmg_temp / "README.txt", "w") as f:
            f.write(readme_content)
        
        # Remove existing DMG if present
        if dmg_path.exists():
            dmg_path.unlink()
        
        # Create DMG using hdiutil
        subprocess.check_call([
            "hdiutil", "create",
            "-volname", "Project Launcher Installer",
            "-srcfolder", str(dmg_temp),
            "-ov",
            "-format", "UDZO",  # Compressed DMG
            str(dmg_path)
        ])
        
        print(f"[*] Created DMG: {dmg_path}")
        return dmg_path
        
    except Exception as e:
        print(f"[!] Warning: Could not create .dmg ({e}), falling back to binary")
        # If DMG creation fails, zip the binary instead
        zip_name = f"{installer_name}.zip"
        zip_path = root / "dist" / zip_name
        
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(installer_binary, installer_name)
            print(f"[*] Created ZIP fallback: {zip_path}")
            return zip_path
        except Exception as e2:
            print(f"[!] ZIP also failed ({e2}), returning raw binary")
            return installer_binary


def build_installer_linux(root, temp_dir):
    """Build Linux installer."""
    print("[*] Building Linux installer...")
    
    binary_path = root / "dist" / "project-launcher"
    
    if not binary_path.exists():
        print("[*] App not built yet, building now...")
        subprocess.check_call([sys.executable, str(root / "build.py")])
    
    # Copy files to temp
    shutil.copy2(binary_path, temp_dir / "project-launcher")
    
    icon_path = root / "assets" / "icon.png"
    if icon_path.exists():
        shutil.copy2(icon_path, temp_dir / "icon.png")
    
    # Build installer with version in name
    installer_name = f"project-launcher-installer-{VERSION}"
    installer_script = temp_dir / "installer_main.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={installer_name}",
        "--onefile",
        "--add-data", f"{temp_dir / 'project-launcher'}:.",
        "--add-data", f"{temp_dir / 'icon.png'}:." if (temp_dir / "icon.png").exists() else "",
        str(installer_script)
    ]
    cmd = [c for c in cmd if c]
    
    subprocess.check_call(cmd, cwd=root)
    
    return root / "dist" / installer_name


def main():
    print("""
============================================================
   PROJECT LAUNCHER - INSTALLER BUILDER
============================================================
""")
    
    root = get_project_root()
    plat = get_platform()
    
    # Create temp directory
    temp_dir = root / "installer_build"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Write installer script
    installer_script = temp_dir / "installer_main.py"
    with open(installer_script, "w") as f:
        f.write(create_installer_script())
    
    try:
        if plat == "windows":
            result = build_installer_windows(root, temp_dir)
            installer_name = f"ProjectLauncher-Setup-{VERSION}.exe"
        elif plat == "macos":
            result = build_installer_macos(root, temp_dir)
            installer_name = f"ProjectLauncher-Installer-{VERSION}"
        else:
            result = build_installer_linux(root, temp_dir)
            installer_name = f"project-launcher-installer-{VERSION}"
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        if result and result.exists():
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"\nInstaller built: {result}")
            print(f"Size: {result.stat().st_size / 1024 / 1024:.1f} MB")
            print("\nThis single file will:")
            print("  1. Install the application")
            print("  2. Create shortcuts/menu entries")
            print("  3. Set up auto-start")
            print("  4. Create uninstaller")
            print("\nDistribute this file to users - they just double-click it!")
        else:
            print("\n[ERROR] Build failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        sys.exit(1)


if __name__ == "__main__":
    main()
