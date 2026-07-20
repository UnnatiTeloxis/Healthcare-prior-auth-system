# Frontend Validation: Patient - Valid

**Status:** PASS
**Timestamp:** 2026-07-14T10:27:07
**Run ID:** `2026-07-14_10-27_Frontend-Validation-Patient---Valid`

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
**IG:** hl7.fhir.us.bulkdata
**Compliance Score:** 85%
**Execution Time:** 3.066s


## Issues

| Severity | Location | Message | Rule | Suggestion |
|----------|----------|---------|------|------------|
| IssueSeverity.warning | Patient.address[0].state | A definition for CodeSystem 'https://www.usps.com/' could not be found, so the code cannot be validated; Unable to check whether the code is in the value set 'http://hl7.org/fhir/us/core/ValueSet/us-core-usps-state\|3.1.1' because the code system https://www.usps.com/ was not found | patient-terminology | Use a code from the value set required by the selected IG profile. |
| IssueSeverity.warning | Patient.communication[0].language.coding[0].system | A definition for CodeSystem 'urn:ietf:bcp:47' could not be found, so the code cannot be validated | patient-terminology | Use a code from the value set required by the selected IG profile. |
| IssueSeverity.warning | Patient.communication[0].language | Unable to check whether the code is in the value set 'http://hl7.org/fhir/ValueSet/languages\|4.0.1' because the code system urn:ietf:bcp:47 was not found | patient-terminology | Use a code from the value set required by the selected IG profile. |
| IssueSeverity.warning | Patient.communication[0].language | Unable to check whether the code is in the value set 'http://hl7.org/fhir/us/core/ValueSet/simple-language\|3.1.1' because the code system urn:ietf:bcp:47 was not found | patient-terminology | Use a code from the value set required by the selected IG profile. |
| IssueSeverity.warning | Patient | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) | patient-profile-conformance | Review the warning and align the element with the IG's guidance when applicable. |
