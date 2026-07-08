# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T07:47:59
**Run ID:** `2026-06-29_07-47_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 10 error(s) | Missing required: Observation

## Issue Counts

- **Errors:** 10
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation.status | This element is not allowed by the profile http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0 |
| IssueSeverity.error | Observation.code | This element is not allowed by the profile http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0 |
| IssueSeverity.error | Observation.subject | This element is not allowed by the profile http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0 |
| IssueSeverity.error | Observation.value.ofType(Quantity) | This element is not allowed by the profile http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0 |
| IssueSeverity.error | Observation | Observation.category: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bodyheight\|4.0.1) |
| IssueSeverity.error | Observation | Observation.effective[x]: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/bodyheight\|4.0.1) |
| IssueSeverity.error | Observation | Patient.gender: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) |
| IssueSeverity.error | Observation | Patient.identifier: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) |
| IssueSeverity.error | Observation | Patient.name: minimum required = 1, but only found 0 (from http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient\|6.1.0) |
| IssueSeverity.error | Observation | Slice 'Observation.category:VSCat': a matching slice is required, but not found (from http://hl7.org/fhir/StructureDefinition/bodyheight\|4.0.1). Note that other slices are allowed in addition to this required slice |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
