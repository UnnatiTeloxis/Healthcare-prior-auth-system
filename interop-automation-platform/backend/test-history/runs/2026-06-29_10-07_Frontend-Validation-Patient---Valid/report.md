# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:07:54
**Run ID:** `2026-06-29_10-07_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 1 warning(s) and 1 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 1
- **Informational:** 1

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Patient.contained[0]/*Organization/managing-org*/.type[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/organization-type\|4.0.1 |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
