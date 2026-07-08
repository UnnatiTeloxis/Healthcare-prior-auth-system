# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-30T04:42:13
**Run ID:** `2026-06-30_04-42_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 3 error(s) | Missing required: Observation

## Issue Counts

- **Errors:** 3
- **Warnings:** 2
- **Informational:** 4

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation | Observation.category: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bodytemp\|4.0.1) |
| IssueSeverity.error | Observation | Slice 'Observation.category:VSCat': a matching slice is required, but not found (from http://hl7.org/fhir/StructureDefinition/bodytemp\|4.0.1). Note that other slices are allowed in addition to this required slice |
| IssueSeverity.error | Observation | Unrecognized property 'valueString' |
| IssueSeverity.information | Observation.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.value.ofType(Quantity).code | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.value.ofType(Quantity).code | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/ucum-bodytemp\|4.0.1 |
| IssueSeverity.information | Observation | Validate Observation against the Body temperature profile (http://hl7.org/fhir/StructureDefinition/bodytemp) which is required by the FHIR specification because the LOINC code 8310-5 was found |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
