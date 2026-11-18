from datetime import datetime
from pydantic import BaseModel


class Resena(BaseModel):
    usuario_id: str
    evento_id: str
    puntuacion: int
    comentario: str
    asistencia_confirmada: bool
    fecha_resena: datetime
