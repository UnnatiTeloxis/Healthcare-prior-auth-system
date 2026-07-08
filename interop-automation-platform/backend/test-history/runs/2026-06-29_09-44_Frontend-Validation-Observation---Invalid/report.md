# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:44:22
**Run ID:** `2026-06-29_09-44_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 3 error(s) | Missing required: Observation.component[0]

## Issue Counts

- **Errors:** 3
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation | Slice 'Observation.component:SystolicBP': a matching slice is required, but not found (from http://hl7.org/fhir/StructureDefinition/bp\|4.0.1). Note that other slices are allowed in addition to this required slice |
| IssueSeverity.error | Observation.component[0] | Observation.component.code: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/Observation\|4.0.1) |
| IssueSeverity.error | Observation.component[0] | Observation.component.code: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bp\|4.0.1) |
| IssueSeverity.information | Observation.component[0] | This element does not match any known slice defined in the profile http://hl7.org/fhir/StructureDefinition/bp\|4.0.1 (this may not be a problem, but you should check that it's not intended to match a slice) |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
