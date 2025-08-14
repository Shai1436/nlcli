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
python -m pip install .

if errorlevel 1 (
    echo.
    echo Installation failed. Trying alternative method...
    echo Installing in development mode...
    python -m pip install -e .
)

echo.
echo Installation complete!
echo You can now use 'nlcli' command from anywhere
echo.
pause