import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", maxWidth: 720 }}>
      <h1>Interop Automation Platform</h1>
      <p>FHIR Validator | CRD Simulator | DTR Simulator</p>
      <ul>
        <li>
          <a href="/health" target="_blank" rel="noreferrer">
            Backend health (via nginx)
          </a>
        </li>
        <li>
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            API docs
          </a>
        </li>
      </ul>
      <p style={{ color: "#047857", fontWeight: 600 }}>MVP frontend is running in Docker.</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
