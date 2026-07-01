# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:21:59
**Run ID:** `2026-06-29_10-21_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 3 warning(s) and 2 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 3
- **Informational:** 2

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' does not resolve |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
