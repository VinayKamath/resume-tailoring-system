from __future__ import annotations

import os
import random
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_FILE = DATA_DIR / "resume_templates.txt"
ACTION_VERBS_FILE = DATA_DIR / "action_verbs.txt"


class BulletRewrite(BaseModel):
    original_bullet: str = Field(default="", description="Original resume bullet")
    rewritten_bullet: str = Field(default="", description="Improved resume bullet")
    reason: str = Field(default="", description="Short explanation of the rewrite")


def build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")

    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=0,
    )


def load_lines(file_path: Path) -> List[str]:
    """
    Load non-empty lines from a text file.
    Ignores blank lines and comment lines starting with #.
    """
    if not file_path.exists():
        return []

    lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                lines.append(cleaned)
    return lines


def pick_context_templates(n: int = 3) -> List[str]:
    templates = load_lines(TEMPLATES_FILE)
    if not templates:
        return []
    return random.sample(templates, k=min(n, len(templates)))


def pick_action_verbs(n: int = 5) -> List[str]:
    verbs = load_lines(ACTION_VERBS_FILE)
    if not verbs:
        return []
    return random.sample(verbs, k=min(n, len(verbs)))


def rewrite_single_bullet(
    original_bullet: str,
    resume_skills: List[str],
    job_skills: List[str],
    match_score: float
) -> BulletRewrite:
    """
    Rewrite one bullet point using the resume/job context.
    """
    if not original_bullet or not original_bullet.strip():
        raise ValueError("original_bullet is empty.")

    llm = build_llm().with_structured_output(BulletRewrite)

    templates = pick_context_templates(3)
    verbs = pick_action_verbs(5)

    prompt = f"""
You are an expert resume writer.

Rewrite the original bullet into a stronger ATS-friendly bullet point.
Rules:
- Preserve the original meaning and facts.
- Do not invent new metrics, tools, or achievements.
- Make it concise, professional, and impact-driven.
- Use one strong action verb.
- Keep it suitable for a resume.
- Prefer keywords relevant to the job.

Original bullet:
{original_bullet}

Resume skills:
{resume_skills}

Job skills:
{job_skills}

Match score:
{match_score}

Useful action verbs:
{verbs}

Helpful resume templates:
{templates}
"""

    result = llm.invoke(prompt)
    return result


def rewrite_bullets(
    bullets: List[str],
    resume_skills: List[str],
    job_skills: List[str],
    match_score: float
) -> List[BulletRewrite]:
    """
    Rewrite a list of bullets.
    """
    rewrites = []

    for bullet in bullets:
        if bullet and bullet.strip():
            rewrites.append(
                rewrite_single_bullet(
                    original_bullet=bullet,
                    resume_skills=resume_skills,
                    job_skills=job_skills,
                    match_score=match_score,
                )
            )

    return rewrites


if __name__ == "__main__":
    sample_bullets = [
        "Built a dashboard for sales data.",
        "Worked on data cleaning and analysis."
    ]

    sample_resume_skills = ["Python", "Pandas", "Streamlit", "SQL"]
    sample_job_skills = ["Python", "Tableau", "Data Analysis"]

    results = rewrite_bullets(
        bullets=sample_bullets,
        resume_skills=sample_resume_skills,
        job_skills=sample_job_skills,
        match_score=72.5
    )

    for item in results:
        print(item.model_dump())
        print("-" * 80)