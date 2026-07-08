# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:34:44
**Run ID:** `2026-06-29_10-34_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 2 warning(s) and 1 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
