# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:48:06
**Run ID:** `2026-06-29_09-48_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 4
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.extension[2] | The Extension 'http://hl7.org/fhir/StructureDefinition/patient-disability' definition allows for the types [CodeableConcept] but found type boolean |
| IssueSeverity.warning | Patient.extension[0].extension[0].value.ofType(CodeableConcept) | Reference to draft CodeSystem urn:iso:std:iso:3166\|1.0.0 |
| IssueSeverity.warning | Patient.communication[0].language | Reference to draft CodeSystem urn:ietf:bcp:47\| |
| IssueSeverity.warning | Patient.communication[1].language | Reference to draft CodeSystem urn:ietf:bcp:47\| |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
