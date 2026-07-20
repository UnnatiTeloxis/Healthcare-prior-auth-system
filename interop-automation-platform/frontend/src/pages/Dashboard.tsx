import type { CSSProperties } from "react";

export default function Dashboard() {
  return (
    <div style={styles.page}>
      <h1 style={styles.title}>Interop Automation Platform</h1>
      <p style={styles.subtitle}>FHIR validation, CRD, and DTR tooling</p>
      <div style={styles.grid}>
        <a href="/fhir-validator" style={styles.card}>
          <h2 style={styles.cardTitle}>FHIR Validator</h2>
          <p style={styles.cardBody}>
            Validate FHIR resources against base R4 or Implementation Guides using Inferno.
          </p>
        </a>
        <a href="/crd-simulator" style={styles.card}>
          <h2 style={styles.cardTitle}>CRD Simulator</h2>
          <p style={styles.cardBody}>Coverage Requirements Discovery simulation.</p>
        </a>
        <a href="/dtr-simulator" style={styles.card}>
          <h2 style={styles.cardTitle}>DTR Simulator</h2>
          <p style={styles.cardBody}>Documentation Templates and Rules simulation.</p>
        </a>
      </div>
      <p style={styles.footer}>
        API docs: <a href="http://localhost:8000/docs">/docs</a>
        {" · "}
        HTML validator: <a href="/fhir-validator.html">/fhir-validator.html</a>
      </p>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  page: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "2rem 1.5rem",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  title: { margin: 0, fontSize: "1.85rem" },
  subtitle: { color: "#6b7280", marginTop: "0.35rem" },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: "1rem",
    marginTop: "1.5rem",
  },
  card: {
    display: "block",
    textDecoration: "none",
    color: "inherit",
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 12,
    padding: "1.25rem",
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  },
  cardTitle: { margin: "0 0 0.5rem", fontSize: "1.1rem", color: "#1d4ed8" },
  cardBody: { margin: 0, color: "#4b5563", fontSize: "0.9rem" },
  footer: { marginTop: "1.5rem", color: "#6b7280", fontSize: "0.85rem" },
};
