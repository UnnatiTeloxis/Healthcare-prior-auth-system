import asyncio
import json
import logging
from typing import Any

import httpx

from app.config import settings
from app.services.fhir_validator.fhir_loader import get_fhir_package_loader
from app.utils.fhir_helpers import extract_meta_profiles

logger = logging.getLogger(__name__)


class InfernoClient:
    def __init__(self) -> None:
        self.base_url = settings.inferno_validator_url.rstrip("/")
        self.client: httpx.AsyncClient | None = None
        self._loaded_igs: set[str] = set()
        self._attempted_default_load = False
        self._igs_ready = asyncio.Event()

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=600.0)
        return self.client

    async def close(self) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def validate_resource(self, resource: str, profiles: list[str]) -> dict[str, Any]:
        await self._wait_for_igs()
        await self.load_default_igs()
        await self._ensure_igs_for_meta_profiles(resource)

        client = await self._get_client()
        headers = {"Content-Type": "application/json"}
        # Match Inferno default: no profile query param unless user explicitly selects one.
        # The engine still validates meta.profile URLs declared on the resource.
        params = {"profile": ",".join(profiles)} if profiles else None

        response = await client.post(
            f"{self.base_url}/validate",
            content=resource,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def get_profiles(self) -> list[str]:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/profiles")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("Failed to fetch validator profiles: %s", exc)
            return []

    async def get_profiles_by_ig(self) -> dict[str, list[str]]:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/profiles-by-ig")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("Failed to fetch profiles by IG: %s", exc)
            return {}

    async def get_igs(self) -> dict[str, Any]:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/igs")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("Failed to fetch loaded IGs: %s", exc)
            return {}

    async def load_ig_by_id(self, package_id: str, version: str | None = None) -> dict[str, Any]:
        # Prefer offline/local packages when available to avoid outbound network calls.
        loader = get_fhir_package_loader()
        if loader.is_enabled():
            package_bytes = loader.load_package_bytes(package_id, version)
            if package_bytes:
                result = await self.upload_custom_ig(package_bytes)
                # Response usually includes package metadata; still mark requested key as loaded.
                self._loaded_igs.add(_ig_key(package_id, version))
                try:
                    resp_pid = str(result.get("package_id") or result.get("packageId") or "").strip()
                    resp_ver = str(result.get("version") or "").strip() or None
                    if resp_pid:
                        self._loaded_igs.add(_ig_key(resp_pid, resp_ver))
                except Exception:
                    pass
                logger.info("Loaded FHIR IG from local package %s", _ig_key(package_id, version))
                return result

        client = await self._get_client()
        params = {"version": version} if version else None

        response = await client.put(f"{self.base_url}/igs/{package_id}", params=params)
        response.raise_for_status()
        result = response.json()
        self._loaded_igs.add(_ig_key(package_id, version))
        logger.info("Loaded FHIR IG %s", _ig_key(package_id, version))
        return result

    async def upload_custom_ig(self, package_data: bytes) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/igs",
            content=package_data,
            headers={"Content-Encoding": "gzip"},
        )
        response.raise_for_status()
        return response.json()

    async def get_version(self) -> dict[str, Any]:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/version")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("Failed to fetch validator version: %s", exc)
            return {}

    async def load_default_igs(self) -> None:
        if self._attempted_default_load:
            self._igs_ready.set()
            return

        self._attempted_default_load = True
        all_loaded = True
        for ig_spec in settings.default_igs_list:
            package_id, version = _split_ig_spec(ig_spec)
            key = _ig_key(package_id, version)
            if key in self._loaded_igs:
                continue

            try:
                await self.load_ig_by_id(package_id, version)
            except Exception as exc:
                all_loaded = False
                logger.warning("Unable to load default IG %s: %s", key, exc)

        if not all_loaded:
            self._attempted_default_load = False
        self._igs_ready.set()

    async def _wait_for_igs(self, timeout: float = 600.0) -> None:
        if self._igs_ready.is_set():
            return
        try:
            await asyncio.wait_for(self._igs_ready.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for default IGs; continuing validation")
            self._igs_ready.set()

    async def _ensure_igs_for_meta_profiles(self, resource: str) -> None:
        """Load IGs referenced by meta.profile so validation matches Inferno hosted."""
        for profile_url in extract_meta_profiles(resource):
            ig_spec = _ig_spec_for_profile_url(profile_url)
            if not ig_spec:
                continue
            package_id, version = _split_ig_spec(ig_spec)
            key = _ig_key(package_id, version)
            if key in self._loaded_igs:
                continue
            try:
                await self.load_ig_by_id(package_id, version)
            except Exception as exc:
                logger.warning("Unable to load IG for profile %s: %s", profile_url, exc)


def _split_ig_spec(ig_spec: str) -> tuple[str, str | None]:
    if "#" not in ig_spec:
        return ig_spec, None

    package_id, version = ig_spec.split("#", 1)
    return package_id.strip(), version.strip() or None


def _ig_spec_for_profile_url(profile_url: str) -> str | None:
    """Map a StructureDefinition URL to a loadable IG package when known."""
    url = profile_url.lower()
    if "/us/core/" in url or "hl7.org/fhir/us/core" in url:
        for ig_spec in settings.default_igs_list:
            if ig_spec.startswith("hl7.fhir.us.core"):
                return ig_spec
    return None


def _ig_key(package_id: str, version: str | None) -> str:
    return f"{package_id}#{version}" if version else package_id


inferno_client = InfernoClient()
