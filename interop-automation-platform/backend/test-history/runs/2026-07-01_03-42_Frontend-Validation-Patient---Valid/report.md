# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-07-01T03:42:25
**Run ID:** `2026-07-01_03-42_Frontend-Validation-Patient---Valid`

## Summary

Validation successful with 3 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Patient.address[0].state | The value provided ('OK') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [Error from http://tx.hl7europe.eu/r4: Error: The cache '8ad74ce1-ce04-4989-b744-a0e9e101ee48' is not known to this server. Caches are created with $cache-control?mode=start; this one was never created, or has expired or been released]; The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|6.1.0') |
| IssueSeverity.warning | Patient.communication[0].language | None of the codings provided are in the value set 'Language codes with language and optionally a region modifier' (http://hl7.org/fhir/us/core/ValueSet/simple-language\|6.1.0), and a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = urn:ietf:bcp:47#en-US) |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
