# Frontend Validation: Encounter - Valid

**Status:** PASS
**Timestamp:** 2026-06-30T04:43:52
**Run ID:** `2026-06-30_04-43_Frontend-Validation-Encounter---Valid`

## Summary

Validation successful with 1 warning(s) and 2 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 1
- **Informational:** 2

## Validation Details

**Resource Type:** Encounter
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Encounter.reasonCode[0] | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/encounter-reason\|4.0.1 |
| IssueSeverity.information | Encounter.hospitalization.dischargeDisposition | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/discharge-disposition\|0.1.0 |
| IssueSeverity.warning | Encounter | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
