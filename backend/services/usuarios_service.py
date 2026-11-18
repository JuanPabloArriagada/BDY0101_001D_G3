from bson import ObjectId
from backend.database import get_database
from backend.models.usuario import Usuario
from backend.utils.serializer import serializar_lista, serializar_documento


def listar_usuarios():
    return serializar_lista(get_database().usuarios.find())


def buscar_usuario_por_id(id: str):
    usuario = get_database().usuarios.find_one({"_id": ObjectId(id)})
    return serializar_documento(usuario)


def agregar_usuario(usuario: Usuario):
    documento = usuario.model_dump()
    get_database().usuarios.insert_one(documento)
    return {"mensaje": "Usuario agregado correctamente"}


def modificar_usuario(id: str, usuario: Usuario):
    resultado = get_database().usuarios.update_one(
        {"_id": ObjectId(id)},
        {"$set": usuario.model_dump()},
    )
    return resultado.matched_count > 0


def desactivar_usuario(id: str):
    resultado = get_database().usuarios.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"activo": False}},
    )
    return resultado.matched_count > 0
