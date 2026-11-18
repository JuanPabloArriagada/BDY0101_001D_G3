from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pymongo.errors import WriteError
from backend.models.usuario import Usuario
from backend.services.usuarios_service import (
    listar_usuarios,
    buscar_usuario_por_id,
    agregar_usuario,
    modificar_usuario,
    desactivar_usuario,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get("/")
def obtener_usuarios():
    return listar_usuarios()


@router.get("/{id}")
def obtener_usuario(id: str):
    try:
        usuario = buscar_usuario_por_id(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.") from None

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return usuario


@router.post("/")
def crear_usuario(usuario: Usuario):
    try:
        return agregar_usuario(usuario)
    except WriteError as error:
        if error.code == 121:
            raise HTTPException(
                status_code=400,
                detail="El usuario no cumple con las reglas de la colección.",
            ) from None
        raise


@router.put("/{id}")
def actualizar_usuario(id: str, usuario: Usuario):
    try:
        encontrado = modificar_usuario(id, usuario)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.") from None
    except WriteError as error:
        if error.code == 121:
            raise HTTPException(
                status_code=400,
                detail="El usuario no cumple con las reglas de la colección.",
            ) from None
        raise

    if not encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return {"mensaje": "Usuario actualizado correctamente"}


@router.delete("/{id}")
def eliminar_usuario(id: str):
    try:
        encontrado = desactivar_usuario(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.") from None

    if not encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return {"mensaje": "Usuario desactivado correctamente"}
