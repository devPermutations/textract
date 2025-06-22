"""Extractor for CSV files (comma-separated values)."""

from __future__ import annotations

from pathlib import Path
import typing as _t

from .base_extractor import BaseExtractor, DocumentType

__all__ = ["CsvExtractor"]


class CsvExtractor(BaseExtractor):
    DOCUMENT_TYPE = DocumentType.CSV

    def can_process(self, source: _t.Union[str, Path]) -> bool:
        return str(source).lower().endswith(".csv")

    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        # Similar strategy to TextExtractor: read raw bytes and decode using chardet.
        if isinstance(source, (bytes, bytearray)):
            raw: bytes = source  # type: ignore[assignment]
        else:
            path = self._to_path(source)
            with open(path, "rb") as fh:
                raw = fh.read()

        if not raw:
            return ""

        import chardet  # local import to avoid top-level requirement for csv only

        detected = chardet.detect(raw)
        encoding = (detected.get("encoding") or "utf-8").strip()

        try:
            text = raw.decode(encoding)
        except Exception:
            text = raw.decode("utf-8", errors="replace")

        # Ensure we preserve original line endings and delimiter characters – no modifications.
        return text 