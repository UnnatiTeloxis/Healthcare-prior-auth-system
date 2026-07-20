"""FHIR Implementation Guide catalog: fetch, cache, search, and categorize packages."""

from __future__ import annotations

import asyncio
import logging
import re
import string
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

REGISTRY_BASE = "https://packages.fhir.org/catalog"
CACHE_TTL_SECONDS = 24 * 60 * 60
R4_VERSIONS = frozenset({"R4", "4.0.1", "4.0.0", "4.3.0"})
_REGISTRY_RETRY_MAX = 8
_REGISTRY_RETRY_BASE_DELAY = 3.0
_DEFAULT_REQUEST_DELAY = 1.5

# Packages that are FHIR core/tooling, not implementation guides.
_EXCLUDED_SUFFIXES = (
    ".core",
    ".corexml",
    ".examples",
    ".expansions",
    ".elements",
    ".template",
    "terminology",
    "pubpack",
)

_EXCLUDED_EXACT = frozenset({
    "hl7.fhir.r4.core",
    "hl7.fhir.r4.corexml",
    "hl7.fhir.r4.examples",
    "hl7.fhir.r4.expansions",
    "hl7.fhir.r4.elements",
    "hl7.terminology.r4",
    "hl7.terminology.r5",
    "hl7.fhir.pubpack",
    "us.nlm.vsac",
})

_CATALOG_PREFIXES = ("hl7.fhir.us",)
_US_DISCOVERY_PREFIX = "hl7.fhir.us."
# packages.fhir.org truncates large prefix searches (~25 rows); subdivide when hit.
_REGISTRY_TRUNCATION_THRESHOLD = 20

# International base IGs that US Realm profiles depend on.
_ALLOWED_INTL_DEPS = frozenset({
    "hl7.fhir.uv.smart-app-launch",
    "hl7.fhir.uv.sdc",
    "hl7.fhir.uv.extensions",
    "hl7.fhir.uv.ips",
    "hl7.fhir.uv.ipa",
})

POPULAR_IGS: list[dict[str, str]] = [
    {"package_id": "hl7.fhir.us.core", "name": "US Core", "description": "US Realm base profiles for common clinical data", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.ccda", "name": "C-CDA on FHIR", "description": "C-CDA documents mapped to FHIR resources", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.qicore", "name": "QI-Core", "description": "Quality improvement and clinical decision support profiles", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.carin-bb", "name": "CARIN Blue Button", "description": "Consumer-directed payer data exchange", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.bulkdata", "name": "Bulk Data Access", "description": "FHIR Bulk Data Export (Flat FHIR)", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.odh", "name": "Occupational Data for Health (ODH)", "description": "Occupational health data elements", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.military-service", "name": "Military Service", "description": "Military service history for patients", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.vrdr", "name": "Vital Records Death Reporting", "description": "Mortality data reporting to public health", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.davinci-crd", "name": "Da Vinci CRD", "description": "Coverage Requirements Discovery", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-dtr", "name": "Da Vinci DTR", "description": "Documentation Templates and Rules", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-pas", "name": "Da Vinci PAS", "description": "Prior Authorization Support", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-pdex", "name": "Da Vinci PDex", "description": "Payer Data Exchange", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-cdex", "name": "Da Vinci CDex", "description": "Clinical Data Exchange", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-hrex", "name": "Da Vinci HRex", "description": "Health Record Exchange framework", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-pcde", "name": "Da Vinci PCDE", "description": "Payer Coverage Decision Exchange", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-alerts", "name": "Da Vinci Alerts", "description": "Alerts for clinical decision support", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.Davinci-drug-formulary", "name": "Da Vinci Drug Formulary", "description": "Drug formulary and pricing", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-deqm", "name": "Da Vinci DEQM", "description": "Data Exchange for Quality Measures", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.davinci-ra", "name": "Da Vinci Risk Adjustment", "description": "Risk adjustment data exchange", "category": "Da Vinci"},
    {"package_id": "hl7.fhir.us.mcode", "name": "mCODE", "description": "Minimal Common Oncology Data Elements", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.ecr", "name": "eCR", "description": "Electronic Case Reporting to public health", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.pacio-adi", "name": "PACIO ADI", "description": "Advance Directives and Interventions", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.pacio-cs", "name": "PACIO Cognitive Status", "description": "Cognitive status assessment profiles", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.us.pacio-fs", "name": "PACIO Functional Status", "description": "Functional status assessment profiles", "category": "HL7 US Realm"},
    {"package_id": "hl7.fhir.uv.ipa", "name": "International Patient Access", "description": "Cross-border patient access to health data", "category": "Base Dependencies"},
    {"package_id": "hl7.fhir.uv.ips", "name": "International Patient Summary", "description": "Cross-border patient summary document", "category": "Base Dependencies"},
    {"package_id": "hl7.fhir.uv.smart-app-launch", "name": "SMART App Launch", "description": "SMART on FHIR authorization and launch", "category": "Base Dependencies"},
    {"package_id": "hl7.fhir.uv.extensions", "name": "FHIR Extensions", "description": "Common FHIR extension definitions", "category": "Base Dependencies"},
    {"package_id": "hl7.fhir.uv.sdc", "name": "Structured Data Capture (SDC)", "description": "Questionnaires and form-driven data capture", "category": "Base Dependencies"},
]


@dataclass(frozen=True)
class IgVersionEntry:
    version: str
    fhir_version: str
    is_latest: bool
    tarball: str
    shasum: str

    def to_dict(self, *, cached: bool = False) -> dict[str, str | bool]:
        return {
            "version": self.version,
            "fhir_version": self.fhir_version,
            "is_latest": self.is_latest,
            "tarball": self.tarball,
            "shasum": self.shasum,
            "cached": cached,
        }


@dataclass(frozen=True)
class IgCatalogEntry:
    package_id: str
    name: str
    description: str
    fhir_version: str
    category: str

    def to_dict(self) -> dict[str, str]:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "description": self.description,
            "fhir_version": self.fhir_version,
            "category": self.category,
        }


def _normalize_fhir_version(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip()


def _is_r4_version(value: str | None) -> bool:
    normalized = _normalize_fhir_version(value)
    if not normalized:
        return False
    if normalized in R4_VERSIONS:
        return True
    return normalized.startswith("4.")


def _is_excluded_package(package_id: str) -> bool:
    lowered = package_id.lower()
    if lowered in _EXCLUDED_EXACT:
        return True
    return any(lowered.endswith(suffix) for suffix in _EXCLUDED_SUFFIXES)


def _is_allowed_package(package_id: str) -> bool:
    lowered = package_id.lower()
    return lowered.startswith("hl7.fhir.us.") or lowered in _ALLOWED_INTL_DEPS


def _humanize_package_id(package_id: str) -> str:
    slug = package_id.split(".")[-1]
    slug = re.sub(r"[-_]+", " ", slug)
    return slug.replace("davinci", "Da Vinci").title()


def _categorize_package(package_id: str) -> str:
    lowered = package_id.lower()
    if lowered in _ALLOWED_INTL_DEPS:
        return "Base Dependencies"
    if "davinci" in lowered:
        return "Da Vinci"
    if lowered.startswith("hl7.fhir.us."):
        return "HL7 US Realm"
    return "HL7 US Realm"


def _entry_from_registry_row(row: dict[str, Any], *, require_r4: bool = True) -> IgCatalogEntry | None:
    package_id = str(row.get("Name") or row.get("name") or "").strip()
    if not package_id or _is_excluded_package(package_id) or not _is_allowed_package(package_id):
        return None

    fhir_version = _normalize_fhir_version(row.get("FhirVersion") or row.get("fhirVersion"))
    if require_r4 and fhir_version and not _is_r4_version(fhir_version):
        return None

    description = str(row.get("Description") or row.get("description") or "").strip()
    if len(description) > 240:
        description = description[:237] + "..."

    popular = next((p for p in POPULAR_IGS if p["package_id"] == package_id), None)
    name = popular["name"] if popular else _humanize_package_id(package_id)
    category = popular["category"] if popular else _categorize_package(package_id)

    return IgCatalogEntry(
        package_id=package_id,
        name=name,
        description=description or f"FHIR implementation guide: {package_id}",
        fhir_version=fhir_version or "R4",
        category=category,
    )


class IgCatalogService:
    def __init__(self) -> None:
        self._entries: dict[str, IgCatalogEntry] = {}
        self._loaded_at: float = 0.0
        self._lock = asyncio.Lock()
        self._client: httpx.AsyncClient | None = None
        self._request_delay = _DEFAULT_REQUEST_DELAY
        self._last_request_at: float = 0.0

    async def _pace_registry_request(self) -> None:
        if self._request_delay <= 0:
            return
        if self._last_request_at:
            elapsed = time.monotonic() - self._last_request_at
            remaining = self._request_delay - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)

    async def _fetch_registry_list(self, query: str) -> list[dict[str, Any]]:
        client = await self._get_client()
        response: httpx.Response | None = None

        for attempt in range(1, _REGISTRY_RETRY_MAX + 1):
            await self._pace_registry_request()
            try:
                response = await client.get(REGISTRY_BASE, params={"name": query})
                self._last_request_at = time.monotonic()
            except Exception as exc:
                logger.warning("Failed to fetch IG catalog query %s: %s", query, exc)
                return []

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "").strip()
                delay = float(retry_after) if retry_after.isdigit() else _REGISTRY_RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited (429) for catalog query %r; waiting %.0fs (attempt %d/%d)",
                    query,
                    delay,
                    attempt,
                    _REGISTRY_RETRY_MAX,
                )
                if attempt >= _REGISTRY_RETRY_MAX:
                    return []
                await asyncio.sleep(delay)
                continue

            if response.status_code in {502, 503, 504} and attempt < _REGISTRY_RETRY_MAX:
                delay = _REGISTRY_RETRY_BASE_DELAY * attempt
                logger.warning(
                    "Registry %s for catalog query %r; retry in %.0fs",
                    response.status_code,
                    query,
                    delay,
                )
                await asyncio.sleep(delay)
                continue

            try:
                response.raise_for_status()
                data = response.json()
                return data if isinstance(data, list) else []
            except Exception as exc:
                logger.warning("Failed to fetch IG catalog query %s: %s", query, exc)
                return []

        return []

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0))
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _is_cache_valid(self) -> bool:
        return bool(self._entries) and (time.monotonic() - self._loaded_at) < CACHE_TTL_SECONDS

    async def _fetch_prefix(self, prefix: str) -> list[dict[str, Any]]:
        return await self._fetch_registry_list(prefix)

    async def _fetch_query(self, query: str) -> list[dict[str, Any]]:
        return await self._fetch_registry_list(query)

    async def _discover_us_registry_rows(
        self,
        *,
        pause_seconds: float = 2.0,
    ) -> list[dict[str, Any]]:
        """Enumerate all hl7.fhir.us.* packages; registry search truncates broad prefixes."""
        rows_by_id: dict[str, dict[str, Any]] = {}

        def _merge(rows: list[dict[str, Any]]) -> None:
            for row in rows:
                package_id = str(row.get("Name") or row.get("name") or "").strip()
                if package_id:
                    rows_by_id[package_id] = row

        for letter in string.ascii_lowercase:
            prefix = f"{_US_DISCOVERY_PREFIX}{letter}"
            batch = await self._fetch_query(prefix)
            _merge(batch)
            if len(batch) >= _REGISTRY_TRUNCATION_THRESHOLD:
                for letter2 in string.ascii_lowercase:
                    sub_batch = await self._fetch_query(f"{prefix}{letter2}")
                    _merge(sub_batch)
                    if pause_seconds > 0:
                        await asyncio.sleep(pause_seconds)
            if pause_seconds > 0:
                await asyncio.sleep(pause_seconds)

        logger.info("Discovered %d US registry package(s) via subdivided catalog search", len(rows_by_id))
        return list(rows_by_id.values())

    async def refresh(self, *, force: bool = False) -> int:
        async with self._lock:
            if not force and self._is_cache_valid():
                return len(self._entries)

            merged: dict[str, IgCatalogEntry] = {}

            for popular in POPULAR_IGS:
                merged[popular["package_id"]] = IgCatalogEntry(
                    package_id=popular["package_id"],
                    name=popular["name"],
                    description=popular["description"],
                    fhir_version="R4",
                    category=popular["category"],
                )

            for row in await self._discover_us_registry_rows():
                entry = _entry_from_registry_row(row, require_r4=False)
                if entry:
                    merged[entry.package_id] = entry

            for package_id in _ALLOWED_INTL_DEPS:
                rows = await self._fetch_query(package_id)
                for row in rows:
                    entry = _entry_from_registry_row(row)
                    if entry:
                        merged[entry.package_id] = entry

            self._entries = merged
            self._loaded_at = time.monotonic()
            logger.info("IG catalog refreshed: %d R4 packages cached", len(self._entries))
            return len(self._entries)

    async def ensure_loaded(self) -> None:
        if not self._is_cache_valid():
            await self.refresh()

    async def warm_up(self) -> None:
        try:
            await self.refresh()
        except Exception as exc:
            logger.warning("IG catalog warm-up failed (will retry on search): %s", exc)

    def _score_match(self, entry: IgCatalogEntry, query: str) -> int:
        q = query.lower()
        pid = entry.package_id.lower()
        name = entry.name.lower()
        desc = entry.description.lower()

        if pid == q or name == q:
            return 100
        if pid.startswith(q) or name.startswith(q):
            return 80
        if q in pid or q in name:
            return 60
        if q in desc:
            return 40
        return 0

    async def search(
        self,
        query: str = "",
        *,
        fhir_version: str = "R4",
        limit: int = 50,
    ) -> list[dict[str, str]]:
        await self.ensure_loaded()

        q = query.strip().lower()
        limit = max(1, min(limit, 200))

        if not q:
            return [entry.to_dict() for entry in self._popular_entries(limit)]

        local_matches: list[tuple[int, IgCatalogEntry]] = []
        for entry in self._entries.values():
            score = self._score_match(entry, q)
            if score > 0:
                local_matches.append((score, entry))

        if len(local_matches) < limit:
            live_rows = await self._fetch_query(query.strip())
            for row in live_rows:
                entry = _entry_from_registry_row(row)
                if entry and entry.package_id not in self._entries:
                    self._entries[entry.package_id] = entry
                if entry:
                    score = self._score_match(entry, q)
                    if score > 0:
                        local_matches.append((score, entry))

        seen: set[str] = set()
        results: list[dict[str, str]] = []
        for _, entry in sorted(local_matches, key=lambda item: (-item[0], item[1].name.lower())):
            if entry.package_id in seen:
                continue
            seen.add(entry.package_id)
            if fhir_version.upper() == "R4" and not _is_r4_version(entry.fhir_version):
                continue
            results.append(entry.to_dict())
            if len(results) >= limit:
                break

        return results

    def _popular_entries(self, limit: int) -> list[IgCatalogEntry]:
        ordered: list[IgCatalogEntry] = []
        seen: set[str] = set()

        for popular in POPULAR_IGS:
            entry = self._entries.get(popular["package_id"])
            if entry and entry.package_id not in seen:
                ordered.append(entry)
                seen.add(entry.package_id)

        for entry in sorted(self._entries.values(), key=lambda e: e.name.lower()):
            if entry.package_id in seen:
                continue
            ordered.append(entry)
            seen.add(entry.package_id)
            if len(ordered) >= limit:
                break

        return ordered[:limit]

    async def get_package_versions(
        self,
        package_id: str,
        *,
        fhir_version: str = "R4",
    ) -> tuple[str | None, list[IgVersionEntry]]:
        """Fetch all published versions for a package from packages.fhir.org."""
        client = await self._get_client()
        try:
            response = await client.get(f"{REGISTRY_BASE.rsplit('/catalog', 1)[0]}/{package_id}")
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.warning("Failed to fetch versions for %s: %s", package_id, exc)
            return None, []

        if not isinstance(data, dict):
            return None, []

        latest = str((data.get("dist-tags") or {}).get("latest") or "").strip() or None
        versions_raw = data.get("versions") or {}
        if not isinstance(versions_raw, dict):
            return latest, []

        entries: list[IgVersionEntry] = []
        for version, row in versions_raw.items():
            if not isinstance(row, dict):
                continue
            fv = _normalize_fhir_version(row.get("fhirVersion") or row.get("fhirVersion"))
            if fhir_version.upper() == "R4" and fv and not _is_r4_version(fv):
                continue
            dist = row.get("dist") or {}
            tarball = str(dist.get("tarball") or dist.get("url") or "").strip()
            shasum = str(dist.get("shasum") or "").strip()
            entries.append(
                IgVersionEntry(
                    version=str(version),
                    fhir_version=fv or "R4",
                    is_latest=latest == str(version),
                    tarball=tarball,
                    shasum=shasum,
                )
            )

        def _version_sort_key(entry: IgVersionEntry) -> tuple:
            parts: list[int] = []
            for token in re.split(r"[.\-]", entry.version):
                if token.isdigit():
                    parts.append(int(token))
                else:
                    parts.append(-1)
            return tuple(parts)

        entries.sort(key=_version_sort_key, reverse=True)
        return latest, entries


ig_catalog_service = IgCatalogService()
