from datetime import datetime
from pydantic import BaseModel


class Usuario(BaseModel):
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_nacimiento: datetime
    fecha_registro: datetime
