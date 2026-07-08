# Frontend Validation: Observation - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T07:50:27
**Run ID:** `2026-06-29_07-50_Frontend-Validation-Observation---Valid`

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
| IssueSeverity.warning | Observation.category[0] | Reference to draft CodeSystem http://terminology.hl7.org/CodeSystem/observation-category\|0.1.0 |
| IssueSeverity.warning | Observation | Best Practice Recommendation: In general, all observations should have a performer |
| IssueSeverity.warning | Observation | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
