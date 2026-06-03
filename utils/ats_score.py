from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from agents.skill_matcher import SkillMatchResult


class ATSScoreResult(BaseModel):
    overall_score: float = Field(default=0.0, description="Overall ATS score from 0 to 100")
    skill_match_score: float = Field(default=0.0, description="Score from skill comparison")
    keyword_coverage_score: float = Field(default=0.0, description="Keyword coverage score")
    resume_quality_score: float = Field(default=0.0, description="Basic resume quality score")
    explanation: str = Field(default="")


def _normalize(text: str) -> str:
    return text.strip().lower()


def _unique_nonempty(items: List[str]) -> List[str]:
    cleaned = []
    seen = set()

    for item in items:
        item = item.strip()
        if not item:
            continue

        key = _normalize(item)
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


def calculate_keyword_coverage(resume_text: str, job_keywords: List[str]) -> float:
    """
    Very simple keyword coverage score.
    Counts how many job keywords appear in the resume text.
    """
    if not resume_text or not resume_text.strip():
        return 0.0

    job_keywords = _unique_nonempty(job_keywords)
    if not job_keywords:
        return 0.0

    resume_lower = resume_text.lower()

    matched = 0
    for keyword in job_keywords:
        if keyword.lower() in resume_lower:
            matched += 1

    return round((matched / len(job_keywords)) * 100, 2)


def calculate_resume_quality_score(resume_text: str) -> float:
    """
    Lightweight heuristic score based on resume length and structure.
    This is not a real ATS metric — just a simple proxy for the MVP.
    """
    if not resume_text or not resume_text.strip():
        return 0.0

    text = resume_text.strip()
    length = len(text)

    score = 0.0

    # Length heuristic
    if length >= 3000:
        score += 40
    elif length >= 1500:
        score += 30
    elif length >= 800:
        score += 20
    else:
        score += 10

    # Structure heuristic
    lower = text.lower()
    sections = ["experience", "education", "skills", "projects"]
    found_sections = sum(1 for section in sections if section in lower)
    score += found_sections * 15

    return min(round(score, 2), 100.0)


def calculate_ats_score(
    skill_match_result: SkillMatchResult,
    resume_text: str = "",
    job_keywords: List[str] | None = None
) -> ATSScoreResult:
    """
    Calculate a simple ATS-style score.

    Weights:
    - Skill match score: 50%
    - Keyword coverage: 30%
    - Resume quality: 20%
    """
    job_keywords = job_keywords or []

    skill_match_score = float(skill_match_result.match_score)
    keyword_coverage_score = calculate_keyword_coverage(resume_text, job_keywords)
    resume_quality_score = calculate_resume_quality_score(resume_text)

    overall_score = (
        skill_match_score * 0.50 +
        keyword_coverage_score * 0.30 +
        resume_quality_score * 0.20
    )

    overall_score = round(overall_score, 2)

    if overall_score >= 80:
        explanation = "Strong ATS alignment. Resume matches the role well."
    elif overall_score >= 60:
        explanation = "Moderate ATS alignment. A few improvements could help."
    elif overall_score >= 40:
        explanation = "Below-average ATS alignment. Several important improvements are needed."
    else:
        explanation = "Weak ATS alignment. The resume needs significant tailoring."

    return ATSScoreResult(
        overall_score=overall_score,
        skill_match_score=round(skill_match_score, 2),
        keyword_coverage_score=keyword_coverage_score,
        resume_quality_score=resume_quality_score,
        explanation=explanation,
    )


if __name__ == "__main__":
    from agents.skill_matcher import SkillMatchResult

    sample_match = SkillMatchResult(
        matched_skills=["Python", "SQL"],
        missing_required_skills=["Tableau"],
        extra_resume_skills=["Pandas"],
        match_score=68.0,
        summary="Moderate match."
    )

    sample_resume_text = """
    Experience
    Skills
    Python, SQL, Pandas
    Projects
    """

    sample_job_keywords = ["Python", "SQL", "Tableau", "Data Analysis"]

    result = calculate_ats_score(
        skill_match_result=sample_match,
        resume_text=sample_resume_text,
        job_keywords=sample_job_keywords
    )

    print(result.model_dump())