# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:02:31
**Run ID:** `2026-06-29_10-02_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 7 error(s) | Missing required: Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Invalid values in: Bundle.entry[3].fullUrl

## Issue Counts

- **Errors:** 7
- **Warnings:** 6
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[3].resource/*Patient/txn-patient-bad*/.gender | The value provided ('not-a-valid-gender') was not found in the value set 'AdministrativeGender' (http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'not-a-valid-gender' in the ValueSet 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1'; The provided code '#not-a-valid-gender' was not found in the value set 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1') |
| IssueSeverity.error | Bundle.entry[3].fullUrl | UUIDs must be valid and lowercase (invalid-request-entry) |
| IssueSeverity.error | Bundle.entry[2] | Bundle entry missing fullUrl |
| IssueSeverity.error | Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Observation.category: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/heartrate\|4.0.1) |
| IssueSeverity.error | Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Observation.effective[x]: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/heartrate\|4.0.1) |
| IssueSeverity.error | Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Slice 'Observation.category:VSCat': a matching slice is required, but not found (from http://hl7.org/fhir/StructureDefinition/heartrate\|4.0.1). Note that other slices are allowed in addition to this required slice |
| IssueSeverity.error | Bundle | Constraint failed: bdl-3: 'entry.request mandatory for batch/transaction/history, otherwise prohibited' |
| IssueSeverity.warning | Bundle.entry[1].resource/*Observation/txn-obs-1*/.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[1].resource/*Observation/txn-obs-1*/ | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/txn-patient-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[2].resource/*Condition/txn-condition-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[3].resource/*Patient/txn-patient-bad*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
