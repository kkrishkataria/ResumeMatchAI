import pytest
from app.matcher import calculate_similarity, calculate_skill_similarity


def test_similarity_is_high_for_identical_text():
    assert calculate_similarity("Python React developer", "Python React developer") == 100.0


def test_similarity_rejects_empty_text():
    with pytest.raises(ValueError, match="empty"):
        calculate_similarity("", "Python developer")


def test_skill_similarity_uses_matched_job_skills():
    assert calculate_skill_similarity(["Python", "Git"], ["Python", "Git", "Docker"]) == 66.7
    assert calculate_skill_similarity([], []) == 0.0

