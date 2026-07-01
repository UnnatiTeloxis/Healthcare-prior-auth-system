# Inferno Parity Test Suite (20 cases)

Use these files to validate your FHIR Conformance Validator and cross-check each result
against [Inferno Resource Validator](https://inferno.healthit.gov/validator/) with
**no profile selected** (base FHIR R4 StructureDefinition only).

Our platform sends `profiles: []` to the backend, which matches Inferno's default
behavior for resources without forcing a US Core profile URL.

## How to test

1. Upload each JSON file in the validator UI (Provide Data → Upload File).
2. Run validation and note errors / warnings / info counts.
3. Paste the same JSON into Inferno (Resource tab, no profile parameter).
4. Compare issue counts and messages — they should match.

## Test matrix

| # | File | Resource | Category | Expected (base FHIR) |
|---|------|----------|----------|----------------------|
| 01 | `01-valid-patient-minimal.json` | Patient | Valid | Pass (0 errors; warnings possible: dom-6 narrative) |
| 02 | `02-valid-patient-complete.json` | Patient | Valid | Pass |
| 03 | `03-valid-observation-vital-height.json` | Observation | Valid | Pass (~3 warnings vs Inferno: draft CodeSystem, performer, dom-6) |
| 04 | `04-valid-observation-lab-glucose.json` | Observation | Valid | Pass (~3 warnings) |
| 05 | `05-valid-condition-diabetes.json` | Condition | Valid | Pass |
| 06 | `06-valid-practitioner-basic.json` | Practitioner | Valid | Pass |
| 07 | `07-valid-bundle-two-patients.json` | Bundle | Valid | Pass or minor reference warnings |
| 08 | `08-invalid-patient-bad-gender.json` | Patient | Invalid | Error: gender not in value set |
| 09 | `09-invalid-patient-bad-birthdate.json` | Patient | Invalid | Error: invalid date format |
| 10 | `10-invalid-patient-wrong-resource-type.json` | Patient | Invalid | Error: unknown/wrong resourceType |
| 11 | `11-invalid-observation-missing-status.json` | Observation | Invalid | Error: required `status` |
| 12 | `12-invalid-observation-missing-code.json` | Observation | Invalid | Error: required `code` |
| 13 | `13-invalid-observation-bad-value-type.json` | Observation | Invalid | Error: wrong datatype for value |
| 14 | `14-invalid-bundle-bad-fullurl-uuid.json` | Bundle | Invalid | Error: UUID must be lowercase |
| 15 | `15-invalid-bundle-example-identifier-system.json` | Bundle | Invalid | Error: example URLs not allowed |
| 16 | `16-invalid-patient-bad-reference.json` | Patient | Invalid | Error/warning: invalid reference |
| 17 | `17-invalid-json-trailing-comma.json` | n/a | Syntax | Frontend parse error (not FHIR engine) |
| 18 | `18-edge-patient-no-identifier.json` | Patient | Edge valid | Pass on base Patient (identifier 0..*) |
| 19 | `19-edge-observation-with-meta-profile-lab.json` | Observation | Profile edge | Extra validation vs `us-core-observation-lab` if Inferno loads US Core |
| 20 | `20-stress-huge-bundle.json` | Bundle | Stress | Multiple errors (UUID, example URLs) + warnings |

## Notes

- Files **01–07, 18** are structurally valid for base FHIR R4.
- Files **08–16, 20** should produce **errors** in both tools.
- File **17** is intentionally invalid JSON — tests UI parsing only.
- File **19** includes `meta.profile` for US Core Lab; Inferno may validate both base
  Observation and the declared profile. Compare with profile **unset** in Inferno for
  strict parity with our default, or set the same profile in Inferno to test IG rules.
- Warnings such as `dom-6` (missing narrative) and best-practice performer are normal
  and should match Inferno when validator settings align (`DISPLAY_ISSUES_ARE_WARNINGS`).

## Complex suite (`complex/`)

Fifteen additional advanced scenarios for nested structures, bundles, polymorphic fields,
contained resources, and multi-resource clinical documents. See
[`complex/README.md`](complex/README.md) for the full matrix.

| Group | Files | What they stress |
|-------|-------|------------------|
| Valid complex | C01–C10 | BP components, contained refs, nested extensions, MedicationRequest dosage, DiagnosticReport, QuestionnaireResponse, searchset Bundle, Encounter, valueCodeableConcept, CarePlan |
| Invalid complex | C11–C14 | Dual value[x], missing component code, broken transaction Bundle, wrong extension value type |
| Stress | C15 | Document Bundle (Composition + 7 nested resources, one invalid entry) |
