from app.skill_extractor import analyze_skill_gap, extract_skills


def test_extracts_skill_aliases_without_substring_matches():
    assert "Go" not in extract_skills("A good communicator")
    assert {"Python", "React", "SQL"} <= set(extract_skills("Python, React.js, and PostgreSQL"))


def test_gap_analysis():
    result = analyze_skill_gap("Python and Git", "Python, Docker and Git")
    assert result["matched_skills"] == ["Git", "Python"]
    assert result["missing_skills"] == ["Docker"]

