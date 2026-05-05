"""
Streamlit Dashboard - Candidate Q&A Screening Bot
PRJ-110 | Yashwanth N.V PSVPEC
"""

import streamlit as st
import pandas as pd
import json
import sys
import os
import io
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.scoring_model import CandidateScoringModel

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Candidate Screening Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load model ────────────────────────────────────────────────────────────────
RUBRIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scoring_rubric.json")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "candidates.csv")

@st.cache_resource
def load_model():
    return CandidateScoringModel(RUBRIC_PATH)

@st.cache_data
def load_and_score(data_path):
    model = load_model()
    df = pd.read_csv(data_path)
    scored_df, details = model.score_all_candidates(df)
    return scored_df, details

model = load_model()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #7c9ef0; }
    .metric-label { font-size: 0.85rem; color: #9aa0b8; margin-top: 5px; }
    .tier-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .tier-strong { background: #1a4731; color: #4ade80; }
    .tier-yes { background: #1e3a5f; color: #60a5fa; }
    .tier-maybe { background: #3d2b00; color: #fbbf24; }
    .tier-no { background: #3b1111; color: #f87171; }
    .stDataFrame { border-radius: 10px; }
    div[data-testid="stSidebarNav"] { background: #1a1d2e; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🤖 Screening Bot")
    st.markdown("**PRJ-110** | HR AI/ML Tool")
    st.divider()
    page = st.radio("Navigate", [
        "📊 Dashboard",
        "👥 All Candidates",
        "⭐ Shortlist",
        "🔍 Candidate Detail",
        "➕ New Candidate",
        "📤 Export",
    ])
    st.divider()
    st.caption("Built with FastAPI + Scikit-learn + Streamlit")

# ── Load Data ────────────────────────────────────────────────────────────────
scored_df, details = load_and_score(DATA_PATH)

# ── Helper functions ─────────────────────────────────────────────────────────
def tier_badge(tier):
    cls = {"Strong Yes": "tier-strong", "Yes": "tier-yes", "Maybe": "tier-maybe", "No": "tier-no"}.get(tier, "tier-no")
    return f'<span class="tier-badge {cls}">{tier}</span>'

def score_color(score):
    if score >= 75: return "🟢"
    if score >= 60: return "🔵"
    if score >= 45: return "🟡"
    return "🔴"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Screening Dashboard")
    st.caption("Overview of all candidate evaluations")

    # Metrics Row
    total = len(scored_df)
    shortlisted = int(scored_df["shortlisted"].sum())
    avg_score = round(scored_df["final_score"].mean(), 1)
    top_score = round(scored_df["final_score"].max(), 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", total)
    with col2:
        st.metric("Shortlisted", shortlisted, f"{round(shortlisted/total*100)}%")
    with col3:
        st.metric("Avg Score", f"{avg_score}%")
    with col4:
        st.metric("Top Score", f"{top_score}%")

    st.divider()
    col_left, col_right = st.columns(2)

    # Score Distribution
    with col_left:
        st.subheader("Score Distribution")
        fig = px.histogram(
            scored_df, x="final_score", nbins=10,
            color_discrete_sequence=["#7c9ef0"],
            labels={"final_score": "Final Score (%)"},
        )
        fig.update_layout(
            plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
            font_color="#e0e0e0", bargap=0.1,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tier Breakdown
    with col_right:
        st.subheader("Tier Breakdown")
        tier_counts = scored_df["tier"].value_counts()
        fig2 = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            color_discrete_map={
                "Strong Yes": "#4ade80", "Yes": "#60a5fa",
                "Maybe": "#fbbf24", "No": "#f87171"
            },
            hole=0.5,
        )
        fig2.update_layout(
            plot_bgcolor="#1e2130", paper_bgcolor="#1e2130", font_color="#e0e0e0"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Score breakdown per candidate
    st.subheader("Score Breakdown by Candidate")
    fig3 = go.Figure()
    for col, name, color in [
        ("qa_score", "Q&A Score", "#7c9ef0"),
        ("resume_score", "Resume Score", "#4ade80"),
        ("experience_score", "Experience Score", "#fbbf24"),
    ]:
        fig3.add_trace(go.Bar(
            name=name, x=scored_df["name"], y=scored_df[col],
            marker_color=color, opacity=0.85,
        ))
    fig3.update_layout(
        barmode="group", plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
        font_color="#e0e0e0", xaxis_tickangle=-30,
        legend=dict(bgcolor="#1e2130"),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: All Candidates
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 All Candidates":
    st.title("👥 All Candidates")

    col1, col2, col3 = st.columns(3)
    with col1:
        pos_filter = st.selectbox("Position", ["All"] + scored_df["position"].unique().tolist())
    with col2:
        tier_filter = st.selectbox("Tier", ["All", "Strong Yes", "Yes", "Maybe", "No"])
    with col3:
        sort_col = st.selectbox("Sort By", ["rank", "final_score", "experience_years"])

    filtered = scored_df.copy()
    if pos_filter != "All":
        filtered = filtered[filtered["position"] == pos_filter]
    if tier_filter != "All":
        filtered = filtered[filtered["tier"] == tier_filter]
    filtered = filtered.sort_values(sort_col)

    st.caption(f"Showing {len(filtered)} candidates")

    display_cols = ["rank", "name", "position", "experience_years", "final_score", "qa_score", "resume_score", "tier", "shortlisted"]
    st.dataframe(
        filtered[display_cols].rename(columns={
            "final_score": "Score (%)", "qa_score": "Q&A (%)",
            "resume_score": "Resume (%)", "experience_years": "Exp (yrs)"
        }),
        use_container_width=True, height=400,
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Shortlist
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⭐ Shortlist":
    st.title("⭐ Shortlisted Candidates")
    shortlist = scored_df[scored_df["shortlisted"] == True].copy()
    st.success(f"✅ {len(shortlist)} candidates shortlisted (score ≥ 60%)")

    for _, row in shortlist.iterrows():
        with st.expander(f"#{row['rank']} — {row['name']} | {row['position']} | Score: {row['final_score']}%"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Final Score", f"{row['final_score']}%")
            col2.metric("Q&A Score", f"{row['qa_score']}%")
            col3.metric("Resume Score", f"{row['resume_score']}%")
            st.markdown(f"**Tier:** {row['tier']}  |  **Experience:** {row['experience_years']} yrs")
            st.markdown(f"**Required Skills Matched:** {', '.join(row['matched_required_skills']) if row['matched_required_skills'] else 'None'}")
            st.markdown(f"**Bonus Skills:** {', '.join(row['matched_bonus_skills']) if row['matched_bonus_skills'] else 'None'}")
            notes = st.text_area("Reviewer Notes", value=row.get("reviewer_notes", ""), key=f"notes_{row['candidate_id']}")
            if st.button("Save Notes", key=f"save_{row['candidate_id']}"):
                df = pd.read_csv(DATA_PATH)
                df.loc[df["candidate_id"] == row["candidate_id"], "reviewer_notes"] = notes
                df.to_csv(DATA_PATH, index=False)
                st.cache_data.clear()
                st.success("Notes saved!")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Candidate Detail
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Candidate Detail":
    st.title("🔍 Candidate Detail View")
    candidate_names = scored_df["name"].tolist()
    selected_name = st.selectbox("Select Candidate", candidate_names)
    selected_row = scored_df[scored_df["name"] == selected_name].iloc[0]
    candidate_detail = next((d for d in details if d["candidate_id"] == selected_row["candidate_id"]), None)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Score", f"{selected_row['final_score']}%")
    col2.metric("Q&A Score", f"{selected_row['qa_score']}%")
    col3.metric("Resume Score", f"{selected_row['resume_score']}%")
    col4.metric("Rank", f"#{selected_row['rank']}")

    st.markdown(f"**Tier:** `{selected_row['tier']}`  |  **Position:** {selected_row['position']}  |  **Experience:** {selected_row['experience_years']} yrs")
    st.divider()

    if candidate_detail and "question_details" in candidate_detail:
        st.subheader("📝 Question-by-Question Breakdown")
        for qd in candidate_detail["question_details"]:
            score_pct = round(qd["combined_score"] * 100, 1)
            with st.expander(f"Q{qd['question_id'][1:]}: {qd['question']} — {score_pct}%"):
                st.markdown(f"**Answer:** {qd['answer']}")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Keyword Score", f"{round(qd['keyword_score']*100, 1)}%")
                col_b.metric("TF-IDF Score", f"{round(qd['tfidf_score']*100, 1)}%")
                col_c.metric("Length Score", f"{round(qd['length_score']*100, 1)}%")
                st.progress(qd["combined_score"])

    st.divider()
    st.subheader("Radar Chart — Score Dimensions")
    radar_values = [
        selected_row["qa_score"],
        selected_row["resume_score"],
        selected_row["experience_score"],
    ]
    categories = ["Q&A Performance", "Resume Skills", "Experience"]
    fig = go.Figure(go.Scatterpolar(
        r=radar_values + [radar_values[0]],
        theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(124,158,240,0.2)",
        line_color="#7c9ef0",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#9aa0b8"),
            bgcolor="#1e2130",
        ),
        paper_bgcolor="#1e2130", font_color="#e0e0e0",
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: New Candidate
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ New Candidate":
    st.title("➕ Score a New Candidate")
    with st.form("candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            cid = st.text_input("Candidate ID (e.g. C009)")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
        with col2:
            position = st.selectbox("Position", ["Software Engineer", "Data Scientist"])
            exp = st.number_input("Years of Experience", 0, 30, 2)
            skills = st.text_input("Resume Skills (comma-separated)", "Python, SQL, Git")

        st.subheader("Answers to Screening Questions")
        with open(RUBRIC_PATH) as f:
            rubric = json.load(f)
        questions = rubric["positions"][position]["questions"]
        answers = {}
        for q in questions:
            answers[f"answer_{q['id'][1:]}"] = st.text_area(f"Q{q['id'][1:]}: {q['question']}", height=80)

        submitted = st.form_submit_button("🎯 Score Candidate", use_container_width=True)
        if submitted:
            candidate_data = {
                "candidate_id": cid, "name": name, "email": email,
                "position": position, "experience_years": exp,
                "resume_skills": skills, **answers,
            }
            result = model.score_candidate(candidate_data)
            st.success(f"✅ Scored! Final Score: **{result['final_score']}%** | Tier: **{result['tier']}**")
            st.json({k: v for k, v in result.items() if k != "question_details"})

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Export
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Export":
    st.title("📤 Export Rankings")
    export_cols = [
        "rank", "candidate_id", "name", "email", "position",
        "experience_years", "final_score", "qa_score", "resume_score",
        "tier", "shortlisted", "reviewer_notes"
    ]
    export_df = scored_df[export_cols]
    st.dataframe(export_df, use_container_width=True)

    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Rankings CSV",
        data=csv_data,
        file_name="candidate_rankings.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Upload New Candidates CSV")
    uploaded = st.file_uploader("Upload candidates.csv", type=["csv"])
    if uploaded:
        new_df = pd.read_csv(uploaded)
        new_scored, _ = model.score_all_candidates(new_df)
        st.success(f"Scored {len(new_scored)} candidates!")
        st.dataframe(new_scored[export_cols], use_container_width=True)
        new_csv = new_scored[export_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Scored Results", data=new_csv, file_name="scored_results.csv", mime="text/csv")
