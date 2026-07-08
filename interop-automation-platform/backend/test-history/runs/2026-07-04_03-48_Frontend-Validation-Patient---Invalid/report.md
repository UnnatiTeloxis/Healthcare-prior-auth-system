# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-04T03:48:17
**Run ID:** `2026-07-04_03-48_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.gender | The value provided ('unknown-gender-value') was not found in the value set 'AdministrativeGender' (http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'unknown-gender-value' in the ValueSet 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1'; The provided code '#unknown-gender-value' was not found in the value set 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1') |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
