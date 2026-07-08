# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-30T04:29:21
**Run ID:** `2026-06-30_04-29_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 3 error(s) | Missing required: Observation.component[0]

## Issue Counts

- **Errors:** 3
- **Warnings:** 4
- **Informational:** 4

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
| IssueSeverity.information | Observation.component[0].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.component[1].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation | Validate Observation against the Blood pressure systolic and diastolic profile (http://hl7.org/fhir/StructureDefinition/bp) which is required by the FHIR specification because the LOINC code 85354-9 was found |
| IssueSeverity.information | Observation.component[0] | This element does not match any known slice defined in the profile http://hl7.org/fhir/StructureDefinition/bp\|4.0.1 (this may not be a problem, but you should check that it's not intended to match a slice) |
| IssueSeverity.warning | Observation.code | None of the codings provided are in the value set 'Vital Signs' (http://hl7.org/fhir/ValueSet/observation-vitalsignresult\|4.0.1), and a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = http://loinc.org#85354-9) |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation.code.coding[0].display | Wrong Display Name 'Blood pressure panel' for http://loinc.org#85354-9. Valid display is 'Blood pressure panel with all children optional' (en) (for the language(s) 'en') |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
