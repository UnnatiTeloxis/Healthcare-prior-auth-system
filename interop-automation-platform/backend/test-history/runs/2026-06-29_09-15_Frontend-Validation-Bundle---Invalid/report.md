# Frontend Validation: Bundle - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T09:15:02
**Run ID:** `2026-06-29_09-15_Frontend-Validation-Bundle---Invalid`

## Summary

Validation failed with 2 error(s)

## Issue Counts

- **Errors:** 2
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Bundle
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Bundle.entry[0] | The fullUrl 'http://example.org/fhir/Patient/example' looks like a RESTful server URL, so it must end with the correct type and id (/Patient/example-url-patient) |
| IssueSeverity.error | Bundle.entry[0].resource/*Patient/example-url-patient*/.identifier[0].system | Example URLs are not allowed in this context (http://example.org/fhir/identifier/mrn) |
| IssueSeverity.warning | Bundle.entry[0].resource/*Patient/example-url-patient*/ | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
