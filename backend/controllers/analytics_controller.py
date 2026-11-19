from fastapi import APIRouter
from backend.services.analytics_service import compras_por_usuario_ciudad, reporte_ventas_eventos

router = APIRouter(prefix="/api/v1/analytics", tags=["Analítica"])


@router.get("/compras-por-usuario-ciudad")
def obtener_compras_por_usuario_ciudad(email: str, ciudad: str):
    return compras_por_usuario_ciudad(email, ciudad)


@router.get("/reporte-ventas-eventos")
def obtener_reporte_ventas_eventos():
    return reporte_ventas_eventos()
