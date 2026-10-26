"""Editable, intentionally small technical-skill dictionary and extraction rules."""
import re

# Extend this list as your target roles change. Keys are display names; each value
# contains accepted spellings. Boundaries prevent false matches such as "go" in "good".
SKILL_DICTIONARY: dict[str, list[str]] = {
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cplusplus"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "SQL": ["sql", "mysql", "postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo db"],
    "Git": ["git", "github"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Machine Learning": ["machine learning", "ml"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "HTML": ["html"],
    "CSS": ["css", "tailwind"],
}


def _contains_term(text: str, term: str) -> bool:
    """Match a term without matching inside larger alphanumeric words."""
    pattern = rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])"
    return bool(re.search(pattern, text.lower()))


def extract_skills(text: str) -> list[str]:
    if not text:
        return []
    return sorted(
        skill for skill, aliases in SKILL_DICTIONARY.items()
        if any(_contains_term(text, alias) for alias in aliases)
    )


def analyze_skill_gap(resume_text: str, job_description: str) -> dict[str, list[str]]:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    resume_set, job_set = set(resume_skills), set(job_skills)
    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": sorted(resume_set & job_set),
        "missing_skills": sorted(job_set - resume_set),
    }

