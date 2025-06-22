from pathlib import Path

import pytest
import shutil

from extracttext.extractors.image_ocr import ImageOcrExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"

tesseract_ok = shutil.which("tesseract") is not None

@pytest.mark.skipif(not tesseract_ok, reason="Tesseract binary not found – install to run real OCR test")
def test_image_extractor_real_ocr():
    path = SAMPLES_DIR / "image.png"
    ext = ImageOcrExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[image OCR] extracted (first 120 chars): {text[:120].strip()!r}")

    assert text.strip(), "Expected non-empty OCR text output" 