# FHIR Conformance Validator - Test Cases

Test cases organized by Implementation Guide (IG). Upload these files to the FHIR Conformance Validator to verify correct validation behavior.

## How to Use

1. Open the FHIR Conformance Validator at `http://localhost:8000/fhir-validator.html`
2. Select the appropriate **Implementation Guide** from the IG dropdown
3. Upload or paste the test file
4. Click **Validate** and verify the expected result

---

## US Core (hl7.fhir.us.core v9.0.0)

| # | File | Resource Type | Expected Result | Scenarios Covered |
|---|------|---------------|-----------------|-------------------|
| 1 | `01-patient-valid.json` | Patient | ✅ PASS | All required fields, race/ethnicity extensions, narrative |
| 2 | `02-patient-missing-required.json` | Patient | ❌ FAIL (errors) | Missing `identifier` (required by US Core) |
| 3 | `03-patient-invalid-values.json` | Patient | ❌ FAIL (errors) | Invalid `gender` code, invalid `birthDate` format, bad `telecom.system` |
| 4 | `04-observation-vital-signs-valid.json` | Observation | ✅ PASS | Blood pressure with systolic/diastolic components, LOINC codes |
| 5 | `05-observation-missing-required.json` | Observation | ❌ FAIL (errors) | Missing `subject`, `category`, `effectiveDateTime`, `component` |
| 6 | `06-condition-valid.json` | Condition | ✅ PASS | Encounter diagnosis with SNOMED, clinical/verification status |
| 7 | `07-condition-invalid.json` | Condition | ❌ FAIL (errors) | Invalid `clinicalStatus` code, wrong category system, missing `code` |
| 8 | `08-encounter-valid.json` | Encounter | ✅ PASS | Ambulatory encounter with type, period, location |
| 9 | `09-medication-request-valid.json` | MedicationRequest | ✅ PASS | Active order with RxNorm, dosage instructions |
| 10 | `10-empty-resource.json` | Patient | ❌ FAIL (errors) | Minimal resource missing all required elements |

---

## DaVinci CRD (hl7.fhir.us.davinci-crd v2.2.1)

| # | File | Resource Type | Expected Result | Scenarios Covered |
|---|------|---------------|-----------------|-------------------|
| 1 | `01-coverage-valid.json` | Coverage | ✅ PASS | Active coverage with plan/group classes, proper coding |
| 2 | `02-coverage-missing-fields.json` | Coverage | ❌ FAIL (errors) | Missing `beneficiary`, `payor`, `subscriberId` |
| 3 | `03-service-request-valid.json` | ServiceRequest | ✅ PASS | Order with CPT code, insurance reference, reason |
| 4 | `04-service-request-invalid.json` | ServiceRequest | ❌ FAIL (errors) | Invalid `status`, invalid `intent`, missing code |
| 5 | `05-device-request-valid.json` | DeviceRequest | ✅ PASS | CPAP device order with HCPCS code, insurance |
| 6 | `06-medication-request-valid.json` | MedicationRequest | ✅ PASS | High-cost biologic with RxNorm, dosage, insurance |
| 7 | `07-nutrition-order-invalid.json` | NutritionOrder | ❌ FAIL (errors) | Invalid status/intent, invalid dateTime, wrong code system |

---

## DaVinci DTR (hl7.fhir.us.davinci-dtr v2.2.0)

| # | File | Resource Type | Expected Result | Scenarios Covered |
|---|------|---------------|-----------------|-------------------|
| 1 | `01-questionnaire-response-valid.json` | QuestionnaireResponse | ✅ PASS | Completed response with multiple answer types |
| 2 | `02-questionnaire-response-invalid.json` | QuestionnaireResponse | ❌ FAIL (errors) | Invalid `status`, missing `questionnaire` |
| 3 | `03-questionnaire-response-incomplete.json` | QuestionnaireResponse | ⚠️ WARNINGS | In-progress response (partial answers) |
| 4 | `04-task-valid.json` | Task | ✅ PASS | Questionnaire completion task with input |
| 5 | `05-task-invalid.json` | Task | ❌ FAIL (errors) | Invalid status/intent, bad date format |
| 6 | `06-questionnaire-valid.json` | Questionnaire | ✅ PASS | Adaptive questionnaire with items |
| 7 | `07-parameters-valid.json` | Parameters | ✅ PASS | DTR launch context with inline resources |

---

## DaVinci PAS (hl7.fhir.us.davinci-pas v2.2.1)

| # | File | Resource Type | Expected Result | Scenarios Covered |
|---|------|---------------|-----------------|-------------------|
| 1 | `01-claim-valid.json` | Claim | ✅ PASS | Prior auth request with diagnosis, items, insurance |
| 2 | `02-claim-missing-required.json` | Claim | ❌ FAIL (errors) | Missing `patient`, `provider`, `insurer`, `insurance`, `item` |
| 3 | `03-claim-invalid-values.json` | Claim | ❌ FAIL (errors) | Invalid status/use/type codes, bad date, missing references |
| 4 | `04-claim-response-valid.json` | ClaimResponse | ✅ PASS | Approved auth response with adjudication |
| 5 | `05-bundle-submit-valid.json` | Bundle | ✅ PASS | PAS request bundle with Claim + Patient + Coverage |
| 6 | `06-bundle-invalid.json` | Bundle | ❌ FAIL (errors) | Invalid bundle type, malformed entries |
| 7 | `07-organization-valid.json` | Organization | ✅ PASS | Payer organization with NPI, contact info |
| 8 | `08-encounter-valid.json` | Encounter | ✅ PASS | Planned inpatient admission |

---

## Scenario Coverage Matrix

| Scenario Type | US Core | CRD | DTR | PAS |
|---------------|---------|-----|-----|-----|
| Valid resource (all fields) | ✅ | ✅ | ✅ | ✅ |
| Missing required fields | ✅ | ✅ | ✅ | ✅ |
| Invalid coded values | ✅ | ✅ | ✅ | ✅ |
| Invalid data types | ✅ | ✅ | ✅ | ✅ |
| Empty/minimal resource | ✅ | ✅ | ✅ | ✅ |
| Multiple resource types | ✅ | ✅ | ✅ | ✅ |
| Bundle validation | — | — | — | ✅ |
| Extension validation | ✅ | — | — | — |
| Nested resources | — | — | ✅ | ✅ |
| In-progress/partial | — | — | ✅ | — |

---

## Batch Testing

You can upload all files from a single IG directory at once using the **Batch Mode** in Step 1. This validates all files concurrently and shows a summary of pass/fail results.
