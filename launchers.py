"""
Launchers for Project Launcher
Handles launching VS Code, terminals, browsers, and other applications.
"""

import os
import sys
import platform
import subprocess
import webbrowser
import time
from pathlib import Path
from typing import List, Optional


def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()


# =============================================================================
# VS Code Launcher
# =============================================================================

def launch_vscode(project_path: str) -> bool:
    """
    Open a project folder in VS Code.
    
    Args:
        project_path: Path to the project folder
        
    Returns:
        True if successful, False otherwise
    """
    return launch_ide(project_path, "vscode")


def launch_ide(project_path: str, ide: str) -> bool:
    """
    Open a project folder in the specified IDE.
    
    Args:
        project_path: Path to the project folder
        ide: IDE to use (vscode, cursor, zed, windsurf, sublime, webstorm, pycharm, intellij)
        
    Returns:
        True if successful, False otherwise
    """
    # Map IDE names to their command-line commands
    ide_commands = {
        "vscode": "code",
        "cursor": "cursor",
        "zed": "zed",
        "windsurf": "windsurf",
        "sublime": "subl",
        "webstorm": "webstorm",
        "pycharm": "pycharm",
        "intellij": "idea",
    }
    
    cmd = ide_commands.get(ide, "code")
    
    try:
        subprocess.Popen(
            [cmd, project_path],
            shell=(get_platform() == "Windows"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        print(f"IDE '{ide}' command '{cmd}' not found. Make sure it is installed and in PATH.")
        return False
    except Exception as e:
        print(f"Error launching IDE: {e}")
        return False


def launch_ai_tool(project_path: str, tool: str, terminal_app: str) -> bool:
    """
    Launch an AI coding tool in a terminal.
    
    Args:
        project_path: Path to the project folder
        tool: AI tool to use (opencode, claude, aider, copilot)
        terminal_app: Terminal application to use
        
    Returns:
        True if successful, False otherwise
    """
    # Map tool names to their commands
    tool_commands = {
        "opencode": "opencode",
        "claude": "claude",
        "aider": "aider",
        "copilot": "gh copilot",
    }
    
    cmd = tool_commands.get(tool, tool)
    
    return launch_terminal(project_path, terminal_app, [cmd])


# =============================================================================
# Terminal Launcher
# =============================================================================

def launch_terminal(
    project_path: str,
    terminal_app: str,
    commands: Optional[List[str]] = None
) -> bool:
    """
    Open a terminal window at the project path, optionally running commands.
    
    Args:
        project_path: Path to open the terminal in
        terminal_app: Terminal application to use
        commands: Optional list of commands to run
        
    Returns:
        True if successful, False otherwise
    """
    system = get_platform()
    
    try:
        if system == "Windows":
            return _launch_windows_terminal(project_path, terminal_app, commands)
        elif system == "Darwin":
            return _launch_mac_terminal(project_path, terminal_app, commands)
        else:
            return _launch_linux_terminal(project_path, terminal_app, commands)
    except Exception as e:
        print(f"Error launching terminal: {e}")
        return False


def _launch_windows_terminal(
    project_path: str,
    terminal_app: str,
    commands: Optional[List[str]] = None
) -> bool:
    """Launch terminal on Windows."""
    
    # Build the command string to execute
    cmd_string = ""
    if commands:
        cmd_string = " && ".join(commands)
    
    if terminal_app == "terminal" or terminal_app == "wt":
        # Windows Terminal
        args = ["wt", "-d", project_path]
        if cmd_string:
            args.extend(["cmd", "/k", cmd_string])
        subprocess.Popen(args, shell=True)
        
    elif terminal_app == "powershell":
        # PowerShell
        if cmd_string:
            ps_commands = "; ".join(commands) if commands else ""
            args = ["powershell", "-NoExit", "-Command", 
                   f"Set-Location '{project_path}'; {ps_commands}"]
        else:
            args = ["powershell", "-NoExit", "-Command", 
                   f"Set-Location '{project_path}'"]
        subprocess.Popen(args, shell=True)
        
    elif terminal_app == "cmd":
        # Command Prompt
        if cmd_string:
            args = ["cmd", "/k", f"cd /d \"{project_path}\" && {cmd_string}"]
        else:
            args = ["cmd", "/k", f"cd /d \"{project_path}\""]
        subprocess.Popen(args, shell=True)
        
    else:
        # Default to Windows Terminal
        args = ["wt", "-d", project_path]
        if cmd_string:
            args.extend(["cmd", "/k", cmd_string])
        subprocess.Popen(args, shell=True)
    
    return True


def _launch_mac_terminal(
    project_path: str,
    terminal_app: str,
    commands: Optional[List[str]] = None
) -> bool:
    """Launch terminal on macOS."""
    
    cmd_string = ""
    if commands:
        cmd_string = " && ".join(commands)
    
    if terminal_app == "ghostty":
        # Ghostty
        args = ["open", "-a", "Ghostty", "--args", f"--working-directory={project_path}"]
        subprocess.Popen(args)
        
        # If we have commands, we need to use a different approach
        # Ghostty doesn't have a direct command execution flag like some terminals
        if commands:
            # Give Ghostty time to open, then use osascript to type commands
            time.sleep(0.5)
            script = f'''
            tell application "Ghostty"
                activate
            end tell
            tell application "System Events"
                keystroke "cd {project_path} && {cmd_string}"
                keystroke return
            end tell
            '''
            subprocess.Popen(["osascript", "-e", script])
        
    elif terminal_app == "terminal":
        # Terminal.app
        if cmd_string:
            script = f'''
            tell application "Terminal"
                do script "cd {project_path} && {cmd_string}"
                activate
            end tell
            '''
        else:
            script = f'''
            tell application "Terminal"
                do script "cd {project_path}"
                activate
            end tell
            '''
        subprocess.Popen(["osascript", "-e", script])
        
    elif terminal_app == "iterm":
        # iTerm2
        if cmd_string:
            script = f'''
            tell application "iTerm"
                create window with default profile
                tell current session of current window
                    write text "cd {project_path} && {cmd_string}"
                end tell
            end tell
            '''
        else:
            script = f'''
            tell application "iTerm"
                create window with default profile
                tell current session of current window
                    write text "cd {project_path}"
                end tell
            end tell
            '''
        subprocess.Popen(["osascript", "-e", script])
        
    else:
        # Default to Ghostty
        return _launch_mac_terminal(project_path, "ghostty", commands)
    
    return True


def _launch_linux_terminal(
    project_path: str,
    terminal_app: str,
    commands: Optional[List[str]] = None
) -> bool:
    """Launch terminal on Linux."""
    
    cmd_string = ""
    if commands:
        cmd_string = " && ".join(commands)
    
    # Build the full command to run in terminal
    if cmd_string:
        full_cmd = f"cd \"{project_path}\" && {cmd_string}; exec $SHELL"
    else:
        full_cmd = f"cd \"{project_path}\"; exec $SHELL"
    
    if terminal_app == "ghostty":
        # Ghostty
        args = ["ghostty", f"--working-directory={project_path}"]
        if commands:
            args.extend(["-e", "bash", "-c", full_cmd])
        subprocess.Popen(args)
        
    elif terminal_app == "gnome-terminal":
        # GNOME Terminal
        args = ["gnome-terminal", f"--working-directory={project_path}"]
        if commands:
            args.extend(["--", "bash", "-c", full_cmd])
        subprocess.Popen(args)
        
    elif terminal_app == "konsole":
        # Konsole
        args = ["konsole", "--workdir", project_path]
        if commands:
            args.extend(["-e", "bash", "-c", full_cmd])
        subprocess.Popen(args)
        
    elif terminal_app == "xterm":
        # XTerm
        args = ["xterm", "-e", f"cd \"{project_path}\" && $SHELL"]
        if commands:
            args = ["xterm", "-e", f"bash -c '{full_cmd}'"]
        subprocess.Popen(args)
        
    else:
        # Try to detect available terminal
        for term in ["ghostty", "gnome-terminal", "konsole", "xterm"]:
            try:
                subprocess.run(["which", term], capture_output=True, check=True)
                return _launch_linux_terminal(project_path, term, commands)
            except subprocess.CalledProcessError:
                continue
        
        print("No supported terminal found on this system.")
        return False
    
    return True


# =============================================================================
# Browser Launcher
# =============================================================================

def get_browser_command(browser: str) -> Optional[List[str]]:
    """
    Get the command to launch a specific browser.
    
    Args:
        browser: Browser name (chrome, firefox, edge, safari, brave, arc, opera)
        
    Returns:
        Command list or None if browser not supported
    """
    system = get_platform()
    
    if system == "Windows":
        browser_paths = {
            "chrome": ["start", "chrome"],
            "firefox": ["start", "firefox"],
            "edge": ["start", "msedge"],
            "brave": ["start", "brave"],
            "opera": ["start", "opera"],
        }
    elif system == "Darwin":
        browser_paths = {
            "chrome": ["open", "-a", "Google Chrome"],
            "firefox": ["open", "-a", "Firefox"],
            "safari": ["open", "-a", "Safari"],
            "edge": ["open", "-a", "Microsoft Edge"],
            "brave": ["open", "-a", "Brave Browser"],
            "arc": ["open", "-a", "Arc"],
            "opera": ["open", "-a", "Opera"],
        }
    else:  # Linux
        browser_paths = {
            "chrome": ["google-chrome"],
            "firefox": ["firefox"],
            "edge": ["microsoft-edge"],
            "brave": ["brave-browser"],
            "opera": ["opera"],
        }
    
    return browser_paths.get(browser)


def launch_browser(tabs: List[str], browsers: Optional[List[str]] = None, delay_between_tabs: float = 0.5) -> bool:
    """
    Open browser with multiple tabs.
    
    Args:
        tabs: List of URLs to open
        browsers: List of browsers to open (if None, uses system default)
        delay_between_tabs: Delay between opening each tab (to prevent issues)
        
    Returns:
        True if successful, False otherwise
    """
    if not tabs:
        return True
    
    system = get_platform()
    
    # If no specific browsers selected, use system default
    use_browsers: List[Optional[str]] = list(browsers) if browsers else [None]
    
    try:
        for browser in use_browsers:
            for i, url in enumerate(tabs):
                # Ensure URL has a protocol
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                
                if browser and browser != "default":
                    # Open in specific browser
                    browser_cmd = get_browser_command(browser)
                    if browser_cmd:
                        if system == "Windows":
                            subprocess.Popen(["cmd", "/c"] + browser_cmd + [url], shell=True)
                        elif system == "Darwin":
                            subprocess.Popen(browser_cmd + [url])
                        else:
                            subprocess.Popen(browser_cmd + [url])
                    else:
                        # Browser not found, fall back to default
                        _open_url_default(url, system)
                else:
                    _open_url_default(url, system)
                
                # Small delay between tabs
                if i < len(tabs) - 1:
                    time.sleep(delay_between_tabs)
            
            # Delay between different browsers
            if len(use_browsers) > 1:
                time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"Error launching browser: {e}")
        # Fallback to webbrowser module
        try:
            for i, url in enumerate(tabs):
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open(url, new=2 if i > 0 else 1)
                if i < len(tabs) - 1:
                    time.sleep(delay_between_tabs)
            return True
        except Exception as e2:
            print(f"Fallback browser launch also failed: {e2}")
            return False


def _open_url_default(url: str, system: str):
    """Open URL in the system default browser."""
    if system == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=True)
    elif system == "Darwin":
        subprocess.Popen(["open", url])
    else:
        subprocess.Popen(["xdg-open", url])


# =============================================================================
# Action Executor
# =============================================================================

def execute_project_actions(project: dict, terminal_app: str) -> dict:
    """
    Execute all actions for a project.
    
    Args:
        project: Project configuration dict with 'name', 'path', and 'actions'
        terminal_app: Terminal application to use
        
    Returns:
        Dict with results for each action type
    """
    results = {
        "ide": None,
        "vscode": None,
        "ai_tools": [],
        "terminals": [],
        "browser": None,
        "errors": []
    }
    
    project_path = project.get("path", "")
    actions = project.get("actions", [])
    
    if not project_path or not os.path.exists(project_path):
        results["errors"].append(f"Project path does not exist: {project_path}")
        return results
    
    for action in actions:
        action_type = action.get("type", "")
        
        try:
            if action_type == "ide":
                ide = action.get("ide", "vscode")
                results["ide"] = launch_ide(project_path, ide)
                
            elif action_type == "vscode":
                # Legacy support
                results["vscode"] = launch_vscode(project_path)
                
            elif action_type == "ai_tool":
                tool = action.get("tool", "")
                success = launch_ai_tool(project_path, tool, terminal_app)
                results["ai_tools"].append(success)
                time.sleep(0.3)
                
            elif action_type == "terminal":
                commands = action.get("commands", [])
                success = launch_terminal(project_path, terminal_app, commands)
                results["terminals"].append(success)
                # Small delay between terminal launches
                time.sleep(0.3)
                
            elif action_type == "browser":
                tabs = action.get("tabs", [])
                browsers = action.get("browsers", [])
                results["browser"] = launch_browser(tabs, browsers if browsers else None)
                
            else:
                results["errors"].append(f"Unknown action type: {action_type}")
                
        except Exception as e:
            results["errors"].append(f"Error executing {action_type}: {e}")
    
    return results


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print("\nTesting launchers...")
    
    # Test browser
    print("\nOpening browser with test tab...")
    # launch_browser(["https://example.com"])
    
    # Test terminal (uncomment to test)
    # print("\nOpening terminal...")
    # launch_terminal(os.getcwd(), "terminal", ["echo 'Hello from launcher!'"])
    
    print("\nLauncher module loaded successfully!")
