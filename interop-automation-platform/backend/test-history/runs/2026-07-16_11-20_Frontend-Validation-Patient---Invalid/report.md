# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-16T11:20:25
**Run ID:** `2026-07-16_11-20_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org) |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
