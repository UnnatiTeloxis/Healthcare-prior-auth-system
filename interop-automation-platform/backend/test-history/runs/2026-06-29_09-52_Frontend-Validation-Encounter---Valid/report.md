# Frontend Validation: Encounter - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T09:52:37
**Run ID:** `2026-06-29_09-52_Frontend-Validation-Encounter---Valid`

## Summary

Validation successful with 2 warning(s) and 1 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** Encounter
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Encounter.reasonCode[0] | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/encounter-reason\|4.0.1 |
| IssueSeverity.warning | Encounter.hospitalization.dischargeDisposition | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/discharge-disposition\|4.0.1 |
| IssueSeverity.warning | Encounter | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
