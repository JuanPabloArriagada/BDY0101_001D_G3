from backend.database import get_database


def calcular_kpis():
    db = get_database()
    pipeline_compras = [
        {"$match": {"estado": "confirmada"}},
        {
            "$group": {
                "_id": None,
                "recaudacion_total": {"$sum": "$total"},
                "gasto_promedio_orden": {"$avg": "$total"}
            }
        }
    ]
    compras = list(db.ordenes_compra.aggregate(pipeline_compras))

    pipeline_resenas = [
        {
            "$group": {
                "_id": None,
                "calificacion_promedio": {"$avg": "$puntuacion"}
            }
        }
    ]
    resenas = list(db.resenas_evaluaciones.aggregate(pipeline_resenas))

    recaudacion_total = compras[0]["recaudacion_total"] if compras else 0
    gasto_promedio_orden = compras[0]["gasto_promedio_orden"] if compras else 0
    calificacion_promedio = resenas[0]["calificacion_promedio"] if resenas else 0

    return {
        "recaudacion_total": recaudacion_total,
        "gasto_promedio_orden": round(gasto_promedio_orden, 2),
        "calificacion_promedio": round(calificacion_promedio, 2)
    }
