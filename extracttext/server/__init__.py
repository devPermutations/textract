"""Lightweight API for ExtractText.

Launch with:
    python -m extracttext.server                # starts on http://0.0.0.0:6060
    # or, using uvicorn directly:
    uvicorn extracttext.server:app --host 0.0.0.0 --port 6060
"""

from time import perf_counter

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from extracttext import load as extract_text

app = FastAPI(title="ExtractText API")

# Allow requests from any origin (handy for demos / local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/gettext")
async def gettext(file: UploadFile = File(...)):
    """Extract raw text from an uploaded document.

    Accepts *any* file type supported by `extracttext.load()`.  Returns the JSON
    envelope serialisable via `ExtractionResult.dict()`, plus a few extras.
    """
    try:
        data = await file.read()
        start = perf_counter()

        result = extract_text(data, filename=file.filename)
        elapsed_ms = (perf_counter() - start) * 1000

        payload = result.dict()
        payload["elapsed_ms"] = round(elapsed_ms, 2)
        payload["char_count"] = len(result.text_payload)
        return payload
    except Exception as exc:  # pragma: no cover – pass through verbatim
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _run_dev_server():
    """Convenience entry-point when invoking `python -m extracttext.server`."""

    import uvicorn

    uvicorn.run(
        "extracttext.server:app",
        host="0.0.0.0",
        port=6060,
        reload=True,
    )


# ---------------------------------------------------------------------------
# `python -m extracttext.server` → run the helper above
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _run_dev_server() 