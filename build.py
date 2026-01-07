#!/usr/bin/env python3
"""
Build script for Project Launcher
Creates standalone executables for Windows, macOS, and Linux.

Usage:
    python build.py          # Build for current platform
    python build.py --all    # Build for all platforms (requires each OS)
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_platform():
    """Get current platform."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "linux"


def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"])
        print("[OK] PyInstaller installed")
        return True


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.absolute()


def clean_build():
    """Clean previous build artifacts."""
    root = get_project_root()
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        dir_path = root / dir_name
        if dir_path.exists():
            print(f"[*] Removing {dir_name}/")
            shutil.rmtree(dir_path)
    
    for pattern in files_to_clean:
        for file_path in root.glob(pattern):
            print(f"[*] Removing {file_path.name}")
            file_path.unlink()


def build_windows():
    """Build Windows executable."""
    print("\n" + "=" * 60)
    print("Building for Windows...")
    print("=" * 60)
    
    root = get_project_root()
    icon_path = root / "assets" / "icon.ico"
    
    # Check if icon exists
    if not icon_path.exists():
        print("[*] Icon not found, generating...")
        subprocess.check_call([sys.executable, str(root / "create_icons.py")])
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ProjectLauncher",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        "--add-data", f"{root / 'config_manager.py'};.",
        "--add-data", f"{root / 'launchers.py'};.",
        "--add-data", f"{root / 'startup_manager.py'};.",
        "--add-data", f"{root / 'update_checker.py'};.",
        "--add-data", f"{root / 'assets'};assets",
        "--hidden-import=pystray._win32",
        "--hidden-import=PIL._tkinter_finder",
        str(root / "project_launcher.py")
    ]
    
    subprocess.check_call(cmd, cwd=root)
    
    # Move to dist folder with clear name
    dist_dir = root / "dist"
    exe_path = dist_dir / "ProjectLauncher.exe"
    
    if exe_path.exists():
        print(f"\n[OK] Windows build complete: {exe_path}")
        print(f"    Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        return exe_path
    else:
        print("[ERROR] Build failed - executable not found")
        return None


def build_macos():
    """Build macOS application."""
    print("\n" + "=" * 60)
    print("Building for macOS...")
    print("=" * 60)
    
    root = get_project_root()
    icon_path = root / "assets" / "icon.icns"
    
    # Check if icon exists, try to generate
    if not icon_path.exists():
        print("[*] Icon not found, generating...")
        subprocess.check_call([sys.executable, str(root / "create_icons.py")])
    
    # PyInstaller command for macOS
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ProjectLauncher",
        "--onefile",
        "--windowed",
    ]
    
    # Add icon if it exists
    if icon_path.exists():
        cmd.append(f"--icon={icon_path}")
    
    cmd.extend([
        "--add-data", f"{root / 'config_manager.py'}:.",
        "--add-data", f"{root / 'launchers.py'}:.",
        "--add-data", f"{root / 'startup_manager.py'}:.",
        "--add-data", f"{root / 'update_checker.py'}:.",
        "--add-data", f"{root / 'assets'}:assets",
        "--hidden-import=pystray._darwin",
        "--hidden-import=PIL._tkinter_finder",
        str(root / "project_launcher.py")
    ])
    
    subprocess.check_call(cmd, cwd=root)
    
    dist_dir = root / "dist"
    app_path = dist_dir / "ProjectLauncher.app"
    exe_path = dist_dir / "ProjectLauncher"
    
    if app_path.exists():
        print(f"\n[OK] macOS build complete: {app_path}")
        return app_path
    elif exe_path.exists():
        print(f"\n[OK] macOS build complete: {exe_path}")
        return exe_path
    else:
        print("[ERROR] Build failed - application not found")
        return None


def build_linux():
    """Build Linux executable."""
    print("\n" + "=" * 60)
    print("Building for Linux...")
    print("=" * 60)
    
    root = get_project_root()
    icon_path = root / "assets" / "icon.png"
    
    # Check if icon exists
    if not icon_path.exists():
        print("[*] Icon not found, generating...")
        subprocess.check_call([sys.executable, str(root / "create_icons.py")])
    
    # PyInstaller command for Linux
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=project-launcher",
        "--onefile",
        "--windowed",
        "--add-data", f"{root / 'config_manager.py'}:.",
        "--add-data", f"{root / 'launchers.py'}:.",
        "--add-data", f"{root / 'startup_manager.py'}:.",
        "--add-data", f"{root / 'update_checker.py'}:.",
        "--add-data", f"{root / 'assets'}:assets",
        "--hidden-import=pystray._xorg",
        "--hidden-import=PIL._tkinter_finder",
        str(root / "project_launcher.py")
    ]
    
    subprocess.check_call(cmd, cwd=root)
    
    dist_dir = root / "dist"
    exe_path = dist_dir / "project-launcher"
    
    if exe_path.exists():
        # Make executable
        os.chmod(exe_path, 0o755)
        print(f"\n[OK] Linux build complete: {exe_path}")
        print(f"    Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        return exe_path
    else:
        print("[ERROR] Build failed - executable not found")
        return None


def create_dmg(app_path):
    """Create DMG file for macOS (only works on macOS)."""
    if platform.system() != "Darwin":
        print("[SKIP] DMG creation only available on macOS")
        return None
    
    print("\n[*] Creating DMG...")
    
    root = get_project_root()
    dist_dir = root / "dist"
    dmg_path = dist_dir / "ProjectLauncher.dmg"
    
    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()
    
    try:
        # Create DMG using hdiutil
        cmd = [
            "hdiutil", "create",
            "-volname", "Project Launcher",
            "-srcfolder", str(app_path),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ]
        subprocess.check_call(cmd)
        
        print(f"[OK] DMG created: {dmg_path}")
        return dmg_path
    except Exception as e:
        print(f"[WARNING] Could not create DMG: {e}")
        return None


def create_appimage(exe_path):
    """Create AppImage for Linux (only works on Linux)."""
    if platform.system() != "Linux":
        print("[SKIP] AppImage creation only available on Linux")
        return None
    
    print("\n[*] Creating AppImage...")
    print("[INFO] AppImage creation requires appimagetool")
    print("       Install: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
    
    # For now, the standalone binary works well on Linux
    # AppImage creation is more complex and requires additional setup
    return None


def build_current_platform():
    """Build for the current platform."""
    plat = get_platform()
    
    if plat == "windows":
        return build_windows()
    elif plat == "macos":
        app = build_macos()
        if app:
            create_dmg(app)
        return app
    else:
        exe = build_linux()
        if exe:
            create_appimage(exe)
        return exe


def print_banner():
    """Print build banner."""
    print("""
============================================================
            PROJECT LAUNCHER - BUILD TOOL                
============================================================
""")


def main():
    print_banner()
    
    # Check dependencies
    print("[*] Checking dependencies...")
    check_pyinstaller()
    
    # Parse arguments
    clean = "--clean" in sys.argv
    
    if clean:
        print("\n[*] Cleaning previous builds...")
        clean_build()
    
    # Build for current platform
    print(f"\n[*] Building for {get_platform()}...")
    result = build_current_platform()
    
    if result:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\nOutput: {result}")
        print("\nYou can distribute this file to users.")
        print("They can run it without installing Python!")
    else:
        print("\n[ERROR] Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
