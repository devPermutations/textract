"""OCR-based extractor for scanned / image-only PDF files.

Will convert each page to images via `pdf2image.convert_from_path` then feed
those images to `pytesseract.image_to_string`.
"""

from __future__ import annotations

from pathlib import Path
import typing as _t

import pdf2image  # type: ignore  # noqa: F401
import pytesseract  # type: ignore  # noqa: F401

from .base_extractor import BaseExtractor, DocumentType

__all__ = ["PdfOcrExtractor"]


def _ocr_page(img_bytes_lang: tuple[bytes, str]) -> str:
    """Run Tesseract on a single page image passed as raw bytes."""

    from io import BytesIO

    import pytesseract  # local import inside process
    from PIL import Image

    img_bytes, lang = img_bytes_lang
    img = Image.open(BytesIO(img_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return pytesseract.image_to_string(img, lang=lang).strip()


class PdfOcrExtractor(BaseExtractor):
    """Fallback extractor for PDFs that *lack* a text layer."""

    DOCUMENT_TYPE = DocumentType.PDF_IMAGE

    def can_process(self, source: _t.Union[str, Path]) -> bool:
        path = self._to_path(source)
        if path.suffix.lower() != ".pdf":
            return False

        try:
            from extracttext.detector import peek_pdf_has_text

            return not peek_pdf_has_text(path)
        except Exception:
            return True

    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        """Run OCR on every page of *source* and concatenate with form-feeds.

        Pipeline:
        1. Convert PDF pages to PIL Images via `pdf2image` (uses poppler).
        2. Feed each page to `pytesseract.image_to_string`.
        3. Join page texts with the ``\f`` form-feed character so downstream
           callers can split if needed.

        Environment overrides:
            • ``OCR_LANG`` – language passed to Tesseract (default ``eng``).
            • ``OCR_DPI``  – conversion resolution for `pdf2image` (default 300).
        """

        import os
        from concurrent.futures import ProcessPoolExecutor
        from io import BytesIO

        lang = os.getenv("OCR_LANG", "eng")
        dpi = int(os.getenv("OCR_DPI", "300"))

        try:
            if isinstance(source, (bytes, bytearray)):
                pages = pdf2image.convert_from_bytes(source, dpi=dpi)
            else:
                path = self._to_path(source)
                pages = pdf2image.convert_from_path(str(path), dpi=dpi)

            if not pages:
                return ""

            # Convert each page PIL.Image to raw bytes to make them picklable
            page_payloads: list[tuple[bytes, str]] = []
            for p in pages:
                if p.mode != "RGB":
                    p = p.convert("RGB")
                buf = BytesIO()
                p.save(buf, format="PNG")
                page_payloads.append((buf.getvalue(), lang))

            with ProcessPoolExecutor() as pool:
                texts = list(pool.map(_ocr_page, page_payloads, chunksize=1))

            return "\f".join(t.strip() for t in texts)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("PDF OCR failed") from exc 