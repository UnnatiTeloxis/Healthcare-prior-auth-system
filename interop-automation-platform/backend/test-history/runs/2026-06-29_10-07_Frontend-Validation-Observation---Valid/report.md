# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:07:52
**Run ID:** `2026-06-29_10-07_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 1 warning(s) and 3 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 1
- **Informational:** 3

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.component[0].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.component[1].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation | Validate Observation against the Blood pressure systolic and diastolic profile (http://hl7.org/fhir/StructureDefinition/bp) which is required by the FHIR specification because the LOINC code 85354-9 was found |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
