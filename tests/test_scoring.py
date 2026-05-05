"""
Test Cases - Candidate Q&A Screening Bot
PRJ-110 | Yashwanth N.V PSVPEC
Run: python tests/test_scoring.py
"""

import sys
import os
import unittest
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.scoring_model import CandidateScoringModel

RUBRIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scoring_rubric.json")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "candidates.csv")


class TestScoringModel(unittest.TestCase):

    def setUp(self):
        self.model = CandidateScoringModel(RUBRIC_PATH)
        self.sample_candidate = {
            "candidate_id": "TEST001",
            "name": "Test User",
            "email": "test@test.com",
            "position": "Software Engineer",
            "experience_years": 5,
            "answer_1": "I have 5 years of Python experience building REST APIs with FastAPI and Django.",
            "answer_2": "I debug by isolating the issue using logs and systematic reproduction, then implement a fix.",
            "answer_3": "I prioritize tasks by urgency and impact, using Kanban boards and daily standups.",
            "answer_4": "I improved query performance by 60% using proper indexing and query optimization.",
            "answer_5": "I collaborate through pair programming, code reviews, and knowledge sharing sessions.",
            "resume_skills": "Python, FastAPI, Django, PostgreSQL, Docker, Git, REST API, SQL",
            "reviewer_notes": "",
        }

    # ── TC-01: Score is within valid range ──
    def test_score_in_valid_range(self):
        result = self.model.score_candidate(self.sample_candidate)
        self.assertGreaterEqual(result["final_score"], 0)
        self.assertLessEqual(result["final_score"], 100)
        print(f"TC-01 PASS | Score: {result['final_score']}")

    # ── TC-02: Strong candidate gets high score ──
    def test_strong_candidate_high_score(self):
        result = self.model.score_candidate(self.sample_candidate)
        self.assertGreater(result["final_score"], 55)
        print(f"TC-02 PASS | Strong candidate score: {result['final_score']}")

    # ── TC-03: Weak candidate gets lower score ──
    def test_weak_candidate_lower_score(self):
        weak = {
            **self.sample_candidate,
            "candidate_id": "TEST002",
            "answer_1": "I know python a little.",
            "answer_2": "I search online when there are bugs.",
            "answer_3": "I make lists.",
            "answer_4": "I haven't done much optimization.",
            "answer_5": "I can work in teams.",
            "resume_skills": "Python, HTML",
            "experience_years": 0,
        }
        weak_result = self.model.score_candidate(weak)
        strong_result = self.model.score_candidate(self.sample_candidate)
        self.assertLess(weak_result["final_score"], strong_result["final_score"])
        print(f"TC-03 PASS | Weak: {weak_result['final_score']} < Strong: {strong_result['final_score']}")

    # ── TC-04: Shortlisted flag correct ──
    def test_shortlisted_flag(self):
        result = self.model.score_candidate(self.sample_candidate)
        expected_shortlisted = result["final_score"] >= 60
        self.assertEqual(result["shortlisted"], expected_shortlisted)
        print(f"TC-04 PASS | Shortlisted: {result['shortlisted']} | Score: {result['final_score']}")

    # ── TC-05: Tier assignment correct ──
    def test_tier_assignment(self):
        result = self.model.score_candidate(self.sample_candidate)
        valid_tiers = ["Strong Yes", "Yes", "Maybe", "No"]
        self.assertIn(result["tier"], valid_tiers)
        print(f"TC-05 PASS | Tier: {result['tier']}")

    # ── TC-06: Resume skills matching ──
    def test_resume_skills_matching(self):
        candidate = {**self.sample_candidate, "resume_skills": "Python, FastAPI, SQL, Docker, Git"}
        result = self.model.score_candidate(candidate)
        self.assertGreater(result["resume_score"], 0)
        print(f"TC-06 PASS | Resume score: {result['resume_score']}")

    # ── TC-07: Empty answers handled without crash ──
    def test_empty_answers_handled(self):
        empty_candidate = {
            **self.sample_candidate,
            "answer_1": "", "answer_2": "", "answer_3": "",
            "answer_4": "", "answer_5": "",
        }
        try:
            result = self.model.score_candidate(empty_candidate)
            self.assertGreaterEqual(result["final_score"], 0)
            print(f"TC-07 PASS | Empty answers handled. Score: {result['final_score']}")
        except Exception as e:
            self.fail(f"TC-07 FAIL | Crashed with: {e}")

    # ── TC-08: Data Scientist position scoring ──
    def test_data_scientist_position(self):
        ds_candidate = {
            **self.sample_candidate,
            "position": "Data Scientist",
            "resume_skills": "Python, Scikit-learn, TensorFlow, SQL, NLP",
            "answer_1": "I have 5 years in ML with expertise in NLP and computer vision using TensorFlow and sklearn.",
        }
        result = self.model.score_candidate(ds_candidate)
        self.assertIn(result["tier"], ["Strong Yes", "Yes", "Maybe", "No"])
        print(f"TC-08 PASS | Data Scientist tier: {result['tier']}")

    # ── TC-09: Batch scoring of all candidates ──
    def test_batch_scoring(self):
        df = pd.read_csv(DATA_PATH)
        scored_df, _ = self.model.score_all_candidates(df)
        self.assertEqual(len(scored_df), len(df))
        self.assertTrue((scored_df["rank"] >= 1).all())
        print(f"TC-09 PASS | Batch scored {len(scored_df)} candidates")

    # ── TC-10: Metrics generation ──
    def test_metrics_generation(self):
        df = pd.read_csv(DATA_PATH)
        metrics = self.model.get_model_metrics(df)
        required_keys = ["total_candidates", "shortlisted", "avg_score", "tier_distribution"]
        for key in required_keys:
            self.assertIn(key, metrics)
        print(f"TC-10 PASS | Metrics: {metrics}")

    # ── TC-11: Experience score capped at 100% ──
    def test_experience_score_capped(self):
        high_exp = {**self.sample_candidate, "experience_years": 50}
        result = self.model.score_candidate(high_exp)
        self.assertLessEqual(result["final_score"], 100)
        print(f"TC-11 PASS | High experience capped. Score: {result['final_score']}")

    # ── TC-12: Question details present in output ──
    def test_question_details_present(self):
        result = self.model.score_candidate(self.sample_candidate)
        self.assertIn("question_details", result)
        self.assertEqual(len(result["question_details"]), 5)
        print(f"TC-12 PASS | 5 question details returned")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Test Suite - Candidate Q&A Screening Bot PRJ-110")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScoringModel)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("=" * 60)
    print(f"Tests run: {result.testsRun} | Failures: {len(result.failures)} | Errors: {len(result.errors)}")
    print("=" * 60)
