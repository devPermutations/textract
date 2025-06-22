from pathlib import Path

from extracttext.extractors.pdf_text import PdfTextExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"

def test_pdf_text_extractor():
    path = SAMPLES_DIR / "pdf_text.pdf"
    ext = PdfTextExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[pdf_text] extracted (first 120 chars): {text[:120].strip()!r}")

    assert text.strip(), "Expected non-empty text layer in PDF" 