# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-30T04:22:53
**Run ID:** `2026-06-30_04-22_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 2
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.link[0].url | Example URLs are not allowed in this context (https://api.example.org/fhir/Patient?name=Smith&_count=2) |
| IssueSeverity.error | Bundle.link[1].url | Example URLs are not allowed in this context (https://api.example.org/fhir/Patient?name=Smith&_count=2&_offset=2) |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/search-1*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
| IssueSeverity.warning | Bundle.entry[1].resource/*Patient/search-2*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
