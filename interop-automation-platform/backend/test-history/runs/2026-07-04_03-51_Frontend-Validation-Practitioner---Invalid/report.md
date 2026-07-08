# Frontend Validation: Practitioner - Invalid

**Status:** FAIL
**Timestamp:** 2026-07-04T03:51:24
**Run ID:** `2026-07-04_03-51_Frontend-Validation-Practitioner---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 1
- **Informational:** 0

## Validation Details

**Resource Type:** Practitioner
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | Practitioner.qualification[0].code.coding[0] | java.net.SocketTimeoutException: timeout |
| IssueSeverity.warning | Practitioner | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
