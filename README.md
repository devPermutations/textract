# ExtractText

ExtractText is a lightweight Python library that automatically detects a document type (PDF, image, DOCX, CSV, TXT …), routes the file to the optimal extractor, and returns the raw text ‑ all via a single call:

```python
from extracttext import load

result = load("/path/to/document.pdf")
print(result.text_payload)
```

## Features

* 🧠 Automatic extractor selection (heuristics + fallbacks)
* 📄 Support for text-PDF, scanned PDF (OCR), images, DOCX, TXT, CSV
* 🔍 OCR powered by **Tesseract** and **pdf2image**
* ⚡ Concurrency: OCR runs in a background **ProcessPoolExecutor** when `prefer_ocr=True`
* 🔑 Simple, JSON-serialisable envelope (`ExtractionResult`)
* ❌ Clear error hierarchy (`UnsupportedDocumentError`, `ExtractionFailedError`)
* 🧪 100 % type-annotated & unit-tested

## Installation

```bash
pip install extracttext          # when published to PyPI

# or, for a local dev clone – run the helper to install *all* deps
chmod +x extracttext/build.sh
./extracttext/build.sh           # installs system + Python requirements
```

The build script detects **Homebrew** (macOS) or **apt** (Debian/Ubuntu) to pull in Tesseract & Poppler automatically. If you use another OS/package manager, install those tools manually, then rerun the script.

## Quick-start

### Basic usage
```python
from extracttext import load

res = load("invoice.pdf")
print(res.document_type)  # DocumentType.PDF_TEXT or .PDF_IMAGE
print(res.text_payload[:200])
```

### Forced OCR (images & scanned PDFs first)
```python
res = load("invoice.pdf", prefer_ocr=True)
```

# CLI usage

ExtractText ships with a tiny command-line wrapper.  After installation you can run:

```bash
# via python -m (always works)
python -m extracttext.cli path/to/document.pdf

# or, if your user-site bin directory is on PATH (see below):
extracttext path/to/document.pdf
```

By default the CLI prints a JSON envelope – exactly what `ExtractionResult.json()` returns:

```jsonc
{
  "document_id": "8cd0fc1e-…",
  "document_name": "document.pdf",
  "document_type": "PDF_TEXT",
  "text_payload": "Lorem ipsum …"
}
```

Flags:

* `--prefer-ocr` – try OCR extractors first (handy when a PDF's embedded text layer is junk).
* (`--json` is kept for backwards-compatibility but is now redundant.)

If the short `extracttext` command is not found, add Python's user-site scripts directory to your shell `PATH`:

```bash
export PATH="$(python3 -m site --user-base)/bin:$PATH"
```

### Running the automated test-suite

After setup, execute:

```bash
chmod +x extracttext/test/runtests.sh
./extracttext/test/runtests.sh   # runs unit + integration first, E2E last
```

### Running OCR in your own process pool
```python
from concurrent.futures import ProcessPoolExecutor
from extracttext import load

with ProcessPoolExecutor(max_workers=4) as pool:
    res = load("scan.jpg", prefer_ocr=True, executor=pool)
```

## FastAPI example
See [`docs/EXAMPLES.md`](docs/EXAMPLES.md#fastapi-upload-example) for a fully-working snippet that turns ExtractText into a micro-service.

## Contributing
Pull requests are welcome! Please run `ruff`, `mypy` and `pytest -q` before submitting.

## License
MIT

## Docker container

ExtractText ships with a ready-to-use `Dockerfile` that packages the library together with its OCR dependencies (Tesseract + Poppler) and exposes a lightweight FastAPI service on **port 6060**.

### Build the image
```bash
# from repository root
docker build -t extracttext-api .
```

### Run the API server
```bash
docker run -d --name extracttext -p 6060:6060 extracttext-api
# → http://localhost:6060/gettext is now live
```

### Quick end-to-end test (sample scanned PDF)
With the container running on the **same machine** as the source code, execute:
```bash
curl -X POST \
     -F "file=@extracttext/test/testsamples/pdf-notext.pdf" \
     http://localhost:6060/gettext | jq
```
The response will resemble:
```jsonc
{
  "document_id": "... uuid ...",
  "document_name": "pdf-notext.pdf",
  "document_type": "PDF_IMAGE",
  "text_payload": "Lorem ipsum …",
  "elapsed_ms": 275.42,
  "char_count": 1987
}
```
If the server runs on a **remote VPS**, just swap `localhost` for the public IP or DNS (`http://<vps-ip>:6060/gettext`).

> **Tip:** view runtime logs in another terminal with `docker logs -f extracttext`.

--- 