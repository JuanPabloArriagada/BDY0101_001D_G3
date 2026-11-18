from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pymongo.errors import WriteError
from backend.models.evento import Evento
from backend.services.eventos_service import listar_eventos, buscar_evento_por_id, agregar_evento

router = APIRouter(prefix="/api/v1/eventos", tags=["Eventos"])


@router.get("/")
def obtener_eventos():
    return listar_eventos()


@router.get("/{id}")
def obtener_evento(id: str):
    try:
        evento = buscar_evento_por_id(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de evento no válido.") from None

    if evento is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")

    return evento


@router.post("/")
def crear_evento(evento: Evento):
    try:
        return agregar_evento(evento)
    except WriteError as error:
        if error.code == 121:
            raise HTTPException(
                status_code=400,
                detail="El evento no cumple con las reglas de la colección.",
            ) from None
        raise
