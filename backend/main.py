"""
FastAPI Backend for Candidate Q&A Screening Bot
PRJ-110 | Yashwanth N.V PSVPEC
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import pandas as pd
import json
import io
import sys
import os
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.scoring_model import CandidateScoringModel
from backend.database import init_db, get_candidates_df, add_candidate, update_notes
from backend.pdf_processor import extract_text_from_pdf, extract_resume_data

app = FastAPI(
    title="Candidate Q&A Screening Bot API",
    description="AI-powered candidate screening and ranking system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RUBRIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scoring_rubric.json")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

model = CandidateScoringModel(RUBRIC_PATH)


class CandidateInput(BaseModel):
    candidate_id: str
    name: str
    email: str
    position: str
    experience_years: int
    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str
    answer_5: str
    resume_skills: str
    reviewer_notes: Optional[str] = ""


class ReviewerNoteUpdate(BaseModel):
    candidate_id: str
    notes: str


@app.get("/")
def root():
    return {"message": "Candidate Screening Bot API is running!", "version": "1.0.0"}


@app.get("/candidates")
def get_all_candidates():
    """Get all candidates with their scores"""
    df = get_candidates_df()
    scored_df, _ = model.score_all_candidates(df)
    return {"candidates": scored_df.to_dict(orient="records")}


@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    """Get detailed score for a specific candidate"""
    df = get_candidates_df()
    row = df[df["candidate_id"] == candidate_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    result = model.score_candidate(row.iloc[0].to_dict())
    return result


@app.post("/candidates/score")
def score_new_candidate(candidate: CandidateInput):
    """Score a new candidate"""
    result = model.score_candidate(candidate.dict())
    return result


@app.get("/dashboard/metrics")
def get_metrics():
    """Get overall screening metrics"""
    df = get_candidates_df()
    metrics = model.get_model_metrics(df)
    return metrics


@app.get("/shortlist")
def get_shortlist():
    """Get shortlisted candidates only"""
    df = get_candidates_df()
    scored_df, _ = model.score_all_candidates(df)
    shortlisted = scored_df[scored_df["shortlisted"] == True]
    return {"shortlisted_candidates": shortlisted.to_dict(orient="records")}


@app.get("/export/csv")
def export_rankings():
    """Export candidate rankings as CSV string"""
    df = get_candidates_df()
    scored_df, _ = model.score_all_candidates(df)
    export_cols = [
        "rank", "candidate_id", "name", "email", "position",
        "experience_years", "final_score", "qa_score",
        "resume_score", "tier", "shortlisted", "reviewer_notes"
    ]
    export_df = scored_df[export_cols]
    output = io.StringIO()
    export_df.to_csv(output, index=False)
    return {"csv_data": output.getvalue(), "total": len(export_df)}


@app.post("/candidates/upload")
async def upload_candidates(file: UploadFile = File(...)):
    """Upload CSV of candidates and score them all"""
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    for _, row in df.iterrows():
        candidate_data = row.to_dict()
        add_candidate(candidate_data)
    scored_df, _ = model.score_all_candidates(df)
    return {"total": len(scored_df), "candidates": scored_df.to_dict(orient="records")}


@app.put("/candidates/notes")
def update_reviewer_notes(update: ReviewerNoteUpdate):
    """Update reviewer notes for a candidate"""
    success = update_notes(update.candidate_id, update.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Notes updated successfully", "candidate_id": update.candidate_id}


@app.post("/candidates/upload-pdf")
async def upload_resume_pdf(
    candidate_id: str = Form(...),
    name: str = Form(""),
    email: str = Form(""),
    position: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload PDF resume, extract data, and add candidate"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()
    try:
        text = extract_text_from_pdf(contents)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse PDF: {exc}")

    if not text:
        raise HTTPException(status_code=400, detail="No text could be extracted from the uploaded PDF.")

    extracted_data = extract_resume_data(text)

    candidate_data = {
        "candidate_id": candidate_id,
        "name": name or extracted_data.get("name", ""),
        "email": email or extracted_data.get("email", ""),
        "position": position,
        "experience_years": extracted_data.get("experience_years", 0),
        "answer_1": "",
        "answer_2": "",
        "answer_3": "",
        "answer_4": "",
        "answer_5": "",
        "resume_skills": extracted_data.get("resume_skills", ""),
        "resume_text": text,
        "reviewer_notes": "",
    }

    try:
        add_candidate(candidate_data)
    except Exception as exc:
        if "UNIQUE constraint" in str(exc) or "IntegrityError" in type(exc).__name__:
            raise HTTPException(status_code=400, detail="Candidate ID already exists")
        raise HTTPException(status_code=500, detail="Failed to save candidate data")

    return {"message": "Candidate added from PDF", "candidate": candidate_data}


@app.get("/rubric")
def get_rubric():
    """Get the scoring rubric"""
    with open(RUBRIC_PATH, "r") as f:
        rubric = json.load(f)
    return rubric


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)