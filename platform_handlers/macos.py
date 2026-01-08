"""
macOS Platform Handler
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import tkinter as tk

from platform_handlers.base import PlatformHandler


class MacOSPlatformHandler(PlatformHandler):
    """macOS-specific platform implementation."""
    
    # =========================================================================
    # Dialog Configuration
    # =========================================================================
    
    @property
    def use_native_dialog_titlebar(self) -> bool:
        """macOS: Use native title bars to fix keyboard input issues."""
        return True
    
    @property
    def use_native_window_titlebar(self) -> bool:
        """macOS: Use native title bar for stability."""
        return True
    
    @property
    def supports_tray_icon(self) -> bool:
        """macOS: Disable pystray to avoid Cocoa event loop conflicts."""
        return False
    
    @property
    def supports_menu_bar(self) -> bool:
        """macOS: Has native top menu bar."""
        return True
    
    # =========================================================================
    # Path Helpers
    # =========================================================================
    
    def _get_executable_path(self) -> Path:
        """Get the path to the running executable or .app bundle."""
        if getattr(sys, 'frozen', False):
            exe_path = Path(sys.executable)
            
            # Check if we're inside a .app bundle
            parts = exe_path.parts
            for i, part in enumerate(parts):
                if part.endswith('.app'):
                    # Return the .app bundle path
                    return Path(*parts[:i+1])
            
            return exe_path
        else:
            return Path(__file__).parent.parent / "project_launcher.py"
    
    def _get_launch_agent_path(self) -> Path:
        """Get path to the macOS LaunchAgent plist."""
        return Path.home() / "Library" / "LaunchAgents" / "com.projectlauncher.plist"
    
    # =========================================================================
    # Installation
    # =========================================================================
    
    def get_install_dir(self) -> Path:
        """macOS: Install to /Applications or ~/Applications."""
        system_apps = Path("/Applications")
        if os.access(system_apps, os.W_OK):
            return system_apps
        return Path.home() / "Applications"
    
    def get_installed_exe_path(self) -> Path:
        """macOS: Return .app bundle path."""
        return self.get_install_dir() / "ProjectLauncher.app"
    
    # =========================================================================
    # Startup
    # =========================================================================
    
    def is_startup_enabled(self) -> bool:
        """Check if macOS startup is enabled."""
        return self._get_launch_agent_path().exists()
    
    def set_startup_enabled(self, enabled: bool) -> bool:
        """Enable or disable macOS startup via LaunchAgent."""
        if enabled:
            return self._enable_startup()
        else:
            return self._disable_startup()
    
    def _enable_startup(self) -> bool:
        """Enable startup on macOS using LaunchAgent."""
        try:
            launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            exe_path = self._get_executable_path()
            
            # For .app bundles, use 'open' command with --args
            if str(exe_path).endswith(".app"):
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.projectlauncher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-a</string>
        <string>{exe_path}</string>
        <string>--args</string>
        <string>--auto</string>
    </array>
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
            else:
                # For standalone binary (non-.app)
                working_dir = exe_path.parent
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
            
            plist_path = self._get_launch_agent_path()
            with open(plist_path, "w") as f:
                f.write(plist_content)
            
            # Load the LaunchAgent
            subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
            
            return True
        except Exception as e:
            print(f"Error enabling macOS startup: {e}")
            return False
    
    def _disable_startup(self) -> bool:
        """Disable startup on macOS."""
        try:
            plist_path = self._get_launch_agent_path()
            
            if plist_path.exists():
                # Unload the LaunchAgent
                subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
                plist_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error disabling macOS startup: {e}")
            return False
    
    def get_startup_location(self) -> str:
        """Get macOS LaunchAgent path."""
        return str(self._get_launch_agent_path())
    
    # =========================================================================
    # Shortcuts (macOS doesn't use shortcuts like Windows)
    # =========================================================================
    
    def has_desktop_shortcut(self) -> bool:
        """macOS doesn't use desktop shortcuts."""
        return False
    
    def create_desktop_shortcut(self) -> bool:
        """macOS doesn't use desktop shortcuts."""
        return False
    
    def remove_desktop_shortcut(self) -> bool:
        """macOS doesn't use desktop shortcuts."""
        return False
    
    def has_start_menu_shortcut(self) -> bool:
        """macOS doesn't have a start menu."""
        return False
    
    def create_start_menu_shortcut(self) -> bool:
        """macOS doesn't have a start menu."""
        return False
    
    def remove_start_menu_shortcut(self) -> bool:
        """macOS doesn't have a start menu."""
        return False
    
    # =========================================================================
    # Install/Uninstall
    # =========================================================================
    
    def install_application(self, create_desktop: bool, create_start_menu: bool, 
                            create_startup: bool) -> dict:
        """Install the application on macOS."""
        result = {"success": False, "install_path": "", "error": ""}
        
        try:
            current_app = self._get_executable_path()
            install_dir = self.get_install_dir()
            target_app = self.get_installed_exe_path()
            
            # Check if already installed
            try:
                current_app.relative_to(install_dir)
                # Already installed
                result["success"] = True
                result["install_path"] = str(target_app)
                
                if create_startup:
                    self.set_startup_enabled(True)
                
                return result
            except ValueError:
                pass  # Not installed, continue
            
            # On macOS, copy the entire .app bundle
            if str(current_app).endswith(".app"):
                # Remove existing .app if present
                if target_app.exists():
                    shutil.rmtree(target_app)
                # Copy entire .app bundle
                shutil.copytree(current_app, target_app, symlinks=True)
            else:
                # For non-.app (script mode), just copy the executable
                install_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(current_app, target_app)
                os.chmod(target_app, 0o755)
            
            result["success"] = True
            result["install_path"] = str(target_app)
            
            # Enable startup if requested
            if create_startup:
                self.set_startup_enabled(True)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def uninstall_application(self, remove_app: bool, remove_config: bool) -> dict:
        """Uninstall the application on macOS."""
        result = {"success": False, "error": ""}
        
        try:
            # Always disable startup
            self.set_startup_enabled(False)
            
            if remove_app:
                target_app = self.get_installed_exe_path()
                if target_app.exists():
                    if target_app.is_dir():  # .app bundle
                        shutil.rmtree(target_app)
                    else:
                        target_app.unlink()
            
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
    # Dialog/Window Configuration
    # =========================================================================
    
    def configure_dialog(self, dialog: tk.Toplevel) -> None:
        """Configure dialog for macOS - use native title bar."""
        # Don't use overrideredirect on macOS to ensure keyboard input works
        dialog.resizable(False, False)
        # Ensure dialog gets focus
        dialog.lift()
        dialog.focus_force()
    
    def configure_main_window(self, window: tk.Tk) -> None:
        """Configure main window for macOS - use native title bar."""
        # Don't use overrideredirect for better stability
        pass
    
    # =========================================================================
    # Menu Bar (macOS native)
    # =========================================================================
    
    def setup_menu_bar(self, window: tk.Tk, menu_config: dict) -> None:
        """Setup native macOS menu bar."""
        menubar = tk.Menu(window)
        
        # Application menu (macOS standard)
        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(label="About Project Launcher", 
                            command=menu_config.get("about"))
        app_menu.add_separator()
        app_menu.add_command(label="Settings...", 
                            command=menu_config.get("settings"),
                            accelerator="Cmd+,")
        app_menu.add_separator()
        app_menu.add_command(label="Quit Project Launcher", 
                            command=menu_config.get("quit"),
                            accelerator="Cmd+Q")
        menubar.add_cascade(label="Project Launcher", menu=app_menu)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add Project...", 
                             command=menu_config.get("add_project"),
                             accelerator="Cmd+N")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Window menu (macOS standard)
        window_menu = tk.Menu(menubar, tearoff=0)
        window_menu.add_command(label="Minimize", 
                               command=lambda: window.iconify(),
                               accelerator="Cmd+M")
        menubar.add_cascade(label="Window", menu=window_menu)
        
        window.config(menu=menubar)
        
        # Bind keyboard shortcuts
        window.bind("<Command-q>", lambda e: menu_config.get("quit", lambda: None)())
        window.bind("<Command-comma>", lambda e: menu_config.get("settings", lambda: None)())
        window.bind("<Command-n>", lambda e: menu_config.get("add_project", lambda: None)())
