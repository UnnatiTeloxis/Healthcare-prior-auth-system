from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.fhir_validator.test_case_catalog import (
    folder_for_package,
    list_catalog,
    read_sample,
    test_cases_root,
)

router = APIRouter()


@router.get("/catalog")
async def get_test_case_catalog() -> dict[str, Any]:
    """List test-case samples for all popular IGs."""
    catalog = list_catalog()
    return {
        "success": True,
        "root": str(test_cases_root()),
        "count": len(catalog),
        "igs": catalog,
    }


@router.get("/by-ig/{package_id}")
async def get_test_cases_for_ig(package_id: str) -> dict[str, Any]:
    folder = folder_for_package(package_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"No test cases mapped for {package_id}")
    for entry in list_catalog():
        if entry["package_id"] == package_id:
            return {"success": True, **entry}
    raise HTTPException(status_code=404, detail=f"Test cases not found for {package_id}")


@router.get("/content")
async def get_test_case_content(path: str = Query(..., description="Relative path: folder/tier/file.json")):
    try:
        content = read_sample(path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "success": True,
        "path": path,
        "content": content,
    }
