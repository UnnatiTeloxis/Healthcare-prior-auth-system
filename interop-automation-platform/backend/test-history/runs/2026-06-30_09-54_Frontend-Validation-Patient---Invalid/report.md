# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-30T09:54:04
**Run ID:** `2026-06-30_09-54_Frontend-Validation-Patient---Invalid`

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
| IssueSeverity.error | Patient.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
