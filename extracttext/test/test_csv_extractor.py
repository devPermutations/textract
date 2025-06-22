from pathlib import Path

from extracttext.extractors.csv_file import CsvExtractor

SAMPLES_DIR = Path(__file__).parent / "testsamples"


def test_csv_extractor():
    path = SAMPLES_DIR / "csv.csv"
    ext = CsvExtractor()

    assert ext.can_process(path)

    text = ext.extract_text(path)

    print(f"[csv] extracted:\n{text}")

    # ensure header line present
    assert text.startswith("id,first_name"), "CSV header missing in extraction" 