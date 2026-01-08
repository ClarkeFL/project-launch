"""
Platform Base - Abstract base class for platform-specific functionality
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import tkinter as tk


class PlatformHandler(ABC):
    """Abstract base class for platform-specific functionality."""
    
    # =========================================================================
    # Dialog Configuration
    # =========================================================================
    
    @property
    @abstractmethod
    def use_native_dialog_titlebar(self) -> bool:
        """Return True if dialogs should use native OS title bar."""
        pass
    
    @property
    @abstractmethod
    def use_native_window_titlebar(self) -> bool:
        """Return True if main window should use native OS title bar."""
        pass
    
    @property
    @abstractmethod
    def supports_tray_icon(self) -> bool:
        """Return True if platform supports system tray icon."""
        pass
    
    @property
    @abstractmethod
    def supports_menu_bar(self) -> bool:
        """Return True if platform has native menu bar (like macOS)."""
        pass
    
    # =========================================================================
    # Startup & Installation
    # =========================================================================
    
    @abstractmethod
    def get_install_dir(self) -> Path:
        """Get the installation directory for this platform."""
        pass
    
    @abstractmethod
    def get_installed_exe_path(self) -> Path:
        """Get the path where the exe/app should be installed."""
        pass
    
    @abstractmethod
    def is_startup_enabled(self) -> bool:
        """Check if startup is enabled."""
        pass
    
    @abstractmethod
    def set_startup_enabled(self, enabled: bool) -> bool:
        """Enable or disable startup."""
        pass
    
    @abstractmethod
    def get_startup_location(self) -> str:
        """Get the path to startup file/entry."""
        pass
    
    # =========================================================================
    # Shortcuts
    # =========================================================================
    
    @abstractmethod
    def has_desktop_shortcut(self) -> bool:
        """Check if desktop shortcut exists."""
        pass
    
    @abstractmethod
    def create_desktop_shortcut(self) -> bool:
        """Create desktop shortcut."""
        pass
    
    @abstractmethod
    def remove_desktop_shortcut(self) -> bool:
        """Remove desktop shortcut."""
        pass
    
    @abstractmethod
    def has_start_menu_shortcut(self) -> bool:
        """Check if start menu shortcut exists."""
        pass
    
    @abstractmethod
    def create_start_menu_shortcut(self) -> bool:
        """Create start menu shortcut."""
        pass
    
    @abstractmethod
    def remove_start_menu_shortcut(self) -> bool:
        """Remove start menu shortcut."""
        pass
    
    # =========================================================================
    # Installation
    # =========================================================================
    
    @abstractmethod
    def install_application(self, create_desktop: bool, create_start_menu: bool, 
                            create_startup: bool) -> dict:
        """
        Install the application.
        
        Returns dict with:
            - success: bool
            - install_path: str
            - error: str (if failed)
        """
        pass
    
    @abstractmethod
    def uninstall_application(self, remove_app: bool, remove_config: bool) -> dict:
        """
        Uninstall the application.
        
        Args:
            remove_app: Whether to remove the application files
            remove_config: Whether to remove config/data files
            
        Returns dict with:
            - success: bool
            - error: str (if failed)
        """
        pass
    
    # =========================================================================
    # Dialog/Window Configuration
    # =========================================================================
    
    def configure_dialog(self, dialog: tk.Toplevel) -> None:
        """
        Configure a dialog window for this platform.
        Override in subclasses for platform-specific setup.
        
        Args:
            dialog: The Toplevel dialog to configure
        """
        pass
    
    def configure_main_window(self, window: tk.Tk) -> None:
        """
        Configure the main application window for this platform.
        Override in subclasses for platform-specific setup.
        
        Args:
            window: The main Tk window to configure
        """
        pass
    
    # =========================================================================
    # Tray Icon
    # =========================================================================
    
    def setup_tray_icon(self, on_show, on_hide, on_quit) -> Optional[object]:
        """
        Setup system tray icon.
        
        Args:
            on_show: Callback to show window
            on_hide: Callback to hide window  
            on_quit: Callback to quit application
            
        Returns:
            Tray icon object if supported, None otherwise
        """
        return None
    
    def setup_menu_bar(self, window: tk.Tk, menu_config: dict) -> None:
        """
        Setup native menu bar (macOS).
        
        Args:
            window: Main window
            menu_config: Dictionary defining menu structure
        """
        pass
