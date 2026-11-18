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
