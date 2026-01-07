# Project Launcher

A desktop application that helps developers quickly launch their development projects with one click. Open IDEs, terminals, AI coding tools, and browser tabs - all configured per project.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **One-click project launching** - Open everything you need for a project instantly
- **IDE Support** - VS Code, Cursor, Zed, Windsurf, Sublime Text, JetBrains IDEs
- **AI Coding Tools** - OpenCode, Claude Code, Aider, GitHub Copilot CLI
- **Terminal Commands** - Run custom commands on project launch
- **Multi-browser Support** - Chrome, Firefox, Edge, Safari, Brave, Arc
- **System Tray** - Runs minimized in the system tray
- **Auto-start** - Launches automatically on login
- **Cross-platform** - Works on Windows, macOS, and Linux

## Installation

Download the latest installer for your platform from the [Releases](https://github.com/ClarkeFL/project-launch/releases) page:

| Platform | File | Instructions |
|----------|------|--------------|
| **Windows** | `ProjectLauncher-Setup-Windows.exe` | Double-click to install |
| **macOS** | `ProjectLauncher-Installer-macOS` | `chmod +x` then run |
| **Linux** | `project-launcher-installer-Linux` | `chmod +x` then run |

### What the installer does

- Installs the application
- Creates desktop/menu shortcuts
- Sets up auto-start on login
- Registers uninstaller (Windows: Add/Remove Programs)

## Usage

### Adding a Project

1. Click **"+ Add Project"**
2. Fill in the project details:
   - **Name** - Display name for the project
   - **Path** - Root directory of your project
   - **IDE** - Which editor to open
   - **AI Tool** - Optional AI coding assistant
   - **Terminal Command** - Optional command to run (e.g., `npm run dev`)
   - **Browser URLs** - URLs to open (e.g., `http://localhost:3000`)

### Launching a Project

Click the **"Launch"** button on any project card. This will:
1. Open the project in your selected IDE
2. Start the AI coding tool (if configured)
3. Run the terminal command (if configured)
4. Open browser tabs (if configured)

### Configuration

Projects are stored in a YAML config file:
- **Windows:** `%LOCALAPPDATA%\ProjectLauncher\config.yaml`
- **macOS/Linux:** `~/.config/ProjectLauncher/config.yaml`

Example configuration:

```yaml
projects:
  - name: My Web App
    path: /path/to/project
    ide: cursor
    ai_tool: opencode
    terminal_command: npm run dev
    browser_urls:
      - http://localhost:3000
      - http://localhost:3000/admin
    browser: chrome
```

## Supported Tools

### IDEs
- VS Code (`code`)
- Cursor (`cursor`)
- Zed (`zed`)
- Windsurf (`windsurf`)
- Sublime Text (`sublime`)
- JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.)

### AI Coding Tools
- OpenCode (`opencode`)
- Claude Code (`claude`)
- Aider (`aider`)
- GitHub Copilot CLI (`copilot`)

### Browsers
- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Safari (macOS)
- Brave
- Arc

## Development

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
git clone https://github.com/ClarkeFL/project-launch.git
cd project-launch
pip install -r requirements.txt
```

### Running from Source

```bash
python project_launcher.py
```

### Building

```bash
# Build the standalone app
python build.py

# Build the installer
python build_installer.py
```

## Uninstalling

### Windows
- **Settings > Apps > Project Launcher > Uninstall**, or
- **Start Menu > Project Launcher > Uninstall Project Launcher**

### macOS
- Run `~/Applications/ProjectLauncher/uninstall.sh`, or
- Find "Uninstall Project Launcher" in Applications

### Linux
- Find "Uninstall Project Launcher" in your application menu, or
- Run `~/.local/share/ProjectLauncher/uninstall.sh`

## License

[MIT](LICENSE)
