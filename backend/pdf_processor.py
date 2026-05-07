"""
PDF processing utilities
"""

import io
import pdfplumber
import re
from typing import Dict


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\(cid:\d+\)", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def extract_page_text(page) -> str:
    text = page.extract_text()
    if text:
        return text

    words = page.extract_words()
    if words:
        words_sorted = sorted(words, key=lambda x: (x["top"], x["x0"]))
        return " ".join(word["text"] for word in words_sorted)

    return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_texts = []
        for page in pdf.pages:
            page_text = extract_page_text(page)
            if page_text:
                page_texts.append(page_text)
    return normalize_text("\n".join(page_texts))


def extract_resume_data(text: str) -> Dict[str, str]:
    """Simple extraction of resume data from text"""
    name_pattern = r"(?:Name|Candidate Name|Applicant Name)[:\s]*([A-Za-z ,.'\-]+)"
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    experience_pattern = r"(\d+)\s*(?:years?|yrs?)\b"
    skills_pattern = r"Skills?[:\s]*([A-Za-z0-9,\-\+\./ ]+)"

    lines = [line.strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
    name = ""
    email = ""
    experience_years = 0
    resume_skills = ""

    for line in lines:
        if not name:
            match = re.search(name_pattern, line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
        if not email:
            match = re.search(email_pattern, line)
            if match:
                email = match.group(0)
        if experience_years == 0:
            match = re.search(experience_pattern, line, re.IGNORECASE)
            if match:
                experience_years = int(match.group(1))
        if not resume_skills:
            match = re.search(skills_pattern, line, re.IGNORECASE)
            if match:
                resume_skills = match.group(1).strip()

    if not name and lines:
        first_line = lines[0]
        if not re.search(email_pattern, first_line) and len(first_line.split()) <= 6:
            name = first_line

    if not resume_skills:
        match = re.search(skills_pattern, text, re.IGNORECASE)
        if match:
            resume_skills = match.group(1).strip()

    return {
        "name": name,
        "email": email,
        "experience_years": experience_years,
        "resume_skills": resume_skills,
        "resume_text": text,
    }