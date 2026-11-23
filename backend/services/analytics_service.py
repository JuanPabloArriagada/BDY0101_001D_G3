from datetime import datetime, timezone
from backend.database import get_database


def compras_por_usuario_ciudad(email: str, ciudad: str):
    pipeline = [
        {
            "$match": {
                "estado": "confirmada"
            }
        },
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "_id",
                "as": "detalle_usuario"
            }
        },
        {"$unwind": "$detalle_usuario"},
        {
            "$match": {
                "detalle_usuario.email": email
            }
        },
        {
            "$lookup": {
                "from": "eventos",
                "localField": "evento_id",
                "foreignField": "_id",
                "as": "detalle_evento"
            }
        },
        {"$unwind": "$detalle_evento"},
        {
            "$match": {
                "detalle_evento.recinto.ciudad": ciudad
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$detalle_usuario.email",
                "gasto_total": {
                    "$sum": "$items.subtotal"
                },
                "compras": {
                    "$push": {
                        "evento": "$detalle_evento.nombre",
                        "tipo_ticket": "$items.tipo",
                        "cantidad": "$items.cantidad",
                        "precio_unitario": "$items.precio_unitario",
                        "subtotal": "$items.subtotal"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "usuario": "$_id",
                "ciudad": ciudad,
                "compras": 1,
                "gasto_total": 1
            }
        }
    ]
    return list(get_database().ordenes_compra.aggregate(pipeline))


def reporte_ventas_eventos(umbral: float = 70):
    pipeline = [
        {
            "$project": {
                "nombre": 1,
                "ciudad": "$recinto.ciudad",
                "stock_inicial": {
                    "$sum": "$tickets_disponibles.stock_inicial"
                }
            }
        },
        {
            "$lookup": {
                "from": "ordenes_compra",
                "localField": "_id",
                "foreignField": "evento_id",
                "as": "compras"
            }
        },
        {
            "$unwind": {
                "path": "$compras",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$unwind": {
                "path": "$compras.items",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$group": {
                "_id": {
                    "evento_id": "$_id",
                    "evento": "$nombre",
                    "ciudad": "$ciudad",
                    "stock_inicial": "$stock_inicial"
                },
                "total_recaudado": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$compras.estado", "confirmada"]},
                            "$compras.items.subtotal",
                            0
                        ]
                    }
                },
                "tickets_vendidos": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$compras.estado", "confirmada"]},
                            "$compras.items.cantidad",
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "evento": "$_id.evento",
                "ciudad": "$_id.ciudad",
                "stock_inicial": "$_id.stock_inicial",
                "total_recaudado": 1,
                "tickets_vendidos": 1,
                "porcentaje_venta": {
                    "$cond": [
                        {"$gt": ["$_id.stock_inicial", 0]},
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        "$tickets_vendidos",
                                        "$_id.stock_inicial"
                                    ]
                                },
                                100
                            ]
                        },
                        0
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "evento": 1,
                "ciudad": 1,
                "stock_inicial": 1,
                "total_recaudado": 1,
                "tickets_vendidos": 1,
                "porcentaje_venta": 1,
                "etiqueta": {
                    "$cond": [
                        {"$gte": ["$porcentaje_venta", umbral]},
                        "Exitoso",
                        "Por Mejorar"
                    ]
                }
            }
        }
    ]
    return list(get_database().eventos.aggregate(pipeline))


def eventos_futuros(ciudad: str, precio_maximo: float):
    fecha_actual = datetime.now(timezone.utc)
    pipeline = [
        {
            "$match": {
                "fecha_evento": {"$gt": fecha_actual},
                "recinto.ciudad": ciudad,
                "estado": "programado",
                "activo": True
            }
        },
        {"$unwind": "$tickets_disponibles"},
        {
            "$match": {
                "tickets_disponibles.stock_disponible": {
                    "$gt": 0
                },
                "tickets_disponibles.precio": {
                    "$lt": precio_maximo
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "evento": "$nombre",
                "fecha_evento": 1,
                "ciudad": "$recinto.ciudad",
                "tipo_ticket": "$tickets_disponibles.tipo",
                "precio": "$tickets_disponibles.precio",
                "stock_disponible": "$tickets_disponibles.stock_disponible"
            }
        }
    ]
    return list(get_database().eventos.aggregate(pipeline))


def clientes_frecuentes(minimo: int = 2):
    pipeline = [
        {
            "$match": {
                "rol": "cliente"
            }
        },
        {
            "$lookup": {
                "from": "ordenes_compra",
                "let": {"idUsuario": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$usuario_id", "$$idUsuario"]
                            }
                        }
                    },
                    {
                        "$match": {
                            "estado": "confirmada"
                        }
                    }
                ],
                "as": "compras"
            }
        },
        {
            "$addFields": {
                "cantidad_compras": {
                    "$size": "$compras"
                },
                "total_gastado": {
                    "$sum": "$compras.total"
                }
            }
        },
        {
            "$addFields": {
                "tipo_cliente": {
                    "$cond": [
                        {"$gte": ["$cantidad_compras", minimo]},
                        "Frecuente",
                        "Ocasional"
                    ]
                }
            }
        },
        {
            "$match": {
                "cantidad_compras": {"$gte": minimo}
            }
        },
        {
            "$project": {
                "_id": 0,
                "nombre": 1,
                "email": 1,
                "cantidad_compras": 1,
                "total_gastado": 1,
                "tipo_cliente": 1
            }
        }
    ]
    return list(get_database().usuarios.aggregate(pipeline))
