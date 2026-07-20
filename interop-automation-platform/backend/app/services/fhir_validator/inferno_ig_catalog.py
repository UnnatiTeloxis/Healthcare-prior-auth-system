"""
Catalog of Implementation Guides discoverable for the Inferno-backed validator UI.

Prefer POPULAR_IGS / packages.fhir.org (same family of packages Inferno loads via
PUT /igs/{package_id}). Used by GET /api/v1/igs/available?source=inferno|all.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.services.fhir_validator.ig_catalog import POPULAR_IGS, ig_catalog_service

logger = logging.getLogger(__name__)

_CACHE_TTL_S = 3600.0
_CATALOG_SOURCE = "https://packages.fhir.org/catalog"


class InfernoIgCatalog:
    """Async catalog used by the IG dropdown (Inferno / remote package list)."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._loaded_at: float = 0.0
        self.source_url = _CATALOG_SOURCE

    def _is_cache_valid(self) -> bool:
        return bool(self._entries) and (time.monotonic() - self._loaded_at) < _CACHE_TTL_S

    @staticmethod
    def _from_popular() -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for item in POPULAR_IGS:
            package_id = item["package_id"]
            rows.append(
                {
                    "package_id": package_id,
                    "name": package_id,
                    "version": "",
                    "title": item.get("name") or package_id,
                    "description": item.get("description") or "",
                    "fhir_version": "4.0.1",
                    "fhir_versions": ["4.0.1"],
                    "canonical": "",
                    "package_type": "ImplementationGuide",
                    "structure_definition_count": 1,
                    "is_profile_ig": True,
                    "source": "inferno",
                    "cached": False,
                    "popular": True,
                    "category": item.get("category") or "",
                }
            )
        return rows

    async def list_entries(self, *, force: bool = False) -> list[dict[str, Any]]:
        if not force and self._is_cache_valid():
            return list(self._entries)

        rows = self._from_popular()
        try:
            await ig_catalog_service.ensure_loaded()
            registry = await ig_catalog_service.search("", limit=500)
            known = {row["package_id"] for row in rows}
            for entry in registry:
                package_id = entry.get("package_id") or ""
                if not package_id or package_id in known:
                    continue
                known.add(package_id)
                rows.append(
                    {
                        "package_id": package_id,
                        "name": package_id,
                        "version": "",
                        "title": entry.get("name") or package_id,
                        "description": entry.get("description") or "",
                        "fhir_version": entry.get("fhir_version") or "4.0.1",
                        "fhir_versions": [entry.get("fhir_version") or "4.0.1"],
                        "canonical": "",
                        "package_type": "ImplementationGuide",
                        "structure_definition_count": 1,
                        "is_profile_ig": True,
                        "source": "inferno",
                        "cached": False,
                        "popular": False,
                        "category": entry.get("category") or "",
                    }
                )
        except Exception as exc:
            logger.warning("Inferno IG catalog refresh fell back to popular list: %s", exc)

        self._entries = rows
        self._loaded_at = time.monotonic()
        logger.info("Inferno IG catalog ready (%d entries)", len(self._entries))
        return list(self._entries)


inferno_ig_catalog = InfernoIgCatalog()
