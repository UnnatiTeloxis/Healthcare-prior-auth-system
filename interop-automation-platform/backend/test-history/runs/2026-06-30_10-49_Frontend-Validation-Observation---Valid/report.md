# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-30T10:49:33
**Run ID:** `2026-06-30_10-49_Frontend-Validation-Observation---Valid`

## Summary

Validation successful with 3 warning(s) and 0 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Observation.code | Observation.code: None of the codings provided are in the value set 'US Core Laboratory Test Codes' (http://hl7.org/fhir/us/core/ValueSet/us-core-laboratory-test-codes); a coding should come from this value set unless it has no suitable code (note that the validator cannot judge what is suitable) (codes = http://loinc.org#2339-0) |
