# Frontend Validation: Patient - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-14T16:47:46
**Run ID:** `2026-07-14_16-47_Frontend-Validation-Patient---Invalid`

## Summary

Validation failed with 5 error(s) | Invalid values in: Patient.address[0].use, Patient.gender, Patient.telecom[0].system

## Issue Counts

- **Errors:** 5
- **Warnings:** 2
- **Informational:** 0

## Validation Details

**Resource Type:** Patient
**Valid:** False
**Profiles:** http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
**IG:** hl7.fhir.us.core#6.1.0
**Compliance Score:** 44%
**Execution Time:** 0.001s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.error | Patient.gender | The value provided ('invalid-gender-code') was not found in the value set 'AdministrativeGender' (http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'invalid-gender-code' in the ValueSet 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1'; The provided code '#invalid-gender-code' was not found in the value set 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1') | us-core-patient-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.error | Patient.telecom[0].system | The value provided ('invalid-system') was not found in the value set 'ContactPointSystem' (http://hl7.org/fhir/ValueSet/contact-point-system\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'invalid-system' in the ValueSet 'http://hl7.org/fhir/ValueSet/contact-point-system\|4.0.1'; The provided code '#invalid-system' was not found in the value set 'http://hl7.org/fhir/ValueSet/contact-point-system\|4.0.1') | us-core-patient-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.error | Patient.address[0].use | The value provided ('invalid-use') was not found in the value set 'AddressUse' (http://hl7.org/fhir/ValueSet/address-use\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'invalid-use' in the ValueSet 'http://hl7.org/fhir/ValueSet/address-use\|4.0.1'; The provided code '#invalid-use' was not found in the value set 'http://hl7.org/fhir/ValueSet/address-use\|4.0.1') | us-core-patient-required | Add the required element or provide the allowed data-absent-reason extension. |
| IssueSeverity.error | Patient.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/patients) | us-core-patient-profile-conformance | Update the resource and re-run validation against the selected profile. |
| IssueSeverity.error | Patient.birthDate | Not a valid date ('not-a-date' doesn't meet format requirements for date) | us-core-patient-datatype | Update the resource and re-run validation against the selected profile. |
| IssueSeverity.warning | Patient.address[0].state | The value provided ('INVALID_STATE_TOO_LONG_NOT_A_REAL_CODE') was not found in the value set 'USPS Two Letter Alphabetic Codes' (http://terminology.hl7.org/ValueSet/USPS-State\|1.0.0), and a code should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable)  (error message = The System URI could not be determined for the code 'INVALID_STATE_TOO_LONG_NOT_A_REAL_CODE' in the ValueSet 'http://terminology.hl7.org/ValueSet/USPS-State\|1.0.0': include #0 has system https://www.usps.com/ which could not be found, and the server returned error [Error from http://tx.fhir.org/r4: Error: The cache 'bc82cb9a-8d6a-4b32-a18b-e081c050818d' is not known to this server. Caches are created with $cache-control?mode=start; this one was never created, or has expired or been released]; The System URI could not be determined for the code 'INVALID_STATE_TOO_LONG_NOT_A_REAL_CODE' in the ValueSet 'http://terminology.hl7.org/ValueSet/USPS-State\|1.0.0') | us-core-patient-terminology | Use a code from the value set required by the selected IG profile. |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) | us-core-patient-profile-conformance | Review the warning and align the element with the IG's guidance when applicable. |
