# Eventify Global

Proyecto de la Evaluación 3 de Bases de Datos No Relacionales (BDY0101).
Utiliza FastAPI, Streamlit y MongoDB Atlas.

## Arquitectura

El flujo de datos es **Streamlit → HTTP → Controllers → Services → MongoDB Atlas**.
Los modelos Pydantic validan los datos recibidos por la API.

- `backend/controllers/`: rutas de usuarios, eventos, analítica y KPIs.
- `backend/services/`: operaciones PyMongo y consultas de agregación.
- `backend/models/`: modelos de usuarios, eventos, órdenes y reseñas.
- `backend/database.py`: configuración y cliente MongoDB compartido.
- `backend/utils/serializer.py`: conversión de ObjectId a texto.
- `backend/main.py`: aplicación FastAPI y registro de routers.
- `frontend/app.py`: navegación, visualizaciones y formularios.
- `scripts/`: respaldo original de la Evaluación 2.

## Configuración del entorno de desarrollo

El entorno local utiliza **Python 3.14.4 de 64 bits**. Las nueve dependencias
están en `requirements.txt`, con comentarios y rangos de versión compatibles
con el entorno utilizado.

### Clonar el repositorio

```bash
git clone https://github.com/JuanPabloArriagada/BDY0101_001D_G3.git
cd BDY0101_001D_G3
```

### Crear y activar el entorno virtual

Crea `.venv` solo si todavía no existe.

**Windows PowerShell:**

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS, con Python 3.14 instalado:**

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Con el entorno activado, instala y comprueba las dependencias:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

Si PowerShell bloquea la activación, utiliza directamente
`.\.venv\Scripts\python.exe` seguido del comando necesario.
Para desactivar el entorno, ejecuta `deactivate`.

### Variables de entorno

Copia `.env.example` a `.env` en la raíz y completa tu propia URI de Atlas:

```ini
MONGO_URI=
MONGO_DB_NAME=eventify_db
API_BASE_URL=http://localhost:8000
```

`MONGO_URI` contiene la cadena completa, incluidas las credenciales.
Cada integrante o la profesora puede usar su propia configuración.
Para operaciones CRUD, el usuario de Atlas necesita permisos `readWrite` sobre
`eventify_db` y la IP del equipo debe estar permitida en Atlas.
Los archivos `.env`, el entorno virtual y las cachés están excluidos de Git.

## Conexión a MongoDB Atlas

`backend/database.py` carga la configuración mediante `pydantic-settings` y
comparte una instancia de `MongoClient`, que reutiliza su pool de conexiones.

- `get_database()`: entrega la referencia a la base.
- `ping_database()`: comprueba la conectividad.
- `close_connection()`: cierra el cliente cuando corresponda.

Con el entorno activado, comprueba la conexión desde la raíz:

```bash
python -c "from backend.database import ping_database, close_connection; print(ping_database()); close_connection()"
```

Streamlit utiliza únicamente HTTP; no crea conexiones directas a MongoDB.

## Ejecutar el proyecto

Desde la raíz, activa `.venv` en dos terminales.

**Terminal 1 — FastAPI:**

```bash
uvicorn backend.main:app --reload
```

**Terminal 2 — Streamlit:**

```bash
streamlit run frontend/app.py
```

- API: [http://localhost:8000](http://localhost:8000).
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs).
- Streamlit: [http://localhost:8501](http://localhost:8501).

En **Inicio**, **Comprobar conexión** consulta `GET /` y muestra el mensaje
devuelto por FastAPI.

## Endpoints CRUD

Ambos CRUD reciben documentos completos conforme a los modelos `Usuario` y
`Evento`. El ID se utiliza en la URL; no se envía en el cuerpo de POST o PUT.

| Operación | Método | Usuarios | Eventos |
|---|---|---|---|
| Listar | GET | `/api/v1/usuarios/` | `/api/v1/eventos/` |
| Consultar por ID | GET | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |
| Crear | POST | `/api/v1/usuarios/` | `/api/v1/eventos/` |
| Actualizar | PUT | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |
| Desactivar | DELETE | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |

POST usa `insert_one()` y MongoDB genera `_id`. PUT utiliza `update_one()` con
`$set` y comprueba `matched_count`; responde correctamente aunque los valores
sean idénticos.

DELETE realiza una **baja lógica**: establece solamente `activo: false`.
Conserva el documento y su historial, y responde correctamente si ya estaba
desactivado. Los GET incluyen registros activos e inactivos.

### Respuestas y errores

- `200`: operación correcta. Las escrituras devuelven un objeto con `mensaje`.
- `400`: ObjectId inválido o documento rechazado por el esquema MongoDB,
  código `121`, en POST o PUT.
- `404`: ID válido cuyo registro no existe.
- `422`: campos o tipos incompatibles con Pydantic, o parámetros obligatorios ausentes.
- `500`: otros errores internos que el backend no maneja específicamente.

Se conservan las reglas originales: roles `cliente` y `administrador`, estados
de eventos permitidos, recinto completo y entradas válidas.
No se añade una restricción de correo único.

## Consultas analíticas

Conservan las cuatro agregaciones de la Evaluación 2. Devuelven listas y
responden `200` con `[]` cuando no hay coincidencias.

| Consulta | Endpoint GET | Parámetros |
|---|---|---|
| Compras por usuario y ciudad | `/api/v1/analytics/compras-por-usuario-ciudad` | `email` y `ciudad`, obligatorios |
| Ventas por evento | `/api/v1/analytics/reporte-ventas-eventos` | Ninguno |
| Disponibilidad futura | `/api/v1/analytics/eventos-futuros` | `ciudad=Santiago`, `precio_maximo=25000` |
| Clientes frecuentes | `/api/v1/analytics/clientes-frecuentes` | Ninguno |

### Consulta 1: compras por usuario y ciudad

Relaciona órdenes confirmadas, usuarios y eventos. Devuelve `usuario`, `ciudad`,
`compras` y `gasto_total`. Las compras incluyen evento, tipo de entrada,
cantidad, precio unitario y subtotal.

En **Analítica**, completa el formulario y pulsa **Consultar compras**.
Se muestran todas las compras, incluidas las repetidas, y la métrica de gasto.
El gráfico **Gasto total por usuario y ciudad** utiliza directamente
`gasto_total`, con la ciudad en el eje X y el usuario como color.
Cada envío consulta un usuario y una ciudad; una coincidencia produce una barra.
El frontend no vuelve a sumar las compras ni realiza solicitudes adicionales.

### Consulta 2: ventas y ocupación por evento

Devuelve `evento`, `ciudad`, `stock_inicial`, `total_recaudado`, `tickets_vendidos`,
`porcentaje_venta` y `etiqueta`. Considera compras confirmadas e incluye eventos
inactivos y sin ventas.

El porcentaje compara entradas vendidas con el stock inicial, no asistencia real.
Con stock cero, el porcentaje es cero. La clasificación es `Exitoso` desde
el 70 % y `Por Mejorar` por debajo. Se conservan porcentajes mayores al 100 %.

**Consultar ventas por evento** muestra la tabla completa y dos gráficos Top 10:
recaudación y porcentaje vendido, ordenados de mayor a menor.
Las etiquetas numeradas distinguen eventos repetidos sin fusionarlos.

### Consulta 3: eventos futuros con disponibilidad

Selecciona eventos posteriores al instante UTC actual, en la ciudad indicada
y con estado `programado`, sin filtrar por `activo`. Cada tipo de entrada se
devuelve si tiene stock mayor que cero y precio **estrictamente menor** al máximo.

**Buscar eventos disponibles** muestra evento, fecha, ciudad, tipo, precio y stock.
La tabla conserva todas las filas y el gráfico muestra una barra por registro.
La fecha solo cambia su primera `T` por un espacio; conserva segundos,
fracciones y zona horaria. También puede consultarse al pasar el cursor por la barra.

### Consulta 4: clientes frecuentes

Selecciona clientes con al menos dos **órdenes confirmadas**, incluidos los
inactivos. Cuenta órdenes con `$size` y suma `compras.total`.
Devuelve nombre, email, cantidad de compras, total gastado y tipo de cliente;
el filtro final conserva la clasificación `Frecuente`.

**Consultar clientes frecuentes** muestra la tabla completa y dos gráficos Top 10:
gasto total y cantidad de compras. Las etiquetas incluyen número, nombre y correo.
Streamlit conserva los valores y clasificaciones entregados por la API.

## Indicadores de negocio (KPIs)

`GET /api/v1/kpis` devuelve tres números calculados en MongoDB:

| Indicador | Cálculo | Justificación |
|---|---|---|
| `recaudacion_total` | Suma de `total` de órdenes confirmadas. | Mide el volumen de ventas confirmado. |
| `gasto_promedio_orden` | Promedio de `total` de esas órdenes. | Permite conocer el gasto habitual por compra. |
| `calificacion_promedio` | Promedio de `puntuacion` de las reseñas. | Resume la satisfacción de los asistentes. |

Una agregación obtiene recaudación y gasto promedio; otra calcula la calificación.
Los promedios se redondean a dos decimales. Los indicadores sin datos devuelven cero.

**Dashboard** los presenta con `st.metric()`. Los importes utilizan CLP sin
decimales y con puntos de miles. La calificación muestra dos decimales, coma y `/ 5`.

## Panel administrativo CRUD

En **Administración**, elige **Usuarios** o **Eventos** y una operación:
**Listar**, **Crear**, **Editar** o **Desactivar**.

- **Listar:** incluye IDs y registros inactivos. **Actualizar listado** renueva los datos.
- **Crear:** muestra un formulario con todos los campos del modelo.
- **Editar:** selecciona por `_id` y precarga el documento completo.
- **Desactivar:** requiere confirmación; un registro ya inactivo no envía otro DELETE.

Los usuarios incluyen nombre, correo, rol, activo, nacimiento y registro.
Los eventos incluyen descripción, fecha y hora, estado, activo, recinto y entradas.

El recinto contiene nombre, ciudad, dirección y capacidad. El editor permite
añadir entradas durante la creación y mantiene filas fijas al editar, conservando
General, VIP y otros tipos al cambiar precios o stocks.

Las fechas sin cambios conservan su cadena ISO completa. Al modificar solo la
fecha de un usuario, se preservan su hora y zona. Las fechas nuevas de eventos
se interpretan en UTC; las existentes conservan su zona sin conversiones silenciosas.

Los formularios comprueban campos obligatorios, correo, fechas y entradas.
La capacidad es positiva y los precios y stocks no negativos; los stocks son enteros.
Las escrituras se envían únicamente al confirmar el formulario.

`consultar_api()` realiza GET y `enviar_api()` agrupa POST, PUT y DELETE.
Ambas utilizan timeout de cinco segundos. Las escrituras no se reintentan
automáticamente. Una respuesta fallida no muestra éxito ni datos ficticios.
El último mensaje confirmado permanece al volver al listado.

**Crear, guardar o desactivar modifica la base configurada.**
Revisa los datos antes de confirmar. Ante un error de red, consulta el listado
antes de repetir, porque la operación podría haberse aplicado.

## Base de datos de la Evaluación 2

[G3_Arriagada_Gonzales_001D.mongodb.js](scripts/G3_Arriagada_Gonzales_001D.mongodb.js)
se conserva íntegro. Define `eventify_db`, sus cuatro colecciones, validaciones
`$jsonSchema`, datos de prueba y consultas originales.

**Advertencia: contiene `db.dropDatabase()`. Ejecutarlo elimina las colecciones
y datos existentes de `eventify_db` antes de recrearlos. No forma parte del
inicio de la aplicación.**

## Estado de las comprobaciones

La **tarea #32 permanece pendiente y suspendida**. No es un requisito para
continuar y esta simplificación no completa su batería de pruebas.

Las comprobaciones básicas utilizan solicitudes interceptadas para escrituras
y exclusivamente lecturas en la integración real.

**Comprobación básica (20-11-2026):** se verificaron la importación de FastAPI,
sus 16 operaciones, las cuatro secciones de Streamlit, los tres KPIs y las
cuatro visualizaciones. Consulta 1 utiliza el total recibido de la API.
Las escrituras administrativas fueron interceptadas; se conservaron fechas,
varios tipos de entrada y la confirmación de desactivación.

La API y Swagger iniciaron correctamente. La lectura real de Atlas quedó
pendiente por `ReadTimeout`; un ping acotado devolvió
`ServerSelectionTimeoutError`. No se modificaron credenciales ni datos.
