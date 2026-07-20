# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-07-17T14:18:46
**Run ID:** `2026-07-17_14-18_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 4 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 4
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** http://hl7.org/fhir/us/cdmh/StructureDefinition/cdmh-patient


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Patient.address[0].state | The value provided ('OK') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [No server available]; The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0') |
| IssueSeverity.warning | Patient.communication[0].language.coding[0].system | A definition for CodeSystem 'urn:ietf:bcp:47' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Patient.communication[0].language | Unable to check whether the code is in the value set 'http://hl7.org/fhir/us/core/ValueSet/simple-language\|6.1.0' because the code system urn:ietf:bcp:47 was not found |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
