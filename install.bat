@echo off
setlocal enabledelayedexpansion

rem Natural Language CLI Tool Installation Script for Windows
rem Supports Windows Command Prompt and PowerShell

set TOOL_NAME=nlcli
set PACKAGE_NAME=nlcli
set PYTHON_MIN_VERSION=3.8

echo ===============================================
echo Natural Language CLI Tool Installer (Windows)
echo ===============================================
echo.

rem Check if Python is installed
echo [INFO] Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python %PYTHON_MIN_VERSION% or later from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

rem Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% is installed

rem Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed
    echo [INFO] Please install pip: https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)

echo [SUCCESS] pip is available

rem Install package
echo.
echo [INFO] Installing %PACKAGE_NAME%...

pip install --user %PACKAGE_NAME%
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install from PyPI, trying local installation...
    
    if exist setup.py (
        pip install --user .
        if %errorlevel% neq 0 (
            echo [ERROR] Local installation failed
            pause
            exit /b 1
        )
        echo [SUCCESS] %PACKAGE_NAME% installed successfully from local source
    ) else (
        echo [ERROR] Installation failed and no local setup.py found
        echo [INFO] Please ensure you're in the project directory or that %PACKAGE_NAME% is available on PyPI
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] %PACKAGE_NAME% installed successfully from PyPI
)

rem Check if Scripts directory is in PATH
echo.
echo [INFO] Checking PATH configuration...

set SCRIPTS_DIR=%USERPROFILE%\AppData\Roaming\Python\Python%PYTHON_VERSION:~0,2%\Scripts
if "%PYTHON_VERSION:~2,1%"=="." set SCRIPTS_DIR=%USERPROFILE%\AppData\Roaming\Python\Python%PYTHON_VERSION:~0,1%%PYTHON_VERSION:~2,1%\Scripts

echo %PATH% | find /i "%SCRIPTS_DIR%" >nul
if %errorlevel% neq 0 (
    echo [WARNING] Python Scripts directory is not in PATH
    echo [INFO] Adding %SCRIPTS_DIR% to PATH...
    
    rem Add to system PATH (requires admin privileges)
    setx PATH "%PATH%;%SCRIPTS_DIR%" 2>nul
    if %errorlevel% neq 0 (
        echo [WARNING] Could not automatically update system PATH
        echo [INFO] Please manually add the following to your PATH:
        echo [INFO] %SCRIPTS_DIR%
    ) else (
        echo [SUCCESS] Added Scripts directory to PATH
    )
) else (
    echo [SUCCESS] Python Scripts directory is already in PATH
)

rem Test installation
echo.
echo [INFO] Testing installation...

where %TOOL_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] %TOOL_NAME% is not immediately available in PATH
    echo [INFO] You may need to restart Command Prompt and try: %TOOL_NAME% --help
) else (
    echo [SUCCESS] %TOOL_NAME% is installed and accessible
    
    rem Show version
    %TOOL_NAME% --version 2>nul
    if %errorlevel% neq 0 (
        echo [INFO] Version: unknown
    )
)

rem Setup OpenAI API key
echo.
echo [INFO] Setting up OpenAI API key...

if defined OPENAI_API_KEY (
    echo [SUCCESS] OpenAI API key is already set in environment
) else (
    echo [WARNING] OpenAI API key is not set
    echo [INFO] You can:
    echo [INFO] 1. Set it as environment variable: set OPENAI_API_KEY=your-key-here
    echo [INFO] 2. Add it to system environment variables for persistence
    echo [INFO] 3. %TOOL_NAME% will prompt for it when first used
    echo.
    
    set /p SET_KEY="Would you like to set the API key now? (y/N): "
    if /i "!SET_KEY!"=="y" (
        set /p API_KEY="Enter your OpenAI API key: "
        if not "!API_KEY!"=="" (
            setx OPENAI_API_KEY "!API_KEY!" >nul 2>&1
            if !errorlevel! neq 0 (
                echo [WARNING] Could not set system environment variable
                echo [INFO] Please manually set OPENAI_API_KEY in system environment variables
            ) else (
                echo [SUCCESS] API key set in system environment variables
                echo [WARNING] Please restart Command Prompt to use the API key
            )
        ) else (
            echo [WARNING] No API key entered, skipping setup
        )
    ) else (
        echo [INFO] Skipping API key setup
    )
)

rem Show completion message
echo.
echo ===============================================
echo Installation Complete!
echo ===============================================
echo.
echo [SUCCESS] %TOOL_NAME% has been installed successfully
echo.
echo Getting started:
echo   %TOOL_NAME% --help              # Show help
echo   %TOOL_NAME%                     # Start interactive mode
echo   %TOOL_NAME% "list all files"    # Translate single command
echo.
echo Configuration:
echo   %TOOL_NAME% config              # Show current configuration
echo   %%USERPROFILE%%\.nlcli\config.ini    # Configuration file
echo   %%USERPROFILE%%\.nlcli\logs\nlcli.log # Log file
echo.
echo For more information, visit: https://github.com/nlcli/nlcli
echo.

rem Check if we need to restart
where %TOOL_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] You may need to restart Command Prompt for the tool to be available
    echo [INFO] After restarting, test with: %TOOL_NAME% --help
)

echo.
pause
