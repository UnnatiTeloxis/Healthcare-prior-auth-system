from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def fhir_health():
    return {"status": "ok", "tool": "fhir-validator"}


@router.post("/validate")
async def validate_resource():
    return {"status": "pending", "message": "Validation endpoint ready for implementation"}
