# Frontend Validation: MedicationRequest - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T09:52:37
**Run ID:** `2026-06-29_09-52_Frontend-Validation-MedicationRequest---Valid`

## Summary

Validation successful with 6 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 6
- **Informational:** 0

## Validation Details

**Resource Type:** MedicationRequest
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | MedicationRequest.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/medicationrequest-category\|4.0.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].timing.repeat.periodUnit | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].type | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/dose-rate-type\|4.0.1 |
| IssueSeverity.warning | MedicationRequest.dosageInstruction[0].doseAndRate[0].dose.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | MedicationRequest.dispenseRequest.quantity | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | MedicationRequest | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
