#!/usr/bin/env bash
# Simple helper to spin up the ExtractText demo quickly.
#
# Usage:
#     cd demo
#     ./startdemo.sh
set -euo pipefail

# Resolve repository root (parent of this script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/*}"
cd "$ROOT_DIR"

# -----------------------------------------------------------------------------
# 1) Install lightweight web dependencies (FastAPI + Uvicorn)
# -----------------------------------------------------------------------------
printf "\n[ExtractText demo] Installing FastAPI & Uvicorn if missing…\n"

# Detect python interpreter (prefer python3)
PYTHON_BIN="$(command -v python3 || command -v python || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: Python interpreter not found. Please install Python 3." >&2
  exit 1
fi

"$PYTHON_BIN" -m pip install --quiet --upgrade pip
"$PYTHON_BIN" -m pip install --quiet fastapi "uvicorn[standard]" python-multipart

# -----------------------------------------------------------------------------
# 2) Launch the development server
# -----------------------------------------------------------------------------
DEMO_URL="http://127.0.0.1:8000/demo/index.html"
printf "\n[ExtractText demo] Starting dev server (press Ctrl+C to stop)\n"
printf "   Open %s in your browser.\n\n" "$DEMO_URL"

exec "$PYTHON_BIN" -m uvicorn demo.server:app --reload 