# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-30T10:22:58
**Run ID:** `2026-06-30_10-22_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 2 warning(s) and 4 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 4

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.value.ofType(Quantity).code | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.value.ofType(Quantity).code | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/ucum-bodylength\|4.0.1 |
| IssueSeverity.information | Observation | Validate Observation against the Body height profile (http://hl7.org/fhir/StructureDefinition/bodyheight) which is required by the FHIR specification because the LOINC code 8302-2 was found |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
