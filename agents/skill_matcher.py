from __future__ import annotations

from typing import List, Set

from pydantic import BaseModel, Field

from agents.resume_analyzer import ResumeAnalysis
from agents.job_analyzer import JobAnalysis


class SkillMatchResult(BaseModel):
    matched_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    extra_resume_skills: List[str] = Field(default_factory=list)
    match_score: float = Field(default=0.0, description="Score from 0 to 100")
    summary: str = Field(default="")


SKILL_ALIASES = {
    "machine learning": [
        "machine learning",
        "ml",
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "sklearn",
    ],
    "data visualization": [
        "data visualization",
        "visualization",
        "matplotlib",
        "seaborn",
        "plotly",
        "tableau",
        "power bi",
    ],
    "git": [
        "git",
        "git & gitlab",
        "github",
        "gitlab",
    ],
    "cloud": [
        "aws",
        "gcp",
        "azure",
    ],
}


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def _unique_clean_list(items: List[str]) -> List[str]:
    cleaned = []
    seen = set()

    for item in items:
        item = item.strip()
        if not item:
            continue

        key = _normalize_skill(item)
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


def _expand_skill(skill: str) -> Set[str]:
    """
    Return a set of normalized aliases for a skill.
    """
    normalized = _normalize_skill(skill)
    expanded = {normalized}

    for canonical, aliases in SKILL_ALIASES.items():
        if normalized == canonical or normalized in aliases:
            expanded.add(canonical)
            expanded.update(aliases)

    return expanded


def _skills_match(resume_skill: str, job_skill: str) -> bool:
    resume_set = _expand_skill(resume_skill)
    job_set = _expand_skill(job_skill)
    return len(resume_set.intersection(job_set)) > 0


def compare_skills(
    resume_analysis: ResumeAnalysis,
    job_analysis: JobAnalysis
) -> SkillMatchResult:
    """
    Compare resume skills with job description skills.
    Returns matched skills, missing skills, extra skills, and a basic score.
    """

    resume_skills = _unique_clean_list(resume_analysis.skills + resume_analysis.tools)
    required_skills = _unique_clean_list(job_analysis.required_skills)
    preferred_skills = _unique_clean_list(job_analysis.preferred_skills)

    matched_skills = []
    missing_required_skills = []
    extra_resume_skills = []

    # Find matched required/preferred skills
    for resume_skill in resume_skills:
        is_match = False
        for job_skill in required_skills + preferred_skills:
            if _skills_match(resume_skill, job_skill):
                is_match = True
                break

        if is_match:
            matched_skills.append(resume_skill)
        else:
            extra_resume_skills.append(resume_skill)

    # Required skills missing from resume
    for job_skill in required_skills:
        found = False
        for resume_skill in resume_skills:
            if _skills_match(resume_skill, job_skill):
                found = True
                break
        if not found:
            missing_required_skills.append(job_skill)

    # Score calculation
    required_score = 0.0
    preferred_score = 0.0

    if required_skills:
        matched_required = sum(
            1 for job_skill in required_skills
            if any(_skills_match(resume_skill, job_skill) for resume_skill in resume_skills)
        )
        required_score = (matched_required / len(required_skills)) * 70

    if preferred_skills:
        matched_preferred = sum(
            1 for job_skill in preferred_skills
            if any(_skills_match(resume_skill, job_skill) for resume_skill in resume_skills)
        )
        preferred_score = (matched_preferred / len(preferred_skills)) * 30

    match_score = round(required_score + preferred_score, 2)

    if match_score >= 80:
        summary = "Strong match between resume and job description."
    elif match_score >= 50:
        summary = "Moderate match. Some important skills are missing."
    else:
        summary = "Weak match. Several key skills are missing."

    return SkillMatchResult(
        matched_skills=matched_skills,
        missing_required_skills=missing_required_skills,
        extra_resume_skills=extra_resume_skills,
        match_score=match_score,
        summary=summary,
    )


if __name__ == "__main__":
    sample_resume = ResumeAnalysis(
        skills=["Python", "SQL", "Pandas", "Streamlit", "TensorFlow", "Matplotlib"],
        tools=["Git", "Docker"]
    )

    sample_job = JobAnalysis(
        required_skills=["Python", "SQL", "Machine Learning", "Tableau"],
        preferred_skills=["Docker", "Streamlit", "Data Visualization"]
    )

    result = compare_skills(sample_resume, sample_job)
    print(result.model_dump())