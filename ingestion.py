"""
app/services/ingestion.py

Low-level file handling: where uploaded bytes get written to disk, and
how text is extracted out of PDFs so it can be fed to the LLM as
context (since most models can't read raw PDF bytes directly).

Kept separate from routers/upload.py so this logic is unit-testable
without spinning up FastAPI at all.
"""

from pathlib import Path

import pypdf

from app.core.config import settings


def save_upload(attachment_id: str, original_filename: str, contents: bytes) -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(original_filename).suffix
    dest = upload_dir / f"{attachment_id}{suffix}"
    dest.write_bytes(contents)
    return dest


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Pulls all text out of a PDF for use as LLM context. For scanned/
    image-only PDFs this will return little or nothing — that's a known
    limitation; an OCR fallback (e.g. pytesseract) can be added here later
    without changing the router that calls this function.
    """
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()
    except Exception as exc:  # noqa: BLE001 — surface as empty text, don't crash the upload
        return f"[Could not extract text: {exc}]"
