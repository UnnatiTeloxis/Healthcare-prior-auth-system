# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-03T04:09:15
**Run ID:** `2026-07-03_04-09_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[0].fullUrl | UUIDs must be valid and lowercase (Patient-UPPERCASE-UUID) |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/bad-uuid-patient*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
