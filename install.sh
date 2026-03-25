#!/bin/bash
KLIPPER_PATH="${HOME}/klipper"
PYTHON_ENV="${HOME}/klippy-env"

echo "--- 🛋️ Installing Soak My Bed ---"

# 1. Plugin link in Klipper extras
if [ -d "$KLIPPER_PATH" ]; then
    # Create the symlink
    ln -sf "${HOME}/soak-my-bed/klippy/extras/soak_my_bed.py" "${KLIPPER_PATH}/klippy/extras/soak_my_bed.py"
    echo "✅ Plugin linked to Klipper extras."
else
    echo "❌ Klipper not found at $KLIPPER_PATH. Check your installation path."
    exit 1
fi

# 2. Dependencies installation
echo "📦 Installing Python dependencies (this might take a few minutes on Raspberry Pi)..."
if [ -d "$PYTHON_ENV" ]; then
    # Install numpy, matplotlib, scipy and pillow (required for GIF saving)
    ${PYTHON_ENV}/bin/pip install --upgrade pip
    ${PYTHON_ENV}/bin/pip install numpy matplotlib scipy pillow
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully."
    else
        echo "❌ Failed to install dependencies. Check your internet connection."
        exit 1
    fi
else
    echo "❌ Klipper virtualenv not found at $PYTHON_ENV"
    exit 1
fi

echo "--- 🛋️ Installation Complete! ---"
echo "1. Add [soak_my_bed] to your printer.cfg"
echo "2. Restart Klipper with 'sudo systemctl restart klipper'"
