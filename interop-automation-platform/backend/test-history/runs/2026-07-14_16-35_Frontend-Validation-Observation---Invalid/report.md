# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:35:59
**Run ID:** `2026-07-14_16-35_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fcore%2FStructureDefinition%2Fus-core-observation%7C9.0.0'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500

## Issue Counts

- **Errors:** 1
- **Warnings:** 0
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation|9.0.0
**IG:** hl7.fhir.us.core#9.0.0
**Compliance Score:** 0%
**Execution Time:** 0.520s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | None | Validation service error: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fcore%2FStructureDefinition%2Fus-core-observation%7C9.0.0' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500 | validation-service-error | Retry validation; if the problem persists, check the validator service logs. |
