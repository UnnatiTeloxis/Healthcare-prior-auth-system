"""
Sync curated IG packages from a gaurav-validation checkout into local fhir_packages/.

Preferred versions match the remote POPULAR_IGS / boot_igs set used on that branch.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "fhir_packages"
EXTRA = ROOT / "fhir_packages_extra"
SRC = Path(r"C:\Users\Admin\AppData\Local\Temp\gaurav-validation-inspect\interop-automation-platform\backend\fhir_packages")

# package_id -> preferred version filename stem on remote (name#ver.tgz or alias)
PREFERRED: dict[str, str] = {
    "hl7.fhir.us.core": "hl7.fhir.us.core#9.0.0.tgz",
    "hl7.fhir.us.ccda": "hl7.fhir.us.ccda#2.0.0.tgz",
    "hl7.fhir.us.qicore": "hl7.fhir.us.qicore#7.0.2.tgz",
    "hl7.fhir.us.carin-bb": "hl7.fhir.us.carin-bb#2.1.0.tgz",
    "hl7.fhir.us.bulkdata": "hl7.fhir.us.bulkdata#0.1.0.tgz",
    "hl7.fhir.us.odh": "hl7.fhir.us.odh#1.3.0.tgz",
    "hl7.fhir.us.military-service": "hl7.fhir.us.military-service#1.0.0.tgz",
    "hl7.fhir.us.vrdr": "hl7.fhir.us.vrdr#3.0.0.tgz",
    "hl7.fhir.us.davinci-crd": "hl7.fhir.us.davinci-crd#2.2.1.tgz",
    "hl7.fhir.us.davinci-dtr": "hl7.fhir.us.davinci-dtr#2.2.0.tgz",
    "hl7.fhir.us.davinci-pas": "hl7.fhir.us.davinci-pas#2.2.1.tgz",
    "hl7.fhir.us.davinci-pdex": "hl7.fhir.us.davinci-pdex#2.1.0.tgz",
    "hl7.fhir.us.davinci-cdex": "hl7.fhir.us.davinci-cdex#2.1.0.tgz",
    "hl7.fhir.us.davinci-hrex": "hl7.fhir.us.davinci-hrex#1.2.0.tgz",
    "hl7.fhir.us.davinci-pcde": "hl7.fhir.us.davinci-pcde#1.0.0.tgz",
    "hl7.fhir.us.davinci-alerts": "hl7.fhir.us.davinci-alerts#1.1.0.tgz",
    "hl7.fhir.us.davinci-drug-formulary": "hl7.fhir.us.Davinci-drug-formulary#2.1.0.tgz",
    "hl7.fhir.us.davinci-deqm": "hl7.fhir.us.davinci-deqm#5.0.0.tgz",
    "hl7.fhir.us.davinci-ra": "hl7.fhir.us.davinci-ra#2.1.0.tgz",
    "hl7.fhir.us.mcode": "hl7.fhir.us.mcode#4.0.0.tgz",
    "hl7.fhir.us.ecr": "hl7.fhir.us.ecr#2.1.2.tgz",
    "hl7.fhir.us.pacio-adi": "hl7.fhir.us.pacio-adi#1.0.0.tgz",
    "hl7.fhir.us.pacio-cs": "hl7.fhir.us.pacio-cs#1.0.0.tgz",
    "hl7.fhir.us.pacio-fs": "hl7.fhir.us.pacio-fs#1.0.0.tgz",
    "hl7.fhir.uv.ipa": "hl7.fhir.uv.ipa#1.1.0.tgz",
    "hl7.fhir.uv.ips": "hl7.fhir.uv.ips#2.0.1.tgz",
    "hl7.fhir.uv.smart-app-launch": "hl7.fhir.uv.smart-app-launch#2.2.0.tgz",
    "hl7.fhir.uv.extensions.r4": "hl7.fhir.uv.extensions.r4#5.3.0.tgz",
    "hl7.fhir.uv.sdc": "hl7.fhir.uv.sdc#4.0.0.tgz",
}

# Friendly aliases kept for existing local naming
ALIASES: dict[str, str] = {
    "hl7.fhir.us.core": "us-core.tgz",
    "hl7.fhir.us.davinci-crd": "davinci-crd.tgz",
    "hl7.fhir.us.davinci-dtr": "davinci-dtr.tgz",
    "hl7.fhir.us.davinci-pas": "davinci-pas.tgz",
    "hl7.fhir.us.davinci-hrex": "davinci-hrex.tgz",
}


def _dest_name(package_id: str, src_name: str) -> str:
    # Normalize remote name#ver.tgz → package-ver.tgz for consistency
    if "#" in src_name:
        base = src_name[:-4] if src_name.endswith(".tgz") else src_name
        pid, ver = base.split("#", 1)
        return f"{pid}-{ver}.tgz"
    return src_name


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source not found: {SRC}")
    DEST.mkdir(parents=True, exist_ok=True)
    EXTRA.mkdir(parents=True, exist_ok=True)

    copied = 0
    missing: list[str] = []
    for package_id, src_name in PREFERRED.items():
        src = SRC / src_name
        if not src.is_file():
            missing.append(src_name)
            continue
        dest_file = DEST / _dest_name(package_id, src_name)
        if not dest_file.exists() or dest_file.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest_file)
            copied += 1
            print("copied", dest_file.name)
        else:
            print("exists", dest_file.name)

        alias = ALIASES.get(package_id)
        if alias:
            alias_path = DEST / alias
            if not alias_path.exists() or alias_path.stat().st_size != src.stat().st_size:
                shutil.copy2(src, alias_path)
                print("alias", alias)

    # Keep large support packs discoverable under extras as well
    for pid in ("hl7.fhir.uv.sdc", "hl7.fhir.uv.extensions.r4", "hl7.fhir.us.mcode", "hl7.fhir.us.qicore", "hl7.fhir.us.carin-bb"):
        src_name = PREFERRED[pid]
        src = SRC / src_name
        if not src.is_file():
            continue
        dest = EXTRA / _dest_name(pid, src_name)
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
            print("extra", dest.name)

    print(f"\nDone. newly_copied={copied} missing={len(missing)}")
    for m in missing:
        print(" MISSING", m)


if __name__ == "__main__":
    main()
