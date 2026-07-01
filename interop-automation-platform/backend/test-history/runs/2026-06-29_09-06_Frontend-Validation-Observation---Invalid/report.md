# Frontend Validation: Observation - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:06:55
**Run ID:** `2026-06-29_09-06_Frontend-Validation-Observation---Invalid`

## Summary

Validation failed with 1 error(s) | Missing required: Observation

## Issue Counts

- **Errors:** 1
- **Warnings:** 3
- **Informational:** 0

## Validation Details

**Resource Type:** Observation
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Observation | Observation.code: minimum required = 1, but only found 0 (from http://hl7.org/fhir/StructureDefinition/Observation\|4.0.1) |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have an effective[x] () |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
