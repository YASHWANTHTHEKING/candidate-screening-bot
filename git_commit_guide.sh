#!/bin/bash
# Week-by-Week GitHub Commit Guide — PRJ-110

# ──────────────────────────────────────────────
# INITIAL SETUP (Run once)
# ──────────────────────────────────────────────
git init
git remote add origin https://github.com/<YOUR_USERNAME>/candidate-screening-bot.git
git branch -M main

# ──────────────────────────────────────────────
# WEEK 1 COMMITS (Data + Model + Basic API)
# ──────────────────────────────────────────────

# Commit 1 - Project setup
git add .gitignore README.md requirements.txt
git commit -m "feat: initial project setup and README for PRJ-110"
git push -u origin main

# Commit 2 - Dataset
git add data/
git commit -m "feat: add sample candidates dataset and scoring rubric"
git push

# Commit 3 - Scoring model
git add models/
git commit -m "feat: implement TF-IDF + keyword scoring model"
git push

# Commit 4 - FastAPI backend
git add backend/
git commit -m "feat: add FastAPI backend with scoring endpoints"
git push

# Commit 5 - Tests (Week 1 testing)
git add tests/
git commit -m "test: add 12 unit test cases, all passing"
git push

# ──────────────────────────────────────────────
# WEEK 2 COMMITS (Dashboard + Improvements)
# ──────────────────────────────────────────────

# Commit 6 - Streamlit dashboard
git add frontend/
git commit -m "feat: add Streamlit dashboard with 6 pages"
git push

# Commit 7 - Export feature
git commit -am "feat: add CSV export and upload functionality"
git push

# Commit 8 - Reviewer notes
git commit -am "feat: add reviewer notes save/load to dashboard"
git push

# Commit 9 - Visualizations
git commit -am "feat: add plotly charts - radar, bar, pie, histogram"
git push

# ──────────────────────────────────────────────
# WEEK 3 COMMITS (Polish + Deployment)
# ──────────────────────────────────────────────

# Commit 10 - UI polish
git commit -am "style: improve dashboard UI with dark theme and metrics"
git push

# Commit 11 - Bug fixes
git commit -am "fix: handle edge cases in scoring (empty answers, unknown position)"
git push

# Commit 12 - Deployment config
git add Procfile runtime.txt
git commit -m "feat: add deployment configuration"
git push

# Commit 13 - Final docs
git add README.md
git commit -m "docs: update README with screenshots and deployment link"
git push

echo "✅ All commits done! Check your GitHub repo."
