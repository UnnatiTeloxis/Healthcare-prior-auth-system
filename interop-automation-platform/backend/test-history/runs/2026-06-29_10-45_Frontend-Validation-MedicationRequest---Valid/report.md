# Frontend Validation: MedicationRequest - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:45:20
**Run ID:** `2026-06-29_10-45_Frontend-Validation-MedicationRequest---Valid`

## Summary

Validation successful with 2 warning(s) and 5 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 5

## Validation Details

**Resource Type:** MedicationRequest
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | MedicationRequest.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/medicationrequest-category\|4.0.1 |
| IssueSeverity.information | MedicationRequest.dosageInstruction[0].timing.repeat.periodUnit | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | MedicationRequest.dosageInstruction[0].doseAndRate[0].type | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/dose-rate-type\|4.0.1 |
| IssueSeverity.information | MedicationRequest.dosageInstruction[0].doseAndRate[0].dose.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | MedicationRequest.dispenseRequest.quantity | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | MedicationRequest.medication.ofType(CodeableConcept).coding[0] | A definition for CodeSystem 'http://www.nlm.nih.gov/research/umls/rxnorm' could not be found, so the code cannot be validated |
| IssueSeverity.warning | MedicationRequest | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
