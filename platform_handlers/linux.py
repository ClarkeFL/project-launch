"""
Linux Platform Handler
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Optional
import tkinter as tk

from platform_handlers.base import PlatformHandler


class LinuxPlatformHandler(PlatformHandler):
    """Linux-specific platform implementation."""
    
    # =========================================================================
    # Dialog Configuration
    # =========================================================================
    
    @property
    def use_native_dialog_titlebar(self) -> bool:
        """Linux: Use custom frameless dialogs like Windows."""
        return False
    
    @property
    def use_native_window_titlebar(self) -> bool:
        """Linux: Use custom frameless window like Windows."""
        return False
    
    @property
    def supports_tray_icon(self) -> bool:
        """Linux: Supports system tray."""
        return True
    
    @property
    def supports_menu_bar(self) -> bool:
        """Linux: No native top menu bar like macOS."""
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
    
    def _get_autostart_path(self) -> Path:
        """Get path to the Linux autostart .desktop file."""
        config_home = os.environ.get("XDG_CONFIG_HOME", "")
        if not config_home:
            config_home = Path.home() / ".config"
        else:
            config_home = Path(config_home)
        
        return config_home / "autostart" / "project-launcher.desktop"
    
    # =========================================================================
    # Installation
    # =========================================================================
    
    def get_install_dir(self) -> Path:
        """Linux: Install to ~/.local/share."""
        return Path.home() / ".local" / "share" / "ProjectLauncher"
    
    def get_installed_exe_path(self) -> Path:
        """Linux: Return executable path."""
        return self.get_install_dir() / "project-launcher"
    
    # =========================================================================
    # Startup
    # =========================================================================
    
    def is_startup_enabled(self) -> bool:
        """Check if Linux startup is enabled."""
        return self._get_autostart_path().exists()
    
    def set_startup_enabled(self, enabled: bool) -> bool:
        """Enable or disable Linux startup via XDG autostart."""
        if enabled:
            return self._enable_startup()
        else:
            return self._disable_startup()
    
    def _enable_startup(self) -> bool:
        """Enable startup on Linux using XDG autostart."""
        try:
            autostart_dir = self._get_autostart_path().parent
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            exe_path = self._get_executable_path()
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
            
            desktop_path = self._get_autostart_path()
            with open(desktop_path, "w") as f:
                f.write(desktop_content)
            
            # Make it executable
            os.chmod(desktop_path, 0o755)
            
            return True
        except Exception as e:
            print(f"Error enabling Linux startup: {e}")
            return False
    
    def _disable_startup(self) -> bool:
        """Disable startup on Linux."""
        try:
            desktop_path = self._get_autostart_path()
            if desktop_path.exists():
                desktop_path.unlink()
            return True
        except Exception as e:
            print(f"Error disabling Linux startup: {e}")
            return False
    
    def get_startup_location(self) -> str:
        """Get Linux autostart file path."""
        return str(self._get_autostart_path())
    
    # =========================================================================
    # Shortcuts (Linux uses .desktop files)
    # =========================================================================
    
    def _get_desktop_folder(self) -> Path:
        """Get Linux desktop folder path."""
        # XDG_DESKTOP_DIR may be set in user-dirs.dirs
        xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
        if xdg_desktop:
            return Path(xdg_desktop)
        return Path.home() / "Desktop"
    
    def _get_applications_folder(self) -> Path:
        """Get Linux applications folder path."""
        data_home = os.environ.get("XDG_DATA_HOME", "")
        if not data_home:
            data_home = Path.home() / ".local" / "share"
        else:
            data_home = Path(data_home)
        return data_home / "applications"
    
    def _create_desktop_file(self, path: Path) -> bool:
        """Create a .desktop file."""
        try:
            exe_path = self._get_executable_path()
            working_dir = exe_path.parent
            
            desktop_content = f'''[Desktop Entry]
Type=Application
Name=Project Launcher
Comment=Launch development projects
Exec="{exe_path}"
Path={working_dir}
Terminal=false
Categories=Development;
'''
            
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(desktop_content)
            os.chmod(path, 0o755)
            return True
        except Exception as e:
            print(f"Error creating desktop file: {e}")
            return False
    
    def has_desktop_shortcut(self) -> bool:
        desktop_path = self._get_desktop_folder() / "project-launcher.desktop"
        return desktop_path.exists()
    
    def create_desktop_shortcut(self) -> bool:
        desktop_path = self._get_desktop_folder() / "project-launcher.desktop"
        return self._create_desktop_file(desktop_path)
    
    def remove_desktop_shortcut(self) -> bool:
        try:
            desktop_path = self._get_desktop_folder() / "project-launcher.desktop"
            if desktop_path.exists():
                desktop_path.unlink()
            return True
        except Exception:
            return False
    
    def has_start_menu_shortcut(self) -> bool:
        """Check if applications menu entry exists."""
        apps_path = self._get_applications_folder() / "project-launcher.desktop"
        return apps_path.exists()
    
    def create_start_menu_shortcut(self) -> bool:
        """Create applications menu entry."""
        apps_path = self._get_applications_folder() / "project-launcher.desktop"
        return self._create_desktop_file(apps_path)
    
    def remove_start_menu_shortcut(self) -> bool:
        """Remove applications menu entry."""
        try:
            apps_path = self._get_applications_folder() / "project-launcher.desktop"
            if apps_path.exists():
                apps_path.unlink()
            return True
        except Exception:
            return False
    
    # =========================================================================
    # Install/Uninstall
    # =========================================================================
    
    def install_application(self, create_desktop: bool, create_start_menu: bool, 
                            create_startup: bool) -> dict:
        """Install the application on Linux."""
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
            os.chmod(target_exe, 0o755)
            
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
        """Uninstall the application on Linux."""
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
        """Setup Linux system tray icon using pystray."""
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
