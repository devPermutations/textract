#!/usr/bin/env bash
# Lightweight helper to execute the full test suite.
# Usage: ./runtests.sh

set -euo pipefail

echo "============================================="
echo "  ExtractText – Automated Test Runner"
echo "============================================="

# Resolve script location → repository root so the path works from *any* cwd
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run detector / extractor tests first (everything except E2E_*)
python3 -m pytest -vv -s --color=yes "$PROJECT_ROOT/extracttext/test" -k "not E2E_" || exit 1

# Finally run end-to-end tests (any file starting with E2E_)
python3 -m pytest -vv -s --color=yes "$PROJECT_ROOT/extracttext/test" -k "E2E_" 