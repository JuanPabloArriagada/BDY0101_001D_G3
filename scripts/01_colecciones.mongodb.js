// 01. Crear las cuatro colecciones y sus validaciones.
// ADVERTENCIA: db.dropDatabase() elimina todos los datos existentes de eventify_db.
// Ejecutar antes de 02_poblar_colecciones.mongodb.js.

use("eventify_db");
// dropdatabase lo estoy usando para que el archivo se pueda ejecutar todo de una sola vez
//db.dropDatabase();

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



