"""
Database models and operations for Candidate Screening Bot
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re

# Fallback to local SQLite for development
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/candidates.db")

# SQLAlchemy requires 'postgresql://' instead of 'postgres://' (often provided by Render/Heroku)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite-specific connection arguments
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String)
    position = Column(String)
    experience_years = Column(Integer)
    answer_1 = Column(Text)
    answer_2 = Column(Text)
    answer_3 = Column(Text)
    answer_4 = Column(Text)
    answer_5 = Column(Text)
    resume_skills = Column(Text)
    resume_text = Column(Text)  # Extracted from PDF
    reviewer_notes = Column(Text, default="")

def init_db():
    os.makedirs(os.path.dirname("./data/candidates.db"), exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_candidates_df():
    db = get_db()
    candidates = db.query(Candidate).all()
    data = [{
        "candidate_id": c.candidate_id,
        "name": c.name,
        "email": c.email,
        "position": c.position,
        "experience_years": c.experience_years,
        "answer_1": c.answer_1,
        "answer_2": c.answer_2,
        "answer_3": c.answer_3,
        "answer_4": c.answer_4,
        "answer_5": c.answer_5,
        "resume_skills": c.resume_skills,
        "reviewer_notes": c.reviewer_notes,
    } for c in candidates]
    import pandas as pd
    return pd.DataFrame(data)

def add_candidate(candidate_data):
    db = get_db()
    candidate = Candidate(**candidate_data)
    db.add(candidate)
    try:
        db.commit()
        db.refresh(candidate)
        return candidate
    except IntegrityError:
        db.rollback()
        raise

def update_notes(candidate_id, notes):
    db = get_db()
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if candidate:
        candidate.reviewer_notes = notes
        db.commit()
        return True
    return False