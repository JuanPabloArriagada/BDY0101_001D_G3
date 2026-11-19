from fastapi import APIRouter
from backend.services.kpis_service import calcular_kpis

router = APIRouter(prefix="/api/v1", tags=["KPIs"])


@router.get("/kpis")
def obtener_kpis():
    return calcular_kpis()
