# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:41:56
**Run ID:** `2026-07-14_16-41_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed: Server error '504 Gateway Time-out' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fcore%2FStructureDefinition%2Fus-core-blood-pressure'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504

## Issue Counts

- **Errors:** 1
- **Warnings:** 0
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure
**IG:** hl7.fhir.us.core#6.1.0
**Compliance Score:** 0%
**Execution Time:** 61.779s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | None | Validation service error: Server error '504 Gateway Time-out' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fcore%2FStructureDefinition%2Fus-core-blood-pressure' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504 | validation-service-error | Retry validation; if the problem persists, check the validator service logs. |
