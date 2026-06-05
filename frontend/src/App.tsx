import {useEffect, useState} from 'react';

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function App() {
  const [status, setStatus] = useState("In Progress...");
  const [dbStatus, setDbStatus] = useState("In Progress...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
    .then((r) => r.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("OFFLINE"));
  }, []);

  useEffect(() => {
    fetch(`${API_URL}/db-check`)
    .then((r) => r.json())
      .then((data) => setDbStatus(data.status))
      .catch(() => setDbStatus("OFFLINE"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>F1 Analysis & Prediction</h1>
      <p>Backend status: {status}</p>
      <p>Database status: {dbStatus}</p>
    </div>
  );

  //end of class
}