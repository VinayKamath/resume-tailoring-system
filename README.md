# 🚀 Multi-Agent Resume Tailoring System

An AI-powered resume optimization platform that analyzes resumes against job descriptions, calculates ATS compatibility scores, identifies skill gaps, and generates tailored resume improvements using **Groq LLMs**, **LangChain**, **ChromaDB**, and **Streamlit**.

---

## 📌 Overview

This application helps job seekers tailor their resumes to specific job descriptions by:

* Extracting information from PDF resumes
* Analyzing job requirements
* Comparing candidate skills against role requirements
* Calculating ATS-style match scores
* Identifying missing skills and keywords
* Generating AI-powered resume bullet rewrites

---

## ✨ Features

| Feature                | Description                                                    |
| ---------------------- | -------------------------------------------------------------- |
| 📄 Resume Parsing      | Extracts structured information from PDF resumes               |
| 🎯 Job Analysis        | Identifies required and preferred skills from job descriptions |
| 📊 ATS Scoring         | Calculates candidate-job fit scores                            |
| 🔍 Skill Gap Detection | Highlights missing and matched skills                          |
| 🤖 AI Bullet Rewriting | Generates ATS-friendly resume bullet improvements              |
| 🧠 RAG Pipeline        | Retrieves relevant ATS keywords and templates using ChromaDB   |
| 🌐 Streamlit UI        | Interactive web application for resume analysis                |
| 🐳 Docker Support      | Containerized deployment                                       |

---

## 🏗️ System Architecture

```text
Resume PDF
    │
    ▼
PDF Parser
    │
    ▼
Resume Analyzer Agent
    │
    ▼
Job Analyzer Agent
    │
    ▼
Skill Matcher Agent
    │
    ▼
ATS Scoring Engine
    │
    ▼
Bullet Rewriter Agent
    │
    ▼
Streamlit Dashboard
```

---

## 🛠️ Tech Stack

| Category               | Technologies         |
| ---------------------- | -------------------- |
| LLM                    | Groq (Llama 3.3 70B) |
| AI Framework           | LangChain            |
| Vector Database        | ChromaDB             |
| Frontend               | Streamlit            |
| PDF Processing         | PyPDF                |
| Data Processing        | Pandas, NumPy        |
| Containerization       | Docker               |
| Environment Management | Python Dotenv        |

---

## 📂 Project Structure

```text
resume-tailoring-system/

├── app.py
├── requirements.txt
├── Dockerfile
├── README.md

├── data/
│   ├── ats_keywords.txt
│   ├── resume_templates.txt
│   └── action_verbs.txt

├── agents/
│   ├── resume_analyzer.py
│   ├── job_analyzer.py
│   ├── skill_matcher.py
│   └── bullet_rewriter.py

├── utils/
│   ├── pdf_parser.py
│   ├── chroma_db.py
│   └── ats_score.py
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/VinayKamath/resume-tailoring-system.git

cd resume-tailoring-system
```

### 2. Create Virtual Environment

Using UV:

```bash
uv venv
```

Activate:

#### Windows

```powershell
.venv\Scripts\activate
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv add -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

or

```bash
uv run streamlit run app.py
```

Application URL:

```text
http://localhost:8501
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t resume-system-app .
```

### Run Container

```bash
docker run --rm -p 8501:8501 --env-file .env resume-system-app
```

---

## 📈 ATS Analysis Workflow

| Step | Component       | Output                        |
| ---- | --------------- | ----------------------------- |
| 1    | PDF Parser      | Resume Text                   |
| 2    | Resume Analyzer | Candidate Skills & Experience |
| 3    | Job Analyzer    | Job Requirements              |
| 4    | Skill Matcher   | Matched & Missing Skills      |
| 5    | ATS Scorer      | ATS Compatibility Score       |
| 6    | Bullet Rewriter | Optimized Resume Bullets      |

---

## 📊 Example Output

### ATS Score

| Metric            | Score  |
| ----------------- | ------ |
| ATS Compatibility | 82/100 |
| Skill Match       | 85/100 |
| Keyword Coverage  | 78/100 |

### Skill Analysis

| Matched Skills | Missing Skills |
| -------------- | -------------- |
| Python         | Tableau        |
| SQL            | Power BI       |
| Docker         | Spark          |
| AWS            | Azure          |

---

## 🎯 Key Resume Highlights

* Built a multi-agent resume optimization platform using **LangChain**, **Groq LLMs**, **ChromaDB**, and **Streamlit** to analyze resumes against job descriptions and identify ATS optimization opportunities.
* Engineered a **Retrieval-Augmented Generation (RAG)** pipeline indexing ATS keywords, resume templates, and action verbs to provide context-aware resume recommendations.
* Developed an ATS scoring engine combining skill matching, keyword coverage, and resume-quality heuristics to evaluate candidate-job fit and identify skill gaps.
* Designed and deployed an interactive Streamlit application supporting PDF ingestion, job description analysis, real-time ATS scoring, and AI-powered bullet rewrites.

---

## 🚀 Future Enhancements

* Semantic skill matching using embeddings
* Multi-resume batch processing
* Resume version comparison
* LinkedIn profile integration
* Advanced ATS scoring models
* Support for DOCX resumes
* Resume export functionality

---

## 📄 License

MIT License

---

## 👤 Author

**Vinay Kamath**

* GitHub: https://github.com/VinayKamath
* LinkedIn: https://linkedin.com/in/vinaykamath18
