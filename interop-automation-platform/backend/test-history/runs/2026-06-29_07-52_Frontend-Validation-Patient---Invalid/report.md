# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T07:52:12
**Run ID:** `2026-06-29_07-52_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 2
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.warning | Patient.address[0].state | The value provided ('WI') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'WI' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [No server available]; The System URI could not be determined for the code 'WI' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0') |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
