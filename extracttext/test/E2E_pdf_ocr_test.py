from pathlib import Path
import shutil
import time

import pytest

from extracttext.dataloader import load
from extracttext.extractors.base_extractor import DocumentType

SAMPLES_DIR = Path(__file__).parent / "testsamples"

# Skip when OCR prerequisites missing to keep suite portable
OCR_OK = all(shutil.which(cmd) for cmd in ("tesseract", "pdftoppm"))


@pytest.mark.skipif(not OCR_OK, reason="OCR binaries (tesseract, pdftoppm) not installed")
def test_dataloader_e2e_pdf_ocr():
    """End-to-end: DataLoader should OCR a scanned PDF (no text layer)."""

    path = SAMPLES_DIR / "pdf-notext.pdf"

    print(f"[E2E] receiving file '{path.name}'…")

    # ------------------------------------------------------------------
    # Normalise source (negligible time but measured for completeness)
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    loader = load.__globals__["DataLoader"]()
    path_norm, _, cleanup = loader._normalise_source(path)
    t_norm = time.perf_counter()

    # ------------------------------------------------------------------
    # Detection – iterate through extractors until one claims the file
    # ------------------------------------------------------------------
    print("[E2E] detecting file type…")
    chosen = None
    for ext in loader._iter_extractors():
        if ext.can_process(path_norm):
            chosen = ext
            break

    detect_end = time.perf_counter()

    assert chosen is not None, "No extractor recognised the file"

    print(f"[E2E] file type detected as {chosen.DOCUMENT_TYPE.value!r} in {detect_end - t_norm:.3f}s")

    # ------------------------------------------------------------------
    # Extraction (OCR heavy)
    # ------------------------------------------------------------------
    print("[E2E] extracting text via chosen extractor…")
    text_start = time.perf_counter()
    text_payload = chosen.extract_text(path_norm)
    text_end = time.perf_counter()

    total = text_end - t0

    print(f"[E2E] text extracted ({len(text_payload)} chars) in {text_end - text_start:.3f}s")

    preview = text_payload.strip().replace("\n", " ")[:120]
    print(f"[E2E] preview: {preview!r}")

    print(f"[E2E] total duration: {total:.3f}s")

    cleanup()

    # Build synthetic result for assertions consistency
    class _Res:
        document_type = chosen.DOCUMENT_TYPE

    result = _Res()

    # Expectations
    assert result.document_type == DocumentType.PDF_IMAGE
    assert len(text_payload.strip()) > 50, "OCR extraction seems too short" 