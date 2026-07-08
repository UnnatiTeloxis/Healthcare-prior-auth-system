# Frontend Validation: CarePlan - Invalid

**Status:** FAIL
**Timestamp:** 2026-06-29T10:11:29
**Run ID:** `2026-06-29_10-11_Frontend-Validation-CarePlan---Invalid`

## Summary

Validation failed with 1 error(s)

## Issue Counts

- **Errors:** 1
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** CarePlan
**Valid:** False
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.error | CarePlan.category[0].coding[0] | java.net.SocketTimeoutException: timeout |
| IssueSeverity.information | CarePlan.activity[0].detail.scheduled.ofType(Timing).repeat.periodUnit | Reference to draft CodeSystem http://unitsofmeasure.org\|2.1.1 |
| IssueSeverity.warning | CarePlan.activity[0].detail.code.coding[0] | A definition for CodeSystem 'http://www.nlm.nih.gov/research/umls/rxnorm' could not be found, so the code cannot be validated |
| IssueSeverity.warning | CarePlan | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
