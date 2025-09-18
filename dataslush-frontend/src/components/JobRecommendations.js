// src/components/JobRecommendations.js
import React, { useState, useEffect } from "react";

function JobRecommendations({ jobId }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://127.0.0.1:8000/recommend/${jobId}`);
        const data = await res.json();
        setCandidates(data.top10_candidates || []);
      } catch (err) {
        console.error("Failed to fetch recommendations:", err);
      }
      setLoading(false);
    };
    fetchRecommendations();
  }, [jobId]);

  if (loading) return <p>Loading recommendations...</p>;
  if (!candidates.length) return <p>No candidates found.</p>;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "20px" }}>
      {candidates.map((c) => (
        <div
          key={c.candidate_id}
          style={{
            flex: "1 1 300px",
            borderRadius: "12px",
            padding: "20px",
            backgroundColor: "#1e1e2f",
            color: "white",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
          }}
        >
          <div style={{ fontWeight: "bold", fontSize: "18px", marginBottom: "10px" }}>
            {c.first_name} {c.last_name}
          </div>
          <div style={{ marginBottom: "10px", fontSize: "14px" }}>
            <span style={{ marginRight: "5px" }}>📍</span>
            {c.City}, {c.Country}
          </div>

          {/* Score as a progress bar */}
          <div style={{ marginBottom: "10px" }}>
            <div style={{ fontSize: "14px", marginBottom: "3px" }}>Score: {c.final_score * 100}%</div>
            <div style={{ backgroundColor: "#333", borderRadius: "5px", height: "8px" }}>
              <div
                style={{
                  width: `${c.final_score * 100}%`,
                  height: "8px",
                  borderRadius: "5px",
                  backgroundColor: "#4caf50",
                }}
              />
            </div>
          </div>

          {/* Skills as colored tags */}
          <div style={{ marginBottom: "10px", display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {c.Skills.split(", ").map((skill, index) => (
              <span
                key={index}
                style={{
                  backgroundColor: "#4caf50",
                  padding: "3px 8px",
                  borderRadius: "15px",
                  fontSize: "12px",
                }}
              >
                {skill}
              </span>
            ))}
          </div>

          <div style={{ fontSize: "16px", fontWeight: "bold" }}>💰 ${c["Monthly Rate"]}</div>
        </div>
      ))}
    </div>
  );
}

export default JobRecommendations;
