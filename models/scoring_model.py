"""
Candidate Scoring Model
Uses TF-IDF + cosine similarity + keyword matching for scoring answers
"""

import pandas as pd
import numpy as np
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pickle
import os


class CandidateScoringModel:
    def __init__(self, rubric_path: str):
        with open(rubric_path, "r") as f:
            self.rubric = json.load(f)
        self.vectorizers = {}
        self.scaler = MinMaxScaler()

    def preprocess_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def score_answer_keywords(self, answer: str, keywords: list) -> float:
        answer_lower = answer.lower()
        hits = sum(1 for kw in keywords if kw in answer_lower)
        return min(hits / max(len(keywords) * 0.4, 1), 1.0)

    def score_answer_length(self, answer: str, ideal_length: int) -> float:
        word_count = len(answer.split())
        if word_count >= ideal_length:
            return 1.0
        return min(word_count / ideal_length, 1.0)

    def score_answer_tfidf(self, answer: str, keywords: list, q_id: str) -> float:
        ideal_answer = " ".join(keywords * 3)
        corpus = [self.preprocess_text(ideal_answer), self.preprocess_text(answer)]
        if q_id not in self.vectorizers:
            self.vectorizers[q_id] = TfidfVectorizer(ngram_range=(1, 2))
        try:
            vect = self.vectorizers[q_id]
            tfidf_matrix = vect.fit_transform(corpus)
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except Exception:
            return 0.0

    def score_resume_skills(self, resume_skills: str, position: str) -> dict:
        if position not in self.rubric["positions"]:
            return {"score": 0.0, "matched_required": [], "matched_bonus": []}
        pos_config = self.rubric["positions"][position]
        skills_lower = resume_skills.lower()
        required = pos_config.get("required_skills", [])
        bonus = pos_config.get("bonus_skills", [])
        matched_req = [s for s in required if s in skills_lower]
        matched_bon = [s for s in bonus if s in skills_lower]
        req_score = len(matched_req) / max(len(required), 1)
        bon_score = len(matched_bon) / max(len(bonus), 1) * 0.3
        total = min(req_score * 0.7 + bon_score, 1.0)
        return {
            "score": round(total, 4),
            "matched_required": matched_req,
            "matched_bonus": matched_bon,
        }

    def score_candidate(self, candidate: dict) -> dict:
        position = candidate.get("position", "Software Engineer")
        if position not in self.rubric["positions"]:
            position = "Software Engineer"
        pos_config = self.rubric["positions"][position]
        questions = pos_config["questions"]

        answer_scores = []
        question_details = []
        for q in questions:
            qid = q["id"]
            answer = candidate.get(f"answer_{qid[1:]}", "")
            kw_score = self.score_answer_keywords(answer, q["keywords"])
            len_score = self.score_answer_length(answer, q["ideal_length"])
            tfidf_score = self.score_answer_tfidf(answer, q["keywords"], qid)
            combined = (kw_score * 0.4 + len_score * 0.2 + tfidf_score * 0.4)
            weighted = combined * q["weight"]
            answer_scores.append(weighted)
            question_details.append({
                "question_id": qid,
                "question": q["question"],
                "answer": answer,
                "keyword_score": round(kw_score, 3),
                "length_score": round(len_score, 3),
                "tfidf_score": round(tfidf_score, 3),
                "combined_score": round(combined, 3),
                "weight": q["weight"],
                "weighted_score": round(weighted, 3),
            })

        qa_total = sum(answer_scores) / sum(q["weight"] for q in questions)
        resume_result = self.score_resume_skills(
            candidate.get("resume_skills", ""), position
        )
        exp_score = min(candidate.get("experience_years", 0) / 10.0, 1.0)

        final_score = (qa_total * 0.60 + resume_result["score"] * 0.30 + exp_score * 0.10)
        final_score = round(final_score * 100, 2)

        tier = "Strong Yes" if final_score >= 75 else \
               "Yes" if final_score >= 60 else \
               "Maybe" if final_score >= 45 else "No"

        return {
            "candidate_id": candidate.get("candidate_id"),
            "name": candidate.get("name"),
            "email": candidate.get("email"),
            "position": position,
            "experience_years": candidate.get("experience_years", 0),
            "final_score": final_score,
            "qa_score": round(qa_total * 100, 2),
            "resume_score": round(resume_result["score"] * 100, 2),
            "experience_score": round(exp_score * 100, 2),
            "tier": tier,
            "matched_required_skills": resume_result["matched_required"],
            "matched_bonus_skills": resume_result["matched_bonus"],
            "question_details": question_details,
            "reviewer_notes": candidate.get("reviewer_notes", ""),
            "shortlisted": final_score >= 60,
        }

    def score_all_candidates(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []
        for _, row in df.iterrows():
            result = self.score_candidate(row.to_dict())
            results.append(result)
        results_df = pd.DataFrame([{
            k: v for k, v in r.items() if k != "question_details"
        } for r in results])
        results_df = results_df.sort_values("final_score", ascending=False).reset_index(drop=True)
        results_df["rank"] = results_df.index + 1
        return results_df, results

    def get_model_metrics(self, df: pd.DataFrame) -> dict:
        scored_df, _ = self.score_all_candidates(df)
        return {
            "total_candidates": len(scored_df),
            "shortlisted": int(scored_df["shortlisted"].sum()),
            "avg_score": round(scored_df["final_score"].mean(), 2),
            "max_score": round(scored_df["final_score"].max(), 2),
            "min_score": round(scored_df["final_score"].min(), 2),
            "tier_distribution": scored_df["tier"].value_counts().to_dict(),
        }
