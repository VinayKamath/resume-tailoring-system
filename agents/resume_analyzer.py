from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class ResumeAnalysis(BaseModel):
    name: str = Field(default="", description="Candidate full name")
    headline: str = Field(default="", description="Short professional headline")
    email: str = Field(default="", description="Email address if present")
    phone: str = Field(default="", description="Phone number if present")
    location: str = Field(default="", description="Location if present")

    education: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    summary: str = Field(default="", description="2-3 sentence resume summary")


def build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")

    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=0,
    )


def analyze_resume(resume_text: str) -> ResumeAnalysis:
    """
    Extract structured information from a resume.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text is empty.")

    llm = build_llm().with_structured_output(ResumeAnalysis)

    prompt = f"""
You are a resume parsing assistant.

Extract only facts that are explicitly present in the resume.
Do not guess or invent anything.
Return clean, concise values.

Resume text:
{resume_text}
"""

    result = llm.invoke(prompt)
    return result


if __name__ == "__main__":
    # Quick test
    from utils.pdf_parser import extract_text_from_pdf

    resume_text = extract_text_from_pdf("sample_resume.pdf")
    analysis = analyze_resume(resume_text)

    print(analysis.model_dump())