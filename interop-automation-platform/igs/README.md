# FHIR Implementation Guide Packages

## User-facing IGs (dropdown)

| File | Package ID | Version |
|------|------------|---------|
| `us-core.tgz` | `hl7.fhir.us.core` | 9.0.0 |
| `davinci-crd.tgz` | `hl7.fhir.us.davinci-crd` | 2.2.1 |
| `davinci-dtr.tgz` | `hl7.fhir.us.davinci-dtr` | 2.2.0 |
| `davinci-pas.tgz` | `hl7.fhir.us.davinci-pas` | 2.2.1 |

## Hidden dependency (not in UI)

| File | Package ID | Version |
|------|------------|---------|
| `davinci-hrex.tgz` | `hl7.fhir.us.davinci-hrex` | 1.2.0 |

## Local terminology (Inferno parity, not in UI)

Mounted with IGs so ValueSets/CodeSystems resolve quickly (same family as Inferno TX):

| File | Package |
|------|---------|
| `hl7.terminology.r4-7.1.0.tgz` | `hl7.terminology.r4` 7.1.0 |
| `hl7.fhir.uv.extensions.r4-5.3.0.tgz` | `hl7.fhir.uv.extensions.r4` 5.3.0 |
| `hl7.fhir.uv.sdc-4.0.0.tgz` | `hl7.fhir.uv.sdc` 4.0.0 |

Validator settings: `DISPLAY_ISSUES_ARE_WARNINGS=true`. Remote `tx.fhir.org` is disabled locally (it hangs); ValueSets resolve from the local terminology packages above for Inferno-like binding results with low latency.
