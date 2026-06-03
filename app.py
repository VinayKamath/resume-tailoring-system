# app.py

from __future__ import annotations

import re
from pathlib import Path
from typing import List

import streamlit as st

from agents.bullet_rewriter import rewrite_bullets
from agents.job_analyzer import analyze_job_description
from agents.resume_analyzer import analyze_resume
from agents.skill_matcher import compare_skills
from utils.ats_score import calculate_ats_score
from utils.pdf_parser import extract_text_from_pdf

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Tailoring System",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Multi-Agent Resume Tailoring System")
st.write(
    "Upload a resume PDF, paste a job description, and get skill matching, ATS scoring, and bullet rewrites."
)

SAMPLE_RESUME_PATH = Path("data/vinay_kamath_ai_resume.pdf")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def extract_bullets_from_text(text: str, max_bullets: int = 3) -> List[str]:
    """
    Try to pull a few bullet-like lines from the resume text.
    This is a simple MVP approach.
    """
    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullets = []

    bullet_pattern = re.compile(r"^(\u2022|-|\*|•|▪|◦)\s*(.+)$")

    for line in lines:
        match = bullet_pattern.match(line)
        if match:
            cleaned = match.group(2).strip()
            if cleaned:
                bullets.append(cleaned)

    if bullets:
        return bullets[:max_bullets]

    # Fallback: look for lines under Experience section
    capture = False
    for line in lines:
        lower = line.lower()

        if lower.startswith("experience"):
            capture = True
            continue

        if capture:
            if lower.startswith(("education", "skills", "projects", "certifications")):
                break

            # Ignore very short lines
            if len(line) > 40:
                bullets.append(line)

        if len(bullets) >= max_bullets:
            break

    return bullets[:max_bullets]


def display_skill_list(title: str, items: List[str]):
    st.subheader(title)
    if items:
        st.write(", ".join(items))
    else:
        st.write("None")


def build_report_text(
    resume_name: str,
    match_score: float,
    ats_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    rewritten_bullets: List[str],
) -> str:
    report = []
    report.append(f"Resume Tailoring Report")
    report.append("=" * 40)
    report.append(f"Resume: {resume_name}")
    report.append(f"Skill Match Score: {match_score}")
    report.append(f"ATS Score: {ats_score}")
    report.append("")
    report.append("Matched Skills:")
    report.extend([f"- {s}" for s in matched_skills] if matched_skills else ["- None"])
    report.append("")
    report.append("Missing Skills:")
    report.extend([f"- {s}" for s in missing_skills] if missing_skills else ["- None"])
    report.append("")
    report.append("Rewritten Bullets:")
    report.extend([f"- {b}" for b in rewritten_bullets] if rewritten_bullets else ["- None"])
    return "\n".join(report)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.header("Input Options")
use_sample_resume = st.sidebar.checkbox("Use sample resume from data/", value=True)

uploaded_resume = None
if not use_sample_resume:
    uploaded_resume = st.sidebar.file_uploader("Upload Resume PDF", type=["pdf"])

st.sidebar.markdown("---")
st.sidebar.caption("Tip: paste a job description on the main page and click Analyze.")

# -----------------------------------------------------------------------------
# Main input
# -----------------------------------------------------------------------------
default_job_text = """Data Scientist Intern

Requirements:
- Python
- SQL
- Machine Learning
- Data Visualization
- Tableau

Preferred:
- AWS
- Docker
- LangChain
"""

job_text = st.text_area(
    "Paste Job Description",
    value=default_job_text,
    height=250,
)

run_button = st.button("Analyze Resume", type="primary")

# -----------------------------------------------------------------------------
# Main processing
# -----------------------------------------------------------------------------
if run_button:
    if use_sample_resume:
        if not SAMPLE_RESUME_PATH.exists():
            st.error(f"Sample resume not found at: {SAMPLE_RESUME_PATH}")
            st.stop()
        resume_text = extract_text_from_pdf(str(SAMPLE_RESUME_PATH))
        resume_name = SAMPLE_RESUME_PATH.name
    else:
        if uploaded_resume is None:
            st.error("Please upload a resume PDF or choose the sample resume.")
            st.stop()
        resume_text = extract_text_from_pdf(uploaded_resume.read())
        resume_name = uploaded_resume.name

    if not resume_text.strip():
        st.error("Could not extract text from the resume PDF.")
        st.stop()

    if not job_text.strip():
        st.error("Please paste a job description.")
        st.stop()

    with st.spinner("Analyzing resume and job description..."):
        resume_analysis = analyze_resume(resume_text)
        job_analysis = analyze_job_description(job_text)
        match_result = compare_skills(resume_analysis, job_analysis)

        job_keywords = job_analysis.keywords or (
            job_analysis.required_skills + job_analysis.preferred_skills
        )

        ats_result = calculate_ats_score(
            skill_match_result=match_result,
            resume_text=resume_text,
            job_keywords=job_keywords,
        )

        bullets = extract_bullets_from_text(resume_text, max_bullets=3)

        rewritten = []
        if bullets:
            rewrite_results = rewrite_bullets(
                bullets=bullets,
                resume_skills=resume_analysis.skills,
                job_skills=job_analysis.required_skills + job_analysis.preferred_skills,
                match_score=match_result.match_score,
            )
            rewritten = [item.rewritten_bullet for item in rewrite_results]

    st.session_state["resume_analysis"] = resume_analysis
    st.session_state["job_analysis"] = job_analysis
    st.session_state["match_result"] = match_result
    st.session_state["ats_result"] = ats_result
    st.session_state["original_bullets"] = bullets
    st.session_state["rewritten_bullets"] = rewritten
    st.session_state["resume_name"] = resume_name

# -----------------------------------------------------------------------------
# Results
# -----------------------------------------------------------------------------
if "match_result" in st.session_state:
    resume_analysis = st.session_state["resume_analysis"]
    job_analysis = st.session_state["job_analysis"]
    match_result = st.session_state["match_result"]
    ats_result = st.session_state["ats_result"]
    bullets = st.session_state.get("original_bullets", [])
    rewritten = st.session_state.get("rewritten_bullets", [])
    resume_name = st.session_state.get("resume_name", "resume.pdf")

    col1, col2, col3 = st.columns(3)
    col1.metric("ATS Score", f"{ats_result.overall_score}/100")
    col2.metric("Skill Match", f"{match_result.match_score}/100")
    col3.metric("Missing Skills", str(len(match_result.missing_required_skills)))

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("Resume Analysis")
        st.write(f"**Name:** {resume_analysis.name or 'Not found'}")
        st.write(f"**Headline:** {resume_analysis.headline or 'Not found'}")
        st.write(f"**Email:** {resume_analysis.email or 'Not found'}")
        st.write(f"**Phone:** {resume_analysis.phone or 'Not found'}")
        st.write(f"**Location:** {resume_analysis.location or 'Not found'}")

        display_skill_list("Resume Skills", resume_analysis.skills)
        if resume_analysis.education:
            st.subheader("Education")
            for item in resume_analysis.education:
                st.write(f"- {item}")

    with right:
        st.subheader("Job Analysis")
        st.write(f"**Title:** {job_analysis.title or 'Not found'}")
        st.write(f"**Company:** {job_analysis.company or 'Not found'}")
        st.write(f"**Summary:** {job_analysis.summary or 'Not found'}")

        display_skill_list("Required Skills", job_analysis.required_skills)
        display_skill_list("Preferred Skills", job_analysis.preferred_skills)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Matched Skills")
        if match_result.matched_skills:
            st.write(", ".join(match_result.matched_skills))
        else:
            st.write("None")

        st.subheader("Missing Required Skills")
        if match_result.missing_required_skills:
            st.write(", ".join(match_result.missing_required_skills))
        else:
            st.write("None")

    with col_b:
        st.subheader("ATS Explanation")
        st.write(ats_result.explanation)

        st.subheader("Match Summary")
        st.write(match_result.summary)

    st.markdown("---")
    st.subheader("Bullet Rewrites")

    if bullets and rewritten:
        for i, (orig, rew) in enumerate(zip(bullets, rewritten), start=1):
            with st.expander(f"Rewrite {i}", expanded=(i == 1)):
                st.write("**Original:**")
                st.write(orig)
                st.write("**Rewritten:**")
                st.write(rew)
    else:
        st.write("No bullet-like lines found to rewrite.")

    report_text = build_report_text(
        resume_name=resume_name,
        match_score=match_result.match_score,
        ats_score=ats_result.overall_score,
        matched_skills=match_result.matched_skills,
        missing_skills=match_result.missing_required_skills,
        rewritten_bullets=rewritten,
    )

    st.download_button(
        label="Download Report",
        data=report_text,
        file_name="resume_tailoring_report.txt",
        mime="text/plain",
    )