#!/bin/bash
# Build script for Codex-only Multi-Agent Framework (Linux/Mac)

set -e

echo "Building Codex-only Multi-Agent Orchestration Framework"
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "Python detected"
echo

echo "[1/4] Installing dependencies..."
pip3 install -r ../requirements.txt -q
pip3 install pyinstaller -q
echo "Dependencies installed"
echo

echo "[2/4] Cleaning previous build..."
rm -rf build dist magent
echo "Cleaned"
echo

echo "[3/4] Building executable..."
pyinstaller --clean --noconfirm magent.spec
echo "Build complete"
echo

echo "[4/4] Finalizing..."
if [ -f "dist/magent" ]; then
    mv dist/magent .
    chmod +x magent
    echo "Executable created: magent"
else
    echo "Executable not found"
    exit 1
fi

echo
echo "Testing executable..."
./magent version
echo
echo "Build Complete"
echo "Executable: ./magent"
echo "Usage: ./magent ui"
echo "Then:  ./magent run --task \"...\" --scope \"...\""
