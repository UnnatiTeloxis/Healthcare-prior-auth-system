#!/usr/bin/env python3
"""Install all curated local IG packages into Inferno once.

Run AFTER Inferno is healthy:
  docker compose up -d fhir-validator-wrapper
  docker compose ps   # wait until fhir-validator-wrapper is (healthy)

Usage (from backend/):
  python scripts/preload_igs_into_inferno.py
  python scripts/preload_igs_into_inferno.py --only hl7.fhir.us.odh,hl7.fhir.us.core
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

import httpx

# Allow `python scripts/...` from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.services.fhir_validator.inferno_client import InfernoClient, _ig_key
from app.services.fhir_validator.local_ig_catalog import local_ig_catalog

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("preload_igs")


async def wait_for_inferno(url: str, *, timeout_s: float = 1800.0) -> bool:
    """Poll /version until Inferno answers.

    After a long preload, the Java validator can pause for 1–2+ minutes on GC while
    still installing IGs — use a generous per-request read timeout.
    """
    base = url.rstrip("/")
    deadline = time.monotonic() + timeout_s
    attempt = 0
    # connect=10s, read=120s — /version can take 60–90s when Inferno is busy/GC-paused
    client_timeout = httpx.Timeout(120.0, connect=10.0)
    logger.info(
        "Waiting for Inferno at %s (up to %.0fs; each probe allows up to 120s)…",
        base,
        timeout_s,
    )
    logger.info(
        "If you just finished a preload, Inferno may be busy installing — ReadTimeout "
        "retries are normal; do not restart Docker."
    )
    async with httpx.AsyncClient(timeout=client_timeout) as client:
        while time.monotonic() < deadline:
            attempt += 1
            try:
                response = await client.get(f"{base}/version")
                if response.status_code == 200:
                    logger.info("Inferno is ready (%s)", response.text.strip()[:120])
                    return True
                logger.info("Inferno /version → HTTP %s (attempt %s)", response.status_code, attempt)
            except httpx.ReadTimeout:
                logger.info(
                    "Inferno still busy (attempt %s): /version read timed out after 120s — retrying…",
                    attempt,
                )
            except Exception as exc:
                logger.info("Inferno not ready yet (attempt %s): %s", attempt, repr(exc))
            await asyncio.sleep(5.0)
    return False


async def main(only: set[str] | None, wait_s: float, *, all_cached: bool) -> int:
    # Default: curated popular IGs only (fast). --all installs every cached package.
    entries = (
        local_ig_catalog.list_available()
        if all_cached
        else local_ig_catalog.list_popular_cached()
    )
    if only:
        entries = [e for e in entries if e.package_id in only]
    if not entries:
        logger.error("No local curated packages found. Run download_ig_packages.py first.")
        return 1

    if not await wait_for_inferno(settings.INFERNO_VALIDATOR_URL, timeout_s=wait_s):
        logger.error(
            "Inferno did not become ready in %.0fs.\n"
            "  1) docker compose up -d fhir-validator-wrapper\n"
            "  2) docker compose ps   # wait for (healthy)\n"
            "  3) python scripts/preload_igs_into_inferno.py",
            wait_s,
        )
        return 1

    client = InfernoClient()
    try:
        await client.ensure_ready()
        if not client._engine_warm:
            logger.error("Inferno client still not warm after /version OK.")
            return 1

        total = len(entries)
        ok = 0
        skipped = 0
        logger.info("Installing %d local IG(s) into Inferno…", total)
        for index, entry in enumerate(entries, start=1):
            key = _ig_key(entry.package_id, entry.cached_version)
            existing = await client._find_loaded_ig(entry.package_id)
            if existing:
                skipped += 1
                logger.info("[%s/%s] Already in Inferno: %s", index, total, key)
                ok += 1
                continue
            try:
                logger.info("[%s/%s] Loading %s (%s)…", index, total, entry.name, key)
                await client.load_ig_by_id(entry.package_id, entry.cached_version, startup=True)
                ok += 1
                logger.info("[%s/%s] Ready: %s", index, total, key)
            except Exception as exc:
                logger.error("[%s/%s] Failed %s: %s", index, total, key, exc)
        logger.info("Done. %s/%s IGs in Inferno (%s skipped, already loaded).", ok, total, skipped)
        if ok < total:
            logger.info("Re-run the same command to retry failed packages (already-loaded ones are skipped).")
        return 0 if ok == total else 2
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preload local FHIR IG packages into Inferno")
    parser.add_argument(
        "--only",
        help="Comma-separated package ids to preload (default: all curated local packages)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install every cached package under FHIR_PACKAGES_PATH (slow; default is popular only)",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=1800.0,
        help="Seconds to wait for Inferno /version before failing (default: 1800)",
    )
    args = parser.parse_args()
    only_ids = {p.strip() for p in args.only.split(",") if p.strip()} if args.only else None
    raise SystemExit(asyncio.run(main(only_ids, args.wait, all_cached=args.all)))
