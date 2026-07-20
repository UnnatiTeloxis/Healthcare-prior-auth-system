from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class IssueSeverity(str, Enum):
    fatal = "fatal"
    error = "error"
    warning = "warning"
    information = "information"


class ValidationIssue(BaseModel):
    severity: IssueSeverity
    code: str = "unknown"
    message: str = ""
    location: str | None = None
    line: int | None = None
    column: int | None = None


class ValidationRequest(BaseModel):
    resource: str = Field(..., description="FHIR resource as a JSON or XML string")
    profiles: list[str] = Field(default_factory=list, description="Profile URLs to validate against")
    resource_type: str | None = Field(None, description="FHIR resource type, auto-detected when omitted")
    ig: str | None = Field(
        None,
        description="IG package spec, e.g. hl7.fhir.us.core#6.1.0",
    )
    profile: str | None = Field(
        None,
        description="Single profile URL to validate against",
    )


class BatchValidationRequest(BaseModel):
    resources: list[str] = Field(..., description="FHIR resources as JSON or XML strings")
    profiles: list[str] = Field(default_factory=list, description="Profile URLs to validate against")
    ig: str | None = Field(None, description="IG package spec, e.g. hl7.fhir.us.core#6.1.0")
    profile: str | None = Field(None, description="Single profile URL to validate against")


class LoadIGRequest(BaseModel):
    package_id: str | None = Field(None, description="NPM package ID, for example hl7.fhir.us.core")
    package_name: str | None = Field(None, description="Alias for package_id")
    version: str | None = Field(None, description="Package version, for example 6.1.0")
    retry: bool = Field(False, description="Retry after a previous failed load")

    @model_validator(mode="after")
    def require_package_identifier(self) -> "LoadIGRequest":
        if not (self.package_id or self.package_name):
            raise ValueError("Either package_id or package_name is required")
        return self


class ValidationResult(BaseModel):
    valid: bool
    resource_type: str | None = None
    profiles: list[str] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
    summary: str = ""
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    operation_outcome: dict[str, Any] | None = None
    selected_ig: str | None = None
    resolved_profile: str | None = None
    package_id: str | None = None
    package_version: str | None = None


class BatchValidationResult(BaseModel):
    results: list[ValidationResult]
    total: int
    valid_count: int
    invalid_count: int


class ProfileInfo(BaseModel):
    url: str
    name: str | None = None
    ig: str | None = None


class IGInfo(BaseModel):
    id: str
    version: str | None = None
    profiles: list[str] = Field(default_factory=list)
    canonical_url: str | None = None


class ProfilesByIGResponse(BaseModel):
    igs: dict[str, list[ProfileInfo]]
