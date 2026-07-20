#!/usr/bin/env python3
"""
Validate every test-cases/ sample against its IG and compare to filename expectations.

Expected (from filename):
  *valid*   -> error_count == 0
  *invalid* -> error_count > 0
  other     -> report only (realistic / unnamed)
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from app.services.fhir_validator.ig_constants import IG_PREFERRED_VERSIONS
from app.services.fhir_validator.ig_manager import ig_manager
from app.services.fhir_validator.test_case_catalog import list_catalog, read_sample

API = "http://localhost:8000/api/v1/fhir/validate"
IG_LOAD = "http://localhost:8000/api/v1/igs/load"
TIMEOUT = 120.0


@dataclass
class SampleResult:
    package_id: str
    path: str
    file: str
    tier: str
    resource_type: str
    profile_url: str
    expected: str  # pass | fail | unknown
    error_count: int
    warning_count: int
    info_count: int
    accurate: bool | None
    elapsed_ms: int
    top_issue: str = ""
    note: str = ""


def expected_from_filename(name: str) -> str:
    lower = name.lower()
    if "invalid" in lower:
        return "fail"
    if "valid" in lower:
        return "pass"
    return "unknown"


def is_base_extension_sd(url: str) -> bool:
    u = (url or "").lower().split("|")[0]
    return "hl7.org/fhir/structuredefinition/" in u and "/us/" not in u and "/uv/" not in u


def resolve_profile(
    package_id: str,
    resource: dict,
    profiles: list[str],
    profiles_by_type: dict[str, list[str]],
) -> str | None:
    meta = (resource.get("meta") or {}).get("profile") or []
    if isinstance(meta, str):
        meta = [meta]
    meta_url = meta[0] if meta else ""

    if meta_url and meta_url in profiles:
        return meta_url

    rt = resource.get("resourceType") or ""
    typed = profiles_by_type.get(rt) or []
    typed = [u for u in typed if not is_base_extension_sd(u)]
    if typed:
        return typed[0]

    if meta_url:
        return meta_url

    # Best slug match (same logic as frontend, simplified)
    if not rt or not profiles:
        return None
    kebab = re.sub(r"([A-Z])", r"-\1", rt).lower().lstrip("-")
    best = None
    best_score = 0
    for url in profiles:
        if is_base_extension_sd(url):
            continue
        slug = (url.split("/")[-1]).split("|")[0].lower()
        score = 0
        if slug in (f"profile-{kebab}", f"us-core-{kebab}", f"qicore-{kebab}"):
            score = 100
        elif slug == kebab:
            score = 90
        elif slug.endswith(f"-{kebab}"):
            score = 85
        if score > best_score:
            best_score = score
            best = url
    return best if best_score > 0 else None


async def ensure_ig(client: httpx.AsyncClient, package_id: str, *, wait: bool = True) -> dict:
    version = IG_PREFERRED_VERSIONS.get(package_id)
    r = await client.post(
        IG_LOAD,
        json={"package_name": package_id, "version": version, "wait": wait},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("ig") or {}


async def validate_sample(
    client: httpx.AsyncClient,
    package_id: str,
    sample: dict,
    ig_info: dict,
) -> SampleResult:
    path = sample["path"]
    content = read_sample(path)
    resource = json.loads(content)
    profiles = list(ig_info.get("profiles") or [])
    profiles_by_type = dict(ig_info.get("profiles_by_type") or {})
    profile = resolve_profile(package_id, resource, profiles, profiles_by_type)
    profiles_param = [profile] if profile else []

    t0 = time.monotonic()
    try:
        resp = await client.post(
            API,
            json={
                "resource": content,
                "profiles": profiles_param,
                "resource_type": resource.get("resourceType"),
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        elapsed = int((time.monotonic() - t0) * 1000)
        return SampleResult(
            package_id=package_id,
            path=path,
            file=sample["file"],
            tier=sample["tier"],
            resource_type=resource.get("resourceType") or "",
            profile_url=profile or "",
            expected=expected_from_filename(sample["file"]),
            error_count=-1,
            warning_count=0,
            info_count=0,
            accurate=False,
            elapsed_ms=elapsed,
            top_issue="",
            note=f"API error: {exc}",
        )

    elapsed = int((time.monotonic() - t0) * 1000)
    errors = int(data.get("error_count") or 0)
    warnings = int(data.get("warning_count") or 0)
    infos = int(data.get("info_count") or 0)
    issues = data.get("issues") or []
    top = ""
    if issues:
        top = str(issues[0].get("message") or "")[:120]

    expected = expected_from_filename(sample["file"])
    accurate: bool | None
    if expected == "pass":
        accurate = errors == 0
    elif expected == "fail":
        accurate = errors > 0
    else:
        accurate = None

    note = ""
    if not profile and package_id != "hl7.fhir.uv.extensions.r4":
        note = "no profile resolved"

    return SampleResult(
        package_id=package_id,
        path=path,
        file=sample["file"],
        tier=sample["tier"],
        resource_type=resource.get("resourceType") or "",
        profile_url=profile or "",
        expected=expected,
        error_count=errors,
        warning_count=warnings,
        info_count=infos,
        accurate=accurate,
        elapsed_ms=elapsed,
        top_issue=top,
        note=note,
    )


async def run_all() -> list[SampleResult]:
    catalog = list_catalog()
    results: list[SampleResult] = []
    sem = asyncio.Semaphore(6)
    async with httpx.AsyncClient() as client:
        for entry in catalog:
            pkg = entry["package_id"]
            print(f"\n=== {pkg} ({entry['sample_count']} samples) ===", flush=True)
            try:
                ig_info = await ensure_ig(client, pkg)
            except Exception as exc:
                print(f"  IG load failed: {exc}", flush=True)
                for sample in entry["samples"]:
                    results.append(
                        SampleResult(
                            package_id=pkg,
                            path=sample["path"],
                            file=sample["file"],
                            tier=sample["tier"],
                            resource_type="",
                            profile_url="",
                            expected=expected_from_filename(sample["file"]),
                            error_count=-1,
                            warning_count=0,
                            info_count=0,
                            accurate=False,
                            elapsed_ms=0,
                            note=f"IG load failed: {exc}",
                        )
                    )
                continue

            local = ig_manager._local_resource_profiles(pkg, IG_PREFERRED_VERSIONS.get(pkg))
            if local:
                ig_info.setdefault("profiles", local.get("profiles") or [])
                ig_info.setdefault("profiles_by_type", local.get("profiles_by_type") or {})

            async def one(sample: dict) -> SampleResult:
                async with sem:
                    return await validate_sample(client, pkg, sample, ig_info)

            batch = await asyncio.gather(*(one(s) for s in entry["samples"]))
            for r in batch:
                results.append(r)
                mark = "?" if r.accurate is None else ("OK" if r.accurate else "MISS")
                print(
                    f"  [{mark}] {r.file}: E={r.error_count} W={r.warning_count} "
                    f"exp={r.expected} {r.elapsed_ms}ms",
                    flush=True,
                )
    return results


def print_summary(results: list[SampleResult]) -> int:
    labeled = [r for r in results if r.expected in ("pass", "fail")]
    ok = [r for r in labeled if r.accurate]
    miss = [r for r in labeled if r.accurate is False]
    unknown = [r for r in results if r.expected == "unknown"]
    api_errors = [r for r in results if r.error_count < 0]

    print("\n" + "=" * 72)
    print("VALIDATION ACCURACY SUMMARY")
    print("=" * 72)
    print(f"Total samples:     {len(results)}")
    print(f"Labeled (v/i):     {len(labeled)}  (valid={sum(1 for r in labeled if r.expected=='pass')}, "
          f"invalid={sum(1 for r in labeled if r.expected=='fail')})")
    print(f"Accurate:          {len(ok)} / {len(labeled)} ({100*len(ok)/max(len(labeled),1):.1f}%)")
    print(f"Mismatch:          {len(miss)}")
    print(f"Unlabeled:         {len(unknown)} (realistic/other — manual review)")
    print(f"API/IG errors:     {len(api_errors)}")

    by_ig: dict[str, list[SampleResult]] = {}
    for r in results:
        by_ig.setdefault(r.package_id, []).append(r)

    print("\n--- Per IG (labeled accuracy) ---")
    for pkg in sorted(by_ig):
        rows = by_ig[pkg]
        lab = [r for r in rows if r.expected in ("pass", "fail")]
        if not lab:
            print(f"  {pkg}: no labeled samples")
            continue
        good = sum(1 for r in lab if r.accurate)
        print(f"  {pkg}: {good}/{len(lab)} accurate")

    if miss:
        print("\n--- MISMATCHES (expected vs actual) ---")
        for r in miss:
            exp = "0 errors" if r.expected == "pass" else ">0 errors"
            print(f"  {r.package_id}/{r.path}")
            print(f"    expected {exp}, got E={r.error_count} W={r.warning_count}")
            if r.profile_url:
                print(f"    profile: {r.profile_url}")
            if r.top_issue:
                print(f"    issue: {r.top_issue}")
            if r.note:
                print(f"    note: {r.note}")

    if api_errors:
        print("\n--- API / IG LOAD ERRORS ---")
        for r in api_errors[:20]:
            print(f"  {r.path}: {r.note}")

    # Write JSON report
    out = Path(__file__).resolve().parents[1] / "test-history" / "test-case-validation-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([r.__dict__ for r in results], indent=2),
        encoding="utf-8",
    )
    print(f"\nFull report: {out}")
    return 1 if miss or api_errors else 0


def main() -> int:
    results = asyncio.run(run_all())
    return print_summary(results)


if __name__ == "__main__":
    raise SystemExit(main())
