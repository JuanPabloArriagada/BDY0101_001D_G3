from bson import ObjectId
from backend.database import get_database
from backend.models.evento import Evento
from backend.utils.serializer import serializar_lista, serializar_documento


def listar_eventos():
    return serializar_lista(get_database().eventos.find())


def buscar_evento_por_id(id: str):
    evento = get_database().eventos.find_one({"_id": ObjectId(id)})
    return serializar_documento(evento)


def agregar_evento(evento: Evento):
    documento = evento.model_dump()
    get_database().eventos.insert_one(documento)
    return {"mensaje": "Evento agregado correctamente"}
