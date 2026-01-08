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
- **Auto-start** - Optionally launches automatically on login
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Portable** - Can run without installing, or install with one click

## Installation

Download the latest release for your platform from the [Releases](https://github.com/ClarkeFL/project-launch/releases) page:

| Platform | File | Instructions |
|----------|------|--------------|
| **Windows** | `ProjectLauncher-Windows-vX.X.X.exe` | Download and run |
| **macOS** | `ProjectLauncher-macOS-vX.X.X` | Download, `chmod +x`, and run |
| **Linux** | `project-launcher-Linux-vX.X.X` | Download, `chmod +x`, and run |

### First Run

When you run the application for the first time, you'll be prompted to:

1. **Install** - Copies the app to a standard location (`%LOCALAPPDATA%\ProjectLauncher` on Windows) and creates shortcuts
2. **Run Portable** - Run directly from wherever you downloaded it

Both options work well - installing just makes it easier to find and launch the app.

### What Installing Does

- Copies the executable to your user's app folder (no admin required)
- Optionally creates Desktop shortcut
- Optionally creates Start Menu shortcut
- Optionally enables auto-start on login

### Security Warnings

Since the app is not code-signed, you may see security warnings. This is normal for open-source software.

<details>
<summary><strong>Windows - "Windows protected your PC"</strong></summary>

1. Click **"More info"**
2. Click **"Run anyway"**

This warning appears because the app isn't signed with an expensive code signing certificate. The app is open-source and safe to run.
</details>

<details>
<summary><strong>macOS - "App can't be opened because it is from an unidentified developer"</strong></summary>

**Option 1: Right-click method**
1. Right-click (or Control-click) the app
2. Select **"Open"** from the menu
3. Click **"Open"** in the dialog

**Option 2: System Preferences**
1. Go to **System Preferences > Security & Privacy > General**
2. Click **"Open Anyway"** next to the blocked app message

**Option 3: Terminal**
```bash
xattr -cr ./ProjectLauncher-macOS-*
```
</details>

<details>
<summary><strong>Linux</strong></summary>

Linux generally doesn't show security warnings. Just make sure the file is executable:
```bash
chmod +x ./project-launcher-Linux-*
./project-launcher-Linux-*
```
</details>

## Usage

### Adding a Project

1. Click **"+ Add Project"**
2. Fill in the project details:
   - **Name** - Display name for the project
   - **Path** - Root directory of your project
   - **IDE** - Which editor to open
   - **AI Tools** - Optional AI coding assistants
   - **Terminal Commands** - Commands to run (e.g., `npm run dev`)
   - **Browser URLs** - URLs to open (e.g., `http://localhost:3000`)

### Launching a Project

Click the **"run"** button on any project card. This will:
1. Open the project in your selected IDE
2. Start the AI coding tool(s) (if configured)
3. Run the terminal command(s) (if configured)
4. Open browser tabs (if configured)

### Settings

Access settings from the title bar. From here you can:
- Enable/disable "Start with Windows"
- Create/remove Desktop shortcut
- Create/remove Start Menu shortcut
- Uninstall (removes all shortcuts)

### Configuration

Projects are stored in a YAML config file:
- **Windows:** `%LOCALAPPDATA%\ProjectLauncher\config.yaml`
- **macOS/Linux:** `~/.config/ProjectLauncher/config.yaml`

Example configuration:

```yaml
projects:
  - name: My Web App
    path: /path/to/project
    actions:
      - type: ide
        ide: cursor
      - type: ai_tool
        tool: opencode
      - type: terminal
        commands:
          - npm run dev
      - type: browser
        browsers:
          - chrome
        tabs:
          - http://localhost:3000
          - http://localhost:3000/admin
```

## Supported Tools

### IDEs
- VS Code (`vscode`)
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
# Build the standalone executable
python build.py

# Build with clean (removes previous builds first)
python build.py --clean
```

The built executable will be in the `dist/` folder.

## Uninstalling

### From the App
1. Open Settings (click "settings" in the title bar)
2. Click "Uninstall..." at the bottom
3. This removes all shortcuts

To fully remove the app, delete the installation folder:
- **Windows:** `%LOCALAPPDATA%\ProjectLauncher`
- **macOS:** `~/Applications/ProjectLauncher`
- **Linux:** `~/.local/share/ProjectLauncher`

### Manual Cleanup

Config files are stored separately and won't be removed by uninstall:
- **Windows:** `%LOCALAPPDATA%\ProjectLauncher\config.yaml`
- **macOS/Linux:** `~/.config/ProjectLauncher/config.yaml`

Delete these manually if you want to remove all traces.

## License

[MIT](LICENSE)
