"""Extractor for PDF files that already contain an embedded text layer.

Relies on `pdfminer.six` under the hood (implementation pending).
"""

from __future__ import annotations

from pathlib import Path
import typing as _t

# Third-party library placeholder (import kept so linters know the dependency).
import pdfminer.high_level  # type: ignore  # noqa: F401

from .base_extractor import BaseExtractor, DocumentType

__all__ = ["PdfTextExtractor"]


class PdfTextExtractor(BaseExtractor):
    """Extracts text directly from PDFs that already have a selectable layer."""

    DOCUMENT_TYPE = DocumentType.PDF_TEXT

    def can_process(self, source: _t.Union[str, Path]) -> bool:
        """Accept **only** PDFs that appear to contain a selectable text layer."""

        path = self._to_path(source)
        if path.suffix.lower() != ".pdf":
            return False

        # Light heuristic – inspect first page only
        try:
            from extracttext.detector import peek_pdf_has_text  # local import to avoid cycles

            return peek_pdf_has_text(path)
        except Exception:
            # On any analysis failure fall back to *assuming* text layer present.
            # The heavy extraction phase will raise if this assumption is wrong.
            return True

    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        """Return raw text from *source* using `pdfminer.six`.

        The helper delegates to :func:`pdfminer.high_level.extract_text` which
        handles layout analysis internally.  For in-memory bytes we wrap them
        in a ``BytesIO`` stream so pdfminer can treat it as a file-like object.
        """

        from io import BytesIO

        try:
            if isinstance(source, (bytes, bytearray)):
                fp = BytesIO(source)  # type: ignore[arg-type]
                text = pdfminer.high_level.extract_text(fp)
            else:
                path = self._to_path(source)
                text = pdfminer.high_level.extract_text(str(path))
        except Exception as exc:  # pragma: no cover – escalate explicit failure
            raise RuntimeError("Failed to extract text layer from PDF") from exc

        return text or "" 