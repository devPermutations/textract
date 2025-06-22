"""Public facade that orchestrates all extractors.

End-users are expected to import :func:`load` or instantiate :class:`DataLoader`.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, List, Union, Optional
import io
import os
import shutil
import tempfile
# Forward ref for executor typing hints (avoids heavy import unless needed)
from concurrent.futures import Executor

from .extractors import (
    CsvExtractor,
    DocxExtractor,
    ImageOcrExtractor,
    PdfOcrExtractor,
    PdfTextExtractor,
    TextExtractor,
)
from .extractors.base_extractor import BaseExtractor, DocumentType
from .errors import UnsupportedDocumentError, ExtractionFailedError

SourceType = Union[str, Path, bytes, BinaryIO]


@dataclass
class ExtractionResult:
    document_id: str
    document_name: str
    document_type: DocumentType
    text_payload: str

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def dict(self) -> dict:
        return asdict(self)

    def json(self, **kwargs) -> str:  # noqa: D401
        return json.dumps(self.dict(), default=str, **kwargs)


class DataLoader:
    """Central orchestrator – delegates work to individual extractors."""

    #: Ordered preference of extractors
    _EXTRACTORS: List[BaseExtractor] = [
        PdfTextExtractor(),
        DocxExtractor(),
        TextExtractor(),
        CsvExtractor(),
        ImageOcrExtractor(),
        PdfOcrExtractor(),
    ]

    def __init__(self, *, prefer_ocr: bool = False, executor: Optional["Executor"] = None):
        self.prefer_ocr = prefer_ocr
        if executor is None and prefer_ocr:
            # Lazy import to avoid heavy module unless concurrency requested
            from .concurrency import get_default_executor

            executor = get_default_executor()

        self._executor = executor

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalise_source(source: SourceType, filename: str | None = None) -> tuple[Path, str, _t.Callable[[], None]]:
        """Return a concrete `Path`, resolved filename and a *cleanup* callback.

        If *source* is already a path on disk, it is returned as-is and the
        cleanup callback is a no-op.  For bytes/streams the data is persisted in
        a temporary file which **caller must** remove via the provided cleanup.
        """
        # Late import to avoid polluting global namespace
        import typing as _t

        noop = lambda: None  # noqa: E731 – simple placeholder

        # ------------------------------------------------------------------
        # Case 1 – string / Path pointing to an existing file on disk
        # ------------------------------------------------------------------
        if isinstance(source, (str, Path)):
            path = Path(source).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(path)
            return path, (filename or path.name), noop

        # ------------------------------------------------------------------
        # Case 2 – raw bytes (e.g. FastAPI's UploadFile.read())
        # ------------------------------------------------------------------
        if isinstance(source, (bytes, bytearray)):
            suffix = f"_{filename}" if filename else ""
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(source)  # type: ignore[arg-type]
            tmp.flush()
            tmp.close()
            return Path(tmp.name), (filename or Path(tmp.name).name), lambda: os.remove(tmp.name)

        # ------------------------------------------------------------------
        # Case 3 – binary file-like object (implements read())
        # ------------------------------------------------------------------
        if hasattr(source, "read"):
            suffix = f"_{filename}" if filename else ""
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            shutil.copyfileobj(source, tmp)  # type: ignore[arg-type]
            tmp.flush()
            tmp.close()
            return Path(tmp.name), (filename or Path(tmp.name).name), lambda: os.remove(tmp.name)

        raise TypeError("Unsupported *source* type; expected path, bytes, or BinaryIO")

    def _iter_extractors(self) -> List[BaseExtractor]:
        """Return extractors in order, honouring *prefer_ocr*."""
        if not self.prefer_ocr:
            return self._EXTRACTORS

        # Move OCR variants to the front while preserving original relative order
        ocr_types = {DocumentType.IMAGE, DocumentType.PDF_IMAGE}
        return sorted(self._EXTRACTORS, key=lambda e: e.DOCUMENT_TYPE not in ocr_types)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self, source: SourceType, filename: str | None = None) -> ExtractionResult:  # noqa: D401
        """Return :class:`ExtractionResult` for *source*.

        Current implementation **only identifies** the first extractor capable
        of handling the document.  Text extraction will be added in subsequent
        milestones.
        """
        # 1. Normalise various input shapes into an on-disk file reference
        path, final_name, cleanup = self._normalise_source(source, filename)

        try:
            last_error: Exception | None = None

            # 2. Iterate through extractors in preference order
            for extractor in self._iter_extractors():
                try:
                    if not extractor.can_process(path):
                        continue
                except Exception:
                    # Heuristic should be cheap & fail-safe – skip extractor on error
                    continue

                # Attempt heavy extraction; allow extractor to raise
                try:
                    # OCR heavy tasks can benefit from process pool
                    if self._executor and extractor.DOCUMENT_TYPE in {DocumentType.IMAGE, DocumentType.PDF_IMAGE}:
                        text_future = self._executor.submit(extractor.extract_text, path)
                        text_payload = text_future.result()
                    else:
                        text_payload = extractor.extract_text(path)

                    # Success – build result envelope
                    return ExtractionResult(
                        document_id=str(uuid.uuid4()),
                        document_name=final_name,
                        document_type=extractor.DOCUMENT_TYPE,
                        text_payload=text_payload,
                    )
                except Exception as exc:
                    # Record error and fall back to next extractor
                    last_error = exc
                    continue

            # ------------------------------------------------------------------
            # No extractor succeeded – decide which error to raise
            # ------------------------------------------------------------------
            if last_error is None:
                # None even *recognised* the document
                raise UnsupportedDocumentError("No extractor recognised this document")

            raise ExtractionFailedError("All extractors failed to extract text") from last_error
        finally:
            # Ensure any temp files are cleaned up to avoid /tmp leakage
            try:
                cleanup()
            except Exception:
                # Best-effort cleanup; swallow errors
                pass


# Convenience functional API -------------------------------------------------

def load(source: SourceType, filename: str | None = None, *, prefer_ocr: bool = False, executor: Optional["Executor"] = None) -> ExtractionResult:  # noqa: D401
    """Module-level helper mirroring :pymeth:`DataLoader.load`."""

    return DataLoader(prefer_ocr=prefer_ocr, executor=executor).load(source, filename=filename) 