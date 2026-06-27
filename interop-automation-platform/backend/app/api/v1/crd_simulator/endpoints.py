from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def crd_health():
    return {"status": "ok", "tool": "crd-simulator"}


@router.post("/hooks/{hook_name}")
async def invoke_hook(hook_name: str):
    return {"status": "pending", "hook": hook_name, "cards": []}
