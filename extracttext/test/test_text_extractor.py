from pathlib import Path

from extracttext.extractors.text_file import TextExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"

def test_text_extractor():
    path = SAMPLES_DIR / "text.txt"
    ext = TextExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[text] extracted (first 80 chars): {text[:80].strip()!r}")

    assert text.startswith("This is a TEXT document"), "Extraction did not capture expected opening line" 