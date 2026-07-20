#!/usr/bin/env python3
"""Generate backend/data/us_catalog_package_ids.json (~158 US IGs) for offline download."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.fhir_validator.ig_catalog import (  # noqa: E402
    _US_DISCOVERY_PREFIX,
    _entry_from_registry_row,
    ig_catalog_service,
)

logger = logging.getLogger(__name__)
OUTPUT_PATH = BACKEND_ROOT / "data" / "us_catalog_package_ids.json"


async def _collect_us_package_ids() -> list[str]:
    rows = await ig_catalog_service._discover_us_registry_rows(pause_seconds=2.0)
    package_ids: set[str] = set()
    for row in rows:
        package_id = str(row.get("Name") or row.get("name") or "").strip()
        if not package_id.startswith(_US_DISCOVERY_PREFIX):
            continue
        entry = _entry_from_registry_row(row, require_r4=False)
        if entry:
            package_ids.add(entry.package_id)
    return sorted(package_ids)


async def _run() -> int:
    package_ids = await _collect_us_package_ids()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(package_ids, indent=2), encoding="utf-8")
    logger.info("Wrote %d US package id(s) to %s", len(package_ids), OUTPUT_PATH)
    await ig_catalog_service.close()
    return 0 if len(package_ids) >= 140 else 1


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
