"""
Generate many realistic healthcare-style FHIR test cases for every IG.

Output layout:
  test-cases/<ig-folder>/simple/
  test-cases/<ig-folder>/complex/
  test-cases/<ig-folder>/realistic/   ← EHR/payer/clinic style payloads
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def w(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def patient_base(pid: str, family: str, given: list[str], **extra) -> dict:
    p = {
        "resourceType": "Patient",
        "id": pid,
        "identifier": [
            {
                "use": "usual",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number",
                        }
                    ]
                },
                "system": "http://hospital.example.org/ehr/mrn",
                "value": f"MRN-{pid.upper()}",
            }
        ],
        "active": True,
        "name": [{"use": "official", "family": family, "given": given}],
        "telecom": [
            {"system": "phone", "value": "555-0100", "use": "mobile"},
            {"system": "email", "value": f"{given[0].lower()}.{family.lower()}@example.org"},
        ],
        "gender": extra.get("gender", "female"),
        "birthDate": extra.get("birthDate", "1978-05-14"),
        "address": [
            {
                "use": "home",
                "line": ["742 Evergreen Terrace"],
                "city": "Springfield",
                "state": "IL",
                "postalCode": "62704",
                "country": "US",
            }
        ],
    }
    p.update({k: v for k, v in extra.items() if k not in {"gender", "birthDate"}})
    return p


def main() -> None:
    # -------- US Core realistic --------
    us = ROOT / "hl7.fhir.us.core"
    w(
        us / "realistic/01-ehr-patient-admit.json",
        {
            **patient_base(
                "ehr-admit-001",
                "Patel",
                ["Priya"],
                meta={
                    "profile": [
                        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                    ]
                },
            ),
            "extension": [
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": "urn:oid:2.16.840.1.113883.6.238",
                                "code": "2028-9",
                                "display": "Asian",
                            },
                        },
                        {"url": "text", "valueString": "Asian"},
                    ],
                },
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": "urn:oid:2.16.840.1.113883.6.238",
                                "code": "2186-5",
                                "display": "Not Hispanic or Latino",
                            },
                        },
                        {"url": "text", "valueString": "Not Hispanic or Latino"},
                    ],
                },
            ],
        },
    )
    w(
        us / "realistic/02-ehr-vital-signs-panel.json",
        {
            "resourceType": "Observation",
            "id": "ehr-vs-bp-001",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure"
                ]
            },
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel",
                    }
                ],
                "text": "Blood pressure",
            },
            "subject": {"reference": "Patient/ehr-admit-001"},
            "effectiveDateTime": "2026-07-18T09:15:00-05:00",
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 128,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 82,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
            ],
        },
    )
    w(
        us / "realistic/03-ehr-problem-list-condition.json",
        {
            "resourceType": "Condition",
            "id": "ehr-cond-htn",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-problems-health-concerns"
                ]
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "problem-list-item",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "38341003",
                        "display": "Hypertensive disorder",
                    }
                ],
                "text": "Hypertension",
            },
            "subject": {"reference": "Patient/ehr-admit-001"},
            "onsetDateTime": "2019-03-01",
            "recordedDate": "2026-07-18",
        },
    )
    w(
        us / "realistic/04-ehr-lab-result-missing-subject.json",
        {
            "resourceType": "Observation",
            "id": "ehr-lab-bad",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"
                ]
            },
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "2339-0",
                        "display": "Glucose",
                    }
                ]
            },
            "valueQuantity": {
                "value": 110,
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",
                "code": "mg/dL",
            },
        },
    )
    for i, (code, display, val) in enumerate(
        [
            ("8867-4", "Heart rate", 72),
            ("8310-5", "Body temperature", 98.6),
            ("9279-1", "Respiratory rate", 16),
            ("2708-6", "Oxygen saturation", 98),
            ("29463-7", "Body weight", 70.5),
        ],
        start=5,
    ):
        w(
            us / f"realistic/{i:02d}-ehr-vital-{code}.json",
            {
                "resourceType": "Observation",
                "id": f"ehr-vs-{code}",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs"
                    ]
                },
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "vital-signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": code, "display": display}
                    ]
                },
                "subject": {"reference": "Patient/ehr-admit-001"},
                "effectiveDateTime": "2026-07-18T09:20:00-05:00",
                "valueQuantity": {
                    "value": val,
                    "system": "http://unitsofmeasure.org",
                    "code": "1",
                },
            },
        )

    # -------- CRD realistic (payer coverage check) --------
    crd = ROOT / "hl7.fhir.us.davinci-crd"
    w(
        crd / "realistic/01-payer-coverage-active.json",
        {
            "resourceType": "Coverage",
            "id": "payer-cov-001",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-crd/StructureDefinition/profile-coverage"
                ]
            },
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "HIP",
                    }
                ]
            },
            "subscriberId": "MEM-998877",
            "beneficiary": {"reference": "Patient/ehr-admit-001"},
            "relationship": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                        "code": "self",
                    }
                ]
            },
            "period": {"start": "2026-01-01", "end": "2026-12-31"},
            "payor": [{"reference": "Organization/blue-cross", "display": "Blue Cross"}],
            "class": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                "code": "group",
                            }
                        ]
                    },
                    "value": "GRP-ACME-2026",
                    "name": "ACME Employees",
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                "code": "plan",
                            }
                        ]
                    },
                    "value": "GOLD-PPO",
                    "name": "Gold PPO",
                },
            ],
        },
    )
    for n, (cpt, text) in enumerate(
        [
            ("70553", "MRI brain w/o & w contrast"),
            ("93306", "Echocardiography complete"),
            ("71260", "CT thorax w contrast"),
            ("72148", "MRI lumbar spine w/o contrast"),
            ("27447", "Total knee arthroplasty"),
        ],
        start=2,
    ):
        w(
            crd / f"realistic/{n:02d}-order-{cpt}.json",
            {
                "resourceType": "ServiceRequest",
                "id": f"crd-order-{cpt}",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/davinci-crd/StructureDefinition/profile-servicerequest"
                    ]
                },
                "status": "active",
                "intent": "order",
                "code": {
                    "coding": [
                        {
                            "system": "http://www.ama-assn.org/go/cpt",
                            "code": cpt,
                            "display": text,
                        }
                    ],
                    "text": text,
                },
                "subject": {"reference": "Patient/ehr-admit-001"},
                "authoredOn": "2026-07-18",
                "requester": {"reference": "Practitioner/dr-smith"},
                "insurance": [{"reference": "Coverage/payer-cov-001"}],
                "reasonCode": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                "code": "I10",
                                "display": "Essential hypertension",
                            }
                        ]
                    }
                ],
            },
        )
    w(
        crd / "realistic/07-order-invalid-status.json",
        {
            "resourceType": "ServiceRequest",
            "id": "crd-order-bad",
            "status": "scheduled-wrong",
            "intent": "proposal-wrong",
            "subject": {"reference": "Patient/ehr-admit-001"},
        },
    )

    # -------- DTR realistic --------
    dtr = ROOT / "davinci-dtr"
    w(
        dtr / "realistic/01-pa-documentation-qr.json",
        {
            "resourceType": "QuestionnaireResponse",
            "id": "dtr-pa-doc-001",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-dtr/StructureDefinition/dtr-questionnaireresponse"
                ]
            },
            "questionnaire": "http://example.org/Questionnaire/home-oxygen",
            "status": "completed",
            "subject": {"reference": "Patient/ehr-admit-001"},
            "authored": "2026-07-18T14:00:00Z",
            "author": {"reference": "Practitioner/dr-smith"},
            "item": [
                {
                    "linkId": "diagnosis",
                    "text": "Primary diagnosis",
                    "answer": [
                        {
                            "valueCoding": {
                                "system": "http://snomed.info/sct",
                                "code": "13645005",
                                "display": "COPD",
                            }
                        }
                    ],
                },
                {
                    "linkId": "o2-sat",
                    "text": "Resting O2 saturation",
                    "answer": [{"valueInteger": 88}],
                },
                {
                    "linkId": "tried-alternatives",
                    "text": "Tried alternatives?",
                    "answer": [{"valueBoolean": True}],
                },
                {
                    "linkId": "notes",
                    "text": "Clinical notes",
                    "answer": [
                        {
                            "valueString": "Patient desaturates on room air; qualifies for home O2."
                        }
                    ],
                },
            ],
        },
    )
    for n in range(2, 8):
        w(
            dtr / f"realistic/{n:02d}-qr-item-batch-{n}.json",
            {
                "resourceType": "QuestionnaireResponse",
                "id": f"dtr-qr-batch-{n}",
                "questionnaire": f"http://example.org/Questionnaire/pa-form-{n}",
                "status": "completed",
                "subject": {"reference": "Patient/ehr-admit-001"},
                "authored": "2026-07-18T15:00:00Z",
                "item": [
                    {
                        "linkId": str(i),
                        "text": f"Question {i}",
                        "answer": [{"valueString": f"Answer {i} from clinic EHR"}],
                    }
                    for i in range(1, n + 2)
                ],
            },
        )
    w(
        dtr / "realistic/08-qr-invalid-incomplete-status.json",
        {
            "resourceType": "QuestionnaireResponse",
            "id": "dtr-qr-bad",
            "status": "not-a-status",
            "item": [{"linkId": "1"}],
        },
    )

    # -------- PAS realistic --------
    pas = ROOT / "davinci-pas"
    w(
        pas / "realistic/01-prior-auth-claim.json",
        {
            "resourceType": "Claim",
            "id": "pas-pa-001",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-pas/StructureDefinition/profile-claim"
                ]
            },
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                        "code": "professional",
                    }
                ]
            },
            "use": "preauthorization",
            "patient": {"reference": "Patient/ehr-admit-001"},
            "created": "2026-07-18",
            "insurer": {"reference": "Organization/blue-cross"},
            "provider": {"reference": "Organization/clinic-ortho"},
            "priority": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                        "code": "normal",
                    }
                ]
            },
            "diagnosis": [
                {
                    "sequence": 1,
                    "diagnosisCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                "code": "M17.11",
                                "display": "Unilateral primary osteoarthritis, right knee",
                            }
                        ]
                    },
                }
            ],
            "insurance": [
                {
                    "sequence": 1,
                    "focal": True,
                    "coverage": {"reference": "Coverage/payer-cov-001"},
                }
            ],
            "item": [
                {
                    "sequence": 1,
                    "productOrService": {
                        "coding": [
                            {
                                "system": "http://www.ama-assn.org/go/cpt",
                                "code": "27447",
                                "display": "Total knee arthroplasty",
                            }
                        ]
                    },
                    "servicedDate": "2026-08-15",
                    "quantity": {"value": 1},
                }
            ],
        },
    )
    for n, cpt in enumerate(["70553", "93306", "71260", "72148", "27447"], start=2):
        w(
            pas / f"realistic/{n:02d}-pa-claim-{cpt}.json",
            {
                "resourceType": "Claim",
                "id": f"pas-claim-{cpt}",
                "status": "active",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                            "code": "professional",
                        }
                    ]
                },
                "use": "preauthorization",
                "patient": {"reference": "Patient/ehr-admit-001"},
                "created": "2026-07-18",
                "insurer": {"reference": "Organization/blue-cross"},
                "provider": {"reference": "Organization/clinic-ortho"},
                "priority": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                            "code": "normal",
                        }
                    ]
                },
                "insurance": [
                    {
                        "sequence": 1,
                        "focal": True,
                        "coverage": {"reference": "Coverage/payer-cov-001"},
                    }
                ],
                "item": [
                    {
                        "sequence": 1,
                        "productOrService": {
                            "coding": [
                                {
                                    "system": "http://www.ama-assn.org/go/cpt",
                                    "code": cpt,
                                }
                            ]
                        },
                    }
                ],
            },
        )
    w(
        pas / "realistic/07-claim-missing-patient.json",
        {
            "resourceType": "Claim",
            "id": "pas-claim-bad",
            "status": "active",
            "use": "preauthorization",
            "created": "2026-07-18",
        },
    )

    # -------- SDC realistic --------
    sdc = ROOT / "fhir-uv-sdc"
    w(
        sdc / "realistic/01-clinic-intake-questionnaire.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-intake-001",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "url": "http://hl7.org/fhir/uv/sdc/Questionnaire/clinic-intake",
            "name": "ClinicIntake",
            "title": "Clinic Patient Intake",
            "status": "active",
            "subjectType": ["Patient"],
            "item": [
                {
                    "linkId": "chief-complaint",
                    "text": "Chief complaint",
                    "type": "text",
                    "required": True,
                },
                {
                    "linkId": "allergies",
                    "text": "Known allergies",
                    "type": "string",
                },
                {
                    "linkId": "meds",
                    "text": "Current medications",
                    "type": "text",
                },
                {
                    "linkId": "consent",
                    "text": "Consent to treat",
                    "type": "boolean",
                    "required": True,
                },
            ],
        },
    )
    for n in range(2, 10):
        w(
            sdc / f"realistic/{n:02d}-intake-form-v{n}.json",
            {
                "resourceType": "Questionnaire",
                "id": f"sdc-intake-v{n}",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                    ]
                },
                "status": "draft",
                "title": f"Intake Form Version {n}",
                "item": [
                    {
                        "linkId": f"q{i}",
                        "text": f"Intake question {i}",
                        "type": "string",
                    }
                    for i in range(1, n + 3)
                ],
            },
        )
    w(
        sdc / "realistic/10-intake-missing-status.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-intake-bad",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "title": "Broken intake",
            "item": [{"linkId": "1", "type": "string", "text": "Name"}],
        },
    )

    # -------- Extensions realistic --------
    ext = ROOT / "fhir-uv-extensions"
    w(
        ext / "realistic/01-registration-patient-extensions.json",
        {
            **patient_base("reg-ext-001", "Garcia", ["Maria"]),
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueAddress": {
                        "city": "Mexico City",
                        "country": "MX",
                    },
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-nationality",
                    "extension": [
                        {
                            "url": "code",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "system": "urn:iso:std:iso:3166",
                                        "code": "MX",
                                    }
                                ]
                            },
                        }
                    ],
                },
            ],
        },
    )
    for n in range(2, 8):
        w(
            ext / f"realistic/{n:02d}-patient-birthPlace-variant-{n}.json",
            {
                **patient_base(f"reg-ext-{n:03d}", "Lee", ["Kim"], gender="female"),
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                        "valueAddress": {
                            "city": f"City{n}",
                            "state": "CA",
                            "country": "US",
                        },
                    }
                ],
            },
        )
    w(
        ext / "realistic/08-patient-birthPlace-wrong-type.json",
        {
            **patient_base("reg-ext-bad", "Lee", ["Kim"]),
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueString": "Los Angeles",
                }
            ],
        },
    )

    # -------- Terminology realistic --------
    tho = ROOT / "hl7-terminology"
    codes = [("M", "Married"), ("S", "Never Married"), ("D", "Divorced"), ("W", "Widowed")]
    for n, (code, display) in enumerate(codes, start=1):
        w(
            tho / f"realistic/{n:02d}-patient-marital-{code}.json",
            {
                **patient_base(f"tho-{code.lower()}", "Nguyen", ["Anh"]),
                "maritalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                            "code": code,
                            "display": display,
                        }
                    ]
                },
            },
        )
    w(
        tho / "realistic/05-patient-marital-invalid.json",
        {
            **patient_base("tho-bad", "Nguyen", ["Anh"]),
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "XX-INVALID",
                    }
                ]
            },
        },
    )

    # -------- mCODE / CARIN / QI-Core (uploadable IGs) --------
    mcode = ROOT / "us-mcode"
    w(
        mcode / "simple/01-cancer-patient-minimal.json",
        {
            "resourceType": "Patient",
            "id": "mcode-pt-1",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-patient"
                ]
            },
            "identifier": [{"system": "http://hospital.example.org/mrn", "value": "ONC-1"}],
            "name": [{"family": "Oncology", "given": ["Casey"]}],
            "gender": "female",
            "birthDate": "1965-02-02",
        },
    )
    w(
        mcode / "simple/02-cancer-patient-invalid-gender.json",
        {
            "resourceType": "Patient",
            "id": "mcode-pt-bad",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-patient"
                ]
            },
            "name": [{"family": "Oncology"}],
            "gender": "not-valid",
        },
    )
    w(
        mcode / "complex/01-primary-cancer-condition.json",
        {
            "resourceType": "Condition",
            "id": "mcode-ca-1",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-primary-cancer-condition"
                ]
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "254837009",
                        "display": "Malignant neoplasm of breast",
                    }
                ]
            },
            "subject": {"reference": "Patient/mcode-pt-1"},
            "onsetDateTime": "2025-11-01",
        },
    )
    for n in range(2, 9):
        w(
            mcode / f"realistic/{n:02d}-oncology-patient-{n}.json",
            {
                "resourceType": "Patient",
                "id": f"mcode-pt-{n}",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-patient"
                    ]
                },
                "identifier": [
                    {
                        "system": "http://cancercenter.example.org/mrn",
                        "value": f"ONC-{1000 + n}",
                    }
                ],
                "name": [{"family": f"Patient{n}", "given": ["Oncology"]}],
                "gender": "female" if n % 2 == 0 else "male",
                "birthDate": f"{1950 + n}-06-15",
            },
        )

    carin = ROOT / "us-carin-bb"
    w(
        carin / "simple/01-patient-minimal.json",
        {
            **patient_base("carin-pt-1", "Blue", ["Button"]),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Patient"
                ]
            },
        },
    )
    w(
        carin / "simple/02-patient-invalid.json",
        {
            "resourceType": "Patient",
            "id": "carin-pt-bad",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Patient"
                ]
            },
            "gender": "xyz",
        },
    )
    for n in range(1, 9):
        w(
            carin / f"realistic/{n:02d}-member-patient-{n}.json",
            {
                **patient_base(f"carin-mem-{n}", "Member", [f"User{n}"]),
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Patient"
                    ]
                },
            },
        )

    qicore = ROOT / "us-qicore"
    w(
        qicore / "simple/01-patient-minimal.json",
        {
            **patient_base("qi-pt-1", "Quality", ["Measure"]),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient"
                ]
            },
        },
    )
    w(
        qicore / "simple/02-patient-invalid.json",
        {
            "resourceType": "Patient",
            "id": "qi-pt-bad",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient"
                ]
            },
            "gender": "bad-code",
        },
    )
    for n in range(1, 9):
        w(
            qicore / f"realistic/{n:02d}-quality-patient-{n}.json",
            {
                **patient_base(f"qi-pt-{n}", "Clinic", [f"Patient{n}"]),
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient"
                    ]
                },
            },
        )

    # Count summary
    print("Generated realistic healthcare test cases:")
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir():
            continue
        count = len(list(folder.rglob("*.json")))
        print(f"  {folder.name}: {count} json files")


if __name__ == "__main__":
    main()
