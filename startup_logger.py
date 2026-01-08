"""
Startup Logger for Project Launcher
Lightweight timing/logging utility to diagnose startup performance.
Uses only standard library to avoid import overhead.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Store start time immediately when module is imported
_import_time = time.perf_counter()
_session_start = None
_log_file = None
_is_auto_startup = False

# Maximum number of startup sessions to keep in log
MAX_SESSIONS = 10
SESSION_SEPARATOR = "=" * 60


def _get_log_path() -> Path:
    """Get the log file path."""
    if sys.platform == "win32":
        home = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    else:
        home = os.path.expanduser("~")
    
    log_dir = Path(home) / ".project-launcher"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "startup.log"


def _rotate_log(log_path: Path) -> None:
    """Keep only the last MAX_SESSIONS sessions in the log file."""
    if not log_path.exists():
        return
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by session separator
        sessions = content.split(SESSION_SEPARATOR)
        
        # Filter out empty sessions and keep last MAX_SESSIONS
        sessions = [s.strip() for s in sessions if s.strip()]
        if len(sessions) > MAX_SESSIONS:
            sessions = sessions[-MAX_SESSIONS:]
            
            # Rewrite file with only recent sessions
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"\n{SESSION_SEPARATOR}\n".join(sessions))
                f.write(f"\n{SESSION_SEPARATOR}\n")
    except Exception:
        # If rotation fails, just continue - logging shouldn't break the app
        pass


def _timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _elapsed() -> str:
    """Get elapsed time since session start in milliseconds."""
    if _session_start is None:
        return "0ms"
    elapsed_ms = (time.perf_counter() - _session_start) * 1000
    return f"{elapsed_ms:.0f}ms"


def start_session(auto: bool = False) -> None:
    """
    Start a new logging session.
    
    Args:
        auto: True if this is an auto-startup (from Windows startup folder)
    """
    global _session_start, _log_file, _is_auto_startup
    
    _session_start = _import_time  # Use the time when module was first imported
    _is_auto_startup = auto
    
    log_path = _get_log_path()
    _rotate_log(log_path)
    
    try:
        _log_file = open(log_path, "a", encoding="utf-8")
        
        startup_type = "auto-startup" if auto else "manual"
        _log_file.write(f"\n{SESSION_SEPARATOR}\n")
        _log_file.write(f"[{_timestamp()}] === Startup Begin ({startup_type}) ===\n")
        _log_file.write(f"[{_timestamp()}] [+{_elapsed()}] Python interpreter ready\n")
        _log_file.flush()
    except Exception:
        _log_file = None


def log(message: str) -> None:
    """
    Log a message with timestamp and elapsed time.
    
    Args:
        message: The message to log
    """
    if _log_file is None:
        return
    
    try:
        _log_file.write(f"[{_timestamp()}] [+{_elapsed()}] {message}\n")
        _log_file.flush()
    except Exception:
        pass


def end_session() -> None:
    """End the logging session and record total startup time."""
    global _log_file
    
    if _log_file is None:
        return
    
    try:
        total_ms = (time.perf_counter() - _session_start) * 1000 if _session_start else 0
        _log_file.write(f"[{_timestamp()}] === Startup Complete: {total_ms:.0f}ms ({total_ms/1000:.2f}s) ===\n")
        _log_file.flush()
        _log_file.close()
    except Exception:
        pass
    finally:
        _log_file = None


def log_vbs_timestamp(message: str) -> None:
    """
    Static method to log from VBS script (called via command line).
    This is used by the VBS startup script to log timestamps.
    
    Usage: python -c "from startup_logger import log_vbs_timestamp; log_vbs_timestamp('message')"
    """
    log_path = _get_log_path()
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{_timestamp()}] [VBS] {message}\n")
    except Exception:
        pass


# Allow calling from command line for VBS logging
if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_vbs_timestamp(" ".join(sys.argv[1:]))
