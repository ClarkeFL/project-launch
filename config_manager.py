"""
Configuration Manager for Project Launcher
Handles YAML config loading, saving, and default creation.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional

# Try to import yaml, fail gracefully if not installed
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required but not installed.")
    print("Please install it with: pip install pyyaml")
    sys.exit(1)


def get_config_dir() -> Path:
    """Get the configuration directory path based on platform."""
    if platform.system() == "Windows":
        # Use USERPROFILE on Windows
        home = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    else:
        home = os.path.expanduser("~")
    
    return Path(home) / ".project-launcher"


def get_config_path() -> Path:
    """Get the full path to the config file."""
    return get_config_dir() / "config.yaml"


def get_default_terminal() -> str:
    """Get the default terminal based on platform."""
    system = platform.system()
    if system == "Windows":
        return "terminal"  # Windows Terminal
    elif system == "Darwin":
        return "ghostty"  # Recommended for Mac
    else:
        return "ghostty"  # Recommended for Linux


def get_default_config() -> dict:
    """Return the default configuration structure."""
    return {
        "settings": {
            "show_on_startup": True,
            "terminal": get_default_terminal(),
        },
        "projects": []
    }


def ensure_config_dir() -> Path:
    """Ensure the config directory exists."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def load_config() -> dict:
    """Load configuration from YAML file, or create default if not exists."""
    config_path = get_config_path()
    
    if not config_path.exists():
        # Create default config
        config = get_default_config()
        save_config(config)
        return config
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        # Ensure all required keys exist
        if config is None:
            config = get_default_config()
        
        # Merge with defaults to ensure all keys exist
        default = get_default_config()
        if "settings" not in config:
            config["settings"] = default["settings"]
        else:
            for key, value in default["settings"].items():
                if key not in config["settings"]:
                    config["settings"][key] = value
        
        if "projects" not in config:
            config["projects"] = []
            
        return config
        
    except Exception as e:
        print(f"Error loading config: {e}")
        return get_default_config()


def save_config(config: dict) -> bool:
    """Save configuration to YAML file."""
    try:
        ensure_config_dir()
        config_path = get_config_path()
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def add_project(config: dict, project: dict) -> dict:
    """Add a new project to the configuration."""
    config["projects"].append(project)
    return config


def remove_project(config: dict, index: int) -> dict:
    """Remove a project from the configuration by index."""
    if 0 <= index < len(config["projects"]):
        config["projects"].pop(index)
    return config


def update_project(config: dict, index: int, project: dict) -> dict:
    """Update an existing project in the configuration."""
    if 0 <= index < len(config["projects"]):
        config["projects"][index] = project
    return config


def get_terminal_options() -> dict:
    """Get available terminal options for each platform."""
    return {
        "Windows": [
            ("terminal", "Windows Terminal"),
            ("powershell", "PowerShell"),
            ("cmd", "Command Prompt"),
        ],
        "Darwin": [
            ("ghostty", "Ghostty (Recommended)"),
            ("terminal", "Terminal.app"),
            ("iterm", "iTerm2"),
        ],
        "Linux": [
            ("ghostty", "Ghostty (Recommended)"),
            ("gnome-terminal", "GNOME Terminal"),
            ("konsole", "Konsole"),
            ("xterm", "XTerm"),
        ]
    }


def get_current_platform_terminals() -> list:
    """Get terminal options for the current platform."""
    system = platform.system()
    options = get_terminal_options()
    return options.get(system, options["Linux"])


# Example project structure for reference
EXAMPLE_PROJECT = {
    "name": "Example Project",
    "path": "/path/to/project",
    "actions": [
        {"type": "vscode"},
        {"type": "terminal", "commands": ["npm install", "npm run dev"]},
        {"type": "terminal", "commands": ["opencode"]},
        {"type": "browser", "tabs": ["http://localhost:3000"]},
    ]
}


if __name__ == "__main__":
    # Test the config manager
    print(f"Config directory: {get_config_dir()}")
    print(f"Config path: {get_config_path()}")
    print(f"Default terminal: {get_default_terminal()}")
    
    config = load_config()
    print(f"\nLoaded config:")
    print(yaml.dump(config, default_flow_style=False))
