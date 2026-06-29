from fastapi import APIRouter

from app.api.v1.crd_simulator.endpoints import router as crd_router
from app.api.v1.dtr_simulator.endpoints import router as dtr_router
from app.api.v1.fhir_validator.endpoints import router as fhir_router
from app.api.v1.fhir_validator.igs import router as igs_router

router = APIRouter()

router.include_router(fhir_router, prefix="/fhir", tags=["FHIR Validator"])
router.include_router(fhir_router, prefix="/validate", tags=["FHIR Validator"])
router.include_router(igs_router, prefix="/igs", tags=["FHIR Implementation Guides"])
router.include_router(crd_router, prefix="/crd", tags=["CRD Simulator"])
router.include_router(dtr_router, prefix="/dtr", tags=["DTR Simulator"])


@router.get("/health")
async def api_health():
    return {"status": "ok", "version": "1.0.0"}
