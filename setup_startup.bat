@echo off
:: ============================================================================
:: Project Launcher - Enable Startup
:: ============================================================================
:: This script enables auto-startup using the Windows Registry.
:: No administrator privileges required.
:: ============================================================================

echo ============================================================
echo   Project Launcher - Enable Startup
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

echo Enabling startup...
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
echo Project Launcher will now start automatically when you
echo log in to Windows.
echo.
echo To disable auto-start, run disable_startup.bat or toggle
echo the setting in the app's File ^> Settings menu.
echo.
pause
