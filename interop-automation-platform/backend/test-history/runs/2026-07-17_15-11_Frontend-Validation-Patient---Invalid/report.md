# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-17T15:11:01
**Run ID:** `2026-07-17_15-11_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/cdmh/StructureDefinition/cdmh-patient


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Patient.communication[0].language.coding[0] | java.net.SocketTimeoutException: timeout |
| IssueSeverity.error | Patient.communication[0].language | The value set 'http://hl7.org/fhir/us/core/ValueSet/simple-language\|4.0.0' validation (local) took too long to process (>60sec) |
| IssueSeverity.warning | Patient.address[0].state | The value provided ('OK') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|4.0.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|4.0.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [Error from http://tx.fhir.org/r4: Error: The cache '1d24ebae-c93c-4cc7-a934-21b592a872cb' is not known to this server. Caches are created with $cache-control?mode=start; this one was never created, or has expired or been released]; The System URI could not be determined for the code 'OK' in the ValueSet 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|4.0.0') |
| IssueSeverity.warning | Patient.communication[0].language | None of the codings provided are in the value set 'Language codes with language and optionally a region modifier' (http://hl7.org/fhir/us/core/ValueSet/simple-language\|4.0.0), and a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = urn:ietf:bcp:47#en-US) |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
