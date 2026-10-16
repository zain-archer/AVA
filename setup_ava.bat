@echo off
REM =========================================
REM AVA - Advanced Virtual Assistant
REM Windows Setup Script
REM =========================================

echo.
echo ==========================================
echo   AVA - Advanced Virtual Assistant
echo   Setup Script for Windows 11
echo ==========================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Create virtual environment (optional but recommended)
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [WARNING] Could not create virtual environment. Continuing with system Python.
) else (
    echo [OK] Virtual environment created.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    echo Try running: pip install --upgrade pip
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

REM Create models directory
echo.
echo Creating models directory...
if not exist "ava\models" mkdir "ava\models"
echo [OK] Models directory ready.

REM Check for Vosk model
echo.
echo ==========================================
echo   VOICE RECOGNITION MODEL
echo ==========================================
echo.

if exist "ava\models\vosk-model-small-en-us-0.15" (
    echo [OK] English speech model found.
) else (
    echo [!] No speech model found.
    echo.
    echo To enable voice recognition, download a Vosk model:
    echo.
    echo   English (small, ~50 MB):
    echo   https://alphacephei.com/vosk/models
    echo   Download: vosk-model-small-en-us-0.15
    echo   Extract to: ava\models\
    echo.
    echo   Urdu (~50 MB):
    echo   Download: vosk-model-small-ur-0.1
    echo   Extract to: ava\models\
    echo.
    echo You can still use AVA with text input without a model.
)

echo.
echo ==========================================
echo   SETUP COMPLETE
echo ==========================================
echo.
echo To start AVA, run:
echo   python -m ava.main
echo.
echo Or activate the virtual environment first:
echo   venv\Scripts\activate
echo   python -m ava.main
echo.
pause
