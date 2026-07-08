# Complex Inferno Parity Cases

Advanced FHIR R4 scenarios for regression testing against Inferno (base FHIR, no profile
selected unless noted). These stress nested structures, bundles, polymorphic fields,
contained resources, and cross-resource references.

| # | File | Resource | Category | Expected |
|---|------|----------|----------|----------|
| C01 | `01-valid-observation-blood-pressure-components.json` | Observation | Valid | Pass — 0 errors, 1 warning, 3 info (exact Inferno passthrough) |
| C02 | `02-valid-patient-contained-organization.json` | Patient | Valid | Pass — 0 errors, 1 warning, 1 info |
| C03 | `03-valid-patient-nested-extensions.json` | Patient | Valid | Pass — 0 errors, 2 warnings, 3 info |
| C04 | `04-valid-medication-request-complex-dosage.json` | MedicationRequest | Valid | Pass — 0 errors, 2 warnings, 5 info |
| C05 | `05-valid-diagnostic-report-with-results.json` | DiagnosticReport | Valid | Pass — 0 errors, 2 warnings, 1 info |
| C06 | `06-valid-questionnaire-response-nested.json` | QuestionnaireResponse | Valid | Pass — 0 errors, 2 warnings, 1 info |
| C07 | `07-valid-bundle-searchset-with-links.json` | Bundle | Valid | Pass — 0 errors, 2 warnings |
| C08 | `08-valid-encounter-hospitalization.json` | Encounter | Valid | Pass — 0 errors, 1 warning, 2 info |
| C09 | `09-valid-observation-value-codeable-concept.json` | Observation | Valid | Pass — 0 errors, 2 warnings |
| C10 | `10-valid-careplan-multiple-activities.json` | CarePlan | Valid* | *May show 1 error if TX server times out — restart validator and retry |
| C11 | `11-invalid-observation-dual-value-types.json` | Observation | Invalid | Error — both `valueQuantity` and `valueString` |
| C12 | `12-invalid-observation-component-missing-code.json` | Observation | Invalid | Error — component missing required `code` |
| C13 | `13-invalid-bundle-transaction-broken-reference.json` | Bundle | Invalid | Error — transaction entry references missing resource |
| C14 | `14-invalid-patient-extension-wrong-value-type.json` | Patient | Invalid | Error — extension value type mismatch |
| C15 | `15-stress-clinical-document-bundle.json` | Bundle | Mixed | Errors + warnings — document bundle with valid + invalid nested resources |

Run the same cross-check workflow as the parent suite: upload here, compare counts/messages with Inferno.
