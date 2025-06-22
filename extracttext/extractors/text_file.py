"""Extractor for plain text files (.txt, .log, etc.)."""

from __future__ import annotations

from pathlib import Path
import typing as _t
import chardet  # type: ignore  # noqa: F401

from .base_extractor import BaseExtractor, DocumentType

__all__ = ["TextExtractor"]


class TextExtractor(BaseExtractor):
    DOCUMENT_TYPE = DocumentType.TEXT

    _VALID_EXT = {".txt", ".log", ".md"}

    def can_process(self, source: _t.Union[str, Path]) -> bool:
        return Path(source).suffix.lower() in self._VALID_EXT

    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        # Accept bytes or on-disk file; decode using chardet when encoding unknown.

        # If *source* is bytes directly, work with it; else read file content to bytes
        if isinstance(source, (bytes, bytearray)):
            raw: bytes = source  # type: ignore[assignment]
        else:
            path = self._to_path(source)
            with open(path, "rb") as fh:
                raw = fh.read()

        if not raw:
            return ""  # empty file yields empty string

        # Attempt to detect encoding via chardet; fall back to UTF-8 with replacement
        detected = chardet.detect(raw)
        encoding = (detected.get("encoding") or "utf-8").strip()

        try:
            return raw.decode(encoding)
        except Exception:
            # As last resort decode as UTF-8 with replacement chars
            return raw.decode("utf-8", errors="replace") 