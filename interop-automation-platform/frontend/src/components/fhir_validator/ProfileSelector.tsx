import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { AppDispatch, RootState } from "../../store";
import {
  fetchAvailableIGs,
  loadSelectedIG,
  setSelectedIG,
  setSelectedProfile,
} from "../../store/fhirValidatorSlice";
import { igKey } from "../../services/api/fhirValidator";
import type { AvailableIG } from "../../types/fhirValidator.types";

function packageIdOf(ig: AvailableIG): string {
  return ig.package_id || ig.name || "";
}

export default function ProfileSelector() {
  const dispatch = useDispatch<AppDispatch>();
  const {
    availableIGs,
    selectedIG,
    selectedProfile,
    profilesForIG,
    igsLoading,
    igLoading,
    igLoadStatus,
  } = useSelector((state: RootState) => state.fhirValidator);

  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    void dispatch(fetchAvailableIGs(undefined));
  }, [dispatch]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return availableIGs;
    return availableIGs.filter((ig) => {
      const hay = [
        ig.title,
        packageIdOf(ig),
        ig.description,
        ig.category,
        ig.version,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(needle);
    });
  }, [availableIGs, query]);

  const onSelectIG = async (ig: AvailableIG | null) => {
    dispatch(setSelectedIG(ig));
    setOpen(false);
    setQuery("");
    if (!ig) return;
    const pid = packageIdOf(ig);
    if (!pid) return;
    await dispatch(loadSelectedIG({ packageId: pid, version: ig.version || null }));
  };

  return (
    <section style={styles.card}>
      <h2 style={styles.heading}>Implementation Guide & Profile</h2>
      <p style={styles.hint}>
        Select an IG to validate against Inferno profiles. Leave empty for base FHIR R4.
      </p>

      <label style={styles.label}>Implementation Guide</label>
      <div style={styles.dropdownWrap}>
        <button
          type="button"
          style={styles.selectButton}
          onClick={() => setOpen((v) => !v)}
          disabled={igsLoading}
        >
          {selectedIG
            ? `${selectedIG.title || packageIdOf(selectedIG)}${selectedIG.version ? ` #${selectedIG.version}` : ""}`
            : igsLoading
              ? "Loading IG catalog…"
              : "Base FHIR R4 (No IG)"}
        </button>
        {open && (
          <div style={styles.dropdown}>
            <input
              style={styles.search}
              placeholder="Search IGs…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
            <button type="button" style={styles.option} onClick={() => void onSelectIG(null)}>
              <strong>Base FHIR R4 (No IG)</strong>
              <span style={styles.optionMeta}>Validates against base StructureDefinitions</span>
            </button>
            <div style={styles.optionList}>
              {filtered.map((ig) => {
                const pid = packageIdOf(ig);
                const key = igKey(pid, ig.version);
                const selected =
                  selectedIG &&
                  packageIdOf(selectedIG) === pid &&
                  (selectedIG.version || "") === (ig.version || "");
                return (
                  <button
                    key={key + (ig.filename || "")}
                    type="button"
                    style={{
                      ...styles.option,
                      ...(selected ? styles.optionSelected : null),
                    }}
                    onClick={() => void onSelectIG(ig)}
                  >
                    <strong>{ig.title || pid}</strong>
                    <span style={styles.optionMeta}>
                      {pid}
                      {ig.fhir_version ? ` · FHIR ${ig.fhir_version}` : ""}
                      {ig.cached ? " · Cached" : " · Catalog"}
                    </span>
                    {ig.version ? <span style={styles.version}>{ig.version}</span> : null}
                  </button>
                );
              })}
              {!filtered.length && <div style={styles.empty}>No matching IGs</div>}
            </div>
          </div>
        )}
      </div>

      {selectedIG && (
        <div style={styles.metaRow}>
          <span style={styles.badge}>
            {igLoading || igLoadStatus === "loading"
              ? "Loading IG into Inferno…"
              : igLoadStatus === "ready"
                ? "IG ready"
                : igLoadStatus === "failed"
                  ? "IG load failed"
                  : "IG selected"}
          </span>
          {selectedIG.cached ? <span style={styles.badgeOk}>Cached</span> : <span style={styles.badgeMuted}>Remote</span>}
        </div>
      )}

      <label style={styles.label}>Profile</label>
      <select
        style={styles.select}
        value={selectedProfile}
        disabled={!selectedIG || igLoading}
        onChange={(e) => dispatch(setSelectedProfile(e.target.value))}
      >
        <option value="">Auto (meta.profile or best resource-type match)</option>
        {profilesForIG.map((url) => (
          <option key={url} value={url}>
            {url.split("/").pop()} — {url}
          </option>
        ))}
      </select>
      <p style={styles.hint}>
        {selectedIG
          ? profilesForIG.length
            ? `${profilesForIG.length} profiles available from the loaded IG.`
            : igLoading
              ? "Waiting for Inferno to finish loading profiles…"
              : "No profiles returned yet — validation can still resolve from meta.profile."
          : "Choose an IG to unlock profile selection."}
      </p>
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
  heading: { margin: "0 0 0.35rem", fontSize: "1.1rem" },
  hint: { margin: "0.35rem 0 0", color: "#6b7280", fontSize: "0.85rem" },
  label: { display: "block", marginTop: "1rem", marginBottom: "0.35rem", fontWeight: 600, fontSize: "0.9rem" },
  dropdownWrap: { position: "relative" },
  selectButton: {
    width: "100%",
    textAlign: "left",
    padding: "0.7rem 0.85rem",
    borderRadius: 8,
    border: "1px solid #d1d5db",
    background: "#f9fafb",
    cursor: "pointer",
  },
  dropdown: {
    position: "absolute",
    zIndex: 20,
    top: "110%",
    left: 0,
    right: 0,
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 10,
    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
    maxHeight: 320,
    display: "flex",
    flexDirection: "column",
  },
  search: {
    margin: "0.6rem",
    padding: "0.55rem 0.7rem",
    borderRadius: 6,
    border: "1px solid #d1d5db",
  },
  optionList: { overflowY: "auto", maxHeight: 240 },
  option: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: 2,
    width: "100%",
    textAlign: "left",
    padding: "0.65rem 0.85rem",
    border: "none",
    background: "transparent",
    cursor: "pointer",
    borderBottom: "1px solid #f3f4f6",
  },
  optionSelected: { background: "#eff6ff" },
  optionMeta: { fontSize: "0.75rem", color: "#6b7280" },
  version: { fontSize: "0.75rem", color: "#2563eb", fontWeight: 600 },
  empty: { padding: "0.85rem", color: "#9ca3af", fontSize: "0.85rem" },
  select: {
    width: "100%",
    padding: "0.65rem 0.75rem",
    borderRadius: 8,
    border: "1px solid #d1d5db",
    background: "#fff",
  },
  metaRow: { display: "flex", gap: "0.5rem", marginTop: "0.6rem", flexWrap: "wrap" },
  badge: {
    display: "inline-block",
    padding: "0.2rem 0.55rem",
    borderRadius: 999,
    background: "#eef2ff",
    color: "#3730a3",
    fontSize: "0.75rem",
    fontWeight: 600,
  },
  badgeOk: {
    display: "inline-block",
    padding: "0.2rem 0.55rem",
    borderRadius: 999,
    background: "#ecfdf5",
    color: "#047857",
    fontSize: "0.75rem",
    fontWeight: 600,
  },
  badgeMuted: {
    display: "inline-block",
    padding: "0.2rem 0.55rem",
    borderRadius: 999,
    background: "#f3f4f6",
    color: "#4b5563",
    fontSize: "0.75rem",
    fontWeight: 600,
  },
};
