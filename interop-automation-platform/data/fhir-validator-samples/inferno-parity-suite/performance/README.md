# Performance / Speed Test Suite

Large, structurally valid FHIR R4 JSON files for measuring validation throughput,
batch timing, and UI responsiveness. All samples use proper terminology systems
(no `example.org` identifier URLs) and valid resource shapes.

Compare timing with [Inferno Resource Validator](https://inferno.healthit.gov/validator/)
using the same file and **no profile selected** (base FHIR R4), unless noted.

## Files

| File | Size (approx) | Contents | Use case |
|------|---------------|----------|----------|
| `perf-01-large-patient-rich.json` | ~72 KB | 1 Patient with 50 identifiers, 100 telecoms, 50 addresses, 100 contacts | Single large resource |
| `perf-02-bundle-100-patients.json` | ~207 KB | Collection Bundle, 100 Patients | Batch upload / multi-patient |
| `perf-03-bundle-250-observations.json` | ~279 KB | 1 Patient + 250 vital-sign Observations | Terminology + repetition |
| `perf-04-bundle-75-mixed-clinical.json` | ~342 KB | 75 Patients + Observations + Conditions + Encounters | Mixed clinical workload |
| `perf-05-bundle-500-observations.json` | ~557 KB | 1 Patient + 500 vital-sign Observations | Heavy stress / max timing |

## Expected validation behavior

- All files are **valid base FHIR R4** structure (no intentional errors).
- Expect **warnings** similar to other parity samples (`dom-6` narrative, performer best practice, draft CodeSystem info where applicable).
- Issue **counts** should match Inferno for the same file when validator config aligns (TX server, US Core preload for `meta.profile` resources).

## How to test speed

### Single file (UI)

1. Open FHIR Conformance Validator → **Single File** or **Batch Mode**.
2. Upload a `perf-*.json` file.
3. Note execution time on the Results step (`executionTime` in report).

### Batch mode (UI)

1. Select **Batch Mode** and add `perf-02` through `perf-05` (or all five).
2. Run batch validation and review per-file timing in batch progress.

### CLI / API

```powershell
cd interop-automation-platform\backend
python scripts/parity_check_all_samples.py
```

Or POST directly:

```powershell
curl -X POST http://localhost:8000/api/v1/fhir/validate `
  -H "Content-Type: application/json" `
  -d "{\"resource\": $(Get-Content -Raw ..\\data\\fhir-validator-samples\\inferno-parity-suite\\performance\\perf-05-bundle-500-observations.json), \"profiles\": [], \"resource_type\": \"Bundle\"}"
```

## Regenerating samples

```powershell
cd interop-automation-platform\data\fhir-validator-samples\inferno-parity-suite
python scripts/generate_performance_samples.py
```

Edit counts in `scripts/generate_performance_samples.py` to produce larger or smaller files.
