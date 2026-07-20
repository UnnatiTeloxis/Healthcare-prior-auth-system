import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:8000"


def get(url: str):
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def post(url: str, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return exc.code, detail


def main() -> None:
    avail = get(f"{BASE}/api/v1/igs/available")
    print(f"available={avail.get('count')}")
    for ig in avail.get("igs") or []:
        print(f"  - {ig['name']}#{ig['version']}")

    # Wait briefly for backend warm sync
    for _ in range(10):
        loaded = get(f"{BASE}/api/v1/igs/loaded")
        if loaded.get("count", 0) > 0:
            break
        # Force load each available IG
        for ig in avail.get("igs") or []:
            post(
                f"{BASE}/api/v1/igs/load",
                {"package_name": ig["name"], "version": ig["version"]},
            )
        time.sleep(2)
    loaded = get(f"{BASE}/api/v1/igs/loaded")
    print(f"loaded={loaded.get('count')}")
    for ig in loaded.get("igs") or []:
        print(f"  - {ig.get('package_name')} profiles={len(ig.get('profiles') or [])}")

    cases = [
        (
            Path("/app/data/fhir-validator-samples/us-core-patient/01-valid-complete-us-core-patient.json"),
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
            True,
        ),
        (
            Path("/app/data/fhir-validator-samples/us-core-patient/03-invalid-missing-identifier.json"),
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
            False,
        ),
    ]
    # Host-mounted test-cases may not exist in container; try relative host path copy via data
    for path, profile, expect_valid in cases:
        if not path.is_file():
            print(f"SKIP {path}")
            continue
        resource = path.read_text(encoding="utf-8")
        t0 = time.time()
        status, result = post(
            f"{BASE}/api/v1/fhir/validate",
            {"resource": resource, "profiles": [profile]},
        )
        ms = int((time.time() - t0) * 1000)
        if status != 200:
            print(f"FAIL {path.name} HTTP {status}: {str(result)[:300]}")
            continue
        ok = bool(result.get("valid")) == expect_valid
        print(
            f"{path.name}: valid={result.get('valid')} errors={result.get('error_count')} "
            f"warn={result.get('warning_count')} ms={ms} expect_ok={ok}"
        )
        for issue in (result.get("issues") or [])[:3]:
            print(f"  - {issue.get('severity')}: {str(issue.get('message') or '')[:140]}")


if __name__ == "__main__":
    main()
