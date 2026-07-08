# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T09:27:20
**Run ID:** `2026-06-29_09-27_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 2 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Patient.contained[0]/*Organization/managing-org*/.type[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/organization-type\|0.1.0 |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
