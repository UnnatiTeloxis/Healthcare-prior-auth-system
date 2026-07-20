import { useRef, type CSSProperties } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { AppDispatch, RootState } from "../../store";
import {
  clearError,
  setResourceText,
  validateFhirResource,
} from "../../store/fhirValidatorSlice";
import { igKey } from "../../services/api/fhirValidator";

const SAMPLE_PATIENT = `{
  "resourceType": "Patient",
  "id": "example",
  "meta": {
    "profile": [
      "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://hospital.example.org/mrn",
      "value": "12345"
    }
  ],
  "name": [
    {
      "family": "Doe",
      "given": ["Jane"]
    }
  ],
  "gender": "female",
  "birthDate": "1980-01-15"
}`;

export default function InputPanel() {
  const dispatch = useDispatch<AppDispatch>();
  const fileRef = useRef<HTMLInputElement>(null);
  const {
    resourceText,
    selectedIG,
    selectedProfile,
    validating,
    igLoading,
    error,
  } = useSelector((state: RootState) => state.fhirValidator);

  const onFileChange = async (file: File | null) => {
    if (!file) return;
    const text = await file.text();
    dispatch(setResourceText(text));
  };

  const onValidate = () => {
    dispatch(clearError());
    const packageId = selectedIG?.package_id || selectedIG?.name;
    const ig =
      selectedIG && packageId
        ? igKey(packageId, selectedIG.version || null)
        : null;

    void dispatch(
      validateFhirResource({
        resource: resourceText,
        profiles: selectedProfile ? [selectedProfile] : [],
        profile: selectedProfile || null,
        ig,
      })
    );
  };

  return (
    <section style={styles.card}>
      <div style={styles.headerRow}>
        <h2 style={styles.heading}>FHIR Resource</h2>
        <div style={styles.actions}>
          <button type="button" style={styles.secondaryBtn} onClick={() => dispatch(setResourceText(SAMPLE_PATIENT))}>
            Load sample Patient
          </button>
          <button type="button" style={styles.secondaryBtn} onClick={() => fileRef.current?.click()}>
            Upload .json / .xml
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".json,.xml,application/json,application/xml,text/xml"
            style={{ display: "none" }}
            onChange={(e) => void onFileChange(e.target.files?.[0] ?? null)}
          />
        </div>
      </div>

      <textarea
        style={styles.textarea}
        spellCheck={false}
        placeholder='Paste a FHIR resource JSON or XML here…'
        value={resourceText}
        onChange={(e) => dispatch(setResourceText(e.target.value))}
      />

      {error ? <div style={styles.error}>{error}</div> : null}

      <div style={styles.footer}>
        <button
          type="button"
          style={styles.primaryBtn}
          disabled={!resourceText.trim() || validating || igLoading}
          onClick={onValidate}
        >
          {validating ? "Validating via Inferno…" : "Validate"}
        </button>
        <span style={styles.hint}>
          {selectedIG
            ? `IG: ${selectedIG.package_id || selectedIG.name}${selectedIG.version ? `#${selectedIG.version}` : ""}`
            : "Base FHIR (no IG)"}
          {selectedProfile ? ` · Profile selected` : ""}
        </span>
      </div>
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
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "0.75rem",
    flexWrap: "wrap",
    marginBottom: "0.75rem",
  },
  heading: { margin: 0, fontSize: "1.1rem" },
  actions: { display: "flex", gap: "0.5rem", flexWrap: "wrap" },
  textarea: {
    width: "100%",
    minHeight: 280,
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
    fontSize: "0.85rem",
    padding: "0.85rem",
    borderRadius: 8,
    border: "1px solid #d1d5db",
    resize: "vertical",
    boxSizing: "border-box",
  },
  footer: {
    marginTop: "0.85rem",
    display: "flex",
    alignItems: "center",
    gap: "0.85rem",
    flexWrap: "wrap",
  },
  primaryBtn: {
    background: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "0.7rem 1.2rem",
    fontWeight: 600,
    cursor: "pointer",
  },
  secondaryBtn: {
    background: "#f3f4f6",
    color: "#111827",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "0.45rem 0.75rem",
    cursor: "pointer",
    fontSize: "0.85rem",
  },
  hint: { color: "#6b7280", fontSize: "0.85rem" },
  error: {
    marginTop: "0.75rem",
    background: "#fef2f2",
    color: "#991b1b",
    border: "1px solid #fecaca",
    borderRadius: 8,
    padding: "0.65rem 0.75rem",
    fontSize: "0.875rem",
  },
};
