# Employability AI Tool

> AI-powered student employability assessment platform — no paid API keys needed. Runs fully offline.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What It Does

Students complete assessments, upload a resume, and do a mock video interview.  
The platform computes a weighted **Employability Score (0–100)** + **Placement Probability (%)**  
with top role recommendations and skill gap analysis — all in one scorecard.

---

## Features

| Feature | Description |
|---|---|
| Technical Test | MCQ · 10 questions · 5 role variants (Python / Web / Data / Java / DevOps) |
| Cognitive Test | MCQ · aptitude, reasoning, number series, analogies |
| Communication Test | MCQ · email etiquette, active listening, professional tone |
| Psychometric (Big-5) | 50-question OCEAN personality inventory · Likert 1–5 scale |
| Resume Analyzer | Upload `.txt` resume → skill extraction, role match, gap analysis |
| Video Interview | AI questions + eye-contact simulation + pacing evaluation |
| Scorecard | Radar chart + bar chart + placement % + top roles + skill gaps |
| Student Profile | Email-hash Student ID · name · CGPA · test history |

---

## Scoring System

| Component | Weight | Source |
|---|---|---|
| Technical Skills | **30%** | MCQ auto-graded |
| Cognitive Ability | **20%** | MCQ auto-graded |
| Resume / NLP | **20%** | File upload analysis |
| Video AI | **15%** | Eye-contact + pacing + completion |
| Behavioural (Big-5) | **15%** | Psychometric questionnaire |
Employability Score  =  Σ (component_score × weight)
Placement Probability = score × 0.78 + (cgpa − 6.0) × 6.0 − 5.0
**Video Interview sub-scores:**

| Factor | Points |
|---|---|
| Eye contact ratio | 50 pts |
| Questions completed | 25 pts |
| Pacing (ideal: 2–6 min) | 25 pts |

---

## 🏗️ Architecture
React 19 (port 3000)
↓  Axios proxy
FastAPI (port 8000)
↓
Services: psychometric · interview · scorecard · resume · repository
↓
SQLite (demo) / PostgreSQL (production) + JSON fallback
**Key design decisions:**
- **Demo-first** — works with zero setup using `data/demo_store.json`
- **Fallback layer** — `repository.py` auto-falls back to JSON if DB is unreachable
- **Optional ML** — `scikit-learn` imports wrapped in `try/except`; app never crashes without it
- **Stateless API** — no cookies; React stores `student_id` in `localStorage`

---

## Project Structure
employability_ai_tool/
├── backend/
│   ├── api/main.py              # All 20+ FastAPI endpoints
│   ├── models/db.py             # SQLAlchemy: Student, ScoreSnapshot, AssessmentAttempt
│   └── services/
│       ├── psychometric.py      # Big-5 OCEAN engine (50 questions, reverse scoring)
│       ├── interview_engine.py  # Question generation + video score algorithm
│       ├── scorecard_service.py # Weighted score + placement % formula
│       ├── repository.py        # DB read/write with JSON fallback
│       └── demo_store.py        # Offline JSON persistence layer
├── frontend/
│   └── src/pages/
│       ├── Login.js             # Email-hash ID, no password
│       ├── Dashboard.js         # Score cards + quick links
│       ├── MyTests.js           # Test catalog + history table
│       ├── TestRunner.js        # MCQ radio / Likert scale UI
│       ├── Resume.js            # Upload + role selector + results
│       ├── Scorecard.js         # Radar + bar charts + placement %
│       └── VideoInterview.js    # Mock interview + feedback
├── data/
│   ├── schemas.py               # Pydantic models
│   ├── generate_dataset.py      # Synthetic data generator
│   └── students_enhanced.csv    # 1000+ sample student records
└── ml/                          # Optional scikit-learn predictor
---

## Quick Start

### Backend
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic
pip install scikit-learn joblib   # optional
cd backend/api
uvicorn main:app --reload --port 8000
```
Swagger docs → `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm start
```
App → `http://localhost:3000`

### Demo Login
Name: Ravi Kumar  |  Email: ravi@example.com  |  CGPA: 8.1
---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/student/upsert` | Create / update student profile |
| GET | `/api/tests` | List all assessments |
| GET | `/api/tests/{id}/questions` | Fetch questions (`?variant=python`) |
| POST | `/api/tests/submit` | Submit answers → get score |
| GET | `/api/tests/history/{student_id}` | Past attempts |
| POST | `/api/resume/analyze` | Upload resume → analysis |
| GET | `/api/scorecard/{student_id}` | Full weighted scorecard |
| POST | `/api/interview/start` | Generate interview questions |
| POST | `/api/interview/submit` | Submit session → score + feedback |
| POST | `/api/model/train` | Train ML predictor |
| GET | `/health` | Engine status check |

---

## Database Models

| Table | Purpose |
|---|---|
| `Student` | Profile: email-hash ID, name, email, CGPA |
| `ScoreSnapshot` | Latest score for each of 5 components |
| `AssessmentAttempt` | Full attempt history with raw JSON per submission |

> Set `DATABASE_URL` env variable to switch from SQLite → PostgreSQL. Tables auto-create on startup.

---

## Big-5 Psychometric (OCEAN)

| Trait | Measures |
|---|---|
| Openness | Curiosity, creativity, intellect |
| Conscientiousness | Organisation, discipline, reliability |
| Extraversion | Social energy, assertiveness |
| Agreeableness | Empathy, cooperation, trust |
| Neuroticism | Emotional stability, stress tolerance |

50 questions · 10 per trait · 1–5 Likert scale · reverse-scored items included

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/app.db` | Override for PostgreSQL |

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/employability_db"
```

---

## .gitignore

```gitignore
__pycache__/
*.pyc
venv/
.env
*.pkl
*.joblib
data/app.db
data/demo_store.json
data/students_enhanced*.csv
frontend/node_modules/
frontend/build/
.DS_Store
```

> Remove already committed pkl: `git rm --cached placement_predictor.pkl && git commit -m "remove pkl"`

---

## Contributing

Fork → branch → commit → PR  
**Ideas:** PDF/DOCX resume parsing · real webcam eye-tracking · admin dashboard · JWT auth · larger question banks

---

## License

[MIT](LICENSE) · Built with FastAPI · React 19 · SQLAlchemy · Big-5 OCEAN · scikit-learn
