# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:55:45
**Run ID:** `2026-06-29_09-55_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.extension[0] | The Extension 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace' definition allows for the types [Address] but found type boolean |
| IssueSeverity.error | Patient.extension[1].extension[0].value.ofType(string) | The Profile 'http://hl7.org/fhir/StructureDefinition/patient-nationality\|4.0.1' definition allows for the type CodeableConcept but found type string |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
