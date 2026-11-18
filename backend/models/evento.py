from datetime import datetime
from pydantic import BaseModel


class Recinto(BaseModel):
    nombre: str
    ciudad: str
    direccion: str
    capacidad: int


class TicketDisponible(BaseModel):
    tipo: str
    precio: float
    stock_inicial: int
    stock_disponible: int


class Evento(BaseModel):
    nombre: str
    descripcion: str
    fecha_evento: datetime
    estado: str
    activo: bool
    recinto: Recinto
    tickets_disponibles: list[TicketDisponible]
