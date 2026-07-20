"""Persist loaded IG state across process restarts."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = "loaded_igs_manifest.json"


@dataclass
class LoadedIgRecord:
    package_id: str
    version: str | None = None
    fhir_version: str | None = None
    loaded_at: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class IgManifest:
    def __init__(self, packages_path: Path | None) -> None:
        self.packages_path = packages_path
        self._records: dict[str, LoadedIgRecord] = {}
        self._load()

    @property
    def manifest_path(self) -> Path | None:
        if not self.packages_path:
            return None
        return self.packages_path / MANIFEST_FILENAME

    def _load(self) -> None:
        path = self.manifest_path
        if not path or not path.is_file():
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            items = raw.get("loaded") if isinstance(raw, dict) else raw
            if not isinstance(items, list):
                return
            for item in items:
                if not isinstance(item, dict):
                    continue
                package_id = str(item.get("package_id") or "").strip()
                if not package_id:
                    continue
                self._records[package_id] = LoadedIgRecord(
                    package_id=package_id,
                    version=item.get("version"),
                    fhir_version=item.get("fhir_version"),
                    loaded_at=item.get("loaded_at"),
                    source=item.get("source"),
                )
        except Exception as exc:
            logger.warning("Failed to load IG manifest: %s", exc)

    def _save(self) -> None:
        path = self.manifest_path
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"loaded": [record.to_dict() for record in self._records.values()]}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_loaded(self) -> list[LoadedIgRecord]:
        return list(self._records.values())

    def get(self, package_id: str) -> LoadedIgRecord | None:
        return self._records.get(package_id)

    def is_loaded(self, package_id: str, version: str | None = None) -> bool:
        record = self._records.get(package_id)
        if not record:
            return False
        if version and record.version and record.version != version:
            return False
        return True

    def mark_loaded(
        self,
        package_id: str,
        *,
        version: str | None = None,
        fhir_version: str | None = None,
        source: str | None = None,
    ) -> LoadedIgRecord:
        record = LoadedIgRecord(
            package_id=package_id,
            version=version,
            fhir_version=fhir_version,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            source=source,
        )
        self._records[package_id] = record
        self._save()
        return record

    def remove(self, package_id: str) -> None:
        if package_id in self._records:
            del self._records[package_id]
            self._save()


_manifest: IgManifest | None = None


def get_ig_manifest() -> IgManifest:
    global _manifest
    if _manifest is None:
        from app.config import settings

        path = settings.FHIR_PACKAGES_PATH.strip()
        _manifest = IgManifest(Path(path) if path else None)
    return _manifest
