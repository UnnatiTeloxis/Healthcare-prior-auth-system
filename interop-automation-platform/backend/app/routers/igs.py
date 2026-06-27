from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.requests import LoadIGRequest
from app.models.responses import IGInfo
from app.services.inferno_client import inferno_client
from typing import Dict, Any

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def list_igs():
    """
    List all loaded Implementation Guides.
    """
    try:
        igs = await inferno_client.get_igs()
        return igs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{package_id}", response_model=IGInfo)
async def load_ig(package_id: str, version: str = None):
    """
    Load an Implementation Guide by NPM package ID.
    """
    try:
        result = await inferno_client.load_ig_by_id(package_id, version)
        return IGInfo(**result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load IG {package_id}: {str(e)}"
        )


@router.post("/upload", response_model=IGInfo)
async def upload_ig(file: UploadFile = File(...)):
    """
    Upload a custom Implementation Guide package.tgz file.
    """
    if not file.filename.endswith('.tgz') and not file.filename.endswith('.tar.gz'):
        raise HTTPException(
            status_code=400,
            detail="File must be a .tgz or .tar.gz package"
        )
    
    try:
        package_data = await file.read()
        result = await inferno_client.upload_custom_ig(package_data)
        return IGInfo(**result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to upload IG: {str(e)}"
        )


@router.get("/version")
async def get_version():
    """
    Get validator service version information.
    """
    try:
        version_info = await inferno_client.get_version()
        return version_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
