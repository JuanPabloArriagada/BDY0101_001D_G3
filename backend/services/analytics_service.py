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


def reporte_ventas_eventos():
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
                        {"$gte": ["$porcentaje_venta", 70]},
                        "Exitoso",
                        "Por Mejorar"
                    ]
                }
            }
        }
    ]
    return list(get_database().eventos.aggregate(pipeline))
