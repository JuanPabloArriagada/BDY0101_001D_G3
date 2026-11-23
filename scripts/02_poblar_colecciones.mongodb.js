// 02. Poblar las cuatro colecciones con los datos de prueba originales.
// Ejecutar una sola vez, despues de 01_colecciones.mongodb.js.
// Repetir este archivo vuelve a insertar los datos de prueba.

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


