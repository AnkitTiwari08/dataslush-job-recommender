# -----------------------------
# 1. IMPORTS
# -----------------------------
import pandas as pd
from fastapi import FastAPI
from typing import Dict
import re
import os

# -----------------------------
# 2. CREATE APP
# -----------------------------
app = FastAPI(
    title="DataSlush Recommendation System",
    description="Backend API for matching talents to job posts",
    version="1.1"
)

from fastapi.middleware.cors import CORSMiddleware

# Allow frontend to access backend
origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# 3. LOAD DATASETS
# -----------------------------
jobs = pd.read_csv("data/job_posts.csv")
talents = pd.read_csv("data/talent_profiles.csv")

# -----------------------------
# 4. HELPER FUNCTIONS
# -----------------------------
def extract_number(text):
    """Extract the first number from text, return as int."""
    numbers = re.findall(r"\d+", str(text))
    return int(numbers[0]) if numbers else None

def compute_score(job: Dict, candidate: Dict) -> float:
    """Compute matching score for a candidate against a job posting"""
    score = 0.0

    # --- Skills Match (40%) ---
    job_skills = str(job.get("required_skills", "")).lower().replace(",", ";").split(";")
    candidate_skills = str(candidate.get("Skills", "")).lower().replace(",", ";").split(";")
    skill_matches = sum(1 for s in job_skills if s.strip() and s.strip() in candidate_skills)
    skill_score = skill_matches / len(job_skills) if job_skills else 0
    score += 0.4 * skill_score

    # --- Location Match (20%) ---
    job_location = str(job.get("location_preference", "")).lower()
    candidate_location = f"{candidate.get('City', '')} {candidate.get('Country', '')}".lower()
    location_keywords = ["asia", "india", "usa", "new york", "remote", "uk"]
    if any(keyword in candidate_location for keyword in location_keywords if keyword in job_location):
        score += 0.2

    # --- Rate Match (20%) ---
    job_budget_value = extract_number(job.get("budget", 0))
    candidate_rate_value = extract_number(candidate.get("Monthly Rate", 0))
    if job_budget_value and candidate_rate_value:
        if candidate_rate_value <= job_budget_value:
            score += 0.2

    # --- Past Experience (20%) ---
    if str(job.get("channel", "")).lower() in str(candidate.get("Past Creators", "")).lower():
        score += 0.2

    return score

# -----------------------------
# 5. ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {"message": "FastAPI server is running!"}

@app.get("/jobs")
def get_jobs():
    return jobs.fillna("").to_dict(orient="records")

@app.get("/talents")
def get_talents():
    return talents.fillna("").head(10).to_dict(orient="records")

@app.get("/recommend/{job_id}")
def recommend(job_id: str):
    job_df = jobs[jobs["job_id"] == job_id]
    if job_df.empty:
        return {"error": f"No job found for job_id {job_id}"}
    job = job_df.fillna("").iloc[0].to_dict()

    candidate_scores = []
    for _, row in talents.fillna("").iterrows():
        candidate = row.to_dict()
        score = compute_score(job, candidate)
        candidate_scores.append({
            "candidate_id": candidate.get("candidate_id", row.name),
            "final_score": round(score, 3),
            **candidate
        })

    # Sort by score, then candidate_id for tie-breaking
    ranked_candidates = sorted(candidate_scores, key=lambda x: (-x["final_score"], x["candidate_id"]))

    return {
        "job_id": job_id,
        "job_title": job.get("title", ""),
        "top10_candidates": ranked_candidates[:10]
    }

@app.get("/export_all_jobs_csv_global_rank")
def export_all_jobs_csv_global_rank():
    all_rows = []

    for job_id in jobs["job_id"].unique():
        job_df = jobs[jobs["job_id"] == job_id]
        if job_df.empty:
            continue
        job = job_df.fillna("").iloc[0].to_dict()

        for _, row in talents.fillna("").reset_index().iterrows():
            candidate = row.to_dict()
            candidate_id = candidate.get("candidate_id", row.name)
            try:
                score = compute_score(job, candidate)
            except:
                score = 0.0
            all_rows.append({
                "job_id": job_id,
                "candidate_id": candidate_id,
                "final_score": float(round(score, 6))
            })

    final_df = pd.DataFrame(all_rows)
    final_df = final_df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
    final_df["rank"] = final_df.index + 1

    out_path = os.path.join("data", "sample_output.csv")
    final_df.to_csv(out_path, index=False)

    return {
        "message": f"Exported all candidates for all jobs with global continuous ranking to {out_path}",
        "file": out_path,
        "top_rows": final_df.head(20).to_dict(orient="records")
    }

@app.get("/export_csv/{job_id}")
def export_recommendations_csv(job_id: str):
    job_df = jobs[jobs["job_id"] == job_id]
    if job_df.empty:
        return {"error": f"No job found for job_id {job_id}"}
    job = job_df.fillna("").iloc[0].to_dict()

    rows = []
    for _, row in talents.fillna("").reset_index().iterrows():
        candidate = row.to_dict()
        candidate_id = candidate.get("candidate_id", row.name)
        try:
            score = compute_score(job, candidate)
        except:
            score = 0.0
        rows.append({
            "job_id": job_id,
            "candidate_id": candidate_id,
            "final_score": float(round(score, 6))
        })

    out_df = pd.DataFrame(rows)
    out_df = out_df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
    out_df["rank"] = out_df.index + 1

    top10 = out_df.head(10)[["job_id", "candidate_id", "final_score", "rank"]]

    out_path = os.path.join("data", f"sample_output_{job_id}.csv")
    top10.to_csv(out_path, index=False)

    return {
        "message": f"Exported top {len(top10)} candidates to {out_path}",
        "file": out_path,
        "top_rows": top10.to_dict(orient="records")
    }

@app.get("/debug_talents")
def debug_talents():
    return {"columns": list(talents.columns)}
