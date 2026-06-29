# FHIR Validator Test Suite

A broad set of sample FHIR resources for exercising the FHIR Conformance Validator.
Upload any file in the validator UI (Step 2 → Upload File) or POST it to
`/api/v1/fhir/validate`.

Each resource declares its target profile in `meta.profile`. The validator (and the
standalone HL7 FHIR Validator / Inferno) validates against that declared profile, so
results are reproducible across tools when the same US Core version is loaded
(this stack loads **US Core 6.1.0**).

## Files

| File | Category | Resource | Expected outcome |
|------|----------|----------|------------------|
| `01-valid-basic-patient.json` | Basic / valid | Patient | Passes (minimal required: identifier, name, gender) |
| `02-valid-complete-patient.json` | Complete / valid | Patient | Passes (adds telecom, address, birthDate, language) |
| `03-valid-huge-patient.json` | Huge / valid | Patient | Passes (race/ethnicity/birthsex extensions, multiple identifiers, names, addresses, contacts) |
| `04-valid-observation-vitals-height.json` | Valid | Observation | Passes US Core Vital Signs |
| `05-valid-observation-lab.json` | Valid | Observation | Passes US Core Lab |
| `06-invalid-missing-identifier.json` | Invalid | Patient | Error: missing required `Patient.identifier` |
| `07-invalid-missing-name.json` | Invalid | Patient | Error: missing required `Patient.name` |
| `08-invalid-bad-gender-code.json` | Invalid | Patient | Error: `gender` not in the required value set |
| `09-invalid-birthdate-format.json` | Invalid | Patient | Error: `birthDate` is not a valid FHIR date |
| `10-invalid-wrong-resource-type.json` | Invalid | Observation | Error: Observation submitted against the Patient profile |
| `11-invalid-malformed-syntax.json` | Invalid (syntax) | n/a | Parser error: trailing comma — tests JSON parse handling |
| `12-valid-huge-bundle.json` | Huge / valid | Bundle | Collection of 2 Patients + 3 Observations |

## Notes

- "Valid" files are expected to pass structural and profile validation. Depending on
  the live terminology server (`tx.fhir.org`), you may still see informational or
  warning messages (for example, code `display` mismatches) — these match what the
  HL7 FHIR Validator and Inferno report.
- `11-invalid-malformed-syntax.json` is intentionally not valid JSON; use it to verify
  the UI's "Invalid JSON" error handling, not the FHIR engine.
- To get identical results in another tool, validate against the same `meta.profile`
  URL and the same US Core version (6.1.0).
