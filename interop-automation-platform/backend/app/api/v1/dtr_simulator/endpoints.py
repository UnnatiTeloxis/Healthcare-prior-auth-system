from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def dtr_health():
    return {"status": "ok", "tool": "dtr-simulator"}


@router.get("/questionnaires")
async def list_questionnaires():
    return {"status": "ok", "questionnaires": []}
