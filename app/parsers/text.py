import re


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def detect_sections(text: str) -> dict[str, str]:
    headings = {
        "summary": r"(?:summary|profile|objective)",
        "experience": r"(?:experience|employment|work history)",
        "education": r"education",
        "skills": r"(?:skills|technical skills|core competencies)",
        "projects": r"projects",
        "certifications": r"(?:certifications|licenses)",
    }
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current = "other"
    sections[current] = []
    for line in lines:
        normalized = line.strip().lower().rstrip(":")
        matched = next((name for name, pattern in headings.items() if re.fullmatch(pattern, normalized)), None)
        if matched:
            current = matched
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)
    return {name: "\n".join(values).strip() for name, values in sections.items() if "\n".join(values).strip()}
