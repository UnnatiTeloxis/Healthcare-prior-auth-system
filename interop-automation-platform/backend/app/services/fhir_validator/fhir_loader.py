import functools
import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FHIRPackageRef:
    package_id: str
    version: str | None = None

    @property
    def ig_key(self) -> str:
        return f"{self.package_id}#{self.version}" if self.version else self.package_id


class FHIRPackageLoader:
    """
    Loads FHIR package .tgz files from local disk so the validator can run without
    outbound network access at runtime.

    This loader does not attempt to parse packages; it simply returns the raw bytes
    so they can be uploaded to the Inferno validator wrapper via /igs (POST).
    """

    def __init__(self, packages_path: str | Path | None = None) -> None:
        raw = str(packages_path or os.getenv("FHIR_PACKAGES_PATH", "")).strip()
        self.packages_dir = Path(raw) if raw else None
        extra = str(os.getenv("FHIR_PACKAGES_EXTRA_PATH", "")).strip()
        if not extra and self.packages_dir:
            # Sibling folder for uploadable IGs not auto-mounted into Inferno /home/igs
            candidate = self.packages_dir.parent / "fhir_packages_extra"
            if candidate.is_dir():
                extra = str(candidate)
            else:
                # Docker: /app/fhir_packages → /app/fhir_packages_extra
                candidate = Path("/app/fhir_packages_extra")
                if candidate.is_dir():
                    extra = str(candidate)
        self.extra_packages_dir = Path(extra) if extra else None
        uploads = str(os.getenv("FHIR_UPLOADS_PATH", "")).strip()
        if not uploads and self.packages_dir:
            candidate = self.packages_dir.parent / "fhir_packages_uploads"
            uploads = str(candidate)
        self.uploads_dir = Path(uploads) if uploads else None
        self._bytes_cache: dict[str, bytes] = {}

    def is_enabled(self) -> bool:
        return bool(self.packages_dir and self.packages_dir.is_dir())

    def _resolve_version(self, package_id: str, version: str | None) -> str | None:
        """Prefer explicit version, else catalog pin (so hl7.fhir.uv.ipa → 1.1.0 .tgz)."""
        if version:
            return version
        try:
            from app.services.fhir_validator.ig_constants import IG_PREFERRED_VERSIONS

            return IG_PREFERRED_VERSIONS.get(package_id)
        except Exception:
            return None

    def _candidate_paths(self, ref: FHIRPackageRef) -> list[Path]:
        dirs = [d for d in (self.packages_dir, self.extra_packages_dir, self.uploads_dir) if d]
        if not dirs:
            return []
        pid = ref.package_id
        ver = self._resolve_version(pid, ref.version)

        # Common naming conventions (support both dash and hash variants)
        candidates: list[str] = []
        if ver:
            candidates.extend(
                [
                    f"{pid}#{ver}.tgz",
                    f"{pid}-{ver}.tgz",
                    f"{pid}_{ver}.tgz",
                ]
            )
        candidates.extend([f"{pid}.tgz"])

        # Also support friendly aliases used in docs (e.g., us-core.tgz)
        if pid == "hl7.fhir.us.core":
            candidates.append("us-core.tgz")
        if pid == "hl7.fhir.us.davinci-hrex":
            candidates.append("davinci-hrex.tgz")
        if pid == "hl7.fhir.us.davinci-crd":
            candidates.append("davinci-crd.tgz")
        if pid == "hl7.fhir.us.davinci-dtr":
            candidates.append("davinci-dtr.tgz")
        if pid == "hl7.fhir.us.davinci-pas":
            candidates.append("davinci-pas.tgz")
        if pid == "hl7.fhir.us.mcode":
            candidates.append("mcode.tgz")
        if pid == "hl7.fhir.us.carin-bb":
            candidates.append("carin-bb.tgz")
        if pid == "hl7.fhir.us.qicore":
            candidates.append("qicore.tgz")
        if pid.startswith("hl7.fhir.us.davinci-"):
            short = pid.rsplit(".", 1)[-1]
            candidates.append(f"davinci-{short}.tgz")

        paths: list[Path] = []
        for base in dirs:
            paths.extend(base / name for name in candidates)
            # Fallback: versioned archives when caller omitted version
            # (e.g. hl7.fhir.uv.ipa-1.1.0.tgz).
            if not ver:
                paths.extend(sorted(base.glob(f"{pid}-*.tgz")))
                paths.extend(sorted(base.glob(f"{pid}#*.tgz")))
        return paths

    def register_package_bytes(
        self, package_id: str, version: str | None, data: bytes
    ) -> None:
        """Keep uploaded package bytes in memory so Inferno load does not wait on disk."""
        ref = FHIRPackageRef(package_id=package_id, version=version)
        self._bytes_cache[ref.ig_key] = data

    def load_package_bytes(self, package_id: str, version: str | None = None) -> bytes | None:
        ref = FHIRPackageRef(package_id=package_id, version=version)
        cache_key = ref.ig_key
        if cache_key in self._bytes_cache:
            return self._bytes_cache[cache_key]

        if not self.is_enabled():
            return None

        for path in self._candidate_paths(ref):
            try:
                if path.is_file():
                    data = path.read_bytes()
                    self._bytes_cache[cache_key] = data
                    logger.info("Loaded local FHIR package %s from %s", cache_key, path)
                    return data
            except Exception as exc:
                logger.warning("Failed reading local package %s: %s", path, exc)

        return None

    def iter_local_package_paths(self) -> list[Path]:
        if not self.is_enabled() or not self.packages_dir:
            return []
        return sorted(self.packages_dir.glob("*.tgz"))

    def package_ref_for_path(self, path: Path) -> FHIRPackageRef | None:
        name = path.name.lower()
        alias_map = {
            "us-core.tgz": ("hl7.fhir.us.core", None),
            "davinci-hrex.tgz": ("hl7.fhir.us.davinci-hrex", None),
            "davinci-crd.tgz": ("hl7.fhir.us.davinci-crd", None),
            "davinci-dtr.tgz": ("hl7.fhir.us.davinci-dtr", None),
            "davinci-pas.tgz": ("hl7.fhir.us.davinci-pas", None),
        }
        if name in alias_map:
            package_id, version = alias_map[name]
            return FHIRPackageRef(package_id=package_id, version=version)

        stem = path.stem
        if "#" in stem:
            package_id, version = stem.split("#", 1)
            return FHIRPackageRef(package_id=package_id, version=version or None)
        return FHIRPackageRef(package_id=stem, version=None)


@functools.lru_cache(maxsize=1)
def get_fhir_package_loader() -> FHIRPackageLoader:
    return FHIRPackageLoader()

