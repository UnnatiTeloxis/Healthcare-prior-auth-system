# Frontend Validation: MedicationRequest - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T09:44:21
**Run ID:** `2026-06-29_09-44_Frontend-Validation-MedicationRequest---Valid`

## Summary

Validation successful with 5 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 5
- **Informational:** 0

## Validation Details

**Resource Type:** MedicationRequest
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | MedicationRequest.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/medicationrequest-category\|0.1.0 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].type | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/dose-rate-type\|0.1.0 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].dose.ofType(Quantity) | UCUM Codes that contain human readable annotations like {tablet} can be misleading (e.g. they are ignored when comparing units). Best Practice is not to depend on annotations in the UCUM code, so this usage should be checked |
| IssueSeverity.warning | MedicationRequest.dispenseRequest.quantity | UCUM Codes that contain human readable annotations like {tablet} can be misleading (e.g. they are ignored when comparing units). Best Practice is not to depend on annotations in the UCUM code, so this usage should be checked |
| IssueSeverity.warning | MedicationRequest | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
