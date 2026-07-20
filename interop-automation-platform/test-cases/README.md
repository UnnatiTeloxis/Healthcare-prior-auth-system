# FHIR Conformance Validator - Test Cases

Test cases organized by **Implementation Guide package ID** — folder names match the IG dropdown exactly (e.g. `hl7.fhir.us.core`).

Each IG folder includes:

| Folder | Purpose |
|--------|---------|
| `simple/` | Minimal valid / invalid resources |
| `complex/` | Rich nested / multi-error payloads |
| `realistic/` | EHR / payer / clinic style files (real-world uploads) |

## Folder layout (28 IGs)

```
test-cases/
├── hl7.fhir.us.core/
├── hl7.fhir.us.ccda/
├── hl7.fhir.us.qicore/
├── hl7.fhir.us.carin-bb/
├── hl7.fhir.us.bulkdata/
├── hl7.fhir.us.odh/
├── hl7.fhir.us.military-service/
├── hl7.fhir.us.vrdr/
├── hl7.fhir.us.mcode/
├── hl7.fhir.us.ecr/
├── hl7.fhir.us.pacio-adi/
├── hl7.fhir.us.pacio-cs/
├── hl7.fhir.us.pacio-fs/
├── hl7.fhir.us.davinci-crd/
├── hl7.fhir.us.davinci-dtr/
├── hl7.fhir.us.davinci-pas/
├── hl7.fhir.us.davinci-pdex/
├── hl7.fhir.us.davinci-cdex/
├── hl7.fhir.us.davinci-pcde/
├── hl7.fhir.us.davinci-alerts/
├── hl7.fhir.us.davinci-drug-formulary/
├── hl7.fhir.us.davinci-deqm/
├── hl7.fhir.us.davinci-ra/
├── hl7.fhir.uv.ipa/
├── hl7.fhir.uv.ips/
├── hl7.fhir.uv.smart-app-launch/
├── hl7.fhir.uv.sdc/
├── hl7.fhir.uv.extensions.r4/
└── hl7.terminology.r4/          (terminology pack — upload-only)
```

## How to Use

1. Open `http://localhost:8000/fhir-validator.html` (sign in first)
2. Select an IG from the dropdown — the package ID (e.g. `hl7.fhir.us.core`) matches the test-case folder name
3. Choose a **Profile** (or leave **Auto**)
4. Use **Test sample** to pick a file — it **loads automatically** from `test-cases/<package-id>/`
5. Click **Validate** — each sample validates with its own JSON and profile

Or paste/upload any JSON manually after selecting the IG.

### Inferno parity note

- Structure / profile errors should match Inferno Resource Validator for the same `?profile=` URL.
- With `DISABLE_TX=true` (default, low latency), some **terminology** checks may appear as warnings instead of live-TX errors.
- **Inferno boot mount** contains terminology only. Resource IGs load when you select them in the dropdown.

Regenerate realistic suites: `python test-cases/_generate_realistic_suite.py`

---

## US Core (`hl7.fhir.us.core`) — v9.0.0

### simple/

| File | Expected | Scenario |
|------|----------|----------|
| `01-patient-minimal-valid.json` | PASS | Minimal US Core Patient |
| `02-patient-minimal-invalid.json` | FAIL | Missing identifier + bad gender |

### complex/

| File | Expected | Scenario |
|------|----------|----------|
| `01-patient-full-valid.json` | PASS | Full Patient w/ race/ethnicity extensions |
| `02-observation-blood-pressure-valid.json` | PASS | BP Observation with components |
| `03-medication-request-full-valid.json` | PASS | Full MedicationRequest with dosage |
| `04-patient-multi-error-invalid.json` | FAIL | Multiple invalid coded values |

---

## Da Vinci CRD (`hl7.fhir.us.davinci-crd`) — v2.2.1

See `hl7.fhir.us.davinci-crd/simple/` and `complex/` for Coverage, ServiceRequest, and MedicationRequest samples.

---

## Batch Testing

Use **Batch Mode** in Step 1 and upload an entire `simple/` or `complex/` folder at once for a pass/fail summary.
