# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-13T16:28:03
**Run ID:** `2026-07-13_16-28_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 1 error(s) | Missing required: Patient.name

## Issue Counts

- **Errors:** 1
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
**IG:** hl7.fhir.us.core#6.1.0
**Compliance Score:** 65%
**Execution Time:** 0.003s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | Patient.name | Patient.name: minimum required = 1, but only found 0 | us-core-patient-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.warning | Patient.gender | The code 'x' is an invalid code not found in the value set binding | us-core-patient-terminology | Use a code from the value set required by the selected IG profile. |
