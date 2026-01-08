"""
Windows Platform Handler
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import tkinter as tk

from platform_handlers.base import PlatformHandler


class WindowsPlatformHandler(PlatformHandler):
    """Windows-specific platform implementation."""
    
    # =========================================================================
    # Dialog Configuration
    # =========================================================================
    
    @property
    def use_native_dialog_titlebar(self) -> bool:
        """Windows: Use custom frameless dialogs for consistent look."""
        return False
    
    @property
    def use_native_window_titlebar(self) -> bool:
        """Windows: Use custom frameless window."""
        return False
    
    @property
    def supports_tray_icon(self) -> bool:
        """Windows: Supports system tray."""
        return True
    
    @property
    def supports_menu_bar(self) -> bool:
        """Windows: No native top menu bar like macOS."""
        return False
    
    # =========================================================================
    # Path Helpers
    # =========================================================================
    
    def _get_executable_path(self) -> Path:
        """Get the path to the running executable."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable)
        else:
            return Path(__file__).parent.parent / "project_launcher.py"
    
    def _get_startup_folder(self) -> Path:
        """Get Windows startup folder path."""
        startup = os.environ.get("APPDATA", "")
        if startup:
            return Path(startup) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    
    def _get_desktop_folder(self) -> Path:
        """Get Windows desktop folder path."""
        return Path.home() / "Desktop"
    
    def _get_start_menu_folder(self) -> Path:
        """Get Windows Start Menu programs folder path."""
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    
    # =========================================================================
    # Shortcut Creation (Windows-specific)
    # =========================================================================
    
    def _create_shortcut(self, shortcut_path: Path, target_path: Path, 
                         description: str = "", icon_path: Optional[Path] = None) -> bool:
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
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.WorkingDirectory = "{target_path.parent}"
$Shortcut.Description = "{description}"
$Shortcut.Save()
'''
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                creationflags=creationflags
            )
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False
    
    def _remove_shortcut(self, shortcut_path: Path) -> bool:
        """Remove a Windows shortcut file."""
        try:
            if shortcut_path.exists():
                shortcut_path.unlink()
            return True
        except Exception as e:
            print(f"Error removing shortcut: {e}")
            return False
    
    def _cleanup_legacy_startup(self) -> None:
        """Remove old startup methods (Registry, VBS files, Task Scheduler)."""
        # Remove old VBS from Startup folder
        try:
            vbs_path = self._get_startup_folder() / "ProjectLauncher.vbs"
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
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            subprocess.run(
                ["schtasks", "/delete", "/tn", "ProjectLauncher", "/f"],
                capture_output=True,
                creationflags=creationflags
            )
        except Exception:
            pass
    
    # =========================================================================
    # Installation
    # =========================================================================
    
    def get_install_dir(self) -> Path:
        """Windows: Install to LocalAppData."""
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ProjectLauncher"
    
    def get_installed_exe_path(self) -> Path:
        """Windows: Return .exe path."""
        return self.get_install_dir() / "ProjectLauncher.exe"
    
    # =========================================================================
    # Startup
    # =========================================================================
    
    def is_startup_enabled(self) -> bool:
        """Check if Windows startup is enabled."""
        shortcut_path = self._get_startup_folder() / "ProjectLauncher.lnk"
        return shortcut_path.exists()
    
    def set_startup_enabled(self, enabled: bool) -> bool:
        """Enable or disable Windows startup."""
        if enabled:
            self._cleanup_legacy_startup()
            
            exe_path = self._get_executable_path()
            if not exe_path.exists():
                return False
            
            startup_folder = self._get_startup_folder()
            startup_folder.mkdir(parents=True, exist_ok=True)
            
            shortcut_path = startup_folder / "ProjectLauncher.lnk"
            return self._create_shortcut(shortcut_path, exe_path, "Project Launcher - Launch your projects")
        else:
            self._cleanup_legacy_startup()
            shortcut_path = self._get_startup_folder() / "ProjectLauncher.lnk"
            return self._remove_shortcut(shortcut_path)
    
    def get_startup_location(self) -> str:
        """Get Windows startup shortcut path."""
        return str(self._get_startup_folder() / "ProjectLauncher.lnk")
    
    # =========================================================================
    # Shortcuts
    # =========================================================================
    
    def has_desktop_shortcut(self) -> bool:
        shortcut_path = self._get_desktop_folder() / "Project Launcher.lnk"
        return shortcut_path.exists()
    
    def create_desktop_shortcut(self) -> bool:
        exe_path = self._get_executable_path()
        if not exe_path.exists():
            return False
        
        desktop = self._get_desktop_folder()
        shortcut_path = desktop / "Project Launcher.lnk"
        return self._create_shortcut(shortcut_path, exe_path, "Project Launcher")
    
    def remove_desktop_shortcut(self) -> bool:
        shortcut_path = self._get_desktop_folder() / "Project Launcher.lnk"
        return self._remove_shortcut(shortcut_path)
    
    def has_start_menu_shortcut(self) -> bool:
        shortcut_path = self._get_start_menu_folder() / "Project Launcher.lnk"
        return shortcut_path.exists()
    
    def create_start_menu_shortcut(self) -> bool:
        exe_path = self._get_executable_path()
        if not exe_path.exists():
            return False
        
        start_menu = self._get_start_menu_folder()
        start_menu.mkdir(parents=True, exist_ok=True)
        
        shortcut_path = start_menu / "Project Launcher.lnk"
        return self._create_shortcut(shortcut_path, exe_path, "Project Launcher")
    
    def remove_start_menu_shortcut(self) -> bool:
        shortcut_path = self._get_start_menu_folder() / "Project Launcher.lnk"
        return self._remove_shortcut(shortcut_path)
    
    # =========================================================================
    # Install/Uninstall
    # =========================================================================
    
    def install_application(self, create_desktop: bool, create_start_menu: bool, 
                            create_startup: bool) -> dict:
        """Install the application on Windows."""
        result = {"success": False, "install_path": "", "error": ""}
        
        try:
            current_exe = self._get_executable_path()
            install_dir = self.get_install_dir()
            target_exe = self.get_installed_exe_path()
            
            # Check if already installed
            try:
                current_exe.relative_to(install_dir)
                # Already installed
                result["success"] = True
                result["install_path"] = str(target_exe)
                
                if create_desktop:
                    self.create_desktop_shortcut()
                if create_start_menu:
                    self.create_start_menu_shortcut()
                if create_startup:
                    self.set_startup_enabled(True)
                
                return result
            except ValueError:
                pass  # Not installed, continue
            
            # Create install directory
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            shutil.copy2(current_exe, target_exe)
            
            # Copy assets if they exist
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
                self.create_desktop_shortcut()
            if create_start_menu:
                self.create_start_menu_shortcut()
            if create_startup:
                self.set_startup_enabled(True)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def uninstall_application(self, remove_app: bool, remove_config: bool) -> dict:
        """Uninstall the application on Windows."""
        result = {"success": False, "error": ""}
        
        try:
            # Always remove shortcuts
            self.remove_desktop_shortcut()
            self.remove_start_menu_shortcut()
            self.set_startup_enabled(False)
            
            if remove_app:
                install_dir = self.get_install_dir()
                if install_dir.exists():
                    shutil.rmtree(install_dir)
            
            if remove_config:
                # Import here to avoid circular dependency
                from config_manager import get_config_dir
                config_dir = Path(get_config_dir())
                if config_dir.exists():
                    shutil.rmtree(config_dir)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # =========================================================================
    # Tray Icon
    # =========================================================================
    
    def setup_tray_icon(self, on_show, on_hide, on_quit) -> Optional[object]:
        """Setup Windows system tray icon using pystray."""
        try:
            import pystray
            from PIL import Image, ImageDraw
            import threading
            
            # Load or create icon image
            icon_image = self._load_tray_icon(64)
            if not icon_image:
                return None
            
            menu = pystray.Menu(
                pystray.MenuItem("Show", lambda: on_show(), default=True),
                pystray.MenuItem("Hide", lambda: on_hide()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", lambda: on_quit())
            )
            
            tray_icon = pystray.Icon(
                "project-launcher",
                icon_image,
                "Project Launcher",
                menu
            )
            
            # Run in separate thread
            tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
            tray_thread.start()
            
            return tray_icon
            
        except ImportError:
            return None
    
    def _load_tray_icon(self, size: int = 64):
        """Load or create tray icon image."""
        try:
            from PIL import Image, ImageDraw
            
            # Try to load from source files
            script_dir = Path(__file__).parent.parent
            icon_paths = [
                script_dir / "source_icon.png",
                script_dir / "assets" / "icon.png",
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    try:
                        image = Image.open(icon_path)
                        if image.mode != 'RGBA':
                            image = image.convert('RGBA')
                        if image.size != (size, size):
                            image = image.resize((size, size), Image.Resampling.LANCZOS)
                        return image
                    except Exception:
                        continue
            
            # Fallback: create simple icon
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            margin = size // 8
            draw.ellipse([margin, margin, size - margin, size - margin], fill='#0078d4')
            
            center = size // 2
            tri_size = size // 4
            points = [
                (center - tri_size // 2, center - tri_size),
                (center - tri_size // 2, center + tri_size),
                (center + tri_size, center)
            ]
            draw.polygon(points, fill='white')
            
            return image
            
        except ImportError:
            return None
