# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-01T10:25:14
**Run ID:** `2026-07-01_10-25_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.code.coding[0] | Error from http://tx.fhir.org/r4: Unparseable HTML |
| IssueSeverity.warning | Observation.value.ofType(Quantity) | Error from http://tx.fhir.org/r4: Unparseable HTML |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
