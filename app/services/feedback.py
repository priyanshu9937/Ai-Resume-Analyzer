import re


METRIC_PATTERN = re.compile(
    r"\b\d+(?:[,.]\d+)?\s*(?:%|x\b|k\b|m\b)|"
    r"\b\d[\d,]*\+?\s+(?:users?|customers?|clients?|requests?|records?|teams?|projects?|hours?|days?|weeks?|months?)\b",
    re.IGNORECASE,
)
SECTION_TITLES = {
    "experience": "experience",
    "education": "education",
    "skills": "skills",
    "projects": "projects",
    "certifications": "certifications",
    "summary": "profile summary",
}


def generate_resume_feedback(text: str, sections: dict[str, str], skills: list[str]) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    improvements: list[str] = []
    text_lower = text.lower()

    metric_line = next(
        (re.sub(r"\s+", " ", line).strip(" -*\t") for line in text.splitlines() if METRIC_PATTERN.search(line)),
        None,
    )
    if metric_line:
        excerpt = metric_line if len(metric_line) <= 115 else f"{metric_line[:112].rstrip()}..."
        strengths.append(f"Quantified impact: '{excerpt}'")

    evidenced_skills = [skill for skill in skills if skill.strip() and skill.lower() in text_lower]
    if evidenced_skills:
        strengths.append(f"Shows relevant tools in the resume: {', '.join(evidenced_skills[:4])}.")

    present_sections = [title for key, title in SECTION_TITLES.items() if sections.get(key, "").strip()]
    if len(present_sections) >= 2:
        strengths.append(f"Uses clear sections for {', '.join(present_sections[:4])}.")
    if not strengths:
        strengths.append("The document has a readable text layer for resume screening.")

    experience = sections.get("experience", "").strip()
    if not experience:
        improvements.append("Add an Experience section with role, organization, dates, and results.")
    elif not METRIC_PATTERN.search(experience):
        improvements.append("Add measurable outcomes to experience bullets, such as scale, time saved, or quality improved.")

    if not sections.get("skills", "").strip():
        improvements.append("Add a dedicated Skills section with tools and methods relevant to your target role.")

    has_email = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
    has_phone = re.search(r"(?:\+?\d[\d ()-]{7,}\d)", text)
    if not has_email and not has_phone:
        improvements.append("Include a professional email address or phone number for recruiter follow-up.")

    if not improvements:
        improvements.append("Tailor the strongest experience bullets to the requirements of each target role.")

    return strengths[:3], improvements[:3]