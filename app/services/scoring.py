import re


def ats_score(text: str) -> int:
    terms = ("experience", "education", "skills", "projects", "email", "phone")
    section_score = sum(term in text.lower() for term in terms) * 10
    return max(0, min(100, section_score + min(40, len(text) // 250)))


def job_match(resume_text: str, job_description: str) -> tuple[int, list[str], list[str]]:
    resume_words = {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z+#.-]{2,}", resume_text)}
    job_words = {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z+#.-]{2,}", job_description)}
    ignored = {"and", "the", "with", "for", "from", "that", "this", "are", "you", "will", "our"}
    required = sorted(job_words - ignored)
    matched = [word for word in required if word in resume_words]
    missing = [word for word in required if word not in resume_words]
    score = round(len(matched) / len(required) * 100) if required else 0
    return score, matched[:50], missing[:50]
