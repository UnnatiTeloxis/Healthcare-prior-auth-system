import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ValidationHistoryService:
    """Service to save validation runs to a test-history folder."""

    def __init__(self) -> None:
        docker_path = Path("/test-history")

        if docker_path.exists():
            self.history_dir = docker_path
        else:
            current = Path(__file__).resolve()
            history_dir = None
            for _ in range(10):
                current = current.parent
                candidate = current / "test-history"
                if candidate.exists():
                    history_dir = candidate
                    break
            self.history_dir = history_dir or (Path.cwd() / "test-history")

        self.runs_dir = self.history_dir / "runs"
        self.index_file = self.history_dir / "index.json"

        self.runs_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.write_text("[]")

    def save_validation_run(
        self,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        test_name: Optional[str] = None,
    ) -> str:
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        timestamp_file = timestamp.strftime("%Y-%m-%d_%H-%M")

        if not test_name:
            resource_type = response_data.get("resource_type", "Unknown")
            valid_status = "Valid" if response_data.get("valid") else "Invalid"
            test_name = f"Frontend Validation: {resource_type} - {valid_status}"

        sanitized_name = "".join(
            c if c.isalnum() or c in [" ", "-"] else "" for c in test_name
        ).replace(" ", "-")
        run_id = f"{timestamp_file}_{sanitized_name}"

        run_folder = self.runs_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        result_data = {
            "meta": {"id": run_id, "name": test_name, "timestamp": timestamp_str},
            "request": request_data,
            "response": response_data,
        }

        result_file = run_folder / "result.json"
        result_file.write_text(json.dumps(result_data, indent=2))

        status = "PASS" if response_data.get("valid") else "FAIL"
        error_count = response_data.get("error_count", 0)
        warning_count = response_data.get("warning_count", 0)
        info_count = response_data.get("info_count", 0)
        summary = response_data.get("summary", "")
        resource_type = response_data.get("resource_type", "Unknown")
        profiles = response_data.get("profiles", [])
        issues = response_data.get("issues", [])

        report_content = f"""# {test_name}

**Status:** {status}
**Timestamp:** {timestamp_str}
**Run ID:** `{run_id}`

## Summary

{summary}

## Issue Counts

- **Errors:** {error_count}
- **Warnings:** {warning_count}
- **Informational:** {info_count}

## Validation Details

**Resource Type:** {resource_type}
**Valid:** {response_data.get("valid")}
**Profiles:** {", ".join(profiles) if profiles else "None"}

"""

        if issues:
            report_content += """
## Issues

| Severity | Location | Message |
|----------|----------|---------|
"""
            for issue in issues:
                severity = issue.get("severity", "unknown")
                location = issue.get("location", "N/A")
                message = str(issue.get("message", "")).replace("|", "\\|").replace("\n", " ")
                report_content += f"| {severity} | {location} | {message} |\n"
        else:
            report_content += "\n## Issues\n\nNo issues found. Resource is valid.\n"

        report_file = run_folder / "report.md"
        report_file.write_text(report_content)

        index_data = []
        if self.index_file.exists():
            try:
                index_data = json.loads(self.index_file.read_text())
            except json.JSONDecodeError:
                index_data = []

        index_entry = {
            "id": run_id,
            "timestamp": timestamp_str,
            "name": test_name,
            "valid": response_data.get("valid"),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "summary": summary,
            "folder": f"runs/{run_id}",
        }

        index_data.append(index_entry)
        self.index_file.write_text(json.dumps(index_data, indent=2))

        return run_id


history_service = ValidationHistoryService()
