from pathlib import Path

from extracttext.extractors.docx import DocxExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"

def test_docx_extractor():
    path = SAMPLES_DIR / "docx.docx"
    ext = DocxExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[docx] extracted (first 120 chars): {text[:120].strip()!r}")

    assert text.strip(), "Expected non-empty DOCX text" 