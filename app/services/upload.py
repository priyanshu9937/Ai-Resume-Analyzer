from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.core.errors import AppError
from app.parsers.documents import DocumentParseError
from app.parsers.documents import extract_text
from app.parsers.text import clean_text

ALLOWED_TYPES = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}


class UploadValidationError(AppError):
    def __init__(self, code: str, message: str, status_code: int = 422) -> None:
        super().__init__(status_code, code, message)


@dataclass(frozen=True)
class ParsedDocument:
    text: str
    page_count: int | None = None
    paragraph_count: int | None = None


def validate_upload(filename: str | None, content_type: str | None, content: bytes, settings: Settings) -> tuple[str, str]:
    if not filename:
        raise UploadValidationError("filename_required", "A filename is required")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_TYPES:
        raise UploadValidationError("unsupported_file_type", "Only PDF and DOCX resumes are supported", 415)
    if content_type not in ALLOWED_TYPES[extension]:
        raise UploadValidationError("unsupported_media_type", "The file type does not match its extension", 415)
    if len(content) > settings.max_upload_size_bytes:
        raise UploadValidationError("file_too_large", "The uploaded file exceeds the size limit", 413)
    if len(content) == 0:
        raise UploadValidationError("empty_file", "The uploaded file is empty")
    if extension == ".pdf" and not content.startswith(b"%PDF"):
        raise UploadValidationError("corrupt_file", "The uploaded PDF is invalid")
    if extension == ".docx" and not content.startswith(b"PK"):
        raise UploadValidationError("corrupt_file", "The uploaded DOCX is invalid")
    return extension, f"{uuid4().hex}{extension}"


def save_upload(filename: str, content: bytes, settings: Settings) -> Path:
    path = settings.upload_dir / filename
    path.write_bytes(content)
    return path


def parse_upload(content: bytes, extension: str) -> ParsedDocument:
    try:
        parsed = extract_text(content, extension)
        text = clean_text(parsed.text)
    except DocumentParseError as exc:
        raise UploadValidationError("extraction_failed", "The uploaded document could not be parsed") from exc
    if not text:
        raise UploadValidationError("empty_extracted_text", "The resume contains no extractable text")
    return ParsedDocument(text=text, page_count=parsed.page_count, paragraph_count=parsed.paragraph_count)
