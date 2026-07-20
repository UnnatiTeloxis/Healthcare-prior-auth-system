"""
Generate simple/, complex/, and realistic/ test cases for all popular IGs
not yet covered by _generate_simple_complex.py / _generate_realistic_suite.py.

Run: python test-cases/_generate_popular_igs_suite.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def w(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def patient_base(pid: str, family: str, given: list[str], profile: str | None = None, **extra) -> dict:
    p: dict = {
        "resourceType": "Patient",
        "id": pid,
        "identifier": [{"system": "http://hospital.example.org/mrn", "value": f"MRN-{pid}"}],
        "name": [{"family": family, "given": given}],
        "gender": extra.pop("gender", "female"),
        "birthDate": extra.pop("birthDate", "1980-06-15"),
    }
    if profile:
        p["meta"] = {"profile": [profile]}
    p.update(extra)
    return p


def observation_base(oid: str, profile: str, code: str, display: str, subject: str) -> dict:
    return {
        "resourceType": "Observation",
        "id": oid,
        "meta": {"profile": [profile]},
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": code, "display": display}],
            "text": display,
        },
        "subject": {"reference": f"Patient/{subject}"},
        "effectiveDateTime": "2026-01-15T10:00:00Z",
        "valueCodeableConcept": {
            "coding": [{"system": "http://snomed.info/sct", "code": "224406003", "display": "Employed"}],
            "text": "Employed full time",
        },
    }


def gen_us_ccda() -> None:
    d = ROOT / "us-ccda"
    w(
        d / "simple/01-composition-minimal-valid.json",
        {
            "resourceType": "Composition",
            "id": "ccda-simple-comp",
            "status": "final",
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "34133-9",
                        "display": "Summary of episode note",
                    }
                ]
            },
            "subject": {"reference": "Patient/example"},
            "date": "2026-03-01T12:00:00Z",
            "author": [{"reference": "Practitioner/author-1"}],
            "title": "C-CDA Summary Document",
            "section": [{"title": "Problems", "text": {"status": "generated", "div": "<div>Problems</div>"}}],
        },
    )
    w(
        d / "simple/02-composition-minimal-invalid.json",
        {
            "resourceType": "Composition",
            "id": "ccda-simple-comp-bad",
            "status": "entered-in-error",
            "title": "Missing required fields",
        },
    )
    w(
        d / "complex/01-composition-full-valid.json",
        {
            "resourceType": "Composition",
            "id": "ccda-complex-comp",
            "status": "final",
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "34133-9",
                        "display": "Summary of episode note",
                    }
                ],
                "text": "Clinical Summary",
            },
            "subject": {"reference": "Patient/ccda-pt-001"},
            "date": "2026-03-01T14:30:00Z",
            "author": [{"reference": "Practitioner/dr-smith"}],
            "custodian": {"reference": "Organization/hospital-a"},
            "title": "Continuity of Care Document",
            "confidentiality": "N",
            "section": [
                {
                    "title": "Allergies",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "48765-2",
                                "display": "Allergies and adverse reactions",
                            }
                        ]
                    },
                    "text": {"status": "generated", "div": "<div>No known allergies</div>"},
                },
                {
                    "title": "Medications",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "10160-0",
                                "display": "History of Medication use",
                            }
                        ]
                    },
                    "text": {"status": "generated", "div": "<div>Medication list</div>"},
                },
            ],
        },
    )
    w(
        d / "complex/02-composition-multi-error-invalid.json",
        {
            "resourceType": "Composition",
            "id": "ccda-complex-bad",
            "status": "unknown-status",
            "type": {"text": "Bad type"},
            "date": "not-a-date",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-ccd-summary-v{n}.json",
            {
                "resourceType": "Composition",
                "id": f"ccda-real-{n:03d}",
                "status": "final",
                "type": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "34133-9", "display": "Summary of episode note"}
                    ]
                },
                "subject": {"reference": f"Patient/ccda-pt-{n:03d}"},
                "date": f"2026-0{(n % 9) + 1}-15T09:00:00Z",
                "author": [{"reference": "Practitioner/attending"}],
                "title": f"Hospital Discharge Summary #{n}",
                "section": [
                    {
                        "title": "Reason for Visit",
                        "text": {"status": "generated", "div": f"<div>Visit reason variant {n}</div>"},
                    }
                ],
            },
        )


def gen_us_bulkdata() -> None:
    d = ROOT / "us-bulkdata"
    w(
        d / "simple/01-parameters-export-minimal-valid.json",
        {
            "resourceType": "Parameters",
            "id": "bulk-simple-export",
            "parameter": [
                {"name": "_outputFormat", "valueString": "application/fhir+ndjson"},
                {"name": "_type", "valueString": "Patient,Observation"},
            ],
        },
    )
    w(
        d / "simple/02-parameters-export-minimal-invalid.json",
        {
            "resourceType": "Parameters",
            "id": "bulk-simple-bad",
            "parameter": [{"name": "_since", "valueString": "not-an-instant"}],
        },
    )
    w(
        d / "complex/01-parameters-export-full-valid.json",
        {
            "resourceType": "Parameters",
            "id": "bulk-complex-export",
            "parameter": [
                {"name": "_outputFormat", "valueString": "application/fhir+ndjson"},
                {"name": "_type", "valueString": "Patient,Observation,Condition,Encounter"},
                {"name": "_since", "valueInstant": "2025-01-01T00:00:00Z"},
                {"name": "_typeFilter", "valueString": "Observation?category=vital-signs"},
            ],
        },
    )
    w(
        d / "complex/02-group-export-context-valid.json",
        {
            "resourceType": "Group",
            "id": "bulk-export-group",
            "type": "person",
            "actual": True,
            "member": [
                {"entity": {"reference": "Patient/p1"}},
                {"entity": {"reference": "Patient/p2"}},
            ],
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-bulk-export-request-v{n}.json",
            {
                "resourceType": "Parameters",
                "id": f"bulk-req-{n:03d}",
                "parameter": [
                    {"name": "_outputFormat", "valueString": "application/fhir+ndjson"},
                    {
                        "name": "_type",
                        "valueString": "Patient,Observation,Condition,Procedure,Immunization",
                    },
                    {"name": "_since", "valueInstant": f"2025-0{(n % 9) + 1}-01T00:00:00Z"},
                ],
            },
        )


def gen_us_odh() -> None:
    d = ROOT / "us-odh"
    prof_emp = "http://hl7.org/fhir/us/odh/StructureDefinition/odh-EmploymentStatus"
    prof_job = "http://hl7.org/fhir/us/odh/StructureDefinition/odh-PastOrPresentJob"
    w(d / "simple/01-employment-status-minimal-valid.json", observation_base("odh-emp-1", prof_emp, "74165-2", "Employment status", "odh-pt-1"))
    w(
        d / "simple/02-employment-status-minimal-invalid.json",
        {
            "resourceType": "Observation",
            "id": "odh-emp-bad",
            "meta": {"profile": [prof_emp]},
            "status": "not-a-status",
        },
    )
    w(
        d / "complex/01-past-job-full-valid.json",
        {
            **observation_base("odh-job-1", prof_job, "86188-0", "History of occupation", "odh-pt-1"),
            "component": [
                {
                    "code": {"text": "Industry"},
                    "valueCodeableConcept": {"text": "Healthcare"},
                },
                {
                    "code": {"text": "Occupation"},
                    "valueCodeableConcept": {"text": "Registered Nurse"},
                },
            ],
        },
    )
    w(
        d / "complex/02-employment-multi-error-invalid.json",
        {
            "resourceType": "Observation",
            "id": "odh-job-bad",
            "meta": {"profile": [prof_job]},
            "status": "final",
            "code": {"text": "Job"},
            "valueString": "Should be CodeableConcept",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-worker-employment-v{n}.json",
            observation_base(f"odh-real-{n:03d}", prof_emp, "74165-2", "Employment status", f"odh-pt-{n:03d}"),
        )


def gen_us_military_service() -> None:
    d = ROOT / "us-military-service"
    prof_pt = "http://hl7.org/fhir/us/military-service/StructureDefinition/usveteran"
    prof_ep = "http://hl7.org/fhir/us/military-service/StructureDefinition/military-service-episode"
    w(d / "simple/01-veteran-patient-minimal-valid.json", patient_base("ms-vet-1", "Johnson", ["Alex"], prof_pt))
    w(
        d / "simple/02-veteran-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ms-vet-bad",
            "meta": {"profile": [prof_pt]},
            "gender": "invalid-gender",
        },
    )
    w(
        d / "complex/01-service-episode-full-valid.json",
        {
            "resourceType": "Observation",
            "id": "ms-ep-1",
            "meta": {"profile": [prof_ep]},
            "status": "final",
            "code": {"text": "Military service episode"},
            "subject": {"reference": "Patient/ms-vet-1"},
            "effectivePeriod": {"start": "2010-01-01", "end": "2014-06-30"},
            "valueCodeableConcept": {"text": "Active duty"},
        },
    )
    w(
        d / "complex/02-service-episode-invalid.json",
        {
            "resourceType": "Observation",
            "id": "ms-ep-bad",
            "meta": {"profile": [prof_ep]},
            "status": "final",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-veteran-record-v{n}.json",
            patient_base(f"ms-vet-{n:03d}", "Martinez", [f"Case{n}"], prof_pt, gender="male"),
        )


def gen_us_vrdr() -> None:
    d = ROOT / "us-vrdr"
    prof_dec = "http://hl7.org/fhir/us/vrdr/StructureDefinition/vrdr-decedent"
    prof_cod = "http://hl7.org/fhir/us/vrdr/StructureDefinition/vrdr-cause-of-death-part1"
    w(
        d / "simple/01-decedent-minimal-valid.json",
        {
            **patient_base("vrdr-dec-1", "Smith", ["John"], prof_dec, gender="male"),
            "deceasedDateTime": "2026-01-10T08:00:00Z",
        },
    )
    w(
        d / "simple/02-decedent-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "vrdr-dec-bad",
            "meta": {"profile": [prof_dec]},
            "gender": "not-valid",
        },
    )
    w(
        d / "complex/01-cause-of-death-full-valid.json",
        {
            "resourceType": "Observation",
            "id": "vrdr-cod-1",
            "meta": {"profile": [prof_cod]},
            "status": "final",
            "code": {"text": "Cause of death Part I"},
            "subject": {"reference": "Patient/vrdr-dec-1"},
            "effectiveDateTime": "2026-01-10T08:00:00Z",
            "valueCodeableConcept": {
                "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "I21.9", "display": "Acute MI"}],
                "text": "Acute myocardial infarction",
            },
        },
    )
    w(
        d / "complex/02-cause-of-death-invalid.json",
        {
            "resourceType": "Observation",
            "id": "vrdr-cod-bad",
            "meta": {"profile": [prof_cod]},
            "status": "final",
            "valueString": "Wrong type",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-death-record-v{n}.json",
            {
                **patient_base(f"vrdr-{n:03d}", "Williams", [f"Decedent{n}"], prof_dec),
                "deceasedDateTime": f"2026-0{(n % 9) + 1}-12T14:00:00Z",
            },
        )


def gen_davinci_pdex() -> None:
    d = ROOT / "davinci-pdex"
    prof_org = "http://hl7.org/fhir/us/davinci-pdex/StructureDefinition/mtls-organization"
    prof_eob = "http://hl7.org/fhir/us/davinci-pdex/StructureDefinition/pdex-priorauthorization"
    w(
        d / "simple/01-organization-minimal-valid.json",
        {
            "resourceType": "Organization",
            "id": "pdex-org-1",
            "meta": {"profile": [prof_org]},
            "active": True,
            "name": "Payer Exchange Org",
        },
    )
    w(
        d / "simple/02-organization-minimal-invalid.json",
        {
            "resourceType": "Organization",
            "id": "pdex-org-bad",
            "meta": {"profile": [prof_org]},
        },
    )
    w(
        d / "complex/01-priorauth-eob-full-valid.json",
        {
            "resourceType": "ExplanationOfBenefit",
            "id": "pdex-eob-1",
            "meta": {"profile": [prof_eob]},
            "status": "active",
            "type": {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/claim-type", "code": "professional"}
                ]
            },
            "use": "preauthorization",
            "patient": {"reference": "Patient/example"},
            "created": "2026-02-01",
            "insurer": {"reference": "Organization/pdex-org-1"},
            "provider": {"reference": "Organization/provider-1"},
            "outcome": "complete",
        },
    )
    w(
        d / "complex/02-priorauth-eob-invalid.json",
        {
            "resourceType": "ExplanationOfBenefit",
            "id": "pdex-eob-bad",
            "meta": {"profile": [prof_eob]},
            "status": "active",
            "use": "preauthorization",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-payer-org-v{n}.json",
            {
                "resourceType": "Organization",
                "id": f"pdex-org-{n:03d}",
                "meta": {"profile": [prof_org]},
                "active": True,
                "name": f"Payer Network {n}",
                "telecom": [{"system": "url", "value": f"https://payer{n}.example.org/fhir"}],
            },
        )


def gen_davinci_cdex() -> None:
    d = ROOT / "davinci-cdex"
    prof_pt = "http://hl7.org/fhir/us/davinci-cdex/StructureDefinition/cdex-patient-demographics"
    prof_task = "http://hl7.org/fhir/us/davinci-cdex/StructureDefinition/cdex-task-data-request"
    w(d / "simple/01-patient-minimal-valid.json", patient_base("cdex-pt-1", "Brown", ["Taylor"], prof_pt))
    w(
        d / "simple/02-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "cdex-pt-bad",
            "meta": {"profile": [prof_pt]},
            "gender": "bad-code",
        },
    )
    w(
        d / "complex/01-data-request-task-full-valid.json",
        {
            "resourceType": "Task",
            "id": "cdex-task-1",
            "meta": {"profile": [prof_task]},
            "status": "requested",
            "intent": "order",
            "for": {"reference": "Patient/cdex-pt-1"},
            "description": "Request clinical data exchange",
        },
    )
    w(
        d / "complex/02-data-request-task-invalid.json",
        {
            "resourceType": "Task",
            "id": "cdex-task-bad",
            "meta": {"profile": [prof_task]},
            "status": "bogus",
            "intent": "order",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-member-demographics-v{n}.json",
            patient_base(f"cdex-{n:03d}", "Davis", [f"Member{n}"], prof_pt),
        )


def gen_davinci_pcde() -> None:
    d = ROOT / "davinci-pcde"
    prof_cp = "http://hl7.org/fhir/us/davinci-pcde/StructureDefinition/profile-careplan"
    prof_task = "http://hl7.org/fhir/us/davinci-pcde/StructureDefinition/pcde-task-request"
    w(
        d / "simple/01-careplan-minimal-valid.json",
        {
            "resourceType": "CarePlan",
            "id": "pcde-cp-1",
            "meta": {"profile": [prof_cp]},
            "status": "active",
            "intent": "plan",
            "subject": {"reference": "Patient/example"},
            "title": "Coverage decision care plan",
        },
    )
    w(
        d / "simple/02-careplan-minimal-invalid.json",
        {
            "resourceType": "CarePlan",
            "id": "pcde-cp-bad",
            "meta": {"profile": [prof_cp]},
            "status": "active",
        },
    )
    w(
        d / "complex/01-pcde-task-full-valid.json",
        {
            "resourceType": "Task",
            "id": "pcde-task-1",
            "meta": {"profile": [prof_task]},
            "status": "requested",
            "intent": "order",
            "for": {"reference": "Patient/example"},
            "description": "Request coverage decision exchange",
        },
    )
    w(
        d / "complex/02-pcde-task-invalid.json",
        {
            "resourceType": "Task",
            "id": "pcde-task-bad",
            "meta": {"profile": [prof_task]},
            "status": "requested",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-coverage-careplan-v{n}.json",
            {
                "resourceType": "CarePlan",
                "id": f"pcde-{n:03d}",
                "meta": {"profile": [prof_cp]},
                "status": "active",
                "intent": "plan",
                "subject": {"reference": f"Patient/pcde-{n:03d}"},
                "title": f"Coverage plan variant {n}",
            },
        )


def gen_davinci_alerts() -> None:
    d = ROOT / "davinci-alerts"
    prof_enc = "http://hl7.org/fhir/us/davinci-alerts/StructureDefinition/adt-notification-encounter"
    prof_mh = "http://hl7.org/fhir/us/davinci-alerts/StructureDefinition/admit-notification-messageheader"
    w(
        d / "simple/01-encounter-minimal-valid.json",
        {
            "resourceType": "Encounter",
            "id": "alerts-enc-1",
            "meta": {"profile": [prof_enc]},
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "IMP",
                "display": "inpatient encounter",
            },
            "subject": {"reference": "Patient/example"},
        },
    )
    w(
        d / "simple/02-encounter-minimal-invalid.json",
        {
            "resourceType": "Encounter",
            "id": "alerts-enc-bad",
            "meta": {"profile": [prof_enc]},
            "status": "finished",
        },
    )
    w(
        d / "complex/01-admit-messageheader-full-valid.json",
        {
            "resourceType": "MessageHeader",
            "id": "alerts-mh-1",
            "meta": {"profile": [prof_mh]},
            "eventCoding": {
                "system": "http://hl7.org/fhir/admit-event",
                "code": "admit",
                "display": "Admit",
            },
            "source": {"name": "Hospital EHR", "endpoint": "https://hospital.example.org/fhir"},
            "focus": [{"reference": "Encounter/alerts-enc-1"}],
        },
    )
    w(
        d / "complex/02-admit-messageheader-invalid.json",
        {
            "resourceType": "MessageHeader",
            "id": "alerts-mh-bad",
            "meta": {"profile": [prof_mh]},
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-adt-encounter-v{n}.json",
            {
                "resourceType": "Encounter",
                "id": f"alerts-{n:03d}",
                "meta": {"profile": [prof_enc]},
                "status": "in-progress" if n % 2 else "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "IMP",
                },
                "subject": {"reference": f"Patient/adt-{n:03d}"},
                "period": {"start": f"2026-0{(n % 9) + 1}-01T08:00:00Z"},
            },
        )


def gen_davinci_drug_formulary() -> None:
    d = ROOT / "davinci-drug-formulary"
    prof_plan = "http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-Formulary"
    prof_drug = "http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-FormularyDrug"
    w(
        d / "simple/01-formulary-plan-minimal-valid.json",
        {
            "resourceType": "InsurancePlan",
            "id": "form-plan-1",
            "meta": {"profile": [prof_plan]},
            "status": "active",
            "name": "Gold Rx Formulary 2026",
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type", "code": "drug"}]}],
        },
    )
    w(
        d / "simple/02-formulary-plan-minimal-invalid.json",
        {
            "resourceType": "InsurancePlan",
            "id": "form-plan-bad",
            "meta": {"profile": [prof_plan]},
            "status": "active",
        },
    )
    w(
        d / "complex/01-formulary-drug-full-valid.json",
        {
            "resourceType": "MedicationKnowledge",
            "id": "form-drug-1",
            "meta": {"profile": [prof_drug]},
            "code": {
                "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "197361", "display": "Metformin"}]
            },
            "status": "active",
            "doseForm": {"text": "Tablet"},
        },
    )
    w(
        d / "complex/02-formulary-drug-invalid.json",
        {
            "resourceType": "MedicationKnowledge",
            "id": "form-drug-bad",
            "meta": {"profile": [prof_drug]},
            "status": "active",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-formulary-plan-v{n}.json",
            {
                "resourceType": "InsurancePlan",
                "id": f"form-{n:03d}",
                "meta": {"profile": [prof_plan]},
                "status": "active",
                "name": f"Payer Formulary Tier {n}",
            },
        )


def gen_davinci_deqm() -> None:
    d = ROOT / "davinci-deqm"
    prof_mr = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/indv-measurereport-deqm"
    prof_grp = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/gaps-group-deqm"
    w(
        d / "simple/01-measurereport-minimal-valid.json",
        {
            "resourceType": "MeasureReport",
            "id": "deqm-mr-1",
            "meta": {"profile": [prof_mr]},
            "status": "complete",
            "type": "individual",
            "measure": "http://example.org/Measure/colorectal-screening",
            "subject": {"reference": "Patient/example"},
            "date": "2026-01-31",
        },
    )
    w(
        d / "simple/02-measurereport-minimal-invalid.json",
        {
            "resourceType": "MeasureReport",
            "id": "deqm-mr-bad",
            "meta": {"profile": [prof_mr]},
            "status": "complete",
            "type": "individual",
        },
    )
    w(
        d / "complex/01-gaps-group-full-valid.json",
        {
            "resourceType": "Group",
            "id": "deqm-grp-1",
            "meta": {"profile": [prof_grp]},
            "type": "person",
            "actual": True,
            "member": [{"entity": {"reference": "Patient/example"}}],
        },
    )
    w(
        d / "complex/02-gaps-group-invalid.json",
        {
            "resourceType": "Group",
            "id": "deqm-grp-bad",
            "meta": {"profile": [prof_grp]},
            "type": "person",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-quality-measurereport-v{n}.json",
            {
                "resourceType": "MeasureReport",
                "id": f"deqm-{n:03d}",
                "meta": {"profile": [prof_mr]},
                "status": "complete",
                "type": "individual",
                "measure": f"http://example.org/Measure/quality-measure-{n}",
                "subject": {"reference": f"Patient/qm-{n:03d}"},
                "date": "2026-02-01",
            },
        )


def gen_davinci_ra() -> None:
    d = ROOT / "davinci-ra"
    prof_mr = "http://hl7.org/fhir/us/davinci-ra/StructureDefinition/ra-measurereport"
    prof_grp = "http://hl7.org/fhir/us/davinci-ra/StructureDefinition/ra-patient-group"
    w(
        d / "simple/01-measurereport-minimal-valid.json",
        {
            "resourceType": "MeasureReport",
            "id": "ra-mr-1",
            "meta": {"profile": [prof_mr]},
            "status": "complete",
            "type": "individual",
            "measure": "http://example.org/Measure/risk-adjustment",
            "subject": {"reference": "Patient/example"},
            "date": "2026-01-15",
        },
    )
    w(
        d / "simple/02-measurereport-minimal-invalid.json",
        {
            "resourceType": "MeasureReport",
            "id": "ra-mr-bad",
            "meta": {"profile": [prof_mr]},
            "status": "complete",
        },
    )
    w(
        d / "complex/01-patient-group-full-valid.json",
        {
            "resourceType": "Group",
            "id": "ra-grp-1",
            "meta": {"profile": [prof_grp]},
            "type": "person",
            "actual": True,
            "member": [{"entity": {"reference": "Patient/example"}}],
        },
    )
    w(
        d / "complex/02-patient-group-invalid.json",
        {
            "resourceType": "Group",
            "id": "ra-grp-bad",
            "meta": {"profile": [prof_grp]},
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-risk-adjustment-report-v{n}.json",
            {
                "resourceType": "MeasureReport",
                "id": f"ra-{n:03d}",
                "meta": {"profile": [prof_mr]},
                "status": "complete",
                "type": "individual",
                "measure": f"http://example.org/Measure/ra-model-{n}",
                "subject": {"reference": f"Patient/ra-{n:03d}"},
                "date": "2026-01-20",
            },
        )


def gen_us_ecr() -> None:
    d = ROOT / "us-ecr"
    prof_pt = "http://hl7.org/fhir/us/ecr/StructureDefinition/us-ph-patient"
    prof_obs = "http://hl7.org/fhir/us/ecr/StructureDefinition/rr-reportability-information-observation"
    w(d / "simple/01-ph-patient-minimal-valid.json", patient_base("ecr-pt-1", "Wilson", ["Jordan"], prof_pt))
    w(
        d / "simple/02-ph-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ecr-pt-bad",
            "meta": {"profile": [prof_pt]},
            "gender": "x-invalid",
        },
    )
    w(
        d / "complex/01-reportability-observation-full-valid.json",
        {
            "resourceType": "Observation",
            "id": "ecr-obs-1",
            "meta": {"profile": [prof_obs]},
            "status": "final",
            "code": {"text": "Reportability information"},
            "subject": {"reference": "Patient/ecr-pt-1"},
            "effectiveDateTime": "2026-02-10T09:00:00Z",
            "valueCodeableConcept": {"text": "Reportable condition detected"},
        },
    )
    w(
        d / "complex/02-reportability-observation-invalid.json",
        {
            "resourceType": "Observation",
            "id": "ecr-obs-bad",
            "meta": {"profile": [prof_obs]},
            "status": "final",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-public-health-patient-v{n}.json",
            patient_base(f"ecr-{n:03d}", "Clark", [f"Case{n}"], prof_pt),
        )


def gen_us_pacio_adi() -> None:
    d = ROOT / "us-pacio-adi"
    prof_obs = "http://hl7.org/fhir/us/pacio-adi/StructureDefinition/ADI-PersonalInterventionPreference"
    prof_cp = "http://hl7.org/fhir/us/pacio-adi/StructureDefinition/ADI-PreferenceCarePlan"
    w(
        d / "simple/01-intervention-preference-minimal-valid.json",
        {
            "resourceType": "Observation",
            "id": "adi-obs-1",
            "meta": {"profile": [prof_obs]},
            "status": "final",
            "code": {"text": "Personal intervention preference"},
            "subject": {"reference": "Patient/example"},
            "effectiveDateTime": "2026-01-01",
            "valueCodeableConcept": {"text": "Full code status"},
        },
    )
    w(
        d / "simple/02-intervention-preference-minimal-invalid.json",
        {
            "resourceType": "Observation",
            "id": "adi-obs-bad",
            "meta": {"profile": [prof_obs]},
            "status": "final",
        },
    )
    w(
        d / "complex/01-preference-careplan-full-valid.json",
        {
            "resourceType": "CarePlan",
            "id": "adi-cp-1",
            "meta": {"profile": [prof_cp]},
            "status": "active",
            "intent": "plan",
            "subject": {"reference": "Patient/example"},
            "title": "Advance directive care plan",
        },
    )
    w(
        d / "complex/02-preference-careplan-invalid.json",
        {
            "resourceType": "CarePlan",
            "id": "adi-cp-bad",
            "meta": {"profile": [prof_cp]},
            "status": "active",
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-advance-directive-v{n}.json",
            {
                "resourceType": "Observation",
                "id": f"adi-{n:03d}",
                "meta": {"profile": [prof_obs]},
                "status": "final",
                "code": {"text": "Intervention preference"},
                "subject": {"reference": f"Patient/adi-{n:03d}"},
                "effectiveDateTime": "2026-01-01",
                "valueCodeableConcept": {"text": f"Preference variant {n}"},
            },
        )


def gen_us_pacio_cs() -> None:
    d = ROOT / "us-pacio-cs"
    prof = "http://hl7.org/fhir/us/pacio-cs/StructureDefinition/pacio-cs"
    w(
        d / "simple/01-cognitive-status-minimal-valid.json",
        {
            "resourceType": "Observation",
            "id": "pcs-obs-1",
            "meta": {"profile": [prof]},
            "status": "final",
            "code": {"text": "Cognitive status"},
            "subject": {"reference": "Patient/example"},
            "effectiveDateTime": "2026-01-05",
            "valueCodeableConcept": {"text": "Alert and oriented x3"},
        },
    )
    w(
        d / "simple/02-cognitive-status-minimal-invalid.json",
        {
            "resourceType": "Observation",
            "id": "pcs-obs-bad",
            "meta": {"profile": [prof]},
            "status": "final",
        },
    )
    w(
        d / "complex/01-cognitive-status-full-valid.json",
        {
            "resourceType": "Observation",
            "id": "pcs-obs-full",
            "meta": {"profile": [prof]},
            "status": "final",
            "code": {"text": "Cognitive status assessment"},
            "subject": {"reference": "Patient/example"},
            "effectiveDateTime": "2026-01-05T10:00:00Z",
            "performer": [{"reference": "Practitioner/assessor-1"}],
            "valueCodeableConcept": {
                "coding": [{"system": "http://snomed.info/sct", "code": "248152002", "display": "Mild impairment"}],
                "text": "Mild cognitive impairment",
            },
        },
    )
    w(
        d / "complex/02-cognitive-status-invalid.json",
        {
            "resourceType": "Observation",
            "id": "pcs-obs-full-bad",
            "meta": {"profile": [prof]},
            "status": "entered-in-error",
            "valueBoolean": True,
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-cognitive-assessment-v{n}.json",
            {
                "resourceType": "Observation",
                "id": f"pcs-{n:03d}",
                "meta": {"profile": [prof]},
                "status": "final",
                "code": {"text": "Cognitive status"},
                "subject": {"reference": f"Patient/pcs-{n:03d}"},
                "effectiveDateTime": "2026-01-05",
                "valueCodeableConcept": {"text": f"Assessment result {n}"},
            },
        )


def gen_us_pacio_fs() -> None:
    d = ROOT / "us-pacio-fs"
    prof = "http://hl7.org/fhir/us/pacio-fs/StructureDefinition/pacio-fs"
    w(
        d / "simple/01-functional-status-minimal-valid.json",
        {
            "resourceType": "Observation",
            "id": "pfs-obs-1",
            "meta": {"profile": [prof]},
            "status": "final",
            "code": {"text": "Functional status"},
            "subject": {"reference": "Patient/example"},
            "effectiveDateTime": "2026-01-05",
            "valueCodeableConcept": {"text": "Independent with ADLs"},
        },
    )
    w(
        d / "simple/02-functional-status-minimal-invalid.json",
        {
            "resourceType": "Observation",
            "id": "pfs-obs-bad",
            "meta": {"profile": [prof]},
            "status": "final",
        },
    )
    w(
        d / "complex/01-functional-status-full-valid.json",
        {
            "resourceType": "Observation",
            "id": "pfs-obs-full",
            "meta": {"profile": [prof]},
            "status": "final",
            "code": {"text": "Functional status assessment"},
            "subject": {"reference": "Patient/example"},
            "effectiveDateTime": "2026-01-05T11:00:00Z",
            "valueCodeableConcept": {"text": "Requires assistance with bathing"},
        },
    )
    w(
        d / "complex/02-functional-status-invalid.json",
        {
            "resourceType": "Observation",
            "id": "pfs-obs-full-bad",
            "meta": {"profile": [prof]},
            "status": "final",
            "valueInteger": 5,
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-functional-assessment-v{n}.json",
            {
                "resourceType": "Observation",
                "id": f"pfs-{n:03d}",
                "meta": {"profile": [prof]},
                "status": "final",
                "code": {"text": "Functional status"},
                "subject": {"reference": f"Patient/pfs-{n:03d}"},
                "effectiveDateTime": "2026-01-05",
                "valueCodeableConcept": {"text": f"Functional level {n}"},
            },
        )


def gen_fhir_uv_ipa() -> None:
    d = ROOT / "fhir-uv-ipa"
    prof_pt = "http://hl7.org/fhir/uv/ipa/StructureDefinition/ipa-patient"
    prof_cond = "http://hl7.org/fhir/uv/ipa/StructureDefinition/ipa-condition"
    w(d / "simple/01-patient-minimal-valid.json", patient_base("ipa-pt-1", "Mueller", ["Hans"], prof_pt))
    w(
        d / "simple/02-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ipa-pt-bad",
            "meta": {"profile": [prof_pt]},
            "gender": "invalid",
        },
    )
    w(
        d / "complex/01-condition-full-valid.json",
        {
            "resourceType": "Condition",
            "id": "ipa-cond-1",
            "meta": {"profile": [prof_cond]},
            "clinicalStatus": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
            },
            "verificationStatus": {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}
                ]
            },
            "code": {
                "coding": [{"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes"}]
            },
            "subject": {"reference": "Patient/ipa-pt-1"},
        },
    )
    w(
        d / "complex/02-condition-invalid.json",
        {
            "resourceType": "Condition",
            "id": "ipa-cond-bad",
            "meta": {"profile": [prof_cond]},
            "subject": {"reference": "Patient/ipa-pt-1"},
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-international-patient-v{n}.json",
            patient_base(f"ipa-{n:03d}", "Schmidt", [f"Patient{n}"], prof_pt, gender="male"),
        )


def gen_fhir_uv_ips() -> None:
    d = ROOT / "fhir-uv-ips"
    prof_pt = "http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips"
    prof_cond = "http://hl7.org/fhir/uv/ips/StructureDefinition/Condition-uv-ips"
    w(d / "simple/01-patient-minimal-valid.json", patient_base("ips-pt-1", "Dupont", ["Marie"], prof_pt))
    w(
        d / "simple/02-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ips-pt-bad",
            "meta": {"profile": [prof_pt]},
            "gender": "not-valid",
        },
    )
    w(
        d / "complex/01-condition-full-valid.json",
        {
            "resourceType": "Condition",
            "id": "ips-cond-1",
            "meta": {"profile": [prof_cond]},
            "clinicalStatus": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
            },
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertension"}]},
            "subject": {"reference": "Patient/ips-pt-1"},
        },
    )
    w(
        d / "complex/02-condition-invalid.json",
        {
            "resourceType": "Condition",
            "id": "ips-cond-bad",
            "meta": {"profile": [prof_cond]},
            "clinicalStatus": {"text": "active"},
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-ips-patient-v{n}.json",
            patient_base(f"ips-{n:03d}", "Bernard", [f"Traveler{n}"], prof_pt),
        )


def gen_fhir_uv_smart_app_launch() -> None:
    d = ROOT / "fhir-uv-smart-app-launch"
    prof_task = "http://hl7.org/fhir/smart-app-launch/StructureDefinition/task-standalone-launch"
    prof_org = "http://hl7.org/fhir/smart-app-launch/StructureDefinition/user-access-brand"
    w(
        d / "simple/01-standalone-launch-task-minimal-valid.json",
        {
            "resourceType": "Task",
            "id": "smart-task-1",
            "meta": {"profile": [prof_task]},
            "status": "requested",
            "intent": "order",
            "description": "SMART standalone launch",
        },
    )
    w(
        d / "simple/02-standalone-launch-task-minimal-invalid.json",
        {
            "resourceType": "Task",
            "id": "smart-task-bad",
            "meta": {"profile": [prof_task]},
            "status": "requested",
        },
    )
    w(
        d / "complex/01-user-access-brand-full-valid.json",
        {
            "resourceType": "Organization",
            "id": "smart-org-1",
            "meta": {"profile": [prof_org]},
            "active": True,
            "name": "Community Hospital SMART Brand",
            "telecom": [{"system": "url", "value": "https://hospital.example.org"}],
        },
    )
    w(
        d / "complex/02-user-access-brand-invalid.json",
        {
            "resourceType": "Organization",
            "id": "smart-org-bad",
            "meta": {"profile": [prof_org]},
        },
    )
    for n in range(1, 6):
        w(
            d / f"realistic/{n:02d}-smart-launch-task-v{n}.json",
            {
                "resourceType": "Task",
                "id": f"smart-{n:03d}",
                "meta": {"profile": [prof_task]},
                "status": "requested",
                "intent": "order",
                "description": f"Launch SMART app context {n}",
            },
        )


GENERATORS = [
    gen_us_ccda,
    gen_us_bulkdata,
    gen_us_odh,
    gen_us_military_service,
    gen_us_vrdr,
    gen_davinci_pdex,
    gen_davinci_cdex,
    gen_davinci_pcde,
    gen_davinci_alerts,
    gen_davinci_drug_formulary,
    gen_davinci_deqm,
    gen_davinci_ra,
    gen_us_ecr,
    gen_us_pacio_adi,
    gen_us_pacio_cs,
    gen_us_pacio_fs,
    gen_fhir_uv_ipa,
    gen_fhir_uv_ips,
    gen_fhir_uv_smart_app_launch,
]


def main() -> None:
    for fn in GENERATORS:
        fn()
    print("\nDONE — popular IG test suites:")
    for folder in sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")):
        counts = []
        for kind in ("simple", "complex", "realistic"):
            n = len(list((ROOT / folder / kind).glob("*.json"))) if (ROOT / folder / kind).is_dir() else 0
            counts.append(f"{kind}={n}")
        print(f"  {folder}: {', '.join(counts)}")


if __name__ == "__main__":
    main()
