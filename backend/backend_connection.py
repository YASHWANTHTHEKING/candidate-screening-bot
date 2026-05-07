"""
Backend Connection Client
PRJ-110 | Yashwanth N.V PSVPEC
"""

import requests

API_BASE_URL = "http://localhost:8000"  # change to https://api.myproject.com after deployment


class BackendClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def health_check(self):
        """Check if backend is running"""
        response = requests.get(f"{self.base_url}/")
        return response.json()

    def get_all_candidates(self):
        """Fetch all candidates with scores"""
        response = requests.get(f"{self.base_url}/candidates")
        return response.json()

    def get_candidate(self, candidate_id: str):
        """Fetch a specific candidate by ID"""
        response = requests.get(f"{self.base_url}/candidates/{candidate_id}")
        if response.status_code == 404:
            return {"error": "Candidate not found"}
        return response.json()

    def score_candidate(self, candidate_data: dict):
        """Score a new candidate"""
        response = requests.post(f"{self.base_url}/candidates/score", json=candidate_data)
        return response.json()

    def upload_candidates_csv(self, file_path: str):
        """Upload CSV file of candidates"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/candidates/upload", files=files)
        return response.json()

    def update_notes(self, candidate_id: str, notes: str):
        """Update reviewer notes"""
        payload = {"candidate_id": candidate_id, "notes": notes}
        response = requests.put(f"{self.base_url}/candidates/notes", json=payload)
        return response.json()

    def upload_resume_pdf(self, candidate_id: str, position: str, pdf_path: str, name: str = "", email: str = ""):
        """Upload PDF resume"""
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            data = {
                "candidate_id": candidate_id,
                "name": name,
                "email": email,
                "position": position,
            }
            response = requests.post(f"{self.base_url}/candidates/upload-pdf", data=data, files=files)
        return response.json()

    def get_rubric(self):
        """Fetch scoring rubric"""
        response = requests.get(f"{self.base_url}/rubric")
        return response.json()
