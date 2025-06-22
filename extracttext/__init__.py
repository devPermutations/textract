"""ExtractText – document text extraction façade.

Typical usage::

    from extracttext import load

    text = load("/path/to/document.pdf").text_payload

The heavy lifting is organised in individual extractors inside
`extracttext.extractors` and executed via the :class:`extracttext.dataloader.DataLoader`.
"""

from .dataloader import DataLoader, ExtractionResult, load  # noqa: F401
from .extractors.base_extractor import DocumentType  # noqa: F401

__all__ = [
    "load",
    "DataLoader",
    "ExtractionResult",
    "DocumentType",
    "UnsupportedDocumentError",
    "ExtractionFailedError",
]

# also expose errors for convenience
from .errors import UnsupportedDocumentError, ExtractionFailedError  # noqa: F401 