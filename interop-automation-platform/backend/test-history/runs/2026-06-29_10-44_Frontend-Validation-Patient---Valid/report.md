# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:44:09
**Run ID:** `2026-06-29_10-44_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 2 warning(s) and 3 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 3

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | Patient.extension[0].extension[0].value.ofType(CodeableConcept) | Reference to draft CodeSystem urn:iso:std:iso:3166\|1.0.0 |
| IssueSeverity.information | Patient.communication[0].language | Reference to draft CodeSystem urn:ietf:bcp:47\| |
| IssueSeverity.information | Patient.communication[1].language | Reference to draft CodeSystem urn:ietf:bcp:47\| |
| IssueSeverity.warning | Patient.extension[2].value.ofType(CodeableConcept).coding[0].display | Wrong Display Name 'Visual impairment' for http://snomed.info/sct#228158008. Valid display is 'Walking disability' (en) (for the language(s) 'en') |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
