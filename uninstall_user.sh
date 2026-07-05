#!/bin/bash
# Persian OCR - User Uninstaller
INSTALL_DIR="$HOME/.local/share/persian-ocr"
BIN_LINK="$HOME/.local/bin/screenocr"
DESKTOP_FILE="$HOME/.local/share/applications/persian-ocr.desktop"
ICON="$HOME/.local/share/icons/hicolor/256x256/apps/persian-ocr.png"

echo "Uninstalling Persian OCR..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_LINK"
rm -f "$DESKTOP_FILE"
rm -f "$ICON"
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
echo "Done. Persian OCR removed."
