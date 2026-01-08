"""
Platform Handlers Module - Factory for platform-specific handlers

Usage:
    from platform_handlers import get_platform_handler
    
    handler = get_platform_handler()
    handler.set_startup_enabled(True)
"""
import platform as sys_platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platform_handlers.base import PlatformHandler

# Cached handler instance
_handler = None


def get_platform_handler() -> "PlatformHandler":
    """
    Get the platform-specific handler for the current OS.
    
    Returns a singleton instance of the appropriate platform handler.
    """
    global _handler
    
    if _handler is not None:
        return _handler
    
    system = sys_platform.system()
    
    if system == "Windows":
        from platform_handlers.windows import WindowsPlatformHandler
        _handler = WindowsPlatformHandler()
    elif system == "Darwin":
        from platform_handlers.macos import MacOSPlatformHandler
        _handler = MacOSPlatformHandler()
    else:  # Linux and others
        from platform_handlers.linux import LinuxPlatformHandler
        _handler = LinuxPlatformHandler()
    
    return _handler


def get_platform_name() -> str:
    """Get the current platform name (Windows, Darwin, Linux)."""
    return sys_platform.system()


# Export base class for type hints
from platform_handlers.base import PlatformHandler

__all__ = [
    "get_platform_handler",
    "get_platform_name",
    "PlatformHandler",
]
