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
        "--noupx",
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
    """Build macOS application.
    
    Strategy: Build a --onefile binary (which works reliably) and then
    wrap it in a proper .app bundle structure manually. This avoids
    PyInstaller's --windowed mode issues with standard library modules.
    """
    print("\n" + "=" * 60)
    print("Building for macOS...")
    print("=" * 60)
    
    root = get_project_root()
    icon_path = root / "assets" / "icon.icns"
    
    # Check if icon exists, try to generate
    if not icon_path.exists():
        print("[*] Icon not found, generating...")
        subprocess.check_call([sys.executable, str(root / "create_icons.py")])
    
    # Step 1: Build a --onefile binary (this works reliably)
    print("[*] Building standalone binary...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ProjectLauncher",
        "--onefile",  # Creates a single reliable binary
        "--windowed",  # Still suppress console
        "--noupx",
        "--add-data", f"{root / 'config_manager.py'}:.",
        "--add-data", f"{root / 'launchers.py'}:.",
        "--add-data", f"{root / 'startup_manager.py'}:.",
        "--add-data", f"{root / 'update_checker.py'}:.",
        "--add-data", f"{root / 'assets'}:assets",
        "--hidden-import=pystray._darwin",
        "--hidden-import=PIL._tkinter_finder",
        "--collect-all=pystray",
        "--collect-all=objc",
        "--collect-all=Foundation",
        "--collect-all=AppKit",
        "--collect-all=Quartz",
        str(root / "project_launcher.py")
    ]
    
    subprocess.check_call(cmd, cwd=root)
    
    dist_dir = root / "dist"
    binary_path = dist_dir / "ProjectLauncher"
    
    if not binary_path.exists():
        print("[ERROR] Build failed - binary not found")
        return None
    
    # Step 2: Create .app bundle structure manually
    print("[*] Creating .app bundle...")
    app_path = dist_dir / "ProjectLauncher.app"
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Clean up any existing .app
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # Create directory structure
    macos_path.mkdir(parents=True)
    resources_path.mkdir(parents=True)
    
    # Move binary into .app bundle
    shutil.move(str(binary_path), str(macos_path / "ProjectLauncher"))
    
    # Copy icon if it exists
    if icon_path.exists():
        shutil.copy(str(icon_path), str(resources_path / "icon.icns"))
    
    # Create Info.plist
    info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>ProjectLauncher</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.projectlauncher.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Project Launcher</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
"""
    (contents_path / "Info.plist").write_text(info_plist)
    
    # Step 3: Sign the app
    print("[*] Signing app with ad-hoc signature...")
    try:
        subprocess.check_call([
            "codesign", "--force", "--deep", "--sign", "-",
            str(app_path)
        ])
        print("[OK] App signed successfully")
    except Exception as e:
        print(f"[WARNING] Could not sign app: {e}")
    
    # Step 4: Create zip to preserve permissions
    zip_path = dist_dir / "ProjectLauncher.app.zip"
    print(f"[*] Creating {zip_path.name}...")
    shutil.make_archive(
        str(dist_dir / "ProjectLauncher.app"),
        'zip',
        dist_dir,
        "ProjectLauncher.app"
    )
    
    print(f"\n[OK] macOS build complete: {zip_path}")
    print(f"    Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    return zip_path


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
        "--noupx",
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
        return build_macos()
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
        print("\nThe executable is portable and self-installing.")
        print("Users can run it directly - it will offer to install itself.")
    else:
        print("\n[ERROR] Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
