import React, { useState, useEffect } from "react";
import JobRecommendations from "./components/JobRecommendations";

function App() {
  const [jobs, setJobs] = useState([]);
  const [darkMode, setDarkMode] = useState(true); // state for dark/light mode

  useEffect(() => {
    const fetchJobs = async () => {
      const res = await fetch("http://127.0.0.1:8000/jobs");
      const data = await res.json();
      setJobs(data);
    };
    fetchJobs();
  }, []);

  const toggleMode = () => setDarkMode(!darkMode);

  const bgColor = darkMode ? "#121212" : "#f5f5f5";
  const textColor = darkMode ? "#ffffff" : "#121212";
  const cardColor = darkMode ? "#1e1e2f" : "#ffffff";

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        backgroundColor: bgColor,
        color: textColor,
        minHeight: "100vh",
        transition: "all 0.3s ease",
      }}
    >
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={{ fontSize: "2.2rem", fontWeight: "bold" }}>DataSlush Job Recommendations</h1>
        <button
          onClick={toggleMode}
          style={{
            padding: "8px 16px",
            backgroundColor: darkMode ? "#4caf50" : "#121212",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            color: "#fff",
            fontWeight: "bold",
            transition: "all 0.3s ease",
          }}
        >
          {darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        </button>
      </header>

      <div style={{ marginTop: "30px", display: "flex", flexDirection: "column", gap: "25px" }}>
        {jobs.map((job) => (
          <div
            key={job.job_id}
            style={{
              padding: "20px",
              borderRadius: "12px",
              backgroundColor: cardColor,
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
              transition: "all 0.3s ease",
            }}
          >
            <h2
              style={{
                fontSize: "1.6rem",
                fontWeight: "bold",
                marginBottom: "10px",
                borderBottom: "2px solid #4caf50",
                paddingBottom: "5px",
                color: darkMode ? "#4caf50" : "#2196f3",
              }}
            >
              {job.title}
            </h2>
            <p style={{ marginBottom: "15px", fontStyle: "italic" }}>
              Location Preference: {job.location_preference}
            </p>

            <JobRecommendations jobId={job.job_id} darkMode={darkMode} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
