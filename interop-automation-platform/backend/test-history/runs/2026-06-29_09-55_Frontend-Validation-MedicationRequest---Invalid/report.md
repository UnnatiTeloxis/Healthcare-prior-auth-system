# Frontend Validation: MedicationRequest - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:55:44
**Run ID:** `2026-06-29_09-55_Frontend-Validation-MedicationRequest---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 6
- **Informational:** 0

## Validation Details

**Resource Type:** MedicationRequest
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | MedicationRequest.dosageInstruction[0].doseAndRate[0].dose.ofType(Quantity).code | Unknown code '{tablet}' in the CodeSystem 'http://unitsofmeasure.org' version '2.1.1' |
| IssueSeverity.error | MedicationRequest.dispenseRequest.quantity.code | Unknown code '{tablet}' in the CodeSystem 'http://unitsofmeasure.org' version '2.1.1' |
| IssueSeverity.warning | MedicationRequest.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/medicationrequest-category\|4.0.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].timing.repeat.periodUnit | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].type | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/dose-rate-type\|4.0.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].dose.ofType(Quantity) | UCUM Codes that contain human readable annotations like {tablet} can be misleading (e.g. they are ignored when comparing units). Best Practice is not to depend on annotations in the UCUM code, so this usage should be checked |
| IssueSeverity.warning | MedicationRequest.dispenseRequest.quantity | UCUM Codes that contain human readable annotations like {tablet} can be misleading (e.g. they are ignored when comparing units). Best Practice is not to depend on annotations in the UCUM code, so this usage should be checked |
| IssueSeverity.warning | MedicationRequest | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
