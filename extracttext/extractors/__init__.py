"""Extractor registry sub-package.

Each module defines a concrete `BaseExtractor` implementation.
End-users generally don't import these directly; they are wired up by
`extracttext.dataloader`.
"""

from .base_extractor import BaseExtractor, DocumentType  # noqa: F401
from .pdf_text import PdfTextExtractor  # noqa: F401
from .pdf_ocr import PdfOcrExtractor  # noqa: F401
from .image_ocr import ImageOcrExtractor  # noqa: F401
from .docx import DocxExtractor  # noqa: F401
from .text_file import TextExtractor  # noqa: F401
from .csv_file import CsvExtractor  # noqa: F401

__all__ = [
    "BaseExtractor",
    "DocumentType",
    "PdfTextExtractor",
    "PdfOcrExtractor",
    "ImageOcrExtractor",
    "DocxExtractor",
    "TextExtractor",
    "CsvExtractor",
] 