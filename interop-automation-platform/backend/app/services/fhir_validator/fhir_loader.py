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
        raw = str(packages_path or os.getenv("FHIR_PACKAGES_PATH", "./fhir_packages")).strip()
        self.packages_dir = Path(raw) if raw else None
        self._bytes_cache: dict[str, bytes] = {}

    def is_enabled(self) -> bool:
        return bool(self.packages_dir and self.packages_dir.is_dir())

    def _candidate_paths(self, ref: FHIRPackageRef) -> list[Path]:
        if not self.packages_dir:
            return []
        base = self.packages_dir
        pid = ref.package_id
        ver = ref.version

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
        if pid == "hl7.fhir.us.davinci-crd":
            candidates.append("davinci-crd.tgz")
        if pid == "hl7.fhir.us.davinci-dtr":
            candidates.append("davinci-dtr.tgz")
        if pid == "hl7.fhir.us.davinci-pas":
            candidates.append("davinci-pas.tgz")
        if pid.startswith("hl7.fhir.us.davinci-"):
            short = pid.rsplit(".", 1)[-1]
            candidates.append(f"davinci-{short}.tgz")

        return [base / name for name in candidates]

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

    def resolve_package_path(self, package_id: str, version: str | None = None) -> Path | None:
        ref = FHIRPackageRef(package_id=package_id, version=version)
        for path in self._candidate_paths(ref):
            if path.is_file():
                return path
        return None

    def package_has_index(self, package_id: str, version: str | None = None) -> bool:
        """Inferno POST /igs requires package/.index.json inside the tarball."""
        path = self.resolve_package_path(package_id, version)
        if not path:
            return False
        try:
            import tarfile

            with tarfile.open(path, "r:gz") as tar:
                for member in tar.getmembers():
                    name = member.name.replace("\\", "/")
                    if name.endswith("package/.index.json") or name.endswith("/.index.json"):
                        return True
                    if os.path.basename(name) == ".index.json":
                        return True
        except Exception as exc:
            logger.warning("Failed inspecting package index in %s: %s", path, exc)
        return False

    def iter_local_package_paths(self) -> list[Path]:
        if not self.is_enabled() or not self.packages_dir:
            return []
        return sorted(self.packages_dir.glob("*.tgz"))

    def package_ref_for_path(self, path: Path) -> FHIRPackageRef | None:
        name = path.name.lower()
        alias_map = {
            "us-core.tgz": ("hl7.fhir.us.core", None),
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
            version = version or None
            # Fix misnamed files like hl7.fhir.us.core.3.1.1#3.1.1.tgz
            if version and package_id.endswith(f".{version}"):
                package_id = package_id[: -(len(version) + 1)]
            return FHIRPackageRef(package_id=package_id, version=version)
        return FHIRPackageRef(package_id=stem, version=None)


@functools.lru_cache(maxsize=1)
def get_fhir_package_loader() -> FHIRPackageLoader:
    return FHIRPackageLoader()

