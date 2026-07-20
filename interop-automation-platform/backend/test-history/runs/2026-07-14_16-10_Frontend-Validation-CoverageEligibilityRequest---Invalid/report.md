# Frontend Validation: CoverageEligibilityRequest - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:10:54
**Run ID:** `2026-07-14_16-10_Frontend-Validation-CoverageEligibilityRequest---Invalid`

## Summary

Validation failed: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fdavinci-crd%2FStructureDefinition%2Fprofile-coverageeligibilityrequest'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500

## Issue Counts

- **Errors:** 1
- **Warnings:** 0
- **Informational:** 0

## Validation Details

**Resource Type:** CoverageEligibilityRequest
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/davinci-crd/StructureDefinition/profile-coverageeligibilityrequest
**IG:** hl7.fhir.us.davinci-crd
**Compliance Score:** 0%
**Execution Time:** 2.972s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | None | Validation service error: Server error '500 Server Error' for url 'https://inferno.healthit.gov/validatorapi/validate?profile=http%3A%2F%2Fhl7.org%2Ffhir%2Fus%2Fdavinci-crd%2FStructureDefinition%2Fprofile-coverageeligibilityrequest' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500 | validation-service-error | Retry validation; if the problem persists, check the validator service logs. |
