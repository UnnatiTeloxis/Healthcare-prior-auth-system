# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:22:02
**Run ID:** `2026-06-29_10-22_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 7 error(s)

## Issue Counts

- **Errors:** 7
- **Warnings:** 17
- **Informational:** 16

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[0].fullUrl | UUIDs must be valid and lowercase (patient-1) |
| IssueSeverity.error | Bundle.entry[0].resource/*Patient/bundle-patient-1*/.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.error | Bundle.entry[1].fullUrl | UUIDs must be valid and lowercase (patient-2) |
| IssueSeverity.error | Bundle.entry[1].resource/*Patient/bundle-patient-2*/.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.error | Bundle.entry[2].fullUrl | UUIDs must be valid and lowercase (obs-height) |
| IssueSeverity.error | Bundle.entry[3].fullUrl | UUIDs must be valid and lowercase (obs-weight) |
| IssueSeverity.error | Bundle.entry[4].fullUrl | UUIDs must be valid and lowercase (obs-glucose) |
| IssueSeverity.information | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.value.ofType(Quantity).code | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.value.ofType(Quantity).code | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/ucum-bodylength\|4.0.1 |
| IssueSeverity.information | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.value.ofType(Quantity).code | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.value.ofType(Quantity).code | Reference to draft ValueSet http://hl7.org/fhir/ValueSet/ucum-bodyweight\|4.0.1 |
| IssueSeverity.information | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/.value.ofType(Quantity) | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.information | Bundle.entry[2].resource/*Observation/bundle-obs-height*/ | Validate Observation against the Body height profile (http://hl7.org/fhir/StructureDefinition/bodyheight) which is required by the FHIR specification because the LOINC code 8302-2 was found |
| IssueSeverity.information | Bundle.entry[2].resource | Validate Observation against the Body height profile (http://hl7.org/fhir/StructureDefinition/bodyheight) which is required by the FHIR specification because the LOINC code 8302-2 was found |
| IssueSeverity.information | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/ | Validate Observation against the Body weight profile (http://hl7.org/fhir/StructureDefinition/bodyweight) which is required by the FHIR specification because the LOINC code 29463-7 was found |
| IssueSeverity.information | Bundle.entry[3].resource | Validate Observation against the Body weight profile (http://hl7.org/fhir/StructureDefinition/bodyweight) which is required by the FHIR specification because the LOINC code 29463-7 was found |
| IssueSeverity.information | Bundle.entry[0].resource/*Patient/bundle-patient-1*/.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' does not resolve |
| IssueSeverity.information | Bundle.entry[1].resource/*Patient/bundle-patient-2*/.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' does not resolve |
| IssueSeverity.information | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs' does not resolve |
| IssueSeverity.information | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs' does not resolve |
| IssueSeverity.information | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/.meta.profile[0] | Canonical URL 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' does not resolve |
| IssueSeverity.warning | Bundle.entry[2].resource/*Observation/bundle-obs-height*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[2].resource | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[3].resource | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[4].resource | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.subject | Entry 0 matches the reference Patient/bundle-patient-1 by type and id but it's fullUrl urn:uuid:patient-1 does not match the full target URL urn:uuid:bundle-patient-1 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.subject | Entry 0 matches the reference Patient/bundle-patient-1 by type and id but it's fullUrl urn:uuid:patient-1 does not match the full target URL urn:uuid:bundle-patient-1 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/.subject | Entry 1 matches the reference Patient/bundle-patient-2 by type and id but it's fullUrl urn:uuid:patient-2 does not match the full target URL urn:uuid:bundle-patient-2 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/bundle-patient-1*/.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Bundle.entry[1].resource/*Patient/bundle-patient-2*/.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Bundle.entry[2].resource/*Observation/bundle-obs-height*/.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Bundle.entry[3].resource/*Observation/bundle-obs-weight*/.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/.meta.profile[0] | Profile reference 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab' has not been checked because it could not be found, and the validator is set to not fetch unknown profiles |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/bundle-patient-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[1].resource/*Patient/bundle-patient-2*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[4].resource/*Observation/bundle-obs-glucose*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
