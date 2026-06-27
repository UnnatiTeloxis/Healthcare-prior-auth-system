from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.v1.fhir_validator.schemas import IGInfo
from app.services.fhir_validator.inferno_client import inferno_client

router = APIRouter()


@router.get("/", response_model=dict[str, Any])
async def list_igs():
    return await inferno_client.get_igs()


@router.put("/{package_id}", response_model=IGInfo)
async def load_ig(package_id: str, version: str | None = None):
    try:
        result = await inferno_client.load_ig_by_id(package_id, version)
        return IGInfo(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load IG {package_id}: {exc}",
        ) from exc


@router.post("/upload", response_model=IGInfo)
async def upload_ig(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith((".tgz", ".tar.gz")):
        raise HTTPException(status_code=400, detail="File must be a .tgz or .tar.gz package")

    try:
        package_data = await file.read()
        result = await inferno_client.upload_custom_ig(package_data)
        return IGInfo(**result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to upload IG: {exc}") from exc


@router.get("/version")
async def get_version():
    return await inferno_client.get_version()
