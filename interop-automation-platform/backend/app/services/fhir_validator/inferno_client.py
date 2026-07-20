import asyncio
import hashlib
import logging
import time
from typing import Any

import httpx

from app.config import settings
from app.services.fhir_validator.fhir_loader import get_fhir_package_loader
from app.utils.fhir_helpers import extract_meta_profiles, is_valid_xml

logger = logging.getLogger(__name__)

_ENGINE_POLL_INTERVAL = 2.0
_ENGINE_POLL_TIMEOUT = 300.0
_STARTUP_503_RETRIES = 90
_STARTUP_503_INTERVAL = 1.0
_RUNTIME_503_RETRIES = 15
_RUNTIME_503_INTERVAL = 2.0
_RESULT_CACHE_TTL_S = 3600.0
_US_CORE_PATIENT_PROFILE = (
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
)
# Terminology is network-bound; parallel validates keep batch latency low.
_VALIDATE_CONCURRENCY = 6
_WARMUP_RESOURCE = '{"resourceType":"Patient","id":"warmup"}'


class InfernoClient:
    def __init__(self) -> None:
        self.base_url = settings.inferno_validator_url.rstrip("/")
        self.client: httpx.AsyncClient | None = None
        # Packages we successfully loaded in this process (upload/PUT), or confirmed
        # present via /profiles (auto-loaded from /home/igs).
        self._loaded_igs: set[str] = set()
        self._ready = asyncio.Event()
        self._engine_warm = False
        self._startup_lock = asyncio.Lock()
        self._validate_sem = asyncio.Semaphore(_VALIDATE_CONCURRENCY)
        self._result_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                # Large Bundles + terminology can take minutes; keep connect short.
                timeout=httpx.Timeout(600.0, connect=10.0, write=120.0),
                limits=httpx.Limits(max_connections=32, max_keepalive_connections=16),
            )
        return self.client

    async def close(self) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def _is_engine_ready(self) -> bool:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/profiles")
            if response.status_code == 503:
                return False
            response.raise_for_status()
            return isinstance(response.json(), list)
        except Exception:
            return False

    async def _wait_for_engine(self, timeout: float = _ENGINE_POLL_TIMEOUT) -> None:
        if self._engine_warm:
            return

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if await self._is_engine_ready():
                self._engine_warm = True
                logger.info("Inferno validator engine is ready")
                return
            await asyncio.sleep(_ENGINE_POLL_INTERVAL)
        raise TimeoutError(f"Inferno engine not ready after {timeout:.0f}s")

    async def _request(
        self,
        method: str,
        url: str,
        *,
        startup: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        client = await self._get_client()
        attempts = _STARTUP_503_RETRIES if startup else _RUNTIME_503_RETRIES
        interval = _STARTUP_503_INTERVAL if startup else _RUNTIME_503_INTERVAL
        response: httpx.Response | None = None

        for attempt in range(1, attempts + 1):
            try:
                response = await client.request(method, url, **kwargs)
            except httpx.TransportError as exc:
                if attempt >= attempts:
                    raise
                logger.info("Inferno transport error for %s (attempt %s/%s): %s", url, attempt, attempts, exc)
                await asyncio.sleep(interval)
                continue

            if response.status_code != 503:
                if response.status_code < 500:
                    self._engine_warm = True
                return response

            self._engine_warm = False
            if attempt < attempts:
                logger.info("Inferno 503 for %s (attempt %s/%s)", url, attempt, attempts)
                try:
                    await self._wait_for_engine(timeout=20.0)
                except TimeoutError:
                    await asyncio.sleep(interval)

        assert response is not None
        return response

    def _register_loaded_ig(self, package_id: str, version: str | None, result: dict[str, Any] | None = None) -> None:
        if package_id:
            self._loaded_igs.add(_ig_key(package_id, version))
            self._loaded_igs.add(package_id)
        if result:
            resp_pid = str(
                result.get("package_id") or result.get("packageId") or result.get("id") or ""
            ).strip()
            resp_ver = str(result.get("version") or "").strip() or None
            if resp_pid:
                self._loaded_igs.add(_ig_key(resp_pid, resp_ver))
                self._loaded_igs.add(resp_pid)

    def _is_ig_loaded(self, package_id: str, version: str | None) -> bool:
        if _ig_key(package_id, version) in self._loaded_igs:
            return True
        if package_id in self._loaded_igs:
            return True
        if version:
            prefix = f"{package_id}#"
            return any(key.startswith(prefix) for key in self._loaded_igs)
        return False

    async def _us_core_profiles_loaded(self) -> bool:
        """True when US Core StructureDefinitions are in the engine (not just catalog)."""
        profiles = await self.get_profiles()
        return any(_US_CORE_PATIENT_PROFILE in p for p in profiles)

    async def ensure_ready(self) -> None:
        if self._ready.is_set() and self._engine_warm:
            return

        async with self._startup_lock:
            if self._ready.is_set() and self._engine_warm:
                return

            try:
                await self._wait_for_engine()
            except TimeoutError as exc:
                logger.warning("%s — validation will retry until Inferno is ready", exc)
                return

            # Detect IGs auto-loaded from /home/igs at engine start (terminology only
            # in Inferno-parity mode). Do NOT upload DEFAULT_IGS here — that made
            # Base FHIR apply US Core/Da Vinci while hosted Inferno reported
            # "profile has not been checked because it could not be found".
            await self._detect_preloaded_igs()

            self._ready.set()
            logger.info("Inferno validator ready (%s IGs tracked)", len(self._loaded_igs))

    async def _detect_preloaded_igs(self) -> None:
        """Detect IGs loaded in Inferno by scanning profile URLs."""
        try:
            profiles = await self.get_profiles()
            ig_patterns = {
                "hl7.fhir.us.core": "/us/core/",
                "hl7.fhir.us.davinci-hrex": "/davinci-hrex/",
                "hl7.fhir.us.davinci-crd": "/davinci-crd/",
                "hl7.fhir.us.davinci-dtr": "/davinci-dtr/",
                "hl7.fhir.us.davinci-pas": "/davinci-pas/",
            }
            profiles_lower = [p.lower() for p in profiles]
            for pid, pattern in ig_patterns.items():
                if any(pattern in p for p in profiles_lower):
                    self._register_loaded_ig(pid, None)
            logger.info("Detected %d pre-loaded IGs from profiles", len(self._loaded_igs))
        except Exception as exc:
            logger.warning("Failed to detect pre-loaded IGs: %s", exc)
            if await self._us_core_profiles_loaded():
                self._register_loaded_ig("hl7.fhir.us.core", None)

    @staticmethod
    def _content_type_for_resource(resource: str) -> str:
        # Inferno Resource Validator / HAPI expect FHIR MIME types.
        if is_valid_xml(resource):
            return "application/fhir+xml"
        return "application/fhir+json"

    @staticmethod
    def _cache_key(resource: str, profiles: list[str]) -> str:
        digest = hashlib.sha256()
        digest.update(resource.encode("utf-8") if isinstance(resource, str) else resource)
        digest.update(b"\0")
        digest.update(",".join(profiles).encode("utf-8"))
        return digest.hexdigest()

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        item = self._result_cache.get(key)
        if not item:
            return None
        expires_at, payload = item
        if time.monotonic() > expires_at:
            self._result_cache.pop(key, None)
            return None
        return payload

    def _cache_set(self, key: str, payload: dict[str, Any]) -> None:
        if len(self._result_cache) > 512:
            oldest = sorted(self._result_cache.items(), key=lambda kv: kv[1][0])[:128]
            for old_key, _ in oldest:
                self._result_cache.pop(old_key, None)
        self._result_cache[key] = (time.monotonic() + _RESULT_CACHE_TTL_S, payload)

    async def warm_up(self) -> None:
        """Detect IGs already loaded from /home/igs and probe validate for speed."""
        await self.ensure_ready()
        if not self._engine_warm:
            return

        try:
            from app.services.fhir_validator.ig_manager import ig_manager

            # Catalog packages for the dropdown — do NOT upload resource IGs into Inferno
            # at boot. Hosted Inferno only applies profiles that are already loaded /
            # explicitly selected; auto-loading US Core/Da Vinci caused Base FHIR
            # mismatches (meta.profile applied locally but "not found" on hosted).
            available = ig_manager.list_available_igs(force_refresh=True)
            await self._detect_preloaded_igs()
            logger.info(
                "IG warm-up: %d catalog package(s); %d already in engine (terminology/boot)",
                len(available),
                len(self._loaded_igs),
            )
        except Exception as exc:
            logger.warning("IG warm-up incomplete: %s", exc)

        try:
            await self.validate_resource(_WARMUP_RESOURCE, [])
            logger.info("Inferno warm-up probe complete")
        except Exception as exc:
            logger.warning("Inferno warm-up probe failed: %s", exc)

    async def validate_resource(self, resource: str, profiles: list[str]) -> dict[str, Any]:
        cache_key = self._cache_key(resource, profiles)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        async with self._validate_sem:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            # Ensure IGs only for explicitly requested Advanced profiles (?profile=).
            # Do NOT auto-fetch IGs from meta.profile — Inferno hosted skips unknown
            # profiles ("validator is set to not fetch unknown profiles").
            from app.services.fhir_validator.ig_manager import ig_manager

            if profiles:
                await ig_manager.ensure_inferno_for_profiles(profiles)

            headers = {"Content-Type": self._content_type_for_resource(resource)}
            params = {"profile": ",".join(profiles)} if profiles else None
            body = resource.encode("utf-8") if isinstance(resource, str) else resource

            response = await self._request(
                "POST",
                f"{self.base_url}/validate",
                startup=False,
                content=body,
                headers=headers,
                params=params,
            )
            if response.status_code == 503:
                raise RuntimeError("Validator engine is still initializing. Please wait and try again.")

            # Do not silently fall back to base FHIR — that diverges from Inferno.
            # Surface the engine error so unresolved profiles are visible.
            if response.status_code >= 400:
                detail = ""
                try:
                    detail = response.text[:500]
                except Exception:
                    pass
                if profiles and response.status_code == 500:
                    logger.warning(
                        "Profile validation error for %s: %s",
                        profiles,
                        detail or response.status_code,
                    )
                response.raise_for_status()

            payload = response.json()
            self._engine_warm = True
            self._cache_set(cache_key, payload)
            return payload

    async def _ensure_igs_for_profile_urls(self, profiles: list[str]) -> None:
        for profile_url in profiles:
            ig_spec = _ig_spec_for_profile_url(profile_url)
            if not ig_spec:
                continue
            package_id, version = _split_ig_spec(ig_spec)
            if self._is_ig_loaded(package_id, version):
                continue
            try:
                await self.load_ig_by_id(package_id, version, startup=False)
            except Exception as exc:
                logger.warning("Unable to load IG for profile %s: %s", profile_url, exc)

    async def get_profiles(self) -> list[str]:
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/profiles")
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
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
            if response.status_code == 503:
                return {}
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("Failed to fetch loaded IGs: %s", exc)
            return {}

    async def load_ig_by_id(
        self,
        package_id: str,
        version: str | None = None,
        *,
        startup: bool = False,
    ) -> dict[str, Any]:
        if self._is_ig_loaded(package_id, version):
            return {"package_id": package_id, "version": version}

        loader = get_fhir_package_loader()
        if loader.is_enabled():
            package_bytes = loader.load_package_bytes(package_id, version)
            if package_bytes:
                result = await self.upload_custom_ig(package_bytes, startup=startup)
                self._register_loaded_ig(package_id, version, result)
                logger.info("Loaded FHIR IG from local package %s", _ig_key(package_id, version))
                return result

        params = {"version": version} if version else None
        response = await self._request(
            "PUT",
            f"{self.base_url}/igs/{package_id}",
            startup=startup,
            params=params,
        )
        response.raise_for_status()
        result = response.json()
        self._register_loaded_ig(package_id, version, result)
        logger.info("Loaded FHIR IG %s", _ig_key(package_id, version))
        return result

    async def upload_custom_ig(self, package_data: bytes, *, startup: bool = False) -> dict[str, Any]:
        response = await self._request(
            "POST",
            f"{self.base_url}/igs",
            startup=startup,
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
        await self.ensure_ready()

    async def _ensure_igs_for_meta_profiles(self, resource: str) -> None:
        # Hot path: when default IGs are loaded, skip work for common US Core resources.
        needs_load = False
        for profile_url in extract_meta_profiles(resource):
            ig_spec = _ig_spec_for_profile_url(profile_url)
            if not ig_spec:
                continue
            package_id, version = _split_ig_spec(ig_spec)
            if not self._is_ig_loaded(package_id, version):
                needs_load = True
                break
        if not needs_load:
            return

        for profile_url in extract_meta_profiles(resource):
            ig_spec = _ig_spec_for_profile_url(profile_url)
            if not ig_spec:
                continue
            package_id, version = _split_ig_spec(ig_spec)
            if self._is_ig_loaded(package_id, version):
                continue
            if package_id.startswith("hl7.fhir.us.core") and await self._us_core_profiles_loaded():
                self._register_loaded_ig(package_id, version)
                continue
            try:
                await self.load_ig_by_id(package_id, version, startup=False)
            except Exception as exc:
                logger.warning("Unable to load IG for profile %s: %s", profile_url, exc)


def _split_ig_spec(ig_spec: str) -> tuple[str, str | None]:
    if "#" not in ig_spec:
        return ig_spec, None

    package_id, version = ig_spec.split("#", 1)
    return package_id.strip(), version.strip() or None


def _ig_spec_for_profile_url(profile_url: str) -> str | None:
    url = profile_url.lower()
    if "/us/core/" in url or "hl7.org/fhir/us/core" in url:
        for ig_spec in settings.default_igs_list:
            if ig_spec.startswith("hl7.fhir.us.core"):
                return ig_spec
        return "hl7.fhir.us.core"
    if "davinci-hrex" in url or "davinci.hrex" in url:
        return "hl7.fhir.us.davinci-hrex"
    if "davinci-crd" in url or "davinci.crd" in url:
        return "hl7.fhir.us.davinci-crd"
    if "davinci-dtr" in url or "davinci.dtr" in url:
        return "hl7.fhir.us.davinci-dtr"
    if "davinci-pas" in url or "davinci.pas" in url:
        return "hl7.fhir.us.davinci-pas"
    if "davinci-pdex" in url:
        return "hl7.fhir.us.davinci-pdex"
    if "davinci-cdex" in url:
        return "hl7.fhir.us.davinci-cdex"
    if "davinci-pcde" in url:
        return "hl7.fhir.us.davinci-pcde"
    if "davinci-alerts" in url:
        return "hl7.fhir.us.davinci-alerts"
    if "drug-formulary" in url:
        return "hl7.fhir.us.davinci-drug-formulary"
    if "davinci-deqm" in url:
        return "hl7.fhir.us.davinci-deqm"
    if "davinci-ra" in url:
        return "hl7.fhir.us.davinci-ra"
    if "/us/mcode/" in url or "hl7.org/fhir/us/mcode" in url:
        return "hl7.fhir.us.mcode"
    if "/us/carin-bb/" in url or "carin-bb" in url:
        return "hl7.fhir.us.carin-bb"
    if "/us/qicore/" in url or "hl7.org/fhir/us/qicore" in url:
        return "hl7.fhir.us.qicore"
    if "/us/ccda/" in url or "ccda" in url:
        return "hl7.fhir.us.ccda"
    if "/us/odh/" in url:
        return "hl7.fhir.us.odh"
    if "military-service" in url:
        return "hl7.fhir.us.military-service"
    if "/us/vrdr/" in url or "vrdr" in url:
        return "hl7.fhir.us.vrdr"
    if "/us/ecr/" in url:
        return "hl7.fhir.us.ecr"
    if "pacio-adi" in url:
        return "hl7.fhir.us.pacio-adi"
    if "pacio-cs" in url:
        return "hl7.fhir.us.pacio-cs"
    if "pacio-fs" in url:
        return "hl7.fhir.us.pacio-fs"
    if "bulkdata" in url or "bulk-data" in url:
        return "hl7.fhir.us.bulkdata"
    if "/uv/sdc/" in url:
        return "hl7.fhir.uv.sdc"
    if "/uv/ipa/" in url:
        return "hl7.fhir.uv.ipa"
    if "/uv/ips/" in url:
        return "hl7.fhir.uv.ips"
    if "smart-app-launch" in url:
        return "hl7.fhir.uv.smart-app-launch"
    if "/uv/extensions" in url:
        return "hl7.fhir.uv.extensions.r4"
    return None


def _ig_key(package_id: str, version: str | None) -> str:
    return f"{package_id}#{version}" if version else package_id


inferno_client = InfernoClient()
