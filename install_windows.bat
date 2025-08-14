@echo off
echo Installing Natural Language CLI for Windows...
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel build

echo.
echo Installing nlcli...
python -m pip install --user nlcli

if errorlevel 1 (
    echo.
    echo User installation failed. Trying system-wide installation...
    python -m pip install nlcli
)

echo.
echo Finding Python Scripts directory...
for /f "delims=" %%i in ('python -c "import site; print(site.USER_BASE + '\\Scripts')"') do set SCRIPTS_DIR=%%i
echo Scripts directory: %SCRIPTS_DIR%

echo.
echo Checking if nlcli command is accessible...
nlcli --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: nlcli command not found in PATH
    echo.
    echo To fix this, you have two options:
    echo.
    echo Option 1 - Add Scripts to PATH ^(Permanent fix^):
    echo   1. Press Win+X, select System
    echo   2. Click Advanced system settings
    echo   3. Click Environment Variables
    echo   4. Under User variables, find Path and click Edit
    echo   5. Click New and add: %SCRIPTS_DIR%
    echo   6. Click OK on all dialogs
    echo   7. Restart Command Prompt
    echo.
    echo Option 2 - Use Python module ^(Works immediately^):
    echo   Interactive mode: python -m nlcli.main
    echo   Single commands: python -m nlcli.main translate "your command"
    echo.
    echo Testing Python module access...
    python -m nlcli.main --version
    if errorlevel 1 (
        echo Error: Module access also failed
    ) else (
        echo SUCCESS: You can use 'python -m nlcli.main' to run the tool
    )
) else (
    echo SUCCESS: nlcli command is accessible!
)

echo.
echo Installation complete!
echo.
echo Quick test commands:
echo   nlcli                               ^(if PATH is configured^)
echo   python -m nlcli.main                ^(interactive mode^)
echo   python -m nlcli.main translate "show files"  ^(single command^)
echo.
pause