# Frontend Validation: DiagnosticReport - Valid

**Status:** PASS
**Timestamp:** 2026-06-29T10:21:57
**Run ID:** `2026-06-29_10-21_Frontend-Validation-DiagnosticReport---Valid`

## Summary

Validation successful with 2 warning(s) and 1 information message(s)

## Issue Counts

- **Errors:** 0
- **Warnings:** 2
- **Informational:** 1

## Validation Details

**Resource Type:** DiagnosticReport
**Valid:** True
**Profiles:** None


## Issues

| Severity | Location | Message |
|----------|----------|---------|
| IssueSeverity.information | DiagnosticReport.code | None of the codings provided are in the value set 'LOINC Diagnostic Report Codes' (http://hl7.org/fhir/ValueSet/report-codes\|4.0.1), and a coding is recommended to come from this value set (codes = http://loinc.org#58410-2) |
| IssueSeverity.warning | DiagnosticReport.code.coding[0].display | Wrong Display Name 'Complete blood count (hemogram) panel - Blood by Automated count' for http://loinc.org#58410-2. Valid display is 'CBC panel - Blood by Automated count' (en) (for the language(s) 'en') |
| IssueSeverity.warning | DiagnosticReport | Constraint failed: dom-6: 'A resource should have narrative for robust management' (defined in http://hl7.org/fhir/StructureDefinition/DomainResource) (Best Practice Recommendation) |
