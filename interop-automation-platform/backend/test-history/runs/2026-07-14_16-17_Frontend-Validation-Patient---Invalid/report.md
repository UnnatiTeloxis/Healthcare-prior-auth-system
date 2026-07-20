# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:17:56
**Run ID:** `2026-07-14_16-17_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed: Server error '504 Gateway Time-out' for url 'https://inferno.healthit.gov/validatorapi/validate'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504

## Issue Counts

- **Errors:** 1
- **Warnings:** 0
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None
**IG:** Base FHIR
**Compliance Score:** 0%
**Execution Time:** 61.590s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | None | Validation service error: Server error '504 Gateway Time-out' for url 'https://inferno.healthit.gov/validatorapi/validate' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504 | validation-service-error | Retry validation; if the problem persists, check the validator service logs. |
