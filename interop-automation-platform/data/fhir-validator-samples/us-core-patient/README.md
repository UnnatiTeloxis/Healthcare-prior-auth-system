# US Core Patient Validator Samples

Upload these JSON files in the FHIR Conformance Validator UI or POST them to `/api/v1/fhir/validate`.

All files target:

`http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient`

## Files

- `01-valid-complete-us-core-patient.json` - complete Patient with identifier, name, gender, birthDate, telecom, address, and language.
- `02-valid-minimal-us-core-patient.json` - compact Patient containing the core required elements.
- `03-invalid-missing-identifier.json` - missing `Patient.identifier`.
- `04-invalid-missing-name.json` - missing `Patient.name`.
- `05-invalid-bad-gender-code.json` - invalid `Patient.gender` code.
- `06-invalid-birthdate-format.json` - invalid FHIR date format.
- `07-invalid-wrong-resource-type.json` - Observation submitted against the Patient profile.

## Verified Results

These were checked against the real backend endpoint at `/api/v1/fhir/validate`.

- `01-valid-complete-us-core-patient.json` - valid, 0 errors.
- `02-valid-minimal-us-core-patient.json` - valid, 0 errors.
- `03-invalid-missing-identifier.json` - invalid, missing required identifier.
- `04-invalid-missing-name.json` - invalid, missing required name.
- `05-invalid-bad-gender-code.json` - invalid, bad administrative gender code.
- `06-invalid-birthdate-format.json` - invalid, bad FHIR date format.
- `07-invalid-wrong-resource-type.json` - invalid, wrong resource type for Patient profile.
