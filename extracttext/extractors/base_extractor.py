"""Shared abstractions for all extractors (renamed from base.py)."""

# ... existing code ...
from __future__ import annotations

import abc
import enum
import typing as _t
from pathlib import Path

__all__ = [
    "DocumentType",
    "BaseExtractor",
]


class DocumentType(str, enum.Enum):
    """Canonical names for supported document categories."""

    PDF_TEXT = "pdf_text"
    PDF_IMAGE = "pdf_image"  # rasterised or scanned
    IMAGE = "image"  # jpg / png / tiff
    DOCX = "docx"
    TEXT = "text"
    CSV = "csv"

    @property
    def is_pdf(self) -> bool:  # convenience helper
        return self.value.startswith("pdf")


class BaseExtractor(abc.ABC):
    """Abstract extractor contract.

    Concrete subclasses *must* implement both :meth:`can_process` and
    :meth:`extract_text`.
    """

    #: Set by subclasses so that callers can inspect which logical type this
    #: extractor handles (e.g. differentiating PDF-with-text vs. PDF-OCR).
    DOCUMENT_TYPE: DocumentType

    # ---------------------------------------------------------------------
    # Static helpers every extractor can reuse
    # ---------------------------------------------------------------------
    @staticmethod
    def _to_path(source: _t.Union[str, Path]) -> Path:
        """Ensure *source* is a `pathlib.Path`."""
        if isinstance(source, Path):
            return source
        return Path(source)

    # ------------------------------------------------------------------
    # Mandatory interface
    # ------------------------------------------------------------------
    @abc.abstractmethod
    def can_process(self, source: _t.Union[str, Path]) -> bool:  # noqa: D401
        """Cheap check quickly indicating whether this extractor *might* handle the file.

        Should avoid heavy I/O; prefer checking file extensions, magic numbers,
        or the first few bytes. Returning *False* guarantees the orchestrator
        will not invoke :meth:`extract_text` for this extractor.
        """

    @abc.abstractmethod
    def extract_text(self, source: _t.Union[str, Path, bytes]) -> str:  # noqa: D401
        """Return *raw* text from *source*.

        Subclasses should raise an exception (e.g. `RuntimeError`) if extraction
        fails so that the orchestrator can attempt a fallback extractor.
        """ 