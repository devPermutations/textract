"""Tiny FastAPI service exposing /extract for the demo frontend.

Run with:
    uvicorn demo.server:app --reload

Then open http://localhost:8000/demo/index.html (or serve the file via any static file server).
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from extracttext import load as extract_text
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from time import perf_counter

app = FastAPI(title="ExtractText Demo API")

# Allow browser frontend hosted from same origin OR file://
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the demo directory itself (current file's parent) as static under /demo
STATIC_DIR = Path(__file__).parent
app.mount("/demo", StaticFiles(directory=STATIC_DIR, html=True), name="demo")


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    try:
        # Read entire file bytes into memory; alternative: pass file.file (spooledup) to load()
        data = await file.read()
        start = perf_counter()
        result = extract_text(data, filename=file.filename)
        elapsed_ms = (perf_counter() - start) * 1000

        payload = result.dict()
        payload["elapsed_ms"] = round(elapsed_ms, 2)
        payload["char_count"] = len(result.text_payload)
        return payload
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) 