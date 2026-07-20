"""Build interop.terminology.local package for offline CTS ValueSet resolution."""
from __future__ import annotations

import io
import json
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "fhir_packages"
PKG_ID = "interop.terminology.local"
VERSION = "1.3.0"

LOINC = "http://loinc.org"
NULL_FLAVOR = "http://terminology.hl7.org/CodeSystem/v3-NullFlavor"
CDCREC = "urn:oid:2.16.840.1.113883.6.238"

CTS_RE = re.compile(r"http://cts\.nlm\.nih\.gov/fhir/ValueSet/[0-9.]+")


def _scan_us_core_cts_urls() -> set[str]:
    urls: set[str] = set()
    with tarfile.open(OUT_DIR / "us-core.tgz", "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.endswith(".json"):
                continue
            raw = tar.extractfile(member).read().decode("utf-8", "ignore")
            urls.update(CTS_RE.findall(raw))
    return urls


def _vs(
    *,
    vid: str,
    url: str,
    name: str,
    title: str,
    compose_include: list,
    contains: list,
    experimental: bool = False,
    description: str | None = None,
    expansion_only: bool = False,
) -> dict:
    oid = url.rsplit("/", 1)[-1] if "cts.nlm.nih.gov" in url else None
    resource: dict = {
        "resourceType": "ValueSet",
        "id": vid,
        "url": url,
        "version": VERSION,
        "name": name,
        "title": title,
        "status": "active",
        "experimental": experimental,
        "expansion": {
            "identifier": f"urn:uuid:{vid}",
            "timestamp": "2026-07-20T00:00:00Z",
            "total": len(contains),
            "contains": contains,
        },
    }
    # Expansion-only avoids re-expanding via LOINC (not available offline / shadowed).
    if not expansion_only:
        resource["compose"] = {"include": compose_include}
    if oid and oid[0].isdigit():
        resource["identifier"] = [
            {"system": "urn:ietf:rfc:3986", "value": f"urn:oid:{oid}"}
        ]
    if description:
        resource["description"] = description
    return resource


def main() -> None:
    for stale in OUT_DIR.glob(f"{PKG_ID}-*.tgz"):
        if stale.name != f"{PKG_ID}-{VERSION}.tgz":
            stale.unlink()
            print("Removed", stale)

    cts_urls = _scan_us_core_cts_urls()
    print(f"Found {len(cts_urls)} CTS ValueSet URLs in us-core")

    race_codes = [
        ("1002-5", "American Indian or Alaska Native"),
        ("2028-9", "Asian"),
        ("2054-5", "Black or African American"),
        ("2076-8", "Native Hawaiian or Other Pacific Islander"),
        ("2106-3", "White"),
        ("2131-1", "Other Race"),
    ]
    eth_codes = [
        ("2135-2", "Hispanic or Latino"),
        ("2186-5", "Not Hispanic or Latino"),
    ]
    null_codes = [("ASKU", "asked but unknown"), ("UNK", "unknown")]

    vital_loinc = [
        ("85353-1", "Vital signs panel"),
        ("9279-1", "Respiratory rate"),
        ("8867-4", "Heart rate"),
        ("2708-6", "Oxygen saturation in Arterial blood"),
        ("8310-5", "Body temperature"),
        ("8302-2", "Body height"),
        ("8306-3", "Body height --lying"),
        ("8287-5", "Head Occipital-frontal circumference by Tape measure"),
        ("9843-4", "Head Occipital-frontal circumference"),
        ("29463-7", "Body weight"),
        ("29464-5", "Body weight estimated"),
        ("39156-5", "Body mass index (BMI) [Ratio]"),
        ("85354-9", "Blood pressure panel with all children optional"),
        ("8480-6", "Systolic blood pressure"),
        ("8462-4", "Diastolic blood pressure"),
        ("8478-0", "Mean blood pressure"),
        ("59576-9", "Body mass index (BMI) [Percentile] Per age and sex"),
        ("8289-1", "Head Occipital-frontal circumference Percentile"),
        ("77606-2", "Weight-for-length Per age and sex"),
        ("59408-5", "Oxygen saturation in Arterial blood by Pulse oximetry"),
        ("3150-0", "Inhaled oxygen concentration"),
        ("3151-8", "Inhaled oxygen flow rate"),
        ("72514-3", "Pain severity - 0-10 verbal numeric rating [Score] - Reported"),
    ]
    seen: set[str] = set()
    vital_unique: list[tuple[str, str]] = []
    for code, display in vital_loinc:
        if code not in seen:
            seen.add(code)
            vital_unique.append((code, display))

    known: dict[str, dict] = {
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.4.642.2.575": {
            "id": "omb-race-category-cts",
            "name": "OmbRaceCategoriesCTS",
            "title": "OMB Race Categories (offline CTS alias)",
            "contains": (
                [{"system": CDCREC, "code": c, "display": d} for c, d in race_codes]
                + [
                    {"system": NULL_FLAVOR, "code": c, "display": d}
                    for c, d in null_codes
                ]
            ),
            "compose_include": [
                {
                    "system": CDCREC,
                    "concept": [{"code": c, "display": d} for c, d in race_codes],
                },
                {
                    "system": NULL_FLAVOR,
                    "concept": [{"code": c, "display": d} for c, d in null_codes],
                },
            ],
        },
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.4.642.40.2.48.3": {
            "id": "omb-ethnicity-category-cts",
            "name": "OmbEthnicityCategoriesCTS",
            "title": "OMB Ethnicity Categories (offline CTS alias)",
            "contains": (
                [{"system": CDCREC, "code": c, "display": d} for c, d in eth_codes]
                + [
                    {"system": NULL_FLAVOR, "code": c, "display": d}
                    for c, d in null_codes
                ]
            ),
            "compose_include": [
                {
                    "system": CDCREC,
                    "concept": [{"code": c, "display": d} for c, d in eth_codes],
                },
                {
                    "system": NULL_FLAVOR,
                    "concept": [{"code": c, "display": d} for c, d in null_codes],
                },
            ],
        },
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.114222.4.11.836": {
            "id": "race-category-excluding-nulls",
            "name": "RaceCategoryExcludingNulls",
            "title": "Race Category Excluding Nulls (offline)",
            "contains": [
                {"system": CDCREC, "code": c, "display": d} for c, d in race_codes
            ],
            "compose_include": [
                {"system": CDCREC, "concept": [{"code": c} for c, _ in race_codes]}
            ],
        },
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1021.102": {
            "id": "unknown-or-refused",
            "name": "UnknownOrRefusedToAnswer",
            "title": "Unknown or refused to answer (offline)",
            "contains": [
                {"system": NULL_FLAVOR, "code": c, "display": d} for c, d in null_codes
            ],
            "compose_include": [
                {
                    "system": NULL_FLAVOR,
                    "concept": [{"code": c} for c, _ in null_codes],
                }
            ],
        },
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.114222.4.11.837": {
            "id": "ethnicity-omb",
            "name": "EthnicityOMB",
            "title": "Ethnicity OMB (offline)",
            "contains": [
                {"system": CDCREC, "code": c, "display": d} for c, d in eth_codes
            ],
            "compose_include": [
                {"system": CDCREC, "concept": [{"code": c} for c, _ in eth_codes]}
            ],
        },
        "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.88.12.80.62": {
            "id": "vital-sign-result-type",
            "name": "VitalSignResultType",
            "title": "Vital Sign Result Type (offline CTS alias)",
            "expansion_only": True,
            "contains": [
                {"system": LOINC, "code": c, "display": d} for c, d in vital_unique
            ],
            "compose_include": [
                {
                    "system": LOINC,
                    "concept": [
                        {"code": c, "display": d} for c, d in vital_unique
                    ],
                }
            ],
        },
    }

    resources: list[tuple[str, dict]] = []

    resources.append(
        (
            "package/CodeSystem-cdcrec-local.json",
            {
                "resourceType": "CodeSystem",
                "id": "cdcrec-local",
                "url": CDCREC,
                "identifier": [
                    {
                        "system": "urn:ietf:rfc:3986",
                        "value": "urn:oid:2.16.840.1.113883.6.238",
                    }
                ],
                "version": VERSION,
                "name": "CDCRECLocal",
                "title": "CDC Race and Ethnicity Code System (local subset)",
                "status": "active",
                "experimental": False,
                "content": "fragment",
                "caseSensitive": True,
                "concept": [
                    {"code": c, "display": d} for c, d in race_codes + eth_codes
                ],
            },
        )
    )

    # LOINC fragment so vital-sign ValueSet membership works offline
    resources.append(
        (
            "package/CodeSystem-loinc-local.json",
            {
                "resourceType": "CodeSystem",
                "id": "loinc-local",
                "url": LOINC,
                "version": VERSION,
                "name": "LoincLocal",
                "title": "LOINC (local vital-signs subset)",
                "status": "active",
                "experimental": False,
                "content": "fragment",
                "caseSensitive": True,
                "concept": [
                    {"code": c, "display": d} for c, d in vital_unique
                ],
            },
        )
    )

    # UCUM fragment for common vital-sign units
    ucum_units = [
        ("mm[Hg]", "millimeter of mercury"),
        ("/min", "per minute"),
        ("Cel", "degree Celsius"),
        ("[degF]", "degree Fahrenheit"),
        ("kg", "kilogram"),
        ("g", "gram"),
        ("[lb_av]", "pound (US)"),
        ("cm", "centimeter"),
        ("[in_i]", "inch (international)"),
        ("kg/m2", "kilogram / (meter ^ 2)"),
        ("%", "percent"),
        ("L/min", "liter per minute"),
        ("{score}", "score"),
    ]
    resources.append(
        (
            "package/CodeSystem-ucum-local.json",
            {
                "resourceType": "CodeSystem",
                "id": "ucum-local",
                "url": "http://unitsofmeasure.org",
                "version": VERSION,
                "name": "UcumLocal",
                "title": "UCUM (local vital-signs subset)",
                "status": "active",
                "experimental": False,
                "content": "fragment",
                "caseSensitive": True,
                "concept": [{"code": c, "display": d} for c, d in ucum_units],
            },
        )
    )

    # Common vitals units ValueSet used by FHIR vital-sign profiles
    ucum_vs_contains = [
        {"system": "http://unitsofmeasure.org", "code": c, "display": d}
        for c, d in ucum_units
    ]
    resources.append(
        (
            "package/ValueSet-ucum-vitals-common.json",
            _vs(
                vid="ucum-vitals-common-local",
                url="http://hl7.org/fhir/ValueSet/ucum-vitals-common",
                name="VitalSignsUnits",
                title="Vital Signs Units",
                compose_include=[
                    {
                        "system": "http://unitsofmeasure.org",
                        "concept": [
                            {"code": c, "display": d} for c, d in ucum_units
                        ],
                    }
                ],
                contains=ucum_vs_contains,
                expansion_only=True,
            ),
        )
    )
    resources[-1][1]["version"] = "4.0.1"

    # Base FHIR vital-sign result ValueSet (also referenced alongside CTS)
    vitals_contains = [
        {"system": LOINC, "code": c, "display": d} for c, d in vital_unique
    ]
    resources.append(
        (
            "package/ValueSet-observation-vitalsignresult.json",
            _vs(
                vid="observation-vitalsignresult-local",
                url="http://hl7.org/fhir/ValueSet/observation-vitalsignresult",
                name="VitalSigns",
                title="Vital Signs",
                compose_include=[
                    {
                        "system": LOINC,
                        "concept": [
                            {"code": c, "display": d} for c, d in vital_unique
                        ],
                    }
                ],
                contains=vitals_contains,
                expansion_only=True,
            ),
        )
    )
    # Match FHIR core version so our expansion overrides the built-in LOINC-dependent VS
    resources[-1][1]["version"] = "4.0.1"

    hl7_aliases = [
        (
            "http://hl7.org/fhir/us/core/ValueSet/omb-race-category",
            known[
                "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.4.642.2.575"
            ],
        ),
        (
            "http://hl7.org/fhir/us/core/ValueSet/omb-ethnicity-category",
            known[
                "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.4.642.40.2.48.3"
            ],
        ),
        (
            "http://hl7.org/fhir/us/core/ValueSet/us-core-vital-signs",
            known[
                "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.88.12.80.62"
            ],
        ),
    ]
    for url, meta in hl7_aliases:
        vs = _vs(
            vid=meta["id"] + "-hl7",
            url=url,
            name=meta["name"] + "HL7",
            title=meta["title"] + " (HL7 URL alias)",
            compose_include=meta["compose_include"],
            contains=meta["contains"],
            expansion_only=bool(meta.get("expansion_only")),
        )
        resources.append((f"package/ValueSet-{vs['id']}.json", vs))

    for url in sorted(cts_urls | set(known)):
        if url in known:
            meta = known[url]
            vs = _vs(
                vid=meta["id"],
                url=url,
                name=meta["name"],
                title=meta["title"],
                compose_include=meta["compose_include"],
                contains=meta["contains"],
                expansion_only=bool(meta.get("expansion_only")),
            )
        else:
            oid = url.rsplit("/", 1)[-1]
            # Minimal stub: resolves the URL so Inferno stops emitting "ValueSet not found".
            # Do not include LOINC (external offline); empty expansion is intentional.
            vs = _vs(
                vid=f"cts-stub-{oid.replace('.', '-')}",
                url=url,
                name=f"CtsStub{oid.replace('.', '')}",
                title=f"Offline CTS stub for {oid}",
                compose_include=[],
                contains=[],
                experimental=True,
                expansion_only=True,
                description=(
                    "Offline stub so Inferno can resolve this CTS ValueSet URL "
                    "without live tx.fhir.org / VSAC."
                ),
            )
        resources.append((f"package/ValueSet-{vs['id']}.json", vs))

    index = {"index-version": 1, "files": []}
    for path, res in resources:
        index["files"].append(
            {
                "filename": path.split("/", 1)[1],
                "resourceType": res["resourceType"],
                "id": res["id"],
                "url": res["url"],
                "version": res.get("version"),
            }
        )

    manifest = {
        "name": PKG_ID,
        "version": VERSION,
        "description": (
            "Local offline terminology for US Core CTS ValueSets "
            "(race/ethnicity, vital signs, stubs)"
        ),
        "fhirVersions": ["4.0.1"],
        "type": "Conformance",
        "dependencies": {"hl7.fhir.r4.core": "4.0.1"},
        "author": "Interop Automation Platform",
    }

    pkg_path = OUT_DIR / f"{PKG_ID}-{VERSION}.tgz"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:

        def add(name: str, data: bytes) -> None:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        add("package/package.json", json.dumps(manifest, indent=2).encode())
        add("package/.index.json", json.dumps(index, indent=2).encode())
        for path, res in resources:
            add(path, json.dumps(res, indent=2).encode())

    pkg_path.write_bytes(buf.getvalue())
    print("Wrote", pkg_path, "bytes", pkg_path.stat().st_size, "resources", len(resources))

    # Keep Inferno boot mount in sync (terminology-only /home/igs)
    inferno_dir = OUT_DIR.parent / "fhir_packages_inferno"
    inferno_dir.mkdir(parents=True, exist_ok=True)
    for stale in inferno_dir.glob(f"{PKG_ID}-*.tgz"):
        stale.unlink()
    dest = inferno_dir / pkg_path.name
    dest.write_bytes(pkg_path.read_bytes())
    print("Synced", dest)


if __name__ == "__main__":
    main()
