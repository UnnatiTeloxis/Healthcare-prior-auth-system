import { useState, type CSSProperties } from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../../store";
import type { ValidationIssue } from "../../types/fhirValidator.types";

function severityColor(severity: string): string {
  switch (severity) {
    case "fatal":
    case "error":
      return "#b91c1c";
    case "warning":
      return "#b45309";
    default:
      return "#1d4ed8";
  }
}

function IssueRow({ issue }: { issue: ValidationIssue }) {
  return (
    <tr>
      <td style={{ ...styles.td, color: severityColor(issue.severity), fontWeight: 600 }}>
        {issue.severity}
      </td>
      <td style={styles.td}>{issue.location || "—"}</td>
      <td style={styles.td}>{issue.message}</td>
      <td style={styles.td}>{issue.code}</td>
    </tr>
  );
}

export default function ResultsDisplay() {
  const { validationResult, validating } = useSelector((state: RootState) => state.fhirValidator);
  const [showOutcome, setShowOutcome] = useState(false);

  if (validating) {
    return (
      <section style={styles.card}>
        <h2 style={styles.heading}>Results</h2>
        <p style={styles.muted}>Calling Inferno validator…</p>
      </section>
    );
  }

  if (!validationResult) {
    return (
      <section style={styles.card}>
        <h2 style={styles.heading}>Results</h2>
        <p style={styles.muted}>Validation results will appear here.</p>
      </section>
    );
  }

  const result = validationResult;

  return (
    <section style={styles.card}>
      <div
        style={{
          ...styles.banner,
          background: result.valid ? "#ecfdf5" : "#fef2f2",
          borderColor: result.valid ? "#a7f3d0" : "#fecaca",
          color: result.valid ? "#065f46" : "#991b1b",
        }}
      >
        <strong>{result.valid ? "PASSED" : "FAILED"}</strong>
        <span>{result.summary}</span>
      </div>

      <div style={styles.metaGrid}>
        <div><span style={styles.metaLabel}>Resource</span><div>{result.resource_type || "—"}</div></div>
        <div><span style={styles.metaLabel}>Selected IG</span><div>{result.selected_ig || "Base FHIR"}</div></div>
        <div><span style={styles.metaLabel}>Resolved profile</span><div style={styles.mono}>{result.resolved_profile || "—"}</div></div>
        <div>
          <span style={styles.metaLabel}>Counts</span>
          <div>
            <span style={styles.countError}>{result.error_count} errors</span>
            {" · "}
            <span style={styles.countWarn}>{result.warning_count} warnings</span>
            {" · "}
            <span style={styles.countInfo}>{result.info_count} info</span>
          </div>
        </div>
      </div>

      <h3 style={styles.subheading}>Issues</h3>
      {result.issues.length ? (
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Severity</th>
                <th style={styles.th}>Location</th>
                <th style={styles.th}>Message</th>
                <th style={styles.th}>Code</th>
              </tr>
            </thead>
            <tbody>
              {result.issues.map((issue, idx) => (
                <IssueRow key={`${issue.code}-${idx}`} issue={issue} />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p style={styles.muted}>No issues found.</p>
      )}

      <button type="button" style={styles.toggle} onClick={() => setShowOutcome((v) => !v)}>
        {showOutcome ? "Hide" : "Show"} raw OperationOutcome
      </button>
      {showOutcome && (
        <pre style={styles.pre}>{JSON.stringify(result.operation_outcome ?? {}, null, 2)}</pre>
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
  subheading: { margin: "1rem 0 0.5rem", fontSize: "0.95rem" },
  muted: { color: "#6b7280", margin: 0 },
  banner: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
    border: "1px solid",
    borderRadius: 10,
    padding: "0.85rem 1rem",
    marginBottom: "1rem",
  },
  metaGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "0.75rem",
    fontSize: "0.9rem",
  },
  metaLabel: { display: "block", color: "#6b7280", fontSize: "0.75rem", marginBottom: 2 },
  mono: { fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", fontSize: "0.8rem", wordBreak: "break-all" },
  countError: { color: "#b91c1c", fontWeight: 600 },
  countWarn: { color: "#b45309", fontWeight: 600 },
  countInfo: { color: "#1d4ed8", fontWeight: 600 },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" },
  th: {
    textAlign: "left",
    padding: "0.5rem",
    borderBottom: "1px solid #e5e7eb",
    color: "#4b5563",
    fontWeight: 600,
  },
  td: {
    padding: "0.5rem",
    borderBottom: "1px solid #f3f4f6",
    verticalAlign: "top",
  },
  toggle: {
    marginTop: "1rem",
    background: "transparent",
    border: "1px solid #d1d5db",
    borderRadius: 8,
    padding: "0.4rem 0.7rem",
    cursor: "pointer",
  },
  pre: {
    marginTop: "0.75rem",
    background: "#0f172a",
    color: "#e2e8f0",
    padding: "0.85rem",
    borderRadius: 8,
    overflow: "auto",
    maxHeight: 320,
    fontSize: "0.75rem",
  },
};
