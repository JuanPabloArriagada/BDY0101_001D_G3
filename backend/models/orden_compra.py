from datetime import datetime
from pydantic import BaseModel


class ItemCompra(BaseModel):
    tipo: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class OrdenCompra(BaseModel):
    usuario_id: str
    evento_id: str
    items: list[ItemCompra]
    total: float
    estado: str
    fecha_compra: datetime
