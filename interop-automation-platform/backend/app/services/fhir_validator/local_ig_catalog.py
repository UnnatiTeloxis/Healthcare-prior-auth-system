"""IG catalog backed by pre-downloaded packages in FHIR_PACKAGES_PATH."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.fhir_validator.ig_catalog import POPULAR_IGS, _categorize_package
from app.services.fhir_validator.ig_package_fetcher import get_ig_package_fetcher

_POPULAR_BY_ID = {row["package_id"]: row for row in POPULAR_IGS}

# Prefer stable, already-cached versions over newest when both exist locally.
_PREFERRED_VERSIONS = {
    "hl7.fhir.us.core": "6.1.0",
}


@dataclass(frozen=True)
class LocalIgEntry:
    package_id: str
    name: str
    description: str
    fhir_version: str
    category: str
    cached_version: str
    cached: bool = True
    popular: bool = False

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "description": self.description,
            "fhir_version": self.fhir_version,
            "category": self.category,
            "cached_version": self.cached_version,
            "cached": self.cached,
            "popular": self.popular,
        }


class LocalIgCatalog:
    def list_available(self, *, popular_only: bool = False) -> list[LocalIgEntry]:
        """List cached packages. Default: every id#ver.tgz; popular_only for curated preload."""
        fetcher = get_ig_package_fetcher()
        if not fetcher.is_enabled():
            return []

        cached = fetcher.list_cached_packages()
        if not cached:
            return []

        if popular_only:
            package_ids = [row["package_id"] for row in POPULAR_IGS if row["package_id"] in cached]
        else:
            # Prefer popular order first, then remaining packages alphabetically.
            popular_ids = [row["package_id"] for row in POPULAR_IGS if row["package_id"] in cached]
            other_ids = sorted(pid for pid in cached if pid not in _POPULAR_BY_ID)
            package_ids = popular_ids + other_ids

        entries: list[LocalIgEntry] = []
        for package_id in package_ids:
            versions = cached.get(package_id) or []
            if not versions:
                continue
            preferred = _PREFERRED_VERSIONS.get(package_id)
            cached_version = (
                preferred if preferred and preferred in versions else versions[0]
            )
            popular = package_id in _POPULAR_BY_ID
            row = _POPULAR_BY_ID.get(package_id)
            entries.append(
                LocalIgEntry(
                    package_id=package_id,
                    name=(row["name"] if row else package_id),
                    description=(
                        row["description"]
                        if row
                        else f"FHIR implementation guide: {package_id}"
                    ),
                    fhir_version="R4",
                    category=(
                        (row.get("category") if row else None)
                        or _categorize_package(package_id)
                    ),
                    cached_version=cached_version,
                    popular=popular,
                )
            )
        return entries

    def list_popular_cached(self) -> list[LocalIgEntry]:
        return self.list_available(popular_only=True)

    def search(self, query: str = "", *, limit: int = 50) -> list[dict[str, str | bool]]:
        entries = self.list_available()
        q = query.strip().lower()
        limit = max(1, min(limit, 500))

        if not q:
            return [entry.to_dict() for entry in entries[:limit]]

        scored: list[tuple[int, LocalIgEntry]] = []
        for entry in entries:
            score = _score(entry, q)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: (-item[0], item[1].name.lower()))
        return [entry.to_dict() for _, entry in scored[:limit]]

    def get(self, package_id: str) -> LocalIgEntry | None:
        for entry in self.list_available():
            if entry.package_id == package_id:
                return entry
        return None

    def count(self) -> int:
        return len(self.list_available())


def _score(entry: LocalIgEntry, query: str) -> int:
    pid = entry.package_id.lower()
    name = entry.name.lower()
    desc = entry.description.lower()
    if pid == query or name == query:
        return 100
    if pid.startswith(query) or name.startswith(query):
        return 80
    if query in pid or query in name:
        return 60
    if query in desc:
        return 40
    return 0


local_ig_catalog = LocalIgCatalog()
