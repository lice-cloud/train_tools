#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Building Train Tools ==="

if ! command -v npm &>/dev/null; then
    echo "[ERROR] npm not found. Install Node.js first." >&2
    exit 1
fi

echo "[1/4] Building frontend..."
cd "$ROOT/frontend"
npm install && npm run build

echo "[2/4] Installing build dependencies..."
cd "$ROOT"
uv pip install pyinstaller

echo "[3/4] Cleaning old builds..."
rm -rf "$ROOT/dist" "$ROOT/build" "$ROOT"/*.spec

echo "[4/4] Packaging executable..."
cd "$ROOT"
uv run pyinstaller --noconfirm --onefile --windowed \
    --name "train-tools" \
    --add-data "frontend/dist:frontend/dist" \
    --hidden-import pywebview \
    --hidden-import uvicorn \
    --hidden-import fastapi \
    --hidden-import backend.main \
    main.py

echo "=== Build complete: dist/train-tools ==="
