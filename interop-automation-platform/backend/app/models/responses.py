from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class IssueSeverity(str, Enum):
    fatal = "fatal"
    error = "error"
    warning = "warning"
    information = "information"


class ValidationIssue(BaseModel):
    severity: IssueSeverity
    code: str
    message: str
    location: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


class ValidationResult(BaseModel):
    valid: bool
    resource_type: Optional[str] = None
    profiles: List[str] = []
    issues: List[ValidationIssue] = []
    summary: str = ""
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    operation_outcome: Optional[Dict[str, Any]] = None


class BatchValidationResult(BaseModel):
    results: List[ValidationResult]
    total: int
    valid_count: int
    invalid_count: int


class ProfileInfo(BaseModel):
    url: str
    name: Optional[str] = None
    ig: Optional[str] = None


class IGInfo(BaseModel):
    id: str
    version: str
    profiles: List[str] = []
    canonical_url: Optional[str] = None


class ProfilesByIGResponse(BaseModel):
    igs: Dict[str, List[ProfileInfo]]
