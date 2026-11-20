use("eventify_db");
// dropdatabase lo estoy usando para que el archivo se pueda ejecutar todo de una sola vez
db.dropDatabase();

//colecciones
use("eventify_db");
db.createCollection("usuarios",
    {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: [
                    "nombre",
                    "email",
                    "rol",
                    "activo",
                    "fecha_nacimiento",
                    "fecha_registro"
                ],
                properties: {
                    _id: {
                        bsonType: "objectId"
                    },
                    nombre: {
                        bsonType: "string",
                        minLength: 1,
                        description: "El nombre del usuario es obligatorio"
                    },
                    email: {
                        bsonType: "string",
                        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        description: "Debe ser correo valido"
                    },
                    rol: {
                        bsonType: "string",
                        enum: ["cliente", "administrador"]
                    },
                    activo: {
                        bsonType: "bool",
                    },
                    fecha_nacimiento: {
                        bsonType: "date",
                    },
                    fecha_registro: {
                        bsonType: "date",
                    }
                }
            }
        },
        validationAction: "error",
        validationLevel: "strict"
    }
);

// colecion eventos
use('eventify_db');
db.createCollection("eventos", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [
                "nombre",
                "descripcion",
                "fecha_evento",
                "estado",
                "activo",
                "recinto",
                "tickets_disponibles"
            ],
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                nombre: {
                    bsonType: "string",
                },
                descripcion: {
                    bsonType: "string"
                },
                fecha_evento: {
                    bsonType: "date"
                },
                estado: {
                    bsonType: "string",
                    enum: [
                        "programado",
                        "agotado",
                        "finalizado",
                        "cancelado"
                    ]
                },
                activo: {
                    bsonType: "bool"
                },
                // embebido
                recinto: {
                    bsonType: "object",
                    required: [
                        "nombre",
                        "ciudad",
                        "direccion",
                        "capacidad"
                    ],
                    properties: {
                        nombre: {
                            bsonType: "string"
                        },
                        ciudad: {
                            bsonType: "string"
                        },
                        direccion: {
                            bsonType: "string"
                        },
                        capacidad: {
                            bsonType: "int",
                            minimum: 1
                        }
                    }
                },
                tickets_disponibles: {
                    bsonType: "array",
                    minItems: 1,
                    items: {
                        bsonType: "object",
                        required: [
                            "tipo",
                            "precio",
                            "stock_inicial",
                            "stock_disponible"
                        ],
                        properties: {
                            tipo: {
                                bsonType: "string"
                            },
                            precio: {
                                bsonType: "number",
                                minimum: 0
                            },
                            stock_inicial: {
                                bsonType: "int",
                                minimum: 0
                            },
                            stock_disponible: {
                                bsonType: "int",
                                minimum: 0
                            }
                        }
                    }
                }
            }
        }
    },
    validationLevel: "strict",
    validationAction: "error"
});

// orden de compra
use('eventify_db');
db.createCollection("ordenes_compra", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [
                "usuario_id",
                "evento_id",
                "items",
                "total",
                "estado",
                "fecha_compra"
            ],
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                // Rusuario que realiza la compra
                usuario_id: {
                    bsonType: "objectId"
                },
                // evento para el cual se realiza la compra
                evento_id: {
                    bsonType: "objectId"
                },
                // lista de tickets comprados
                items: {
                    bsonType: "array",
                    minItems: 1,
                    items: {
                        bsonType: "object",
                        required: [
                            "tipo",
                            "cantidad",
                            "precio_unitario",
                            "subtotal"
                        ],
                        properties: {
                            tipo: {
                                bsonType: "string"
                            },
                            cantidad: {
                                bsonType: "int",
                                minimum: 1
                            },
                            precio_unitario: {
                                bsonType: "number",
                                minimum: 0
                            },
                            subtotal: {
                                bsonType: "number",
                                minimum: 0
                            }
                        }
                    }
                },
                total: {
                    bsonType: "number",
                    minimum: 0
                },
                estado: {
                    bsonType: "string",
                    enum: [
                        "pendiente",
                        "confirmada",
                        "cancelada"
                    ]
                },
                fecha_compra: {
                    bsonType: "date"
                }
            }
        }
    },
    validationLevel: "strict",
    validationAction: "error"
});

// reserva y evaluacion
use('eventify_db');
db.createCollection("resenas_evaluaciones", {
    validator: {
        $jsonSchema: {
            bsonType: "object",

            required: [
                "usuario_id",
                "evento_id",
                "puntuacion",
                "comentario",
                "asistencia_confirmada",
                "fecha_resena"
            ],
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                // usuario que realiza la reseña
                usuario_id: {
                    bsonType: "objectId"
                },
                // evento al que se refiere la reseña
                evento_id: {
                    bsonType: "objectId"
                },
                puntuacion: {
                    bsonType: "int",
                    minimum: 1,
                    maximum: 5
                },
                comentario: {
                    bsonType: "string",
                    minLength: 3
                },
                asistencia_confirmada: {
                    bsonType: "bool"
                },
                fecha_resena: {
                    bsonType: "date"
                }
            }
        }
    },
    validationLevel: "strict",
    validationAction: "error"
});



// insertar 50 documentos a cada coleccion (se lo pedi a chatgpt)
use("eventify_db");

{
    // Datos de prueba
    const nombres = [
        "Camila", "Matías", "Sofía", "Diego", "Valentina",
        "Felipe", "Catalina", "Javier", "Antonia", "Tomás"
    ];

    const apellidos = [
        "Rojas", "González", "Morales", "Silva", "Pérez"
    ];

    const ciudades = [
        "Santiago", "Valparaíso", "Concepción",
        "La Serena", "Temuco"
    ];

    const tiposEvento = [
        "Concierto", "Festival", "Teatro",
        "Conferencia", "Show cultural"
    ];

    const comentarios = [
        "Muy buena organización del evento.",
        "Lo pasé muy bien, excelente ambiente.",
        "Buena experiencia y atención del personal.",
        "El espectáculo cumplió mis expectativas.",
        "Recomendaría este evento a otras personas."
    ];

    const usuarios = [];
    const eventos = [];
    const ordenes = [];
    const resenas = [];

    // 1. INSERTAR 50 USUARIOS

    for (let i = 0; i < 50; i++) {
        usuarios.push({
            nombre: nombres[i % 10] + " " +
                apellidos[Math.floor(i / 10)],

            email: "usuario" + (i + 1) + "@eventify.cl",

            rol: i < 45 ? "cliente" : "administrador",

            activo: true,

            fecha_nacimiento: new Date(
                1990 + (i % 15),
                i % 12,
                (i % 28) + 1
            ),

            fecha_registro: new Date(
                2025, 0, (i % 28) + 1
            )
        });
    }

    db.usuarios.insertMany(usuarios);


    // 2. INSERTAR 50 EVENTOS

    for (let i = 0; i < 50; i++) {

        const ciudad = ciudades[i % 5];

        const precioGeneral = 15000 + (i % 5) * 5000;

        const stockGeneral =
            i < 10 && i % 2 === 0 ? 16 : 40;

        const disponibleGeneral =
            i < 10 ? stockGeneral - 15 : stockGeneral;

        const stockVip = i % 2 === 0 ? 2 : 10;

        eventos.push({
            nombre: tiposEvento[i % 5] +
                " Eventify " + (i + 1),

            descripcion: "Evento cultural realizado en " +
                ciudad,

            fecha_evento: i < 20
                ? new Date(
                    2026, i % 8, 10 + (i % 15), 20
                )
                : new Date(
                    2027, i % 12, 10 + (i % 15), 20
                ),

            estado: i < 20 ? "finalizado" : "programado",

            activo: i >= 20,

            recinto: {
                nombre: "Centro de Eventos " + ciudad,
                ciudad: ciudad,
                direccion: "Avenida Principal " + (100 + i),
                capacidad: NumberInt(
                    150 + (i % 5) * 50
                )
            },

            tickets_disponibles: [
                {
                    tipo: "General",
                    precio: precioGeneral,
                    stock_inicial: NumberInt(stockGeneral),
                    stock_disponible: NumberInt(
                        disponibleGeneral
                    )
                },
                {
                    tipo: "VIP",
                    precio: precioGeneral + 20000,
                    stock_inicial: NumberInt(stockVip),
                    stock_disponible: NumberInt(stockVip)
                }
            ]
        });
    }

    db.eventos.insertMany(eventos);


    // 3. INSERTAR 50 ÓRDENES DE COMPRA
    // 4. PREPARAR 50 RESEÑAS

    for (let i = 0; i < 50; i++) {

        const indiceEvento = Math.floor(i / 5);

        const usuario = db.usuarios.findOne({
            email: usuarios[i % 45].email
        });

        const evento = db.eventos.findOne({
            nombre: eventos[indiceEvento].nombre
        });

        const precio =
            eventos[indiceEvento].tickets_disponibles[0].precio;

        // Orden de compra
        ordenes.push({
            usuario_id: usuario._id,
            evento_id: evento._id,

            items: [
                {
                    tipo: "General",
                    cantidad: NumberInt(3),
                    precio_unitario: precio,
                    subtotal: precio * 3
                }
            ],

            total: precio * 3,
            estado: "confirmada",

            fecha_compra: new Date(
                2025, 10, (i % 28) + 1
            )
        });

        // Reseña de evento finalizado
        resenas.push({
            usuario_id: usuario._id,
            evento_id: evento._id,

            puntuacion: NumberInt(3 + (i % 3)),

            comentario: comentarios[i % 5],

            asistencia_confirmada: true,

            fecha_resena: new Date(
                2026, 8, (i % 28) + 1
            )
        });
    }

    db.ordenes_compra.insertMany(ordenes);

    db.resenas_evaluaciones.insertMany(resenas);

    print(
        "Carga terminada: 50 usuarios, " +
        "50 eventos, 50 órdenes y 50 reseñas."
    );
}


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