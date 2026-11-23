// 03. Consultas de lectura y cuatro agregaciones de la Evaluacion 2.
// Ejecutar despues de crear y poblar las colecciones.

// toca revisar los insert 
use('eventify_db');
db.usuarios.find()

use('eventify_db');
db.eventos.find()

use('eventify_db');
db.ordenes_compra.find()

use('eventify_db');
db.resenas_evaluaciones.find()




// Consulta 1
use("eventify_db");
db.ordenes_compra.aggregate([
    {
        $match: {
            estado: "confirmada"
        }
    },
    {
        $lookup: {
            from: "usuarios",
            localField: "usuario_id",
            foreignField: "_id",
            as: "detalle_usuario"
        }
    },
    {
        $unwind: "$detalle_usuario"
    },
    {
        $match: {
            "detalle_usuario.email": "usuario1@eventify.cl"
        }
    },
    {
        $lookup: {
            from: "eventos",
            localField: "evento_id",
            foreignField: "_id",
            as: "detalle_evento"
        }
    },
    {
        $unwind: "$detalle_evento"
    },
    {
        $match: {
            "detalle_evento.recinto.ciudad": "Santiago"
        }
    },
    {
        $unwind: "$items"
    },
    {
        $group: {
            _id: "$detalle_usuario.email",
            gasto_total: {
                $sum: "$items.subtotal"
            },
            compras: {
                $push: {
                    evento: "$detalle_evento.nombre",
                    tipo_ticket: "$items.tipo",
                    cantidad: "$items.cantidad",
                    precio_unitario: "$items.precio_unitario",
                    subtotal: "$items.subtotal"
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            usuario: "$_id",
            ciudad: "Santiago",
            compras: 1,
            gasto_total: 1
        }
    }
]);

// Consulta 2
use("eventify_db");
db.eventos.aggregate([
    {
        $project: {
            nombre: 1,
            ciudad: "$recinto.ciudad",
            stock_inicial: {
                $sum: "$tickets_disponibles.stock_inicial"
            }
        }
    },
    {
        $lookup: {
            from: "ordenes_compra",
            localField: "_id",
            foreignField: "evento_id",
            as: "compras"
        }
    },
    {
        $unwind: {
            path: "$compras",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $unwind: {
            path: "$compras.items",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group: {
            _id: {
                evento_id: "$_id",
                evento: "$nombre",
                ciudad: "$ciudad",
                stock_inicial: "$stock_inicial"
            },
            total_recaudado: {
                $sum: {
                    $cond: [
                        { $eq: ["$compras.estado", "confirmada"] },
                        "$compras.items.subtotal",
                        0
                    ]
                }
            },
            tickets_vendidos: {
                $sum: {
                    $cond: [
                        { $eq: ["$compras.estado", "confirmada"] },
                        "$compras.items.cantidad",
                        0
                    ]
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            evento: "$_id.evento",
            ciudad: "$_id.ciudad",
            stock_inicial: "$_id.stock_inicial",
            total_recaudado: 1,
            tickets_vendidos: 1,
            porcentaje_venta: {
                $cond: [
                    { $gt: ["$_id.stock_inicial", 0] },
                    {
                        $multiply: [
                            {
                                $divide: [
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
        $project: {
            _id: 0,
            evento: 1,
            ciudad: 1,
            stock_inicial: 1,
            total_recaudado: 1,
            tickets_vendidos: 1,
            porcentaje_venta: 1,
            etiqueta: {
                $cond: [
                    { $gte: ["$porcentaje_venta", 70] },
                    "Exitoso",
                    "Por Mejorar"
                ]
            }
        }
    }
]);

// Consulta 3
use("eventify_db");
db.eventos.aggregate([
    {
        $match: {
            fecha_evento: { $gt: new Date() },
            "recinto.ciudad": "Santiago",
            estado: "programado"
        }
    },
    {
        $unwind: "$tickets_disponibles"
    },
    {
        $match: {
            "tickets_disponibles.stock_disponible": {
                $gt: 0
            },
            "tickets_disponibles.precio": {
                $lt: 25000
            }
        }
    },
    {
        $project: {
            _id: 0,
            evento: "$nombre",
            fecha_evento: 1,
            ciudad: "$recinto.ciudad",
            tipo_ticket: "$tickets_disponibles.tipo",
            precio: "$tickets_disponibles.precio",
            stock_disponible:
                "$tickets_disponibles.stock_disponible"
        }
    }
]);



// Consulta 4: Identificar clientes frecuentes
use("eventify_db");
db.usuarios.aggregate([
    {
        $match: {
            rol: "cliente"
        }
    },
    {
        $lookup: {
            from: "ordenes_compra",
            let: { idUsuario: "$_id" },
            pipeline: [
                {
                    $match: {
                        $expr: {
                            $eq: ["$usuario_id", "$$idUsuario"]
                        }
                    }
                },
                {
                    $match: {
                        estado: "confirmada"
                    }
                }
            ],
            as: "compras"
        }
    },
    {
        $addFields: {
            cantidad_compras: {
                $size: "$compras"
            },
            total_gastado: {
                $sum: "$compras.total"
            }
        }
    },
    {
        $addFields: {
            tipo_cliente: {
                $cond: [
                    { $gte: ["$cantidad_compras", 2] },
                    "Frecuente",
                    "Ocasional"
                ]
            }
        }
    },
    {
        $match: {
            cantidad_compras: { $gte: 2 }
        }
    },
    {
        $project: {
            _id: 0,
            nombre: 1,
            email: 1,
            cantidad_compras: 1,
            total_gastado: 1,
            tipo_cliente: 1
        }
    }
]);