from pathlib import Path

import pytest
import shutil

from extracttext.extractors.pdf_ocr import PdfOcrExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"


deps_ok = all(shutil.which(cmd) for cmd in ("tesseract", "pdftoppm"))


@pytest.mark.skipif(not deps_ok, reason="OCR binaries (tesseract, poppler) not installed")
def test_pdf_ocr_extractor_real():
    path = SAMPLES_DIR / "pdf-notext.pdf"
    ext = PdfOcrExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[pdf_ocr] extracted (first 120 chars): {text[:120].strip()!r}")

    assert text.strip(), "Expected non-empty OCR text from scanned PDF" 