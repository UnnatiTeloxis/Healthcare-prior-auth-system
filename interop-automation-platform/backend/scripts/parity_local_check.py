"""Compare local Inferno wrapper vs our API for Inferno parity (same engine settings)."""
import json
import time
import urllib.request
from pathlib import Path

WRAPPER = "http://fhir-validator-wrapper:4567"
API = "http://127.0.0.1:8000"


def post_wrapper(resource: str, profiles: list[str]):
    url = f"{WRAPPER}/validate"
    if profiles:
        url += "?profile=" + ",".join(profiles)
    req = urllib.request.Request(
        url,
        data=resource.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.load(resp)


def post_api(resource: str, profiles: list[str]):
    body = json.dumps({"resource": resource, "profiles": profiles}).encode()
    req = urllib.request.Request(
        f"{API}/api/v1/fhir/validate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.load(resp)


def summarize_oo(oo: dict) -> tuple[int, int, int, list[str]]:
    issues = oo.get("issue") or []
    e = w = i = 0
    msgs = []
    for issue in issues:
        sev = (issue.get("severity") or "").lower()
        if sev in ("error", "fatal"):
            e += 1
        elif sev == "warning":
            w += 1
        else:
            i += 1
        details = issue.get("details") or {}
        text = details.get("text") if isinstance(details, dict) else ""
        msgs.append(f"{sev}:{(text or '')[:100]}")
    return e, w, i, msgs


def main() -> None:
    cases = [
        (
            Path("/app/data/fhir-validator-samples/us-core-patient/01-valid-complete-us-core-patient.json"),
            ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"],
        ),
        (
            Path("/app/data/fhir-validator-samples/us-core-patient/04-invalid-missing-name.json"),
            ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"],
        ),
        (
            Path("/app/data/fhir-validator-samples/inferno-parity-suite/01-valid-patient-minimal.json"),
            [],
        ),
        (
            Path("/app/data/fhir-validator-samples/inferno-parity-suite/08-invalid-patient-bad-gender.json"),
            [],
        ),
    ]

    for path, profiles in cases:
        if not path.is_file():
            print(f"SKIP {path.name}")
            continue
        resource = path.read_text(encoding="utf-8")
        t0 = time.time()
        oo = post_wrapper(resource, profiles)
        wrap_ms = int((time.time() - t0) * 1000)
        we, ww, wi, wmsgs = summarize_oo(oo)

        t1 = time.time()
        api = post_api(resource, profiles)
        api_ms = int((time.time() - t1) * 1000)
        ae = api.get("error_count")
        aw = api.get("warning_count")
        ai = api.get("info_count")

        match = (ae == we and aw == ww)
        print(
            f"{path.name} profiles={len(profiles)} "
            f"wrapper E/W/I={we}/{ww}/{wi} ({wrap_ms}ms) "
            f"api E/W/I={ae}/{aw}/{ai} ({api_ms}ms) "
            f"match={match}"
        )
        if not match:
            print("  wrapper msgs:", wmsgs[:5])
            for issue in (api.get("issues") or [])[:5]:
                print(f"  api: {issue.get('severity')}: {str(issue.get('message') or '')[:100]}")


if __name__ == "__main__":
    main()
