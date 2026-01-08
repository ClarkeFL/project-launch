@echo off
:: ============================================================================
:: Project Launcher - Disable Auto-Startup
:: ============================================================================
:: This script disables the auto-startup, removing both Task Scheduler and
:: Registry entries.
::
:: REQUIREMENT: Must be run as Administrator to remove Task Scheduler entry
:: ============================================================================

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================
    echo   ERROR: Administrator privileges required
    echo ============================================================
    echo.
    echo This script needs to run as Administrator to remove the
    echo Task Scheduler entry.
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo   Project Launcher - Disable Auto-Startup
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

echo Disabling auto-startup...
echo.

:: Run Python to disable startup
%PYTHON% -c "import sys; sys.path.insert(0, r'%SCRIPT_DIR%'); from startup_manager import set_startup_enabled; result = set_startup_enabled(False); print('Success!' if result else 'Failed - check the output above')"

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to disable startup.
    echo Check if Python and required modules are installed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Auto-Startup Disabled
echo ============================================================
echo.
echo Project Launcher will no longer start automatically.
echo.
echo To re-enable, run setup_startup.bat as Administrator.
echo.
pause
