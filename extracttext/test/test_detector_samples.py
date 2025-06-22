from pathlib import Path

import pytest

from extracttext.detector import detect_mime_type, peek_pdf_has_text
from extracttext.extractors.base_extractor import DocumentType

SAMPLES_DIR = Path(__file__).parent / "testsamples"

# ---------------------------------------------------------------------------
# Sample set mapping -> expected DocumentType (from base_extractor)
# ---------------------------------------------------------------------------

_SAMPLE_EXPECTATIONS = [
    ("image.png", DocumentType.IMAGE),
    ("text.txt", DocumentType.TEXT),
    ("docx.docx", DocumentType.DOCX),
    ("csv.csv", DocumentType.CSV),
    ("pdf_text.pdf", DocumentType.PDF_TEXT),
    ("pdf-notext.pdf", DocumentType.PDF_IMAGE),
]


@pytest.mark.parametrize("filename,doc_type", _SAMPLE_EXPECTATIONS)
def test_detect_mime_type(filename: str, doc_type: DocumentType):
    """Validate MIME detection matches expected high-level DocumentType."""

    path = SAMPLES_DIR / filename
    mime = detect_mime_type(path)

    # Display info with enum value for visibility
    print(f"[detect] {filename}: expected={doc_type.value}, mime={mime!r}")

    top_level = mime.split("/")[0]

    if doc_type == DocumentType.IMAGE:
        assert top_level == "image"
    elif doc_type in {DocumentType.TEXT, DocumentType.CSV}:
        assert top_level == "text"
    else:
        # DOCX and both PDF variants fall under application/*
        assert top_level == "application"


# ---------------------------------------------------------------------------
# PDF-specific: differentiate text vs. scanned PDFs using peek helper
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "filename,doc_type",
    [
        ("pdf_text.pdf", DocumentType.PDF_TEXT),
        ("pdf-notext.pdf", DocumentType.PDF_IMAGE),
    ],
)
def test_peek_pdf_has_text(filename: str, doc_type: DocumentType):
    path = SAMPLES_DIR / filename
    result = peek_pdf_has_text(path)

    # Display info with enum value for visibility
    print(f"[pdf peek] {filename}: expected={doc_type.value}, has_text_layer={result}")

    if doc_type == DocumentType.PDF_TEXT:
        assert result is True
    else:
        assert result is False 