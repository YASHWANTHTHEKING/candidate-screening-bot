# 🤖 Candidate Q&A Screening Bot — PRJ-110

**Student:** Yashwanth N.V PSVPEC | **Reg No:** 411723104058  
**Category:** Recruitment Screening Tools | **Domain:** HR | **Focus:** AI/ML

---

## 📌 Project Description
An AI-powered candidate screening system that collects short written answers from candidates, scores them using NLP + ML techniques (TF-IDF, cosine similarity, keyword matching), and ranks candidates by fit for a given position.

---

## 🏗️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI |
| ML/Scoring | Scikit-learn, Pandas |
| Frontend | Streamlit |
| Visualizations | Plotly |

---

## ✅ Required Features Implemented
- [x] **Resume Parsing** — Skills extracted and matched against required/bonus skill sets
- [x] **Scoring Criteria** — Multi-factor scoring: Q&A (60%), Resume Skills (30%), Experience (10%)
- [x] **Shortlist Dashboard** — Visual dashboard with metrics, charts, and tier breakdown
- [x] **Reviewer Notes** — Reviewers can add/edit notes per candidate
- [x] **Exportable Ranking** — Download CSV of all ranked candidates

---

## 📁 Project Structure
```
candidate-screening-bot/
├── backend/
│   └── main.py              # FastAPI REST API
├── frontend/
│   └── app.py               # Streamlit dashboard
├── models/
│   └── scoring_model.py     # ML scoring logic
├── data/
│   ├── candidates.csv       # Sample dataset (8 candidates)
│   └── scoring_rubric.json  # Scoring weights & keyword rubric
├── tests/
│   └── test_scoring.py      # 12 unit test cases
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/candidate-screening-bot
cd candidate-screening-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI backend
```bash
uvicorn backend.main:app --reload --port 8000
```
API docs available at: `http://localhost:8000/docs`

### 4. Run the Streamlit dashboard
```bash
streamlit run frontend/app.py
```
Dashboard opens at: `http://localhost:8501`

### 5. Run tests
```bash
python tests/test_scoring.py
```

---

## 🤖 How the Scoring Works

### Score Breakdown
| Component | Weight | Method |
|-----------|--------|--------|
| Q&A Answers | 60% | TF-IDF + Keyword Matching + Length |
| Resume Skills | 30% | Required/Bonus skill matching |
| Experience | 10% | Normalized years of experience |

### Tier Classification
| Score | Tier |
|-------|------|
| ≥ 75% | 🟢 Strong Yes |
| ≥ 60% | 🔵 Yes |
| ≥ 45% | 🟡 Maybe |
| < 45% | 🔴 No |

### Answer Scoring (per question)
- **Keyword Score (40%):** How many relevant keywords appear in the answer
- **TF-IDF Score (40%):** Cosine similarity with ideal answer vector
- **Length Score (20%):** Whether answer meets the expected depth

---

## 📊 Dashboard Pages
1. **Dashboard** — KPIs, score distribution histogram, tier pie chart, per-candidate bar chart
2. **All Candidates** — Filterable, sortable table of all candidates
3. **Shortlist** — Shortlisted candidates with expandable detail + reviewer notes
4. **Candidate Detail** — Full question breakdown + radar chart
5. **New Candidate** — Score any candidate via web form
6. **Export** — Download rankings CSV / upload new CSV

---

## 🔌 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/candidates` | All candidates with scores |
| GET | `/candidates/{id}` | Single candidate detail |
| POST | `/candidates/score` | Score a new candidate |
| GET | `/shortlist` | Shortlisted candidates only |
| GET | `/dashboard/metrics` | Summary metrics |
| GET | `/export/csv` | Export rankings as CSV |
| PUT | `/candidates/notes` | Update reviewer notes |

---

## 🧪 Test Cases (12 total — all passing)
| TC | Test | Result |
|----|------|--------|
| TC-01 | Score in valid range (0–100) | ✅ PASS |
| TC-02 | Strong candidate gets high score | ✅ PASS |
| TC-03 | Weak candidate scores lower than strong | ✅ PASS |
| TC-04 | Shortlisted flag correct | ✅ PASS |
| TC-05 | Tier assignment valid | ✅ PASS |
| TC-06 | Resume skills matching works | ✅ PASS |
| TC-07 | Empty answers handled without crash | ✅ PASS |
| TC-08 | Data Scientist position scoring | ✅ PASS |
| TC-09 | Batch scoring all candidates | ✅ PASS |
| TC-10 | Metrics generation complete | ✅ PASS |
| TC-11 | High experience capped at 100% | ✅ PASS |
| TC-12 | Question details returned in output | ✅ PASS |

---

## 📸 Screenshots
*(Add screenshots of dashboard, shortlist, candidate detail view)*

---

## 🔗 Resources Used
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- Scikit-learn: https://scikit-learn.org/stable/getting_started.html
- Pandas: https://pandas.pydata.org/docs/user_guide/index.html
- Streamlit: https://docs.streamlit.io/get-started
