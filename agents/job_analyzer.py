# agents/job_analyzer.py

from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class JobAnalysis(BaseModel):
    title: str = Field(default="", description="Job title if explicitly stated")
    company: str = Field(default="", description="Company name if explicitly stated")
    summary: str = Field(default="", description="Short summary of the role")

    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    tools_technologies: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


def build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")

    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=0,
    )


def analyze_job_description(job_text: str) -> JobAnalysis:
    """
    Extract structured information from a job description.
    """
    if not job_text or not job_text.strip():
        raise ValueError("job_text is empty.")

    llm = build_llm().with_structured_output(JobAnalysis)

    prompt = f"""
You are a job description analysis assistant.

Extract only facts explicitly present in the job description.
Do not guess or invent anything.

Return:
- job title if present
- company if present
- required skills
- preferred skills
- responsibilities
- qualifications
- tools and technologies
- useful keywords

Job description:
{job_text}
"""

    result = llm.invoke(prompt)
    return result


if __name__ == "__main__":
    sample_job_text = """
    Data Science Intern
    We are looking for a student with Python, SQL, and machine learning experience.
    Responsibilities include data cleaning, analysis, and dashboard creation.
    Experience with Tableau and Git is preferred.
    """

    analysis = analyze_job_description(sample_job_text)
    print(analysis.model_dump())