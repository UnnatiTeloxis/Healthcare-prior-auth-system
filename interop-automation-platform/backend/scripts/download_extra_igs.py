"""Download additional FHIR IG packages into backend/fhir_packages/."""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "backend" / "fhir_packages_extra"

# Realistic US healthcare IGs commonly used by EHR / payer / oncology systems.
PACKAGES = [
    ("hl7.fhir.us.mcode", "4.0.0"),
    ("hl7.fhir.us.carin-bb", "2.1.0"),
    ("hl7.fhir.us.qicore", "6.0.0"),
]


def download(package_id: str, version: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{package_id}-{version}.tgz"
    if dest.is_file() and dest.stat().st_size > 10_000:
        print(f"EXISTS {dest.name} ({dest.stat().st_size} bytes)")
        return dest

    urls = [
        f"https://packages.fhir.org/{package_id}/{version}",
        f"https://packages2.fhir.org/packages/{package_id}/{version}",
    ]
    last_err: Exception | None = None
    for url in urls:
        try:
            print(f"GET {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "interop-automation-platform/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1000:
                raise RuntimeError(f"Too small response ({len(data)} bytes)")
            dest.write_bytes(data)
            print(f"SAVED {dest.name} ({len(data)} bytes)")
            return dest
        except Exception as exc:
            last_err = exc
            print(f"  failed: {exc}")
    raise RuntimeError(f"Could not download {package_id}#{version}: {last_err}")


def main() -> int:
    ok = 0
    for pid, ver in PACKAGES:
        try:
            download(pid, ver)
            ok += 1
        except Exception as exc:
            print(f"ERROR {pid}#{ver}: {exc}", file=sys.stderr)
    print(f"Done: {ok}/{len(PACKAGES)}")
    return 0 if ok == len(PACKAGES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
