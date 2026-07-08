# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-07-04T03:35:32
**Run ID:** `2026-07-04_03-35_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 2 warning(s) and 1 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Patient.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' does not resolve |
| IssueSeverity.warning | Patient.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
