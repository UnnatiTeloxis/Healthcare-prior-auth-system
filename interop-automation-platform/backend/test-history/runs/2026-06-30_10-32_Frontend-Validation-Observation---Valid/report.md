# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-30T10:32:05
**Run ID:** `2026-06-30_10-32_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 2 warning(s) and 2 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 2

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/observation-category\|0.1.0 |
| IssueSeverity.information | Observation.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
