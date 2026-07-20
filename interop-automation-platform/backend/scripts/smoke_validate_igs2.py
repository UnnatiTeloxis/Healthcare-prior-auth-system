import json
import time
import urllib.request
from pathlib import Path


def post(url, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def get(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.load(response)


def main() -> None:
    avail = get("http://localhost:8000/api/v1/igs/available")
    print("available", avail["count"])
    for ig in avail["igs"]:
        res = post(
            "http://localhost:8000/api/v1/igs/load",
            {"package_name": ig["name"], "version": ig["version"]},
        )
        info = res["ig"]
        print(
            f"load {ig['name']}: status={info.get('status')} "
            f"profiles={len(info.get('profiles') or [])} ms={info.get('load_time_ms')}"
        )

    loaded = get("http://localhost:8000/api/v1/igs/loaded")
    print("loaded", loaded["count"])

    cases = [
        (
            "/app/data/fhir-validator-samples/us-core-patient/01-valid-complete-us-core-patient.json",
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
        ),
        (
            "/app/data/fhir-validator-samples/us-core-patient/04-invalid-missing-name.json",
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
        ),
    ]
    for path, profile in cases:
        file_path = Path(path)
        started = time.time()
        body = {"resource": file_path.read_text(encoding="utf-8"), "profiles": [profile]}
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/fhir/validate",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.load(response)
        elapsed_ms = int((time.time() - started) * 1000)
        print(
            f"{file_path.name}: valid={data['valid']} errors={data['error_count']} "
            f"warn={data['warning_count']} ms={elapsed_ms}"
        )
        for issue in (data.get("issues") or [])[:2]:
            print(f"  - {issue.get('severity')}: {str(issue.get('message') or '')[:160]}")


if __name__ == "__main__":
    main()
