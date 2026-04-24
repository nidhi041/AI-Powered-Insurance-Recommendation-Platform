"""
parser.py
---------
Handles PDF text extraction and text chunking.
"""

import logging
from typing import List
from io import BytesIO

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text content from a PDF byte stream.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        ValueError: If the PDF is empty or unreadable.
    """
    try:
        reader = PdfReader(BytesIO(file_bytes))
        if not reader.pages:
            raise ValueError("PDF has no pages.")

        texts: List[str] = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                texts.append(text.strip())
            else:
                logger.debug("Page %d yielded no text; skipping.", page_num + 1)

        if not texts:
            raise ValueError("No extractable text found in the PDF.")

        full_text = "\n\n".join(texts)
        logger.info("Extracted %d characters from %d pages.", len(full_text), len(reader.pages))
        return full_text

    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc)
        raise


def chunk_text(text: str) -> List[str]:
    """
    Split extracted text into overlapping chunks suitable for embedding.

    Args:
        text: The full document text.

    Returns:
        List of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.info("Split text into %d chunks (size=%d, overlap=%d).",
                len(chunks), settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    return chunks
