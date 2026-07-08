# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T07:45:42
**Run ID:** `2026-06-29_07-45_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 2 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Patient.address[0].state | The value provided ('OK') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [No server available]; The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0') |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
