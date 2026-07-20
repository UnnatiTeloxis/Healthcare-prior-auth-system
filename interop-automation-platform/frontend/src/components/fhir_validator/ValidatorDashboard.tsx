import type { CSSProperties } from "react";
import ProfileSelector from "./ProfileSelector";
import InputPanel from "./InputPanel";
import ResultsDisplay from "./ResultsDisplay";
import ValidationHistory from "./ValidationHistory";

export default function ValidatorDashboard() {
  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>FHIR Validator</h1>
          <p style={styles.subtitle}>
            Validate resources against base FHIR or Implementation Guides via the Inferno API
          </p>
        </div>
        <a href="/" style={styles.link}>
          ← Dashboard
        </a>
      </header>

      <div style={styles.grid}>
        <div style={styles.mainCol}>
          <ProfileSelector />
          <InputPanel />
          <ResultsDisplay />
        </div>
        <aside style={styles.sideCol}>
          <ValidationHistory />
        </aside>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  page: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "1.5rem",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    color: "#111827",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "1rem",
    marginBottom: "1.25rem",
  },
  title: { margin: 0, fontSize: "1.75rem" },
  subtitle: { margin: "0.35rem 0 0", color: "#6b7280" },
  link: { color: "#2563eb", textDecoration: "none", fontWeight: 600 },
  grid: {
    display: "grid",
    gridTemplateColumns: "minmax(0, 1fr) 320px",
    gap: "1rem",
    alignItems: "start",
  },
  mainCol: { display: "flex", flexDirection: "column", gap: "1rem" },
  sideCol: { position: "sticky", top: "1rem" },
};
