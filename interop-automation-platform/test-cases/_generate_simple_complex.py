"""Generate simple/ and complex/ test cases for every IG folder."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    print("wrote", path.as_posix())


def copy(src: str, dst: str) -> None:
    dest = ROOT / dst
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / src, dest)
    print("copied", dst)


def main() -> None:
    # ---------- US Core ----------
    write(
        ROOT / "hl7.fhir.us.core/simple/01-patient-minimal-valid.json",
        {
            "resourceType": "Patient",
            "id": "us-core-simple-patient",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                ]
            },
            "identifier": [{"system": "http://example.org/mrn", "value": "MRN-1001"}],
            "name": [{"family": "Lee", "given": ["Sam"]}],
            "gender": "male",
            "birthDate": "1990-01-01",
        },
    )
    write(
        ROOT / "hl7.fhir.us.core/simple/02-patient-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "us-core-simple-patient-invalid",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                ]
            },
            "name": [{"family": "Lee"}],
            "gender": "unknown-code",
        },
    )
    copy("hl7.fhir.us.core/01-patient-valid.json", "hl7.fhir.us.core/complex/01-patient-full-valid.json")
    copy(
        "hl7.fhir.us.core/04-observation-vital-signs-valid.json",
        "hl7.fhir.us.core/complex/02-observation-blood-pressure-valid.json",
    )
    copy(
        "hl7.fhir.us.core/09-medication-request-valid.json",
        "hl7.fhir.us.core/complex/03-medication-request-full-valid.json",
    )
    copy(
        "hl7.fhir.us.core/03-patient-invalid-values.json",
        "hl7.fhir.us.core/complex/04-patient-multi-error-invalid.json",
    )

    # ---------- Da Vinci CRD ----------
    write(
        ROOT / "hl7.fhir.us.davinci-crd/simple/01-coverage-minimal-valid.json",
        {
            "resourceType": "Coverage",
            "id": "crd-simple-coverage",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-crd/StructureDefinition/profile-coverage"
                ]
            },
            "status": "active",
            "beneficiary": {"reference": "Patient/example"},
            "payor": [{"reference": "Organization/payer-1"}],
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-crd/simple/02-coverage-minimal-invalid.json",
        {
            "resourceType": "Coverage",
            "id": "crd-simple-coverage-invalid",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-crd/StructureDefinition/profile-coverage"
                ]
            },
            "status": "not-a-status",
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-crd/simple/03-service-request-minimal-valid.json",
        {
            "resourceType": "ServiceRequest",
            "id": "crd-simple-sr",
            "status": "active",
            "intent": "order",
            "code": {
                "coding": [
                    {"system": "http://www.ama-assn.org/go/cpt", "code": "73721"}
                ]
            },
            "subject": {"reference": "Patient/example"},
        },
    )
    copy("hl7.fhir.us.davinci-crd/01-coverage-valid.json", "hl7.fhir.us.davinci-crd/complex/01-coverage-full-valid.json")
    copy(
        "hl7.fhir.us.davinci-crd/03-service-request-valid.json",
        "hl7.fhir.us.davinci-crd/complex/02-service-request-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-crd/06-medication-request-valid.json",
        "hl7.fhir.us.davinci-crd/complex/03-medication-request-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-crd/04-service-request-invalid.json",
        "hl7.fhir.us.davinci-crd/complex/04-service-request-multi-error-invalid.json",
    )

    # ---------- Da Vinci DTR ----------
    write(
        ROOT / "hl7.fhir.us.davinci-dtr/simple/01-questionnaire-response-minimal-valid.json",
        {
            "resourceType": "QuestionnaireResponse",
            "id": "dtr-simple-qr",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-dtr/StructureDefinition/dtr-questionnaireresponse"
                ]
            },
            "questionnaire": "http://example.org/Questionnaire/simple",
            "status": "completed",
            "subject": {"reference": "Patient/example"},
            "item": [{"linkId": "1", "answer": [{"valueBoolean": True}]}],
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-dtr/simple/02-questionnaire-response-minimal-invalid.json",
        {
            "resourceType": "QuestionnaireResponse",
            "id": "dtr-simple-qr-invalid",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/davinci-dtr/StructureDefinition/dtr-questionnaireresponse"
                ]
            },
            "status": "bogus",
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-dtr/simple/03-task-minimal-valid.json",
        {
            "resourceType": "Task",
            "id": "dtr-simple-task",
            "status": "requested",
            "intent": "order",
            "for": {"reference": "Patient/example"},
        },
    )
    copy(
        "hl7.fhir.us.davinci-dtr/01-questionnaire-response-valid.json",
        "hl7.fhir.us.davinci-dtr/complex/01-questionnaire-response-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-dtr/06-questionnaire-valid.json",
        "hl7.fhir.us.davinci-dtr/complex/02-questionnaire-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-dtr/07-parameters-valid.json",
        "hl7.fhir.us.davinci-dtr/complex/03-parameters-launch-context-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-dtr/02-questionnaire-response-invalid.json",
        "hl7.fhir.us.davinci-dtr/complex/04-questionnaire-response-multi-error-invalid.json",
    )

    # ---------- Da Vinci PAS ----------
    write(
        ROOT / "hl7.fhir.us.davinci-pas/simple/01-claim-minimal-valid.json",
        {
            "resourceType": "Claim",
            "id": "pas-simple-claim",
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
            "patient": {"reference": "Patient/example"},
            "created": "2024-03-01",
            "insurer": {"reference": "Organization/payer"},
            "provider": {"reference": "Organization/provider"},
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
                    "coverage": {"reference": "Coverage/1"},
                }
            ],
            "item": [
                {
                    "sequence": 1,
                    "productOrService": {
                        "coding": [
                            {
                                "system": "http://www.ama-assn.org/go/cpt",
                                "code": "70553",
                            }
                        ]
                    },
                }
            ],
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-pas/simple/02-claim-minimal-invalid.json",
        {
            "resourceType": "Claim",
            "id": "pas-simple-claim-invalid",
            "status": "active",
            "use": "preauthorization",
        },
    )
    write(
        ROOT / "hl7.fhir.us.davinci-pas/simple/03-organization-minimal-valid.json",
        {
            "resourceType": "Organization",
            "id": "pas-simple-org",
            "active": True,
            "name": "Simple Payer Inc",
        },
    )
    copy("hl7.fhir.us.davinci-pas/01-claim-valid.json", "hl7.fhir.us.davinci-pas/complex/01-claim-full-valid.json")
    copy(
        "hl7.fhir.us.davinci-pas/05-bundle-submit-valid.json",
        "hl7.fhir.us.davinci-pas/complex/02-bundle-submit-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-pas/04-claim-response-valid.json",
        "hl7.fhir.us.davinci-pas/complex/03-claim-response-full-valid.json",
    )
    copy(
        "hl7.fhir.us.davinci-pas/06-bundle-invalid.json",
        "hl7.fhir.us.davinci-pas/complex/04-bundle-multi-error-invalid.json",
    )

    # ---------- SDC ----------
    write(
        ROOT / "hl7.fhir.uv.sdc/simple/01-questionnaire-minimal-valid.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-simple-q",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "status": "draft",
            "item": [{"linkId": "1", "type": "boolean", "text": "Agree?"}],
        },
    )
    write(
        ROOT / "hl7.fhir.uv.sdc/simple/02-questionnaire-minimal-invalid.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-simple-q-invalid",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "item": [{"linkId": "1", "type": "string"}],
        },
    )
    write(
        ROOT / "hl7.fhir.uv.sdc/complex/01-questionnaire-multi-item-valid.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-complex-q",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "url": "http://hl7.org/fhir/uv/sdc/Questionnaire/demo-complex",
            "name": "SdcComplexDemo",
            "title": "SDC Complex Multi-item Questionnaire",
            "status": "active",
            "subjectType": ["Patient"],
            "date": "2024-06-01",
            "publisher": "Interop Automation Platform",
            "description": "Complex SDC questionnaire with nested groups and mixed item types.",
            "item": [
                {
                    "linkId": "demographics",
                    "text": "Demographics",
                    "type": "group",
                    "item": [
                        {
                            "linkId": "demographics.name",
                            "text": "Full name",
                            "type": "string",
                            "required": True,
                        },
                        {
                            "linkId": "demographics.dob",
                            "text": "Date of birth",
                            "type": "date",
                            "required": True,
                        },
                        {
                            "linkId": "demographics.gender",
                            "text": "Gender",
                            "type": "choice",
                            "answerOption": [
                                {
                                    "valueCoding": {
                                        "system": "http://hl7.org/fhir/administrative-gender",
                                        "code": "female",
                                        "display": "Female",
                                    }
                                },
                                {
                                    "valueCoding": {
                                        "system": "http://hl7.org/fhir/administrative-gender",
                                        "code": "male",
                                        "display": "Male",
                                    }
                                },
                            ],
                        },
                    ],
                },
                {
                    "linkId": "clinical",
                    "text": "Clinical",
                    "type": "group",
                    "item": [
                        {
                            "linkId": "clinical.symptoms",
                            "text": "Current symptoms",
                            "type": "text",
                        },
                        {
                            "linkId": "clinical.onset",
                            "text": "Onset date",
                            "type": "date",
                        },
                        {
                            "linkId": "clinical.severity",
                            "text": "Severity (1-10)",
                            "type": "integer",
                        },
                    ],
                },
                {
                    "linkId": "consent",
                    "text": "I consent to share this information",
                    "type": "boolean",
                    "required": True,
                },
            ],
        },
    )
    write(
        ROOT / "hl7.fhir.uv.sdc/complex/02-questionnaire-nested-invalid.json",
        {
            "resourceType": "Questionnaire",
            "id": "sdc-complex-q-invalid",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"
                ]
            },
            "url": "http://hl7.org/fhir/uv/sdc/Questionnaire/demo-complex-invalid",
            "name": "SdcComplexInvalid",
            "title": "SDC Complex Invalid",
            "status": "unknown-status",
            "item": [
                {
                    "type": "group",
                    "text": "Missing linkId group",
                    "item": [
                        {
                            "linkId": "x",
                            "type": "not-a-type",
                            "text": "Bad type",
                        }
                    ],
                }
            ],
        },
    )
    copy(
        "hl7.fhir.uv.sdc/03-questionnaireresponse-sdc-profile.json",
        "hl7.fhir.uv.sdc/complex/03-questionnaireresponse-sdc-profile.json",
    )

    # ---------- Extensions ----------
    write(
        ROOT / "hl7.fhir.uv.extensions.r4/simple/01-patient-one-extension-valid.json",
        {
            "resourceType": "Patient",
            "id": "ext-simple-valid",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueAddress": {
                        "city": "Austin",
                        "state": "TX",
                        "country": "US",
                    },
                }
            ],
            "name": [{"family": "Rivera", "given": ["Alex"]}],
            "gender": "male",
        },
    )
    write(
        ROOT / "hl7.fhir.uv.extensions.r4/simple/02-patient-one-extension-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ext-simple-invalid",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueBoolean": True,
                }
            ],
            "name": [{"family": "Rivera"}],
        },
    )
    write(
        ROOT / "hl7.fhir.uv.extensions.r4/complex/01-patient-multi-extension-valid.json",
        {
            "resourceType": "Patient",
            "id": "ext-complex-valid",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueAddress": {
                        "line": ["100 Harbor Dr"],
                        "city": "Boston",
                        "state": "MA",
                        "postalCode": "02110",
                        "country": "US",
                    },
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-religion",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ReligiousAffiliation",
                                "code": "1041",
                                "display": "Roman Catholic Church",
                            }
                        ],
                        "text": "Roman Catholic",
                    },
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-citizenship",
                    "extension": [
                        {
                            "url": "code",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "system": "urn:iso:std:iso:3166",
                                        "code": "US",
                                        "display": "United States of America",
                                    }
                                ]
                            },
                        }
                    ],
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-genderIdentity",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "446151000124109",
                                "display": "Identifies as male gender",
                            }
                        ]
                    },
                },
            ],
            "identifier": [
                {
                    "system": "http://hospital.example.org/patients",
                    "value": "EXT-9001",
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": "Doe",
                    "given": ["Jane", "Marie"],
                    "prefix": ["Ms."],
                },
                {"use": "usual", "given": ["Jamie"]},
            ],
            "telecom": [
                {"system": "phone", "value": "617-555-0147", "use": "mobile"},
                {"system": "email", "value": "jane.doe@example.org"},
            ],
            "gender": "female",
            "birthDate": "1985-04-12",
            "address": [
                {
                    "use": "home",
                    "line": ["42 Beacon Street", "Apt 3B"],
                    "city": "Boston",
                    "state": "MA",
                    "postalCode": "02108",
                    "country": "US",
                }
            ],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "M",
                        "display": "Married",
                    }
                ]
            },
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "en-US",
                                "display": "English (United States)",
                            }
                        ]
                    },
                    "preferred": True,
                }
            ],
        },
    )
    write(
        ROOT / "hl7.fhir.uv.extensions.r4/complex/02-patient-multi-extension-invalid.json",
        {
            "resourceType": "Patient",
            "id": "ext-complex-invalid",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
                    "valueString": "Boston only — should be Address",
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-religion",
                    "valueInteger": 42,
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-genderIdentity",
                    "valueBoolean": False,
                },
            ],
            "name": [{"family": "Doe", "given": ["Jane"]}],
            "gender": "not-a-gender",
            "birthDate": "85-04-12",
        },
    )

    # ---------- Terminology / THO ----------
    write(
        ROOT / "hl7.terminology.r4/simple/01-patient-maritalStatus-minimal-valid.json",
        {
            "resourceType": "Patient",
            "id": "tho-simple-valid",
            "name": [{"family": "Chen", "given": ["Li"]}],
            "gender": "female",
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "S",
                        "display": "Never Married",
                    }
                ]
            },
        },
    )
    write(
        ROOT / "hl7.terminology.r4/simple/02-patient-maritalStatus-minimal-invalid.json",
        {
            "resourceType": "Patient",
            "id": "tho-simple-invalid",
            "name": [{"family": "Chen"}],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "ZZZ-BAD",
                    }
                ]
            },
        },
    )
    write(
        ROOT / "hl7.terminology.r4/complex/01-patient-multi-tho-codes-valid.json",
        {
            "resourceType": "Patient",
            "id": "tho-complex-valid",
            "identifier": [
                {
                    "system": "http://hospital.example.org/mrn",
                    "value": "THO-7788",
                }
            ],
            "active": True,
            "name": [
                {"use": "official", "family": "Nguyen", "given": ["Anh", "Thi"]},
                {"use": "maiden", "family": "Tran"},
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": "+1-415-555-0199",
                    "use": "home",
                },
                {
                    "system": "email",
                    "value": "anh.nguyen@example.org",
                    "use": "work",
                },
            ],
            "gender": "female",
            "birthDate": "1990-08-21",
            "address": [
                {
                    "use": "home",
                    "type": "both",
                    "line": ["500 Market Street", "Suite 200"],
                    "city": "San Francisco",
                    "state": "CA",
                    "postalCode": "94105",
                    "country": "US",
                }
            ],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "M",
                        "display": "Married",
                    }
                ],
                "text": "Married",
            },
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "en",
                                "display": "English",
                            }
                        ]
                    },
                    "preferred": True,
                },
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "vi",
                                "display": "Vietnamese",
                            }
                        ]
                    }
                },
            ],
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-religion",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ReligiousAffiliation",
                                "code": "1008",
                                "display": "Buddhist",
                            }
                        ]
                    },
                }
            ],
        },
    )
    write(
        ROOT / "hl7.terminology.r4/complex/02-patient-multi-tho-codes-invalid.json",
        {
            "resourceType": "Patient",
            "id": "tho-complex-invalid",
            "name": [{"family": "Nguyen", "given": ["Anh"]}],
            "gender": "female",
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "NOT-A-REAL-CODE",
                        "display": "Invalid",
                    }
                ]
            },
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-religion",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ReligiousAffiliation",
                                "code": "FAKE-RELIGION-CODE",
                            }
                        ]
                    },
                }
            ],
        },
    )

    print("\nDONE")
    for ig in [
        "us-core",
        "davinci-crd",
        "davinci-dtr",
        "davinci-pas",
        "fhir-uv-sdc",
        "fhir-uv-extensions",
        "hl7-terminology",
    ]:
        for kind in ["simple", "complex"]:
            folder = ROOT / ig / kind
            files = sorted(folder.glob("*.json")) if folder.exists() else []
            print(f"{ig}/{kind}: {len(files)} -> {[f.name for f in files]}")


if __name__ == "__main__":
    main()
