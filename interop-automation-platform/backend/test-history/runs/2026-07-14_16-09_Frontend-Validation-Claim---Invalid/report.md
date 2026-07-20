# Frontend Validation: Claim - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:09:48
**Run ID:** `2026-07-14_16-09_Frontend-Validation-Claim---Invalid`

## Summary

Validation failed: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fdavinci-pas%2FStructureDefinition%2Fprofile-claim'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500

## Issue Counts

- **Errors:** 1
- **Warnings:** 0
- **Informational:** 0

## Validation Details

**Resource Type:** Claim
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/davinci-pas/StructureDefinition/profile-claim
**IG:** hl7.fhir.us.davinci-pas
**Compliance Score:** 0%
**Execution Time:** 3.858s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | None | Validation service error: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fdavinci-pas%2FStructureDefinition%2Fprofile-claim' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500 | validation-service-error | Retry validation; if the problem persists, check the validator service logs. |
