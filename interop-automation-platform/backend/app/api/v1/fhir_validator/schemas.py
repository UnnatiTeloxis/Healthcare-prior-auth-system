from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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


class BatchValidationRequest(BaseModel):
    resources: list[str] = Field(..., description="FHIR resources as JSON or XML strings")
    profiles: list[str] = Field(default_factory=list, description="Profile URLs to validate against")


class LoadIGRequest(BaseModel):
    package_id: str = Field(..., description="NPM package ID, for example hl7.fhir.us.core")
    version: str | None = Field(None, description="Package version, for example 6.1.0")


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
