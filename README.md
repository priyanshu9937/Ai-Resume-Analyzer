# 🤖 AI Resume Analyzer

**AI Resume Analyzer** is an intelligent resume analysis platform that uses **Artificial Intelligence and Generative AI** to analyze resumes, identify strengths and weaknesses, evaluate job relevance, and provide actionable suggestions for improvement.

The system is designed to help students, freshers, and job seekers create **ATS-friendly, professional, and job-specific resumes**. Instead of manually reviewing every section, users can upload their resume and receive an AI-powered analysis within seconds.

## 🚀 Key Features

* 📄 **Resume Upload & Parsing** — Extracts useful information from PDF resumes.
* 🤖 **AI-Powered Analysis** — Uses Generative AI to understand resume content and structure.
* 🎯 **Job Description Matching** — Compares the resume with a given job description.
* 📊 **ATS Analysis** — Identifies potential ATS-related issues and missing keywords.
* 🔍 **Skill Gap Detection** — Finds missing or weak technical and soft skills.
* 💡 **AI Recommendations** — Provides suggestions to improve resume content.
* 📝 **Section-wise Analysis** — Reviews sections such as Summary, Skills, Education, Experience, and Projects.
* 🎯 **Keyword Optimization** — Suggests relevant keywords based on the target role.
* 📈 **Resume Score** — Generates an overall analysis score based on multiple factors.
* ⚡ **Fast & User-Friendly Interface** — Simple workflow for uploading and analyzing resumes.

## 🛠️ Tech Stack

**Backend:** Python, FastAPI
**AI/GenAI:** Google Gemini API
**Document Processing:** PyMuPDF
**Frontend:** Streamlit
**Database:** SQLite/PostgreSQL
**API:** REST API
**Environment:** Python 3.12+

## 🔄 How It Works

```text
Upload Resume
      ↓
PDF Text Extraction
      ↓
Resume Content Processing
      ↓
AI/GenAI Analysis
      ↓
ATS & Job Description Matching
      ↓
Skill Gap Detection
      ↓
AI Recommendations
      ↓
Detailed Resume Report
```

## 🎯 Project Objective

The main objective of this project is to build an AI-based career assistant that helps candidates understand **how effectively their resume represents their skills and experience for a target job role**.

This project demonstrates practical implementation of **Python development, REST APIs, Generative AI, document processing, prompt engineering, and AI-based text analysis**.

## 🔮 Future Enhancements

* AI-generated resume improvement
* Multiple resume templates
* LinkedIn profile analysis
* Job recommendation system
* Interview question generation
* Resume-to-job semantic matching using embeddings
* Personalized career roadmap

## Deploy on Render

The repository includes a Render Blueprint in `render.yaml`. It creates a Python web service, a private PostgreSQL database, and a persistent disk for uploaded resumes. The web service and disk use a paid Render plan; review the current pricing in Render before creating the Blueprint. The disk keeps uploads across restarts but limits the service to one instance. For horizontal scaling, replace local file storage with an object store such as S3 or Cloudflare R2 before removing the disk.

1. Push the project to GitHub and sign in to the [Render Dashboard](https://dashboard.render.com/).
2. Choose **New +** → **Blueprint**, connect the GitHub repository, and select the `main` branch.
3. Review the resources and costs shown from `render.yaml`, then create the Blueprint. Render generates `API_ACCESS_TOKEN` and privately connects the service to PostgreSQL.
4. When the deploy finishes, open the service's `onrender.com` URL. In the app sidebar, open **Access key** and paste the value of `API_ACCESS_TOKEN` from the web service's Render environment settings.
5. Gemini is optional. To enable AI-generated analysis, add `GEMINI_API_KEY` in the service's Render environment settings and redeploy. Without it, analysis uses the built-in local fallback.

Render's health check uses `/health`. The Blueprint sets `ENVIRONMENT=production`, so missing or weak API tokens prevent startup. Do not put the generated token or Gemini key in GitHub, `render.yaml`, or frontend code.

**AI Resume Analyzer — Analyze your resume. Identify the gaps. Improve your chances. 🚀**
