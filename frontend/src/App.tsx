import {useEffect, useState} from 'react';

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function App() {
  const [status, setStatus] = useState("In Progress...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
    .then((r) => r.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("OFFLINE"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>F1 Analysis & Prediction</h1>
      <p>Backend status: {status}</p>
    </div>
  );

  //end of class
}