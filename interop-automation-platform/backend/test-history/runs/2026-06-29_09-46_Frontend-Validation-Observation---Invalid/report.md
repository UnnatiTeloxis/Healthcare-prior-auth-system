# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:46:20
**Run ID:** `2026-06-29_09-46_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 3 error(s) | Missing required: Observation.component[0]

## Issue Counts

- **Errors:** 3
- **Warnings:** 5
- **Informational:** 0

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
| IssueSeverity.warning | Observation.component[0] | This element does not match any known slice defined in the profile http://hl7.org/fhir/StructureDefinition/bp\|4.0.1 (this may not be a problem, but you should check that it's not intended to match a slice) |
| IssueSeverity.warning | Observation.component[0].value.ofType(Quantity) | The code provided (http://unitsofmeasure.org#mm[Hg]) is not in the value set 'Vital Signs Units' (http://hl7.org/fhir/ValueSet/ucum-vitals-common\|4.0.1), and a code should come from this value set unless it has no suitable code (the validator cannot judge what is suitable) |
| IssueSeverity.warning | Observation.component[1].value.ofType(Quantity) | The code provided (http://unitsofmeasure.org#mm[Hg]) is not in the value set 'Vital Signs Units' (http://hl7.org/fhir/ValueSet/ucum-vitals-common\|4.0.1), and a code should come from this value set unless it has no suitable code (the validator cannot judge what is suitable) |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
