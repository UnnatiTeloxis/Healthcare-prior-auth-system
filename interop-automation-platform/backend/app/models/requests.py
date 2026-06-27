from pydantic import BaseModel, Field
from typing import List, Optional


class ValidationRequest(BaseModel):
    resource: str = Field(..., description="FHIR resource as JSON or XML string")
    profiles: List[str] = Field(default=[], description="List of profile URLs to validate against")
    resource_type: Optional[str] = Field(None, description="FHIR resource type (auto-detected if not provided)")


class BatchValidationRequest(BaseModel):
    resources: List[str] = Field(..., description="List of FHIR resources as JSON or XML strings")
    profiles: List[str] = Field(default=[], description="List of profile URLs to validate against")


class LoadIGRequest(BaseModel):
    package_id: str = Field(..., description="NPM package ID (e.g., hl7.fhir.us.core)")
    version: Optional[str] = Field(None, description="Package version (e.g., 6.1.0)")
