#!/bin/bash
# Persian OCR - User Installer (no sudo needed)
set -e

INSTALL_DIR="$HOME/.local/share/persian-ocr"
BIN_DIR="$HOME/.local/bin"
BIN_LINK="$BIN_DIR/screenocr"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Persian OCR Installer ==="
echo ""

echo "[1/5] Creating install directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "[2/5] Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

echo "[3/5] Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q 2>&1 | tail -1
"$INSTALL_DIR/venv/bin/pip" install -r "$SOURCE_DIR/requirements.txt" -q 2>&1 | tail -1

echo "[4/5] Copying application files..."
cp "$SOURCE_DIR/app.py" "$INSTALL_DIR/"
cp "$SOURCE_DIR/settings.py" "$INSTALL_DIR/"
cp "$SOURCE_DIR/tessdata_manager.py" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/core" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/ui" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/utils" "$INSTALL_DIR/"
cp "$SOURCE_DIR/settings.json" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/assets" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SOURCE_DIR/Tesseract" "$INSTALL_DIR/" 2>/dev/null || true

echo "[5/5] Creating launcher..."
cat > "$BIN_LINK" << LAUNCHER
#!/bin/bash
exec "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/app.py" "\$@"
LAUNCHER
chmod +x "$BIN_LINK"

echo ""
echo "=== Installation complete ==="
echo "Run: screenocr"
echo ""
