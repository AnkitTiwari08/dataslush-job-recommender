# recommender.py
from typing import List, Dict, Any
import pandas as pd
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    HAS_SB = True
except Exception:
    HAS_SB = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, df: pd.DataFrame, embedding_model: str = "all-MiniLM-L6-v2"):
        self.df = df.copy()
        self.embedding_model_name = embedding_model
        self.HAS_SB = HAS_SB
        self._prepare_text()
        self._fit_embeddings_or_tfidf()

    def _prepare_text(self):
        def safe_join(row):
            parts = []
            for col in ["bio", "skills", "software", "niches"]:
                if col in row and pd.notna(row[col]):
                    parts.append(str(row[col]))
            return " | ".join(parts)
        self.df["combined_text"] = self.df.apply(safe_join, axis=1)

    def _fit_embeddings_or_tfidf(self):
        if self.HAS_SB:
            try:
                self.model = SentenceTransformer(self.embedding_model_name)
                texts = self.df["combined_text"].tolist()
                self.embeddings = self.model.encode(texts, show_progress_bar=False)
                self.use_embeddings = True
            except Exception as e:
                print("Embedding model load failed:", e)
                self._fit_tfidf()
        else:
            print("sentence-transformers not available; falling back to TF-IDF.")
            self._fit_tfidf()

    def _fit_tfidf(self):
        self.tfidf = TfidfVectorizer(max_features=5000)
        self.tfidf_matrix = self.tfidf.fit_transform(self.df["combined_text"].fillna(""))
        self.use_embeddings = False

    def _embed_text(self, texts: List[str]):
        if self.use_embeddings:
            return self.model.encode(texts, show_progress_bar=False)
        else:
            return self.tfidf.transform(texts).toarray()

    def _score_budget(self, job, candidate_row):
        score = 0.0
        if "budget_monthly" in job and pd.notna(candidate_row.get("monthly_rate")):
            try:
                cand = float(candidate_row["monthly_rate"])
                if cand <= job["budget_monthly"]:
                    score = 1.0
                elif cand <= job["budget_monthly"] * 1.2:
                    score = 0.6
            except:
                score = 0.0
        if "budget_hourly" in job and pd.notna(candidate_row.get("hourly_rate")):
            try:
                cand = float(candidate_row["hourly_rate"])
                if cand <= job["budget_hourly"]:
                    score = max(score, 1.0)
                elif cand <= job["budget_hourly"] * 1.2:
                    score = max(score, 0.6)
            except:
                pass
        return score

    def recommend_for_job(self, job: Dict[str, Any], top_k: int = 10, weights: Dict[str,float]=None):
        if weights is None:
            weights = {"embedding": 0.6, "skill_overlap": 0.25, "budget": 0.1, "views": 0.05}

        parts = []
        if "title" in job: parts.append(job["title"])
        if "description" in job: parts.append(job["description"])
        if "required_skills" in job:
            if isinstance(job["required_skills"], list):
                parts.append(" ".join(job["required_skills"]))
            else:
                parts.append(job["required_skills"])
        job_text = " | ".join(parts)

        job_vec = self._embed_text([job_text])[0]
        if self.use_embeddings:
            sims = cosine_similarity([job_vec], self.embeddings)[0]
        else:
            sims = cosine_similarity([job_vec], self.tfidf_matrix.toarray())[0]

        def skill_overlap_score(req_skills, cand_skills):
            if not req_skills: return 0.0
            if isinstance(req_skills, str):
                req = set([s.strip().lower() for s in req_skills.split(",") if s.strip()])
            else:
                req = set([s.strip().lower() for s in req_skills])
            if pd.isna(cand_skills) or not cand_skills:
                return 0.0
            cand = set([s.strip().lower() for s in str(cand_skills).split(",") if s.strip()])
            if len(req) == 0:
                return 0.0
            return len(req.intersection(cand))/len(req)

        results = []
        for idx, row in self.df.iterrows():
            emb_score = float(sims[idx])
            skl_score = skill_overlap_score(job.get("required_skills", None), row.get("skills",""))
            bud_score = self._score_budget(job, row)
            try:
                views = float(row.get("views", 0))
            except:
                views = 0.0
            results.append({
                "id": row.get("id"),
                "name": row.get("name"),
                "emb_score": emb_score,
                "skill_score": skl_score,
                "budget_score": bud_score,
                "views": views
            })

        emb_arr = np.array([r["emb_score"] for r in results])
        if emb_arr.max() - emb_arr.min() > 0:
            emb_norm = (emb_arr - emb_arr.min())/(emb_arr.max()-emb_arr.min())
        else:
            emb_norm = emb_arr

        skill_arr = np.array([r["skill_score"] for r in results])
        if skill_arr.max() - skill_arr.min() > 0:
            skill_norm = (skill_arr - skill_arr.min())/(skill_arr.max()-skill_arr.min())
        else:
            skill_norm = skill_arr

        bud_arr = np.array([r["budget_score"] for r in results])
        if bud_arr.max() - bud_arr.min() > 0:
            bud_norm = (bud_arr - bud_arr.min())/(bud_arr.max()-bud_arr.min())
        else:
            bud_norm = bud_arr

        views_arr = np.array([r["views"] for r in results])
        if views_arr.max() - views_arr.min() > 0:
            views_norm = (views_arr - views_arr.min())/(views_arr.max()-views_arr.min())
        else:
            views_norm = views_arr

        final = []
        for i, r in enumerate(results):
            score = (weights["embedding"] * float(emb_norm[i])
                    + weights["skill_overlap"] * float(skill_norm[i])
                    + weights["budget"] * float(bud_norm[i])
                    + weights["views"] * float(views_norm[i]))
            final.append({
                "id": r["id"],
                "name": r["name"],
                "score": float(score),
                "components": {
                    "embedding": float(emb_norm[i]),
                    "skill_overlap": float(skill_norm[i]),
                    "budget": float(bud_norm[i]),
                    "views": float(views_norm[i])
                }
            })
        final_sorted = sorted(final, key=lambda x: x["score"], reverse=True)
        return final_sorted[:top_k]