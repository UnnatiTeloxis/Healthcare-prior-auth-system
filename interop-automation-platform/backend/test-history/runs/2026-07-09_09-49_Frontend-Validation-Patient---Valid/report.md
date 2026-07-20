# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-07-09T09:49:02
**Run ID:** `2026-07-09_09-49_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 5 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 5
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Patient.address[0].state | A definition for CodeSystem 'https://www.usps.com/' could not be found, so the code cannot be validated; Unable to check whether the code is in the value set 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|3.1.1' because the code system https://www.usps.com/ was not found |
| IssueSeverity.warning | Patient.communication[0].language.coding[0].system | A definition for CodeSystem 'urn:ietf:bcp:47' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Patient.communication[0].language | Unable to check whether the code is in the value set 'http://hl7.org/fhir/ValueSet/languages\|4.0.1' because the code system urn:ietf:bcp:47 was not found |
| IssueSeverity.warning | Patient.communication[0].language | Unable to check whether the code is in the value set 'http://hl7.org/fhir/us/core/ValueSet/simple-language\|3.1.1' because the code system urn:ietf:bcp:47 was not found |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
