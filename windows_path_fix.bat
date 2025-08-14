@echo off
echo Windows PATH Fix for nlcli
echo ========================
echo.

REM Check if nlcli is already accessible
nlcli --version >nul 2>&1
if not errorlevel 1 (
    echo nlcli is already accessible! No fix needed.
    pause
    exit /b 0
)

echo nlcli command not found. Diagnosing...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not accessible
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check nlcli installation
python -c "import nlcli" >nul 2>&1
if errorlevel 1 (
    echo Error: nlcli is not installed
    echo Please install with: pip install nlcli
    pause
    exit /b 1
)

echo nlcli package found
echo.

REM Find Scripts directories
echo Finding Python Scripts directories...
for /f "delims=" %%i in ('python -c "import site; print(site.USER_BASE + '\\Scripts')"') do set USER_SCRIPTS=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"') do set SYS_SCRIPTS=%%i

echo User Scripts: %USER_SCRIPTS%
echo System Scripts: %SYS_SCRIPTS%
echo.

REM Check which Scripts directory contains nlcli.exe
set NLCLI_LOCATION=
if exist "%USER_SCRIPTS%\nlcli.exe" (
    set NLCLI_LOCATION=%USER_SCRIPTS%
    echo Found nlcli.exe in User Scripts directory
)
if exist "%SYS_SCRIPTS%\nlcli.exe" (
    set NLCLI_LOCATION=%SYS_SCRIPTS%
    echo Found nlcli.exe in System Scripts directory
)

if "%NLCLI_LOCATION%"=="" (
    echo Warning: nlcli.exe not found in Scripts directories
    echo You may need to reinstall nlcli
    echo.
    echo Try: pip uninstall nlcli && pip install --user nlcli
    pause
    exit /b 1
)

echo.
echo nlcli.exe found in: %NLCLI_LOCATION%
echo.

REM Check if directory is in PATH
echo %PATH% | findstr /i "%NLCLI_LOCATION%" >nul
if not errorlevel 1 (
    echo Directory is already in PATH, but nlcli still not working
    echo This might be a session issue - try restarting Command Prompt
    pause
    exit /b 0
)

echo Directory is NOT in PATH
echo.
echo SOLUTION OPTIONS:
echo.
echo Option 1 - Automatic PATH Update (Requires Administrator):
echo   This will add the Scripts directory to your User PATH
echo.
echo Option 2 - Manual PATH Update:
echo   1. Press Win+X, select System
echo   2. Click Advanced system settings  
echo   3. Click Environment Variables
echo   4. Under User variables, find Path and click Edit
echo   5. Click New and add: %NLCLI_LOCATION%
echo   6. Click OK on all dialogs
echo   7. Restart Command Prompt
echo.
echo Option 3 - Use Python Module (No PATH changes needed):
echo   Always use: python -m nlcli.main
echo.

set /p choice="Choose option (1, 2, or 3): "

if "%choice%"=="1" (
    echo Adding to PATH automatically...
    
    REM Add to user PATH using setx
    setx PATH "%PATH%;%NLCLI_LOCATION%" >nul 2>&1
    if errorlevel 1 (
        echo Failed to update PATH automatically
        echo Please use Option 2 (manual) instead
    ) else (
        echo PATH updated successfully!
        echo Please restart Command Prompt and try: nlcli --help
    )
) else if "%choice%"=="2" (
    echo Manual PATH update instructions:
    echo.
    echo 1. Press Win+X, select System
    echo 2. Click Advanced system settings
    echo 3. Click Environment Variables  
    echo 4. Under User variables, find Path and click Edit
    echo 5. Click New and add: %NLCLI_LOCATION%
    echo 6. Click OK on all dialogs
    echo 7. Restart Command Prompt
    echo 8. Test with: nlcli --help
) else if "%choice%"=="3" (
    echo Testing Python module access...
    python -m nlcli.main --version
    if errorlevel 1 (
        echo Error: Python module access failed
    ) else (
        echo SUCCESS: Use 'python -m nlcli.main' instead of 'nlcli'
        echo.
        echo Examples:
        echo   python -m nlcli.main                    ^(interactive mode^)
        echo   python -m nlcli.main translate "show files"
        echo   python -m nlcli.main translate "list processes"
    )
) else (
    echo Invalid choice. Please run the script again.
)

echo.
pause