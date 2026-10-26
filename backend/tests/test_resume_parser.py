import pytest
from app.resume_parser import validate_pdf


def test_rejects_non_pdf_extension():
    with pytest.raises(ValueError, match="PDF"):
        validate_pdf("resume.docx", "application/pdf", b"%PDF-test")


def test_rejects_non_pdf_contents():
    with pytest.raises(ValueError, match="valid PDF"):
        validate_pdf("resume.pdf", "application/pdf", b"not pdf")

