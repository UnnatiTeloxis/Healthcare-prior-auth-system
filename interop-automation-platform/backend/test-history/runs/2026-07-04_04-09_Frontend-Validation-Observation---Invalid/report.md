# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-04T04:09:38
**Run ID:** `2026-07-04_04-09_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 4
- **Informational:** 1

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.code.coding[0] | java.net.SocketTimeoutException: timeout |
| IssueSeverity.information | Observation.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' does not resolve |
| IssueSeverity.warning | Observation.value.ofType(Quantity) | java.net.SocketTimeoutException: timeout |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
