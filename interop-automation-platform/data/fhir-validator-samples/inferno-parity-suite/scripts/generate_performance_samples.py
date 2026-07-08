#!/usr/bin/env python3
"""Generate large, structurally valid FHIR R4 samples for validation speed testing."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "performance"

GENDERS = ("male", "female", "other", "unknown")
VITAL_CODES = [
    ("8302-2", "Body height", "cm", 150, 200),
    ("29463-7", "Body weight", "kg", 50, 120),
    ("8867-4", "Heart rate", "/min", 60, 100),
    ("8310-5", "Body temperature", "Cel", 36.0, 38.5),
    ("9279-1", "Respiratory rate", "/min", 12, 20),
    ("85354-9", "Blood pressure panel", None, None, None),
]


def _uuid() -> str:
    return str(uuid.uuid4())


def _patient(patient_id: str, index: int) -> dict:
    gender = GENDERS[index % len(GENDERS)]
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [
            {
                "use": "official",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number",
                        }
                    ]
                },
                "system": f"urn:oid:2.16.840.1.113883.19.5.{index % 1000}",
                "value": f"MRN-PERF-{index:05d}",
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official",
                "family": f"Performance{index % 50:02d}",
                "given": [f"Patient{index:04d}"],
            }
        ],
        "telecom": [
            {"system": "phone", "value": f"555-{index % 10000:04d}", "use": "home"},
            {"system": "email", "value": f"patient{index:04d}@healthinterop.test"},
        ],
        "gender": gender,
        "birthDate": f"{1950 + (index % 50):02d}-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}",
        "address": [
            {
                "use": "home",
                "line": [f"{100 + index} Validation Lane"],
                "city": "Interop City",
                "state": "IL",
                "postalCode": f"{60000 + (index % 999):05d}"[:5],
                "country": "US",
            }
        ],
        "contact": [
            {
                "relationship": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                "code": "C",
                                "display": "Emergency Contact",
                            }
                        ]
                    }
                ],
                "name": {"family": "Contact", "given": [f"Rel{index % 100:02d}"]},
                "telecom": [{"system": "phone", "value": f"555-9{index % 10000:04d}"}],
            }
        ],
    }


def _observation(obs_id: str, patient_ref: str, index: int) -> dict:
    code, display, unit, low, high = VITAL_CODES[index % len(VITAL_CODES)]
    obs: dict = {
        "resourceType": "Observation",
        "id": obs_id,
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
            "coding": [{"system": "http://loinc.org", "code": code, "display": display}]
        },
        "subject": {"reference": patient_ref},
        "effectiveDateTime": f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}T"
        f"{(index % 24):02d}:{(index % 60):02d}:00Z",
    }
    if code == "85354-9":
        obs["component"] = [
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
                    "value": 110 + (index % 30),
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
                    "value": 70 + (index % 20),
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]",
                },
            },
        ]
    elif unit:
        value = (low + (index % int((high or 1) - (low or 0)))) if low is not None and high is not None else index
        obs["valueQuantity"] = {
            "value": round(float(value), 1) if unit == "Cel" else value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit,
        }
    return obs


def _condition(cond_id: str, patient_ref: str, index: int) -> dict:
    conditions = [
        ("44054006", "Diabetes mellitus type 2"),
        ("38341003", "Hypertensive disorder"),
        ("13645005", "Chronic obstructive lung disease"),
        ("195967001", "Asthma"),
    ]
    code, display = conditions[index % len(conditions)]
    return {
        "resourceType": "Condition",
        "id": cond_id,
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
            "coding": [{"system": "http://snomed.info/sct", "code": code, "display": display}]
        },
        "subject": {"reference": patient_ref},
        "onsetDateTime": f"20{(10 + index % 10):02d}-01-15",
    }


def _encounter(enc_id: str, patient_ref: str, index: int) -> dict:
    return {
        "resourceType": "Encounter",
        "id": enc_id,
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory",
        },
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "185349003",
                        "display": "Encounter for check up",
                    }
                ]
            }
        ],
        "subject": {"reference": patient_ref},
        "period": {
            "start": f"2024-{(index % 12) + 1:02d}-01T09:00:00Z",
            "end": f"2024-{(index % 12) + 1:02d}-01T09:45:00Z",
        },
    }


def _bundle_entry(resource: dict) -> dict:
    rid = resource["id"]
    return {"fullUrl": f"urn:uuid:{_uuid()}", "resource": resource}


def _write(name: str, payload: dict) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    text = json.dumps(payload, indent=2)
    path.write_text(text, encoding="utf-8")
    size_kb = len(text.encode("utf-8")) / 1024
    entries = len(payload.get("entry", [])) if payload.get("resourceType") == "Bundle" else 1
    return {"file": name, "size_kb": round(size_kb, 1), "entries": entries}


def generate_large_patient() -> dict:
    patient = _patient("perf-large-patient-rich", 0)
    patient["identifier"].extend(
        {
            "use": "secondary",
            "system": f"urn:oid:2.16.840.1.113883.4.1",
            "value": f"{100000000 + i:09d}",
        }
        for i in range(1, 51)
    )
    patient["telecom"].extend(
        {"system": "phone", "value": f"555-8{i:04d}", "use": "work"} for i in range(100)
    )
    patient["address"].extend(
        {
            "use": "work",
            "line": [f"Suite {i}", f"{200 + i} Benchmark Blvd"],
            "city": "Interop City",
            "state": "IL",
            "postalCode": f"{60100 + i:05d}"[:5],
            "country": "US",
        }
        for i in range(50)
    )
    patient["contact"].extend(
        {
            "relationship": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                            "code": "N",
                            "display": "Next-of-Kin",
                        }
                    ]
                }
            ],
            "name": {"family": f"Kin{i:03d}", "given": ["Related"]},
            "telecom": [{"system": "phone", "value": f"555-7{i:04d}"}],
        }
        for i in range(100)
    )
    return patient


def generate_bundle_patients(count: int) -> dict:
    entries = [_bundle_entry(_patient(f"perf-patient-{i:04d}", i)) for i in range(count)]
    return {
        "resourceType": "Bundle",
        "id": f"perf-bundle-{count}-patients",
        "type": "collection",
        "entry": entries,
    }


def generate_bundle_observations(count: int) -> dict:
    patient_id = "perf-obs-subject"
    patient = _patient(patient_id, 0)
    entries = [_bundle_entry(patient)]
    for i in range(count):
        entries.append(
            _bundle_entry(_observation(f"perf-obs-{i:04d}", f"Patient/{patient_id}", i))
        )
    return {
        "resourceType": "Bundle",
        "id": f"perf-bundle-{count}-observations",
        "type": "collection",
        "entry": entries,
    }


def generate_bundle_mixed(count: int) -> dict:
    entries = []
    for i in range(count):
        pid = f"perf-mixed-patient-{i:04d}"
        entries.append(_bundle_entry(_patient(pid, i)))
        pref = f"Patient/{pid}"
        entries.append(_bundle_entry(_observation(f"perf-mixed-obs-{i:04d}", pref, i)))
        entries.append(_bundle_entry(_condition(f"perf-mixed-cond-{i:04d}", pref, i)))
        if i % 5 == 0:
            entries.append(_bundle_entry(_encounter(f"perf-mixed-enc-{i:04d}", pref, i)))
    return {
        "resourceType": "Bundle",
        "id": f"perf-bundle-{count}-mixed-clinical",
        "type": "collection",
        "entry": entries,
    }


def main() -> None:
    specs = [
        ("perf-01-large-patient-rich.json", generate_large_patient()),
        ("perf-02-bundle-100-patients.json", generate_bundle_patients(100)),
        ("perf-03-bundle-250-observations.json", generate_bundle_observations(250)),
        ("perf-04-bundle-75-mixed-clinical.json", generate_bundle_mixed(75)),
        ("perf-05-bundle-500-observations.json", generate_bundle_observations(500)),
    ]
    print(f"Writing performance samples to {OUT_DIR}\n")
    for name, payload in specs:
        info = _write(name, payload)
        print(
            f"  {info['file']}: {info['size_kb']} KB"
            + (f", {info['entries']} entries" if info["entries"] > 1 else "")
        )


if __name__ == "__main__":
    main()
