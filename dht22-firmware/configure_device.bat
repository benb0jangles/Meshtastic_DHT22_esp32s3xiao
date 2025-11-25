@echo off
REM Meshtastic DHT22 Device Configuration Script for Windows
REM ========================================================

echo ============================================
echo  Meshtastic DHT22 Firmware Configuration
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if meshtastic is installed
meshtastic --version >nul 2>&1
if errorlevel 1 (
    echo Installing meshtastic Python package...
    pip install meshtastic
    if errorlevel 1 (
        echo ERROR: Failed to install meshtastic package
        pause
        exit /b 1
    )
)

REM Check for pyserial (needed for port detection)
pip show pyserial >nul 2>&1
if errorlevel 1 (
    echo Installing pyserial for port detection...
    pip install pyserial
)

echo.
echo Starting Configuration GUI...
echo.

REM Run the GUI
python "%~dp0meshtastic_config_gui.py"

pause
