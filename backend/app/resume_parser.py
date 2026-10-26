"""Safe, in-memory PDF validation and text extraction."""
from io import BytesIO
import fitz

MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_pdf(filename: str | None, content_type: str | None, data: bytes, max_size: int = MAX_FILE_SIZE) -> None:
    if not filename or not filename.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF resume.")
    if content_type and content_type not in {"application/pdf", "application/x-pdf"}:
        raise ValueError("The uploaded file must have PDF content type.")
    if not data:
        raise ValueError("The uploaded PDF is empty.")
    if len(data) > max_size:
        raise ValueError(f"The PDF is too large. Maximum size is {max_size // (1024 * 1024)} MB.")
    if not data.startswith(b"%PDF"):
        raise ValueError("The uploaded file is not a valid PDF.")


def extract_pdf_text(data: bytes) -> str:
    try:
        document = fitz.open(stream=BytesIO(data), filetype="pdf")
        text = "\n".join(page.get_text() for page in document).strip()
        document.close()
    except (fitz.FileDataError, RuntimeError) as error:
        raise ValueError("The PDF could not be read. Please upload a valid PDF.") from error
    if not text:
        raise ValueError("No readable text was found. This may be a scanned PDF; use a text-based PDF.")
    return text

