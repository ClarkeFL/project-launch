@echo off
:: ============================================================================
:: Project Launcher - Enable Fast Startup (Task Scheduler)
:: ============================================================================
:: This script enables fast startup using Task Scheduler instead of the slower
:: Windows Startup folder/registry methods. Task Scheduler starts apps 5-15 
:: seconds after login, vs 2-3 minutes for Startup folder entries.
::
:: REQUIREMENT: Must be run as Administrator (right-click -> Run as administrator)
:: ============================================================================

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================
    echo   ERROR: Administrator privileges required
    echo ============================================================
    echo.
    echo This script needs to run as Administrator to create a
    echo Task Scheduler entry for fast startup.
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo   Project Launcher - Fast Startup Setup
echo ============================================================
echo.

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0

:: Check if startup_manager.py exists
if not exist "%SCRIPT_DIR%startup_manager.py" (
    echo ERROR: startup_manager.py not found in %SCRIPT_DIR%
    echo Make sure this script is in the Project Launcher directory.
    pause
    exit /b 1
)

:: Find Python
where pythonw >nul 2>&1
if %errorLevel% neq 0 (
    where python >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Python not found in PATH
        echo Please install Python and try again.
        pause
        exit /b 1
    )
    set PYTHON=python
) else (
    set PYTHON=pythonw
)

echo Enabling fast startup via Task Scheduler...
echo.

:: Run Python to enable startup
%PYTHON% -c "import sys; sys.path.insert(0, r'%SCRIPT_DIR%'); from startup_manager import set_startup_enabled; result = set_startup_enabled(True); print('Success!' if result else 'Failed - check the output above')"

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to enable startup.
    echo Check if Python and required modules are installed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo Project Launcher will now start automatically within 5-15
echo seconds after you log in to Windows (much faster than the
echo default 2-3 minute delay).
echo.
echo To disable auto-start, run the app and toggle the setting
echo in File ^> Settings, or use the system tray menu.
echo.
pause
