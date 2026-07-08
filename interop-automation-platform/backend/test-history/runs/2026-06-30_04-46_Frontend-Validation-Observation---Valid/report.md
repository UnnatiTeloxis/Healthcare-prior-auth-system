# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-30T04:46:17
**Run ID:** `2026-06-30_04-46_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 2 warning(s) and 5 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 5

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Observation.component[0].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.component[1].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation.component[2].value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Observation | Validate Observation against the Blood pressure systolic and diastolic profile (http://hl7.org/fhir/StructureDefinition/bp) which is required by the FHIR specification because the LOINC code 85354-9 was found |
| IssueSeverity.information | Observation.component[2] | This element does not match any known slice defined in the profile http://hl7.org/fhir/StructureDefinition/bp\|4.0.1 (this may not be a problem, but you should check that it's not intended to match a slice) |
| IssueSeverity.warning | Observation.component[2].value.ofType(Quantity) | The Coding provided (http://unitsofmeasure.org#/min) was not found in the value set 'Vital Signs Units' (http://hl7.org/fhir/ValueSet/ucum-vitals-common\|4.0.1), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable).  (error message = Error from http://tx.fhir.org/r4: Error: The cache '4fe7be3a-93e7-49e1-9cc6-8ba5d75d638f' is not known to this server. Caches are created with $cache-control?mode=start; this one was never created, or has expired or been released) |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
