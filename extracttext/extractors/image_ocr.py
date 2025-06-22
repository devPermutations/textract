"""OCR extractor for standalone image files (JPG, PNG, TIFF, ...)."""

from __future__ import annotations

from pathlib import Path
import typing as _t

from PIL import Image  # type: ignore  # noqa: F401
import pytesseract  # type: ignore  # noqa: F401

from .base_extractor import BaseExtractor, DocumentType

__all__ = ["ImageOcrExtractor"]


_VALID_IMG_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif"}


class ImageOcrExtractor(BaseExtractor):
    DOCUMENT_TYPE = DocumentType.IMAGE

    def can_process(self, source: _t.Union[str, Path]) -> bool:
        return Path(source).suffix.lower() in _VALID_IMG_EXT

    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        """Run Tesseract OCR on a standalone image.

        The language used can be overridden via the environment variable
        ``OCR_LANG`` (defaults to ``eng``). Any failure to read or process the
        image raises ``RuntimeError`` so the orchestrator can attempt fallbacks.
        """

        import os
        from io import BytesIO

        lang = os.getenv("OCR_LANG", "eng")

        try:
            if isinstance(source, (bytes, bytearray)):
                img = Image.open(BytesIO(source))  # type: ignore[arg-type]
            else:
                path = self._to_path(source)
                img = Image.open(str(path))

            # Ensure image is in a format Tesseract likes (convert mode if needed)
            if img.mode != "RGB":
                img = img.convert("RGB")

            text = pytesseract.image_to_string(img, lang=lang)
        except Exception as exc:  # pragma: no cover – propagate for orchestrator
            raise RuntimeError("Image OCR failed") from exc

        return text or "" 