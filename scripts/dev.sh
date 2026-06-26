#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Train Tools Dev ==="

if ! command -v npm &>/dev/null; then
    echo "[ERROR] npm not found. Install Node.js first." >&2
    exit 1
fi

cd "$ROOT/frontend"
npm run dev &
VITE_PID=$!

# Wait for Vite (max 15s)
for i in $(seq 1 15); do
    if curl -sf http://localhost:5173 >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

cd "$ROOT"
ENV=dev uv run python -c "from backend.desktop import start_app; start_app()"

kill "$VITE_PID" 2>/dev/null || true
echo "=== Dev stopped ==="
