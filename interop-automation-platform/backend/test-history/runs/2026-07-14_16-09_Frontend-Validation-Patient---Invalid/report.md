# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:09:44
**Run ID:** `2026-07-14_16-09_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 3 error(s) | Missing required: Patient

## Issue Counts

- **Errors:** 3
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient|6.1.0
**IG:** hl7.fhir.us.core#6.1.0
**Compliance Score:** 65%
**Execution Time:** 0.499s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | Patient | Patient.gender: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) | us-core-patient|6.1.0-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.error | Patient | Patient.identifier: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) | us-core-patient|6.1.0-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.error | Patient | Patient.name: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) | us-core-patient|6.1.0-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) | us-core-patient|6.1.0-profile-conformance | Review the warning and align the element with the IG's guidance when applicable. |
