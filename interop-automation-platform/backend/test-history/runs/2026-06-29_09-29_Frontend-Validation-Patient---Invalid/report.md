# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:29:14
**Run ID:** `2026-06-29_09-29_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 5 error(s) | Missing required: Patient.extension[2]

## Issue Counts

- **Errors:** 5
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.extension[2].extension[0][url='condition'] | Sub-extension url 'condition' is not defined by the Extension http://hl7.org/fhir/StructureDefinition/patient-disability\|4.0.1 |
| IssueSeverity.error | Patient.extension[2].extension[1][url='period'] | Sub-extension url 'period' is not defined by the Extension http://hl7.org/fhir/StructureDefinition/patient-disability\|4.0.1 |
| IssueSeverity.error | Patient.extension[2] | Extension.extension: max allowed = 0, but found 2 (from http://hl7.org/fhir/StructureDefinition/patient-disability\|4.0.1) |
| IssueSeverity.error | Patient.extension[2] | Extension.value[x]: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/patient-disability\|4.0.1) |
| IssueSeverity.error | Patient.extension[2] | The Extension 'http://hl7.org/fhir/StructureDefinition/patient-disability' definition is for a simple extension, so it must contain a value, not extensions |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
