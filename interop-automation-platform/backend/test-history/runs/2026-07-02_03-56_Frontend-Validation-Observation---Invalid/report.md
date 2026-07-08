# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-02T03:56:15
**Run ID:** `2026-07-02_03-56_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 4
- **Informational:** 1

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.code.coding[0] | Error from http://tx.fhir.org/r4: Unparseable HTML |
| IssueSeverity.error | Observation.value.ofType(Quantity).code | The value provided ('cm') was not found in the value set 'Body Length Units' (http://hl7.org/fhir/ValueSet/ucum-bodylength\|4.0.1), and a code is required from this value set  (error message = Error from http://tx.fhir.org/r4: Unparseable HTML) |
| IssueSeverity.information | Observation | Validate Observation against the Body height profile (http://hl7.org/fhir/StructureDefinition/bodyheight) which is required by the FHIR specification because the LOINC code 8302-2 was found |
| IssueSeverity.warning | Observation.code | None of the codings provided are in the value set 'Vital Signs' (http://hl7.org/fhir/ValueSet/observation-vitalsignresult\|4.0.1), and a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = http://loinc.org#8302-2) |
| IssueSeverity.warning | Observation.value.ofType(Quantity) | Error from http://tx.fhir.org/r4: Unparseable HTML |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
