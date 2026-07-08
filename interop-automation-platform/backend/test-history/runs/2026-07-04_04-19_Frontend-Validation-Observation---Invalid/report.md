# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-04T04:19:39
**Run ID:** `2026-07-04_04-19_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 4
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.code.coding[0] | java.net.SocketTimeoutException: timeout |
| IssueSeverity.warning | Observation.code | None of the codings provided are in the value set 'US Core Laboratory Test Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-laboratory-test-codes\|9.0.0), and a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = http://loinc.org#2339-0) |
| IssueSeverity.warning | Observation.value.ofType(Quantity) | java.net.SocketTimeoutException: timeout |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
