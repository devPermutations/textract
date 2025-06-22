from pathlib import Path
import time

from extracttext.dataloader import load
from extracttext.extractors.base_extractor import DocumentType

# We need access to DataLoader internals for timing granularity
from extracttext.dataloader import DataLoader

SAMPLES_DIR = Path(__file__).parent / "testsamples"


def test_dataloader_e2e_pdf_with_text():
    """End-to-end: DataLoader should detect and extract text-layer PDF."""

    path = SAMPLES_DIR / "pdf_text.pdf"

    print(f"[E2E] receiving file '{path.name}'…")

    # ------------------------------------------------------------------
    # Normalise source
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    loader = DataLoader()
    path_norm, _, cleanup = loader._normalise_source(path)
    t_norm = time.perf_counter()

    # ------------------------------------------------------------------
    # Detection
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
    # Extraction
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

    # Assertions
    assert chosen.DOCUMENT_TYPE == DocumentType.PDF_TEXT
    assert len(text_payload.strip()) > 100, "Extracted text is unexpectedly short" 