"""
Streamlit Frontend for Candidate Q&A Screening Bot
PRJ-110 | Yashwanth N.V PSVPEC
"""

import streamlit as st
import requests
import os
import pandas as pd

# ── Backend API Base URL ───────────────────────────────────────────────
# Use environment variable for flexibility (dev/staging/prod)
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

# ── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Candidate Screening Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helper Functions to Call Backend ───────────────────────────────────
def get_all_candidates():
    response = requests.get(f"{API_BASE}/candidates")
    return response.json()

def get_candidate(candidate_id: str):
    response = requests.get(f"{API_BASE}/candidates/{candidate_id}")
    return response.json()

def score_candidate(candidate_data: dict):
    response = requests.post(f"{API_BASE}/candidates/score", json=candidate_data)
    return response.json()

def upload_resume_pdf(candidate_id: str, position: str, pdf_file, name="", email=""):
    files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
    data = {
        "candidate_id": candidate_id,
        "name": name,
        "email": email,
        "position": position,
    }
    response = requests.post(f"{API_BASE}/candidates/upload-pdf", data=data, files=files)
    return response.json()

def update_notes(candidate_id: str, notes: str):
    payload = {"candidate_id": candidate_id, "notes": notes}
    response = requests.put(f"{API_BASE}/candidates/notes", json=payload)
    return response.json()

def get_rubric():
    response = requests.get(f"{API_BASE}/rubric")
    return response.json()

# ── Sidebar Navigation ────────────────────────────────────────────────
page = st.sidebar.radio("Go to", [
    "📊 Dashboard",
    "👥 All Candidates",
    "⭐ Shortlist",
    "🔍 Candidate Detail",
    "➕ New Candidate",
])

# ── Pages ─────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Candidate Screening Dashboard")
    data = get_all_candidates()
    df = pd.DataFrame(data["candidates"])
    st.metric("Total Candidates", len(df))
    st.dataframe(df)

elif page == "👥 All Candidates":
    st.title("👥 All Candidates")
    data = get_all_candidates()
    df = pd.DataFrame(data["candidates"])
    st.dataframe(df)

elif page == "⭐ Shortlist":
    st.title("⭐ Shortlisted Candidates")
    response = requests.get(f"{API_BASE}/shortlist")
    df = pd.DataFrame(response.json()["shortlisted_candidates"])
    st.dataframe(df)

elif page == "🔍 Candidate Detail":
    st.title("🔍 Candidate Detail")
    candidate_id = st.text_input("Enter Candidate ID")
    if candidate_id:
        result = get_candidate(candidate_id)
        st.json(result)

elif page == "➕ New Candidate":
    st.title("➕ Add New Candidate")
    tab_manual, tab_pdf = st.tabs(["Manual Entry", "Upload Resume PDF"])

    with tab_manual:
        cid = st.text_input("Candidate ID")
        name = st.text_input("Name")
        email = st.text_input("Email")
        position = st.text_input("Position")
        exp = st.number_input("Experience (years)", 0, 30, 1)
        skills = st.text_input("Resume Skills")
        answers = [st.text_area(f"Answer {i}") for i in range(1, 6)]
        if st.button("Score Candidate"):
            candidate_data = {
                "candidate_id": cid,
                "name": name,
                "email": email,
                "position": position,
                "experience_years": exp,
                "resume_skills": skills,
                "answer_1": answers[0],
                "answer_2": answers[1],
                "answer_3": answers[2],
                "answer_4": answers[3],
                "answer_5": answers[4],
            }
            result = score_candidate(candidate_data)
            st.success(f"Final Score: {result['final_score']}% — Tier: {result['tier']}")
            st.json(result)

    with tab_pdf:
        pdf_id = st.text_input("Candidate ID (PDF)")
        pdf_position = st.text_input("Position (PDF)")
        uploaded_file = st.file_uploader("Upload Resume PDF", type="pdf")
        if st.button("Upload PDF Candidate"):
            if uploaded_file and pdf_id:
                result = upload_resume_pdf(pdf_id, pdf_position, uploaded_file)
                st.success("Candidate added from PDF")
                st.json(result)
