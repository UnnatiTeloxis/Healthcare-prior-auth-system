# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:21:59
**Run ID:** `2026-06-29_10-21_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.error | Patient.birthDate | Not a valid date ('15-03-1986' doesn't meet format requirements for date) |
| IssueSeverity.information | Patient.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' does not resolve |
| IssueSeverity.warning | Patient.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
