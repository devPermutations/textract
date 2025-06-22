# ExtractText Web Demo

This directory contains a **self-contained example** that turns the ExtractText library into a tiny web service and browser UI.

The demo lets you drag-and-drop a PDF, image, DOCX, CSV, or TXT file, immediately shows some metadata, and calls the backend to return the full `ExtractionResult` JSON.

---

## Quick start (recommended)
Execute the helper script from inside this folder:

```bash
cd demo
./startdemo.sh
```

The script will:
1. install the three lightweight web dependencies (`fastapi`, `uvicorn[standard]`, **and** `python-multipart`) into your current Python environment (if they are not already present), and
2. launch the dev server.

When the server starts, open:
```
http://127.0.0.1:8000/demo/index.html
```

---

## Manual steps
Prefer to handle things yourself? Run the following from the **repository root**:

```bash
# 1) install deps once
python -m pip install fastapi "uvicorn[standard]" python-multipart

# 2) start the server (restarts automatically on code changes)
uvicorn demo.server:app --reload
```

---

## File overview
* `index.html` – front-end (drag-and-drop UI)
* `server.py` – FastAPI backend exposing `/extract` and serving static files
* `startdemo.sh` – convenience launcher described above 

---

## How the demo uses ExtractText
The backend demonstrates the simplest way to process an **in-memory** upload.  The relevant lines from [`server.py`](server.py):

```python
from extracttext import load as extract_text

# … inside the FastAPI endpoint
bytes_data = await file.read()          # hold upload purely in RAM
result = extract_text(bytes_data, filename=file.filename)
return result.dict()                    # serialisable JSON envelope
```

`extract_text()` accepts raw `bytes` (or any binary stream) so the document never needs to be written permanently to disk – ideal for privacy-sensitive workflows.

---

## Integrating ExtractText in your own project
Below is a pared-down blueprint distilled from *this* demo.  Copy-paste & adapt to suit your stack.

### 1. Backend (Python / FastAPI example)
```python
from fastapi import FastAPI, File, UploadFile
from extracttext import load as extract_text

app = FastAPI()

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    data = await file.read()                 # → bytes held in RAM only
    result = extract_text(data, filename=file.filename)
    return result.dict()                     # -> JSON serialisable
```
Key points:
* You **do not** need to save the upload to disk.
* Pass either the raw bytes (`await file.read()`) *or* the stream (`file.file`) to `extract_text()`.

### 2. Front-end (vanilla JS example)
```html
<script>
const file = /* File object from <input type=file> or drag-and-drop */
const formData = new FormData();
formData.append('file', file, file.name);

fetch('/extract', { method: 'POST', body: formData })
  .then(r => r.json())
  .then(json => console.log(json.text_payload))
  .catch(console.error);
</script>
```
The snippet above mirrors the logic found in [`index.html`](index.html).  Any framework (React, Vue, Svelte, etc.) can use the exact same `fetch()` call.

### 3. Handling the result
`extract_text()` returns an `ExtractionResult` dataclass →
```jsonc
{
  "document_id": "... uuid ...",
  "document_name": "invoice.pdf",
  "document_type": "PDF_TEXT",
  "text_payload": "Lorem ipsum ..."
}
```
Render `text_payload` as you wish (e.g. search, highlight, store in DB).  The other fields are useful for logging and downstream processing. 