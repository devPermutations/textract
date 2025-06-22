from pathlib import Path
import shutil
import time

import pytest

from extracttext.dataloader import DataLoader
from extracttext.extractors.base_extractor import DocumentType

# Locate sample in project-root /samples
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PDF = PROJECT_ROOT / "samples" / "20170905151939_Arch_Properties_Lease.pdf"

OCR_OK = all(shutil.which(cmd) for cmd in ("tesseract", "pdftoppm"))


@pytest.mark.skipif(not OCR_OK, reason="OCR binaries (tesseract, pdftoppm) not installed")
def test_e2e_ocr_performance():
    """Measure OCR runtime on a ~5 MB scanned PDF sample."""

    if not SAMPLE_PDF.exists():
        pytest.skip("Performance sample PDF not found")

    print(f"[E2E] receiving file '{SAMPLE_PDF.name}' ({SAMPLE_PDF.stat().st_size/1024/1024:.1f} MB)…")

    loader = DataLoader(prefer_ocr=True)

    # Timing starts
    t0 = time.perf_counter()
    path_norm, _, cleanup = loader._normalise_source(SAMPLE_PDF)

    # Detect extractor
    for ext in loader._iter_extractors():
        if ext.can_process(path_norm):
            chosen = ext
            break
    else:
        cleanup()
        pytest.fail("No extractor recognised performance sample")

    detect_end = time.perf_counter()
    print(f"[E2E] file type detected as {chosen.DOCUMENT_TYPE.value!r} in {detect_end - t0:.3f}s")

    # Extraction (OCR heavy)
    print("[E2E] extracting text via chosen extractor… (this may take a while)")
    text_start = time.perf_counter()
    text_payload = chosen.extract_text(path_norm)
    text_end = time.perf_counter()

    cleanup()

    print(f"[E2E] text extracted: {len(text_payload)} chars in {text_end - text_start:.3f}s")
    print(f"[E2E] total duration: {text_end - t0:.3f}s")

    # Sanity assertion – expect at least 1000 chars from 8-page lease PDF
    assert len(text_payload.strip()) > 1000, "OCR payload shorter than expected" 