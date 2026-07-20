"""Extract constraint profiles from local IG packages (for test-case generation)."""
from __future__ import annotations

import json
import tarfile
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[1] / "fhir_packages"

IGS = [
    "hl7.fhir.us.ccda",
    "hl7.fhir.us.bulkdata",
    "hl7.fhir.us.odh",
    "hl7.fhir.us.military-service",
    "hl7.fhir.us.vrdr",
    "hl7.fhir.us.davinci-pdex",
    "hl7.fhir.us.davinci-cdex",
    "hl7.fhir.us.davinci-pcde",
    "hl7.fhir.us.davinci-alerts",
    "hl7.fhir.us.davinci-drug-formulary",
    "hl7.fhir.us.davinci-deqm",
    "hl7.fhir.us.davinci-ra",
    "hl7.fhir.us.ecr",
    "hl7.fhir.us.pacio-adi",
    "hl7.fhir.us.pacio-cs",
    "hl7.fhir.us.pacio-fs",
    "hl7.fhir.uv.ipa",
    "hl7.fhir.uv.ips",
    "hl7.fhir.uv.smart-app-launch",
]


def find_tgz(package_id: str) -> Path | None:
    needle = package_id.lower().replace("davinci-drug-formulary", "drug-formulary")
    for f in PACKAGES.glob("*.tgz"):
        if needle.split(".")[-1] in f.name.lower() or package_id.lower().replace("hl7.fhir.", "") in f.name.lower():
            return f
    for f in PACKAGES.glob("*.tgz"):
        if package_id.split(".")[-1].lower() in f.name.lower():
            return f
    return None


def profiles_for(path: Path, limit: int = 12) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    with tarfile.open(path, "r:gz") as tar:
        for member in tar.getmembers():
            if "StructureDefinition" not in member.name or not member.name.endswith(".json"):
                continue
            fobj = tar.extractfile(member)
            if not fobj:
                continue
            try:
                sd = json.loads(fobj.read().decode("utf-8-sig"))
            except Exception:
                continue
            if sd.get("resourceType") != "StructureDefinition":
                continue
            if sd.get("kind") != "resource" or sd.get("derivation") != "constraint":
                continue
            url = sd.get("url") or ""
            rt = sd.get("type") or ""
            if url:
                out.append((rt, url))
    # Prefer Patient, then common types
    priority = {"Patient": 0, "Observation": 1, "Condition": 2, "Coverage": 3, "Claim": 4, "Bundle": 5}
    out.sort(key=lambda x: (priority.get(x[0], 99), x[0], x[1]))
    return out[:limit]


if __name__ == "__main__":
    for pid in IGS:
        tgz = find_tgz(pid)
        if not tgz:
            print(f"\n=== {pid} MISSING ===")
            continue
        profs = profiles_for(tgz)
        print(f"\n=== {pid} ({tgz.name}) ===")
        for rt, url in profs:
            print(f"  {rt}: {url}")
