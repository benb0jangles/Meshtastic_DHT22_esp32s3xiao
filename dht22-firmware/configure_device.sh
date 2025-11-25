#!/bin/bash
# Meshtastic DHT22 Device Configuration Script for Linux/Mac
# ==========================================================

echo "============================================"
echo " Meshtastic DHT22 Firmware Configuration"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python3 using your package manager"
    exit 1
fi

# Check if meshtastic is installed
if ! command -v meshtastic &> /dev/null; then
    echo "Installing meshtastic Python package..."
    pip3 install meshtastic
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install meshtastic package"
        exit 1
    fi
fi

# Check for pyserial (needed for port detection)
pip3 show pyserial > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing pyserial for port detection..."
    pip3 install pyserial
fi

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: tkinter not found. Install it with:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  macOS: brew install python-tk"
    exit 1
fi

echo
echo "Starting Configuration GUI..."
echo

# Run the GUI
python3 "$SCRIPT_DIR/meshtastic_config_gui.py"
