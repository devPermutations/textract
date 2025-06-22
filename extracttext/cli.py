#!/usr/bin/env python3
"""Command-line interface for ExtractText.

Example:
    extracttext sample.pdf --prefer-ocr --json
"""

import argparse
import json
from pathlib import Path
import sys

from . import load


def main() -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="Extract text from a document")
    parser.add_argument("source", help="path to document")
    parser.add_argument("--prefer-ocr", action="store_true", help="Force OCR-first order")
    parser.add_argument("--json", action="store_true", help="Output JSON envelope instead of raw text")
    args = parser.parse_args()

    try:
        res = load(Path(args.source), prefer_ocr=args.prefer_ocr)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # JSON is now the default output format. Pass --json for explicitness;
    # raw text output is no longer supported through this CLI interface.
    print(res.json(indent=2))


if __name__ == "__main__":  # pragma: no cover
    main() 