from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from app.services.llm import parse_llm_response
from app.services.feedback import generate_resume_feedback
from app.services.scoring import job_match
from app.services.upload import UploadValidationError, parse_upload


def test_malformed_llm_response_uses_validated_fallback() -> None:
    result = parse_llm_response("not json", "Python FastAPI and SQL experience")
    assert 0 <= result.ats_score <= 100
    assert "python" in result.skills


def test_job_matching_is_bounded() -> None:
    score, matched, missing = job_match("Python FastAPI", "Python FastAPI PostgreSQL")
    assert score == 67
    assert matched == ["fastapi", "python"]
    assert "postgresql" in missing


def test_resume_feedback_uses_evidence_and_identifies_gaps() -> None:
    text = (
        "SUMMARY\nBackend engineer focused on reliable APIs.\n"
        "EXPERIENCE\nBuilt FastAPI services processing 120,000 requests daily and cut latency by 35%.\n"
        "EDUCATION\nBSc Computer Science\n"
        "SKILLS\nPython, FastAPI, PostgreSQL, Docker\n"
    )
    sections = {
        "summary": "Backend engineer focused on reliable APIs.",
        "experience": "Built FastAPI services processing 120,000 requests daily and cut latency by 35%.",
        "education": "BSc Computer Science",
        "skills": "Python, FastAPI, PostgreSQL, Docker",
    }

    strengths, improvements = generate_resume_feedback(text, sections, ["Python", "FastAPI", "PostgreSQL"])

    assert any("120,000 requests" in item for item in strengths)
    assert any("Python, FastAPI, PostgreSQL" in item for item in strengths)
    assert not any("measurable outcomes" in item for item in improvements)
    assert any("email address or phone number" in item for item in improvements)


def test_resume_feedback_suggests_missing_experience_and_skills_sections() -> None:
    strengths, improvements = generate_resume_feedback("Built internal dashboards.", {}, [])

    assert strengths == ["The document has a readable text layer for resume screening."]
    assert any("Add an Experience section" in item for item in improvements)
    assert any("dedicated Skills section" in item for item in improvements)


def test_docx_archive_expansion_is_bounded() -> None:
    archive_data = BytesIO()
    with ZipFile(archive_data, "w", ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", b"a" * (20 * 1024 * 1024 + 1))

    with pytest.raises(UploadValidationError, match="could not be parsed"):
        parse_upload(archive_data.getvalue(), ".docx")
