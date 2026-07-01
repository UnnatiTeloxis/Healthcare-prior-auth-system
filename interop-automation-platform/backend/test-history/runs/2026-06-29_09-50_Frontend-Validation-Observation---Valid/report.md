# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T09:50:15
**Run ID:** `2026-06-29_09-50_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 5 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 5
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Observation.component[0].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Observation.component[1].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Observation.component[2].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Observation.component[2] | This element does not match any known slice defined in the profile http://hl7.org/fhir/StructureDefinition/bp\|4.0.1 (this may not be a problem, but you should check that it's not intended to match a slice) |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
