import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ValidationHistoryService:
    """Service to save validation runs to test-history folder"""

    def __init__(self):
        # Check for Docker mount path first, then try to find local path
        docker_path = Path("/test-history")
        
        if docker_path.exists():
            # Running in Docker with volume mount
            self.history_dir = docker_path
        else:
            # Running locally - navigate up to find test-history
            # Path: backend/app/services/fhir_validator/history_service.py
            # Go up to project root (D:\interop-automation-platform)
            current = Path(__file__).resolve()
            # Try to find test-history folder by walking up
            for _ in range(10):  # Max 10 levels up
                current = current.parent
                test_history_path = current / "test-history"
                if test_history_path.exists():
                    self.history_dir = test_history_path
                    break
            else:
                # Fallback: create in current working directory
                self.history_dir = Path.cwd() / "test-history"
        
        self.runs_dir = self.history_dir / "runs"
        self.index_file = self.history_dir / "index.json"

        # Ensure directories exist
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.write_text("[]")

    def save_validation_run(
        self,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        test_name: Optional[str] = None,
    ) -> str:
        """
        Save a validation run to test-history

        Args:
            request_data: The validation request (resource, profiles, etc.)
            response_data: The validation response
            test_name: Optional custom test name

        Returns:
            The run ID
        """
        # Generate timestamp and ID
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        timestamp_file = timestamp.strftime("%Y-%m-%d_%H-%M")

        # Generate test name if not provided
        if not test_name:
            resource_type = response_data.get("resource_type", "Unknown")
            valid_status = "Valid" if response_data.get("valid") else "Invalid"
            test_name = f"Frontend Validation: {resource_type} - {valid_status}"

        # Sanitize name for filename
        sanitized_name = "".join(
            c if c.isalnum() or c in [" ", "-"] else "" for c in test_name
        ).replace(" ", "-")
        run_id = f"{timestamp_file}_{sanitized_name}"

        # Create run folder
        run_folder = self.runs_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        # Build result.json structure
        result_data = {
            "meta": {"id": run_id, "name": test_name, "timestamp": timestamp_str},
            "request": request_data,
            "response": response_data,
        }

        # Save result.json
        result_file = run_folder / "result.json"
        result_file.write_text(json.dumps(result_data, indent=2))

        # Generate report.md
        status = "✅ PASS" if response_data.get("valid") else "❌ FAIL"
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
**Profiles:** {', '.join(profiles) if profiles else 'None'}

"""

        # Add issues table if there are any
        if issues:
            report_content += """
## Issues

| Severity | Location | Message |
|----------|----------|---------|
"""
            for issue in issues:
                severity = issue.get("severity", "unknown")
                location = issue.get("location", "N/A")
                message = issue.get("message", "").replace("|", "\\|").replace("\n", " ")
                report_content += f"| {severity} | {location} | {message} |\n"
        else:
            report_content += "\n## Issues\n\nNo issues found. Resource is valid.\n"

        # Save report.md
        report_file = run_folder / "report.md"
        report_file.write_text(report_content)

        # Update index.json
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


# Global instance
history_service = ValidationHistoryService()
