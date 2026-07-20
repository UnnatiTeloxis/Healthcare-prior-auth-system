#!/usr/bin/env python3
"""Pre-download FHIR IG .tgz packages from packages.fhir.org into fhir_packages/."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.services.fhir_validator.ig_catalog import POPULAR_IGS, ig_catalog_service  # noqa: E402
from app.services.fhir_validator.ig_package_fetcher import IgPackageFetcher  # noqa: E402

logger = logging.getLogger(__name__)

_US_CATALOG_IDS_PATH = BACKEND_ROOT / "data" / "us_catalog_package_ids.json"
_MIN_US_CATALOG_IDS = 140

_FRIENDLY_ALIASES: dict[str, str] = {
    "hl7.fhir.us.core": "us-core.tgz",
    "hl7.fhir.us.davinci-crd": "davinci-crd.tgz",
    "hl7.fhir.us.davinci-dtr": "davinci-dtr.tgz",
    "hl7.fhir.us.davinci-pas": "davinci-pas.tgz",
}


def _curated_package_ids() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for row in POPULAR_IGS:
        package_id = row["package_id"]
        if package_id not in seen:
            seen.add(package_id)
            ordered.append(package_id)
    return ordered


async def _catalog_package_ids() -> list[str]:
    if _US_CATALOG_IDS_PATH.is_file():
        bundled = json.loads(_US_CATALOG_IDS_PATH.read_text(encoding="utf-8"))
        if isinstance(bundled, list) and len(bundled) >= _MIN_US_CATALOG_IDS:
            logger.info(
                "Using bundled US catalog list (%d packages) from %s",
                len(bundled),
                _US_CATALOG_IDS_PATH,
            )
            return sorted(str(item) for item in bundled)

    await ig_catalog_service.refresh(force=True)
    ids = sorted(
        package_id
        for package_id in ig_catalog_service._entries.keys()
        if package_id.startswith("hl7.fhir.us.")
    )
    if len(ids) >= _MIN_US_CATALOG_IDS:
        return ids

    logger.warning("Catalog discovery returned only %d US package(s)", len(ids))
    return ids


async def _download_all(
    fetcher: IgPackageFetcher,
    package_ids: list[str],
    *,
    resolve_dependencies: bool,
    write_aliases: bool,
    skip_cached: bool,
    pause_seconds: float,
) -> tuple[int, int, int, list[str]]:
    ok = 0
    skipped = 0
    failed = 0
    errors: list[str] = []
    pending = list(package_ids)

    for index, package_id in enumerate(pending, start=1):
        if skip_cached and fetcher.has_any_cached_version(package_id):
            skipped += 1
            logger.info("[%d/%d] Skipping %s (already cached)", index, len(pending), package_id)
            continue

        logger.info("[%d/%d] Downloading %s", index, len(pending), package_id)
        try:
            path = await fetcher.download_package(
                package_id,
                version=None,
                resolve_dependencies=resolve_dependencies,
            )
            ok += 1
            if write_aliases and package_id in _FRIENDLY_ALIASES:
                alias = fetcher.packages_dir / _FRIENDLY_ALIASES[package_id]
                if not alias.exists():
                    shutil.copy2(path, alias)
                    logger.info("  alias %s", alias.name)
        except Exception as exc:
            failed += 1
            message = f"{package_id}: {exc}"
            errors.append(message)
            logger.error("  failed: %s", message)

        if pause_seconds > 0 and index < len(pending):
            await asyncio.sleep(pause_seconds)

    return ok, skipped, failed, errors


def _write_manifest(
    output_dir: Path,
    *,
    scope: str,
    package_ids: list[str],
    ok: int,
    skipped: int,
    failed: int,
    errors: list[str],
) -> None:
    manifest = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "target_count": len(package_ids),
        "succeeded": ok,
        "skipped": skipped,
        "failed": failed,
        "cached_tgz_count": len(list(output_dir.glob("*.tgz"))),
        "errors": errors,
    }
    path = output_dir / "download_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Wrote manifest to %s", path)


async def _run(args: argparse.Namespace) -> int:
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.scope == "catalog":
        package_ids = await _catalog_package_ids()
    else:
        package_ids = _curated_package_ids()

    if args.limit:
        package_ids = package_ids[: args.limit]

    logger.info(
        "Downloading %d package(s) to %s (dependencies=%s, delay=%.1fs)",
        len(package_ids),
        output_dir,
        not args.no_deps,
        args.delay,
    )

    fetcher = IgPackageFetcher(packages_path=output_dir, request_delay=args.delay)
    ok, skipped, failed, errors = await _download_all(
        fetcher,
        package_ids,
        resolve_dependencies=not args.no_deps,
        write_aliases=args.aliases,
        skip_cached=not args.force,
        pause_seconds=args.delay,
    )

    if failed and args.retry_failed:
        retry_ids = [err.split(":", 1)[0] for err in errors]
        logger.info("Retrying %d failed package(s) after cooldown...", len(retry_ids))
        await asyncio.sleep(max(args.delay * 5, 30.0))
        retry_ok, retry_skipped, retry_failed, retry_errors = await _download_all(
            fetcher,
            retry_ids,
            resolve_dependencies=not args.no_deps,
            write_aliases=args.aliases,
            skip_cached=False,
            pause_seconds=args.delay * 2,
        )
        ok += retry_ok
        skipped += retry_skipped
        failed = retry_failed
        errors = retry_errors

    _write_manifest(
        output_dir,
        scope=args.scope,
        package_ids=package_ids,
        ok=ok,
        skipped=skipped,
        failed=failed,
        errors=errors,
    )

    await fetcher.close()
    await ig_catalog_service.close()

    logger.info("Done: %d succeeded, %d skipped, %d failed", ok, skipped, failed)
    for err in errors:
        logger.info("  %s", err)

    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download FHIR IG packages into a local folder for offline Inferno loading.",
    )
    parser.add_argument(
        "--output",
        default=settings.FHIR_PACKAGES_PATH,
        help="Destination folder (default: FHIR_PACKAGES_PATH / backend/fhir_packages)",
    )
    parser.add_argument(
        "--scope",
        choices=("popular", "catalog"),
        default="popular",
        help="popular = curated US IGs in the UI; catalog = all US-scoped registry packages",
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip downloading package.json dependencies (faster, smaller)",
    )
    parser.add_argument(
        "--aliases",
        action="store_true",
        default=True,
        help="Write friendly filenames (us-core.tgz, davinci-crd.tgz, ...)",
    )
    parser.add_argument(
        "--no-aliases",
        action="store_false",
        dest="aliases",
        help="Do not write friendly alias copies",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds to wait between registry requests / top-level packages (default: 3)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even when a cached version already exists",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Download only the first N packages (0 = all)",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        default=True,
        help="Retry failed packages once after a cooldown (default: on)",
    )
    parser.add_argument(
        "--no-retry-failed",
        action="store_false",
        dest="retry_failed",
        help="Do not retry failed packages",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
