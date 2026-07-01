# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:16:42
**Run ID:** `2026-06-29_09-16_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 8 error(s)

## Issue Counts

- **Errors:** 8
- **Warnings:** 10
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[5].resource/*Patient/stress-bad-url-patient*/.gender | The value provided ('unknown-gender') was not found in the value set 'AdministrativeGender' (http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'unknown-gender' in the ValueSet 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1'; The provided code '#unknown-gender' was not found in the value set 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1') |
| IssueSeverity.error | Bundle.entry[0].fullUrl | UUIDs must be valid and lowercase (patient-1) |
| IssueSeverity.error | Bundle.entry[0].resource/*Patient/stress-patient-1*/.identifier[0].system | Example URLs are not allowed in this context (http://example.org/fhir/identifier/mrn) |
| IssueSeverity.error | Bundle.entry[1].fullUrl | UUIDs must be valid and lowercase (patient-2) |
| IssueSeverity.error | Bundle.entry[2].fullUrl | UUIDs must be valid and lowercase (obs-height) |
| IssueSeverity.error | Bundle.entry[3].fullUrl | UUIDs must be valid and lowercase (obs-glucose) |
| IssueSeverity.error | Bundle.entry[4].fullUrl | UUIDs must be valid and lowercase (condition-1) |
| IssueSeverity.error | Bundle.entry[0] | The fullUrl 'http://example.org/fhir/Patient/bad-entry' looks like a RESTful server URL, so it must end with the correct type and id (/Patient/stress-bad-url-patient) |
| IssueSeverity.warning | Bundle.entry[2].resource/*Observation/stress-obs-height*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/stress-obs-glucose*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[2].resource/*Observation/stress-obs-height*/.subject | Entry 0 matches the reference Patient/stress-patient-1 by type and id but it's fullUrl urn:uuid:patient-1 does not match the full target URL urn:uuid:stress-patient-1 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/stress-obs-glucose*/.subject | Entry 0 matches the reference Patient/stress-patient-1 by type and id but it's fullUrl urn:uuid:patient-1 does not match the full target URL urn:uuid:stress-patient-1 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[4].resource/*Condition/stress-condition-1*/.subject | Entry 0 matches the reference Patient/stress-patient-1 by type and id but it's fullUrl urn:uuid:patient-1 does not match the full target URL urn:uuid:stress-patient-1 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/stress-patient-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[1].resource/*Patient/stress-patient-2*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/stress-obs-glucose*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[4].resource/*Condition/stress-condition-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[5].resource/*Patient/stress-bad-url-patient*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
