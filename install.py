#!/usr/bin/env python3
"""
Project Launcher - Installation Script
Cross-platform installer that sets up the Project Launcher.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()


def check_python_version() -> bool:
    """Check if Python 3.6+ is installed."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"[ERROR] Python 3.6+ is required, but {version.major}.{version.minor} is installed")
        return False


def install_dependencies() -> bool:
    """Install required Python packages."""
    print("\n[*] Installing dependencies...")
    
    try:
        requirements_file = get_install_dir() / "requirements.txt"
        
        if requirements_file.exists():
            # Install from requirements.txt
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--quiet"
            ])
            print("[OK] All dependencies installed successfully")
        else:
            # Fallback: install packages directly
            packages = ["pyyaml", "pystray", "Pillow"]
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *packages, "--quiet"
            ])
            print("[OK] All dependencies installed successfully")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        print("Try running manually: pip install -r requirements.txt")
        return False


def get_install_dir() -> Path:
    """Get the directory where this script is located."""
    return Path(__file__).parent.absolute()


def setup_path_windows() -> bool:
    """Add the install directory to PATH on Windows (user-level)."""
    install_dir = str(get_install_dir())
    
    print(f"\n[*] Adding to PATH: {install_dir}")
    
    try:
        # Get current user PATH
        import winreg
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except WindowsError:
            current_path = ""
        
        # Check if already in PATH
        if install_dir.lower() in current_path.lower():
            print("[OK] Already in PATH")
            winreg.CloseKey(key)
            return True
        
        # Add to PATH
        new_path = f"{current_path};{install_dir}" if current_path else install_dir
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        # Notify the system of the change
        import ctypes
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
        
        print("[OK] Added to PATH successfully")
        print("[!] You may need to restart your terminal for PATH changes to take effect")
        return True
        
    except Exception as e:
        print(f"[WARNING] Could not add to PATH automatically: {e}")
        print(f"\nManual instructions:")
        print(f"  1. Open System Properties > Environment Variables")
        print(f"  2. Edit 'Path' under User variables")
        print(f"  3. Add: {install_dir}")
        return False


def setup_path_unix() -> bool:
    """Add the install directory to PATH on Mac/Linux."""
    install_dir = str(get_install_dir())
    shell = os.environ.get("SHELL", "/bin/bash")
    
    print(f"\n[*] Adding to PATH: {install_dir}")
    
    # Determine shell config file
    if "zsh" in shell:
        config_file = Path.home() / ".zshrc"
    elif "fish" in shell:
        config_file = Path.home() / ".config" / "fish" / "config.fish"
    else:
        config_file = Path.home() / ".bashrc"
    
    # Make the shell script executable
    shell_script = get_install_dir() / "plaunch"
    if shell_script.exists():
        os.chmod(shell_script, 0o755)
    
    export_line = f'\nexport PATH="$PATH:{install_dir}"\n'
    
    try:
        # Check if already in config
        if config_file.exists():
            content = config_file.read_text()
            if install_dir in content:
                print(f"[OK] Already in {config_file}")
                return True
        
        # Add to config file
        with open(config_file, "a") as f:
            f.write(f"\n# Project Launcher")
            f.write(export_line)
        
        print(f"[OK] Added to {config_file}")
        print(f"[!] Run 'source {config_file}' or restart your terminal")
        return True
        
    except Exception as e:
        print(f"[WARNING] Could not add to PATH automatically: {e}")
        print(f"\nManual instructions:")
        print(f"  Add this line to your {config_file}:")
        print(f"  export PATH=\"$PATH:{install_dir}\"")
        return False


def setup_path() -> bool:
    """Set up PATH based on platform."""
    system = get_platform()
    
    if system == "Windows":
        return setup_path_windows()
    else:
        return setup_path_unix()


def setup_startup(enable: bool = True) -> bool:
    """Set up startup registration."""
    print(f"\n[*] {'Enabling' if enable else 'Disabling'} startup registration...")
    
    try:
        from startup_manager import set_startup_enabled, get_startup_location
        
        success = set_startup_enabled(enable)
        
        if success:
            if enable:
                print(f"[OK] Startup enabled")
                print(f"    Location: {get_startup_location()}")
            else:
                print("[OK] Startup disabled")
        else:
            print("[WARNING] Could not configure startup")
        
        return success
        
    except Exception as e:
        print(f"[WARNING] Could not configure startup: {e}")
        return False


def create_config() -> bool:
    """Create the default configuration directory and file."""
    print("\n[*] Creating default configuration...")
    
    try:
        from config_manager import load_config, get_config_dir
        
        # This will create the config if it doesn't exist
        config = load_config()
        config_dir = get_config_dir()
        
        print(f"[OK] Configuration created at: {config_dir}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Could not create configuration: {e}")
        return False


def print_banner():
    """Print installation banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                   PROJECT LAUNCHER                        ║
║               Installation Script v1.0                    ║
╚═══════════════════════════════════════════════════════════╝
""")


def print_success():
    """Print success message with usage instructions."""
    system = get_platform()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                 INSTALLATION COMPLETE!                    ║
╚═══════════════════════════════════════════════════════════╝

You can now use Project Launcher in the following ways:

  1. CLI Command (after restarting terminal):
     $ plaunch

  2. Direct execution:""")
    
    if system == "Windows":
        print(f"     > python {get_install_dir()}\\project_launcher.py")
        print(f"     > {get_install_dir()}\\plaunch.bat")
    else:
        print(f"     $ python3 {get_install_dir()}/project_launcher.py")
        print(f"     $ {get_install_dir()}/plaunch")
    
    print("""
  3. The app will automatically launch on system startup
     (can be disabled in Settings)

  4. System tray icon - minimize to tray, click to restore

Quick Start:
  - Click '+ Add Project' to add your first project
  - Configure IDE, AI tools, terminal commands, and browser tabs
  - Click on a project to launch it!
""")


def main():
    """Main installation function."""
    print_banner()
    
    # Check Python version
    print("[*] Checking Python version...")
    if not check_python_version():
        print("\nPlease install Python 3.6 or higher:")
        print("  Windows: https://www.python.org/downloads/")
        print("  macOS:   brew install python3")
        print("  Linux:   sudo apt install python3")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n[ERROR] Failed to install dependencies")
        sys.exit(1)
    
    # Create default config
    if not create_config():
        print("\n[WARNING] Could not create default configuration")
    
    # Set up PATH
    setup_path()
    
    # Set up startup
    setup_startup(enable=True)
    
    # Print success
    print_success()
    
    # Ask if user wants to launch now
    try:
        response = input("Would you like to launch Project Launcher now? [Y/n]: ").strip().lower()
        if response != "n":
            print("\nLaunching Project Launcher...")
            subprocess.Popen([sys.executable, str(get_install_dir() / "project_launcher.py")])
    except (KeyboardInterrupt, EOFError):
        print("\n")
    
    print("\nInstallation complete! Enjoy using Project Launcher.")


if __name__ == "__main__":
    main()
