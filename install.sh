#!/bin/bash
# Soak My Bed - Installation Script
# This script installs Python dependencies into the Klipper virtual environment
# and symlinks the plugin to the Klipper extras directory.

set -e

echo "====================================================="
echo "       Installing Soak My Bed for Klipper            "
echo "====================================================="

# --- CONFIGURATION ---
KLIPPER_DIR="${HOME}/klipper"
KLIPPY_ENV="${HOME}/klippy-env"
# Path to the plugin within this repository
PLUGIN_SRC="${HOME}/soak-my-bed/soak_my_bed.py"
# Destination path in Klipper's extras folder
PLUGIN_DEST="${KLIPPER_DIR}/klippy/extras/soak_my_bed.py"

# 1. Environment Validation
if [ ! -d "$KLIPPER_DIR" ]; then
    echo "[ERROR] Klipper directory not found at $KLIPPER_DIR"
    exit 1
fi

if [ ! -d "$KLIPPY_ENV" ]; then
    echo "[ERROR] Klipper virtual environment not found at $KLIPPY_ENV"
    exit 1
fi

# 2. Dependency Installation
# Installs required libraries for data processing and plotting
echo "[1/3] Installing/Updating Python dependencies in klippy-env..."
${KLIPPY_ENV}/bin/pip install -U matplotlib scipy numpy pillow

# 3. Plugin Integration
# Creates a symbolic link so Klipper recognizes the new module
echo "[2/3] Linking plugin to Klipper extras..."
ln -sf "$PLUGIN_SRC" "$PLUGIN_DEST"

# 4. Service Reload
# Restarts Klipper to load the new Python module
echo "[3/3] Restarting Klipper service..."
sudo systemctl restart klipper

echo "====================================================="
echo "             Installation Complete!                  "
echo " Add [soak_my_bed] to your printer.cfg to activate.  "
echo "====================================================="
