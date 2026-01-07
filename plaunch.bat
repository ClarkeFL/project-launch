@echo off
REM plaunch - Project Launcher for Windows
REM Run this to launch the Project Launcher GUI

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Launch the Project Launcher
pythonw "%SCRIPT_DIR%project_launcher.py" %*

REM If pythonw fails, try python
if %ERRORLEVEL% NEQ 0 (
    python "%SCRIPT_DIR%project_launcher.py" %*
)
