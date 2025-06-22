#!/usr/bin/env bash
# Bootstrap script: install system + Python dependencies for ExtractText.
# Usage: ./build.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

printf "\n============================================\n"
printf "  ExtractText – Build / Setup Script\n"
printf "============================================\n\n"

# ------------------------------------------------------------
# 1. Install system-level deps (Tesseract & Poppler)
# ------------------------------------------------------------
install_system_deps() {
  if command -v brew >/dev/null 2>&1; then
    echo "[build] Detected Homebrew – installing tesseract & poppler…"
    brew install tesseract poppler || true
  elif command -v apt-get >/dev/null 2>&1; then
    echo "[build] Detected apt-get – installing tesseract & poppler-utils…"
    sudo apt-get update -qq
    sudo apt-get install -y tesseract-ocr poppler-utils
  else
    echo "[build] ⚠️  Could not detect a supported package manager (brew or apt-get)."
    echo "       Please install Tesseract and Poppler manually if OCR is required."
  fi
}

# ------------------------------------------------------------
# 2. Install Python deps (requirements.txt)
# ------------------------------------------------------------
install_python_deps() {
  PY_EXEC=${PYTHON:-python3}
  if ! command -v "$PY_EXEC" >/dev/null 2>&1; then
    echo "[build] ERROR: $PY_EXEC not found on PATH" >&2
    exit 1
  fi

  echo "[build] Installing Python dependencies via pip…"
  "$PY_EXEC" -m pip install --upgrade pip
  "$PY_EXEC" -m pip install -r "$PROJECT_ROOT/requirements.txt"
}

install_system_deps
install_python_deps

echo "\n[build] All done ✔️" 