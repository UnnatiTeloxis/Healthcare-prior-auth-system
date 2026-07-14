from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.v1.fhir_validator.schemas import IGInfo
from app.services.fhir_validator.ig_manager import ig_manager
from app.services.fhir_validator.inferno_client import inferno_client

router = APIRouter()


class LoadIGRequest(BaseModel):
    package_name: str
    version: str | None = None


@router.get("/", response_model=dict[str, Any])
async def list_igs():
    return await inferno_client.get_igs()


@router.get("/available")
async def list_available_igs():
    """
    Ultra-fast endpoint: returns metadata for all local .tgz packages.
    Only reads package.json from each archive (no full extraction).
    Used by the frontend IG dropdown.
    """
    try:
        igs = ig_manager.list_available_igs()
        return {
            "success": True,
            "igs": igs,
            "count": len(igs),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/load")
async def load_ig_on_demand(request: LoadIGRequest):
    """
    Load a specific IG into the Inferno validator on demand.
    First load takes ~500-2000ms (uploading .tgz to Inferno).
    Subsequent requests return cached result in <10ms.
    """
    try:
        result = await ig_manager.load_ig(request.package_name, request.version)
        return {
            "success": True,
            "ig": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load IG {request.package_name}: {exc}",
        ) from exc


@router.get("/loaded")
async def list_loaded_igs():
    """Return list of IGs currently loaded in the validator."""
    return {
        "success": True,
        "igs": ig_manager.get_loaded_igs(),
        "count": len(ig_manager.get_loaded_igs()),
    }


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
