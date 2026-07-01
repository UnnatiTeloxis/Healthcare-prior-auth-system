# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:34:45
**Run ID:** `2026-06-29_10-34_Frontend-Validation-Patient---Invalid`

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
| IssueSeverity.error | Patient.birthDate | Not a valid date ('15-06-1985' doesn't meet format requirements for date) |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
