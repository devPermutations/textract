"""Lightweight file-type detection utilities.

This subpackage offers small, self-contained helpers that *individual* extractors
can use to make cheap decisions without incurring heavy I/O.

Public API (v1):
    • detect_mime_type(path) -> str  – Prefer python-magic; fallback to mimetypes.
    • peek_pdf_has_text(path) -> bool – Inspect first page with pdfminer.six.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union
import mimetypes

# ----------------------------------------------------------------------------
# Optional dependency – python-magic
# ----------------------------------------------------------------------------
try:
    import magic  # type: ignore

    _HAS_MAGIC = True
    _MAGIC_MIME = magic.Magic(mime=True)
except Exception:  # pragma: no cover – treat *any* failure as unavailable
    _HAS_MAGIC = False
    _MAGIC_MIME = None  # type: ignore

__all__ = [
    "detect_mime_type",
    "peek_pdf_has_text",
]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def detect_mime_type(source: Union[str, Path]) -> str:  # noqa: D401
    """Return best-effort MIME type for *source*.

    Order of preference:
    1. `python-magic` (libmagic) – if installed & functional.
    2. `mimetypes.guess_type` based on file extension.
    3. Fallback to ``application/octet-stream``.
    """
    path = Path(source)

    if _HAS_MAGIC:
        try:
            return _MAGIC_MIME.from_file(str(path))  # type: ignore[union-attr]
        except Exception:
            # Gracefully degrade to extension-based detection
            pass

    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


# pdfminer is an existing dependency (see requirements.txt)
import pdfminer.high_level  # type: ignore


def peek_pdf_has_text(source: Union[str, Path]) -> bool:  # noqa: D401
    """Return ``True`` if the *first page* of *source* has an embedded text layer.

    Falls back to ``False`` for non-PDF files or when detection fails.
    The check is intentionally *shallow* to remain fast – it never parses more
    than one page.
    """
    path = Path(source)

    # Quick escape hatch – non-PDF extensions almost certainly lack PDF data
    if path.suffix.lower() != ".pdf":
        return False

    try:
        text = pdfminer.high_level.extract_text(str(path), maxpages=1)
        return bool(text and text.strip())
    except Exception:
        # Malformed or encrypted PDFs are treated as *no text layer*
        return False 