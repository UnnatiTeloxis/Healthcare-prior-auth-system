# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-08T10:20:03
**Run ID:** `2026-07-08_10-20_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 28 error(s) | Invalid values in: Bundle.entry[0], Bundle.entry[7].resource/*Patient/doc-patient-bad*/.gender, Bundle.entry[8]

## Issue Counts

- **Errors:** 28
- **Warnings:** 33
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[2] | Entry 'urn:uuid:patient-doc-001' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[3] | Entry 'urn:uuid:practitioner-doc-001' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[4] | Entry 'urn:uuid:condition-doc-001' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[5] | Entry 'urn:uuid:medstatement-doc-001' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[6] | Entry 'urn:uuid:diagnosticreport-doc-001' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[7] | Entry 'urn:uuid:observation-doc-wbc' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[8] | Entry 'http://example.org/fhir/Patient/invalid-example-url' isn't reachable by traversing links (forward or backward) from the Composition |
| IssueSeverity.error | Bundle.entry[7].resource/*Patient/doc-patient-bad*/.gender | The value provided ('invalid-gender-code') was not found in the value set 'AdministrativeGender' (http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1), and a code is required from this value set  (error message = The System URI could not be determined for the code 'invalid-gender-code' in the ValueSet 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1'; The provided code '#invalid-gender-code' was not found in the value set 'http://hl7.org/fhir/ValueSet/administrative-gender\|4.0.1') |
| IssueSeverity.error | Bundle | Can't find 'Observation/doc-obs-wbc' in the bundle (Bundle.entry[5].resource.result[0]). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:observation-doc-wbc``) |
| IssueSeverity.error | Bundle | Can't find 'Patient/doc-patient-001' in the bundle (Bundle.entry[3].resource.subject). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:patient-doc-001``) |
| IssueSeverity.error | Bundle | Can't find 'Patient/doc-patient-001' in the bundle (Bundle.entry[4].resource.subject). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:patient-doc-001``) |
| IssueSeverity.error | Bundle | Can't find 'Patient/doc-patient-001' in the bundle (Bundle.entry[5].resource.subject). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:patient-doc-001``) |
| IssueSeverity.error | Bundle | Can't find 'Patient/doc-patient-001' in the bundle (Bundle.entry[6].resource.subject). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:patient-doc-001``) |
| IssueSeverity.error | Bundle.entry[0].fullUrl | UUIDs must be valid and lowercase (composition-root-001) |
| IssueSeverity.error | Bundle.entry[1].resource.subject | Can't find 'Patient/doc-patient-001' in the bundle (Composition.subject). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:patient-doc-001``) |
| IssueSeverity.error | Bundle.entry[1].resource.author[1] | Can't find 'Practitioner/doc-author-001' in the bundle (Composition.author). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:practitioner-doc-001``) |
| IssueSeverity.error | Bundle.entry[1].resource.section[1].entry[1] | Can't find 'Condition/doc-condition-001' in the bundle (Section Entry). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:condition-doc-001``) |
| IssueSeverity.error | Bundle.entry[1].resource.section[2].entry[1] | Can't find 'MedicationStatement/doc-med-001' in the bundle (Section Entry). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:medstatement-doc-001``) |
| IssueSeverity.error | Bundle.entry[1].resource.section[3].entry[1] | Can't find 'DiagnosticReport/doc-report-001' in the bundle (Section Entry). Note that there is a resource in the bundle with the same type and id, but it does not match because of the fullUrl based rules around matching relative references (must be ``urn:uuid:diagnosticreport-doc-001``) |
| IssueSeverity.error | Bundle.entry[1].fullUrl | UUIDs must be valid and lowercase (patient-doc-001) |
| IssueSeverity.error | Bundle.entry[1].resource/*Patient/doc-patient-001*/.identifier[0].system | Example URLs are not allowed in this context (http://hospital.example.org/mrn) |
| IssueSeverity.error | Bundle.entry[2].fullUrl | UUIDs must be valid and lowercase (practitioner-doc-001) |
| IssueSeverity.error | Bundle.entry[3].fullUrl | UUIDs must be valid and lowercase (condition-doc-001) |
| IssueSeverity.error | Bundle.entry[4].fullUrl | UUIDs must be valid and lowercase (medstatement-doc-001) |
| IssueSeverity.error | Bundle.entry[5].fullUrl | UUIDs must be valid and lowercase (diagnosticreport-doc-001) |
| IssueSeverity.error | Bundle.entry[6].fullUrl | UUIDs must be valid and lowercase (observation-doc-wbc) |
| IssueSeverity.error | Bundle.entry[0] | The fullUrl 'http://example.org/fhir/Patient/invalid-example-url' looks like a RESTful server URL, so it must end with the correct type and id (/Patient/doc-patient-bad) |
| IssueSeverity.error | Bundle | Constraint failed: bdl-9: 'A document must have an identifier with a system and a value' |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/.value.ofType(Quantity) | Unable to validate code '10*3/uL' in system 'http://unitsofmeasure.org' because the validator is running without terminology services |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/ | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[6].resource | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/ | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Bundle.entry[6].resource | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.type.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.type | Unable to check whether the code is in the value set 'http://hl7.org/fhir/ValueSet/doc-typecodes\|4.0.1' because the code system http://loinc.org was not found |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[0].code.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[1].code.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[2].code.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[3].resource/*Condition/doc-condition-001*/.code.coding[0].system | A definition for CodeSystem 'http://snomed.info/sct' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[4].resource/*MedicationStatement/doc-med-001*/.medication.ofType(CodeableConcept).coding[0].system | A definition for CodeSystem 'http://www.nlm.nih.gov/research/umls/rxnorm' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[5].resource/*DiagnosticReport/doc-report-001*/.code.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[5].resource/*DiagnosticReport/doc-report-001*/.code | Unable to check whether the code is in the value set 'http://hl7.org/fhir/ValueSet/report-codes\|4.0.1' because the code system http://loinc.org was not found |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/.code.coding[0].system | A definition for CodeSystem 'http://loinc.org' could not be found, so the code cannot be validated |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.subject | Entry 1 matches the reference Patient/doc-patient-001 by type and id but it's fullUrl urn:uuid:patient-doc-001 does not match the full target URL urn:uuid:doc-patient-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[3].resource/*Condition/doc-condition-001*/.subject | Entry 1 matches the reference Patient/doc-patient-001 by type and id but it's fullUrl urn:uuid:patient-doc-001 does not match the full target URL urn:uuid:doc-patient-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[4].resource/*MedicationStatement/doc-med-001*/.subject | Entry 1 matches the reference Patient/doc-patient-001 by type and id but it's fullUrl urn:uuid:patient-doc-001 does not match the full target URL urn:uuid:doc-patient-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[5].resource/*DiagnosticReport/doc-report-001*/.subject | Entry 1 matches the reference Patient/doc-patient-001 by type and id but it's fullUrl urn:uuid:patient-doc-001 does not match the full target URL urn:uuid:doc-patient-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/.subject | Entry 1 matches the reference Patient/doc-patient-001 by type and id but it's fullUrl urn:uuid:patient-doc-001 does not match the full target URL urn:uuid:doc-patient-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.author[0] | Entry 2 matches the reference Practitioner/doc-author-001 by type and id but it's fullUrl urn:uuid:practitioner-doc-001 does not match the full target URL urn:uuid:doc-author-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[0].entry[0] | Entry 3 matches the reference Condition/doc-condition-001 by type and id but it's fullUrl urn:uuid:condition-doc-001 does not match the full target URL urn:uuid:doc-condition-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[1].entry[0] | Entry 4 matches the reference MedicationStatement/doc-med-001 by type and id but it's fullUrl urn:uuid:medstatement-doc-001 does not match the full target URL urn:uuid:doc-med-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/.section[2].entry[0] | Entry 5 matches the reference DiagnosticReport/doc-report-001 by type and id but it's fullUrl urn:uuid:diagnosticreport-doc-001 does not match the full target URL urn:uuid:doc-report-001 by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[5].resource/*DiagnosticReport/doc-report-001*/.result[0] | Entry 6 matches the reference Observation/doc-obs-wbc by type and id but it's fullUrl urn:uuid:observation-doc-wbc does not match the full target URL urn:uuid:doc-obs-wbc by Bundle resolution rules |
| IssueSeverity.warning | Bundle.entry[0].resource/*Composition/composition-root-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[1].resource/*Patient/doc-patient-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[2].resource/*Practitioner/doc-author-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[3].resource/*Condition/doc-condition-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[4].resource/*MedicationStatement/doc-med-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[5].resource/*DiagnosticReport/doc-report-001*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[6].resource/*Observation/doc-obs-wbc*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[7].resource/*Patient/doc-patient-bad*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
