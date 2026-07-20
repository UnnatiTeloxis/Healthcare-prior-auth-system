import type { CSSProperties } from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../../store";

export default function ValidationHistory() {
  const history = useSelector((state: RootState) => state.fhirValidator.validationHistory);

  return (
    <section style={styles.card}>
      <h2 style={styles.heading}>Validation History</h2>
      {!history.length ? (
        <p style={styles.muted}>No validations yet in this session.</p>
      ) : (
        <ul style={styles.list}>
          {history.map((entry) => (
            <li key={entry.id} style={styles.item}>
              <div style={styles.row}>
                <strong style={{ color: entry.valid ? "#047857" : "#b91c1c" }}>
                  {entry.valid ? "PASS" : "FAIL"}
                </strong>
                <span style={styles.time}>{new Date(entry.timestamp).toLocaleString()}</span>
              </div>
              <div style={styles.meta}>
                {entry.resourceType || "Unknown"} · {entry.selectedIg || "Base FHIR"}
              </div>
              <div style={styles.summary}>{entry.summary}</div>
              <div style={styles.counts}>
                {entry.errorCount} errors · {entry.warningCount} warnings
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

const styles: Record<string, CSSProperties> = {
  card: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 12,
    padding: "1.25rem",
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  },
  heading: { margin: "0 0 0.75rem", fontSize: "1.1rem" },
  muted: { color: "#6b7280", margin: 0 },
  list: { listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: "0.75rem" },
  item: {
    border: "1px solid #f3f4f6",
    borderRadius: 8,
    padding: "0.75rem",
    background: "#fafafa",
  },
  row: { display: "flex", justifyContent: "space-between", gap: "0.5rem" },
  time: { color: "#6b7280", fontSize: "0.8rem" },
  meta: { marginTop: 4, fontSize: "0.85rem", color: "#374151" },
  summary: { marginTop: 4, fontSize: "0.8rem", color: "#4b5563" },
  counts: { marginTop: 4, fontSize: "0.75rem", color: "#6b7280" },
};
