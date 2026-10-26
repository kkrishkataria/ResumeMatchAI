"""Small, explainable TF-IDF based matching functions."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(resume_text: str, job_description: str) -> float:
    """Return cosine similarity as a percentage rounded to one decimal place."""
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty.")

    vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
    try:
        matrix = vectorizer.fit_transform([resume_text, job_description])
    except ValueError as error:
        # Scikit-learn raises this for text containing only stop words.
        raise ValueError("The provided text does not contain meaningful terms.") from error

    score = cosine_similarity(matrix[0], matrix[1])[0][0] * 100
    return round(float(score), 1)


def calculate_skill_similarity(matched_skills: list[str], job_skills: list[str]) -> float:
    """Return the percentage of recognized job skills also found in the resume."""
    if not job_skills:
        return 0.0
    return round((len(matched_skills) / len(job_skills)) * 100, 1)


def build_explanation(score: float, matched_count: int, missing_count: int) -> str:
    """Provide a deliberately modest, rule-based interpretation."""
    if score >= 65:
        level = "strong recognized skill overlap"
    elif score >= 35:
        level = "moderate recognized skill overlap"
    else:
        level = "limited recognized skill overlap"

    message = f"The resume and job description show {level} ({score}%). "
    message += f"{matched_count} recognized skill(s) overlap"
    if missing_count:
        message += f", while {missing_count} job skill(s) were not found in the resume."
    else:
        message += ". No listed job skills were identified as missing."
    return message + " This uses a limited, editable skill dictionary and is not a hiring prediction."

