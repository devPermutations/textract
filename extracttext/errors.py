"""Centralised exception hierarchy for ExtractText.

Having a dedicated module simplifies re-use across extractors and user code.
All custom errors subclass :class:`ExtractTextError` so that callers can catch
*everything* with a single `except ExtractTextError:` if desired.
"""
from __future__ import annotations

__all__ = [
    "ExtractTextError",
    "UnsupportedDocumentError",
    "ExtractionFailedError",
    "OcrEngineNotFoundError",
]


class ExtractTextError(RuntimeError):
    """Base-class for all library-specific errors."""


class UnsupportedDocumentError(ExtractTextError):
    """Raised when *no* extractor recognises the input document."""


class ExtractionFailedError(ExtractTextError):
    """Raised when *all* candidate extractors failed to retrieve text."""


class OcrEngineNotFoundError(ExtractTextError):
    """Raised when Tesseract (or underlying OCR engine) is missing/unavailable.""" 