# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:34:45
**Run ID:** `2026-06-29_10-34_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 5 error(s) | Missing required: Observation

## Issue Counts

- **Errors:** 5
- **Warnings:** 3
- **Informational:** 1

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.value[x] | The property valueQuantity must be an Object, not a Primitive property (at Observation.value[x]) |
| IssueSeverity.error | Observation | Observation.category: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bodytemp\|4.0.1) |
| IssueSeverity.error | Observation | Observation.effective[x]: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bodytemp\|4.0.1) |
| IssueSeverity.error | Observation | Slice 'Observation.category:VSCat': a matching slice is required, but not found (from http://hl7.org/fhir/StructureDefinition/bodytemp\|4.0.1). Note that other slices are allowed in addition to this required slice |
| IssueSeverity.error | Observation | Constraint failed: vs-2: 'If there is no component or hasMember element then either a value[x] or a data absent reason must be present.' (defined in http://hl7.org/fhir/StructureDefinition/vitalsigns) |
| IssueSeverity.information | Observation | Validate Observation against the Body temperature profile (http://hl7.org/fhir/StructureDefinition/bodytemp) which is required by the FHIR specification because the LOINC code 8310-5 was found |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
