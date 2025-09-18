DataSlush Job Recommendation System

Full-stack Proof-of-Concept for matching job postings to candidate profiles and ranking top candidates using a FastAPI backend and React frontend.

Table of Contents

Project Overview

Features

Project Structure

Backend Setup

Frontend Setup

API Endpoints

Usage Example

Notes & Next Steps

Author

Project Overview

This system allows recruiters or hiring managers to:

Select a job posting

Fetch top candidate recommendations

View candidate skills, location, score, and monthly rate

Compare candidates based on a computed matching score

The matching logic uses skills overlap, text embeddings, location preference, and budget compatibility.

Features

FastAPI backend with /recommend endpoint

React frontend for interactive candidate browsing

Dark/Light mode toggle for better UI experience

Candidate “cards” with score bars and hover effects

Handles multiple job positions with top N recommendations

Project Structure
job-recommendation-system/
├─ backend/
│  ├─ app.py                 # FastAPI backend main file
│  ├─ recommender.py         # Recommendation logic
│  ├─ requirements.txt       # Backend dependencies
│  └─ data/                  # Dataset CSVs
│     ├─ job_posts.csv
│     ├─ talent_profiles.csv
│     └─ sample_output.csv
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  │  └─ JobList.js
│  │  ├─ App.js
│  │  └─ index.js
│  ├─ package.json
│  └─ README_FRONTEND.md
└─ README.md                 # This file

Backend Setup

Create a Python virtual environment:

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


Install dependencies:

pip install -r backend/requirements.txt


Place dataset CSVs in backend/data/:

job_posts.csv

talent_profiles.csv

Run the backend:

uvicorn backend.app:app --reload --port 8000

Frontend Setup

Navigate to frontend folder:

cd frontend


Install dependencies:

npm install


Run the frontend app:

npm start


The frontend will open in the browser (default: http://localhost:3000) and fetch data from the backend.

API Endpoints
Endpoint	Method	Description
/recommend/{job_id}	GET	Returns top N recommended candidates for the given job ID.

Example Request:

GET http://localhost:8000/recommend/job1?top_k=10


Response Example:

[
  {
    "candidate_id": 88,
    "score": 0.40,
    "skills": ["Splice & Dice", "Community Management"],
    "location": "Shanghai, Germany",
    "monthly_rate": 6471
  },
  ...
]

Usage Example

Open frontend → select job → view top candidate cards

Each card shows: location, score, skills, monthly rate, and a score bar

Toggle between Dark/Light mode for better visibility

Notes & Next Steps

Improve scoring algorithm with more signals (past creators, platform fit)

Add authentication and pagination

Generate automatic CSV exports of top 10 candidates per job

Deploy backend & frontend for production

Author

Name: Ankit Tiwari
Enrollment No.: IU2241230456
College Email: ankittiwari.22.cse@iite.indusuni.ac.in

Personal Email: tiwariankit00059@gmail.com

This README is ready to submit with your GitHub repo.