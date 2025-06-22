from pathlib import Path
import time

from extracttext.dataloader import DataLoader
from extracttext.extractors.base_extractor import DocumentType

SAMPLES_DIR = Path(__file__).parent / "testsamples"

def test_e2e_text():
    path = SAMPLES_DIR / "text.txt"
    print(f"[E2E] receiving file '{path.name}'…")

    t0 = time.perf_counter()
    loader = DataLoader()
    path_norm, _, cleanup = loader._normalise_source(path)
    t_norm = time.perf_counter()

    # Detection
    print("[E2E] detecting file type…")
    chosen = None
    for ext in loader._iter_extractors():
        if ext.can_process(path_norm):
            chosen = ext
            break
    detect_end = time.perf_counter()
    assert chosen is not None
    print(f"[E2E] file type detected as {chosen.DOCUMENT_TYPE.value!r} in {detect_end - t_norm:.3f}s")

    # Extraction
    print("[E2E] extracting text via chosen extractor…")
    text_start = time.perf_counter()
    text_payload = chosen.extract_text(path_norm)
    text_end = time.perf_counter()
    print(f"[E2E] text extracted ({len(text_payload)} chars) in {text_end - text_start:.3f}s")

    preview = text_payload.strip().replace("\n", " ")[:120]
    print(f"[E2E] preview: {preview!r}")
    print(f"[E2E] total duration: {text_end - t0:.3f}s")

    cleanup()

    assert chosen.DOCUMENT_TYPE == DocumentType.TEXT
    assert text_payload.strip().startswith("This is a TEXT document"), "Unexpected text content" 