#!/usr/bin/env python3
"""Copy curated popular IG packages into fhir_packages/boot_igs for Inferno /home/igs."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.services.fhir_validator.fhir_loader import get_fhir_package_loader  # noqa: E402
from app.services.fhir_validator.ig_manager import _should_skip_preload_package  # noqa: E402
from app.services.fhir_validator.local_ig_catalog import local_ig_catalog  # noqa: E402

_BOOT_VERSION_OVERRIDES = {
    "hl7.fhir.us.core": "6.1.0",
}
# Fast boot set — Inferno loads these from /home/igs at container start.
_BOOT_PRIORITY = (
    "hl7.fhir.us.core",
    "hl7.fhir.us.davinci-crd",
    "hl7.fhir.us.davinci-dtr",
    "hl7.fhir.us.davinci-pas",
    "hl7.fhir.uv.ips",
    "hl7.fhir.uv.ipa",
    "hl7.fhir.us.davinci-hrex",
    "hl7.fhir.us.qicore",
)


def main() -> int:
    packages_dir = Path(settings.FHIR_PACKAGES_PATH)
    boot_dir = packages_dir / "boot_igs"
    boot_dir.mkdir(parents=True, exist_ok=True)

    # Clear old copies
    for old in boot_dir.glob("*.tgz"):
        old.unlink()

    loader = get_fhir_package_loader()
    copied = 0
    seen: set[str] = set()

    def _copy(package_id: str, version: str) -> None:
        nonlocal copied
        key = f"{package_id}#{version}"
        if key in seen:
            return
        path = loader.resolve_package_path(package_id, version)
        if not path or not path.is_file():
            print(f"skip missing {key}")
            return
        dest = boot_dir / path.name
        shutil.copy2(path, dest)
        seen.add(key)
        copied += 1
        print(f"copied {dest.name}")

    for package_id in _BOOT_PRIORITY:
        version = _BOOT_VERSION_OVERRIDES.get(package_id)
        if not version:
            entry = local_ig_catalog.get(package_id)
            version = entry.cached_version if entry else None
        if version and not _should_skip_preload_package(package_id):
            _copy(package_id, version)

    # Friendly aliases used by docs/tools
    for alias in ("us-core.tgz", "davinci-crd.tgz", "davinci-dtr.tgz", "davinci-pas.tgz"):
        src = packages_dir / alias
        if src.is_file():
            shutil.copy2(src, boot_dir / alias)
            print(f"copied alias {alias}")

    print(f"Done: {copied} package(s) in {boot_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
