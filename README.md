# Eventify Global

Proyecto de la Evaluación 3 de Bases de Datos No Relacionales (BDY0101).

## Configuración del entorno de desarrollo

Requisito: Python 3.14.x de 64 bits con los módulos `venv` y `pip` disponibles.
El intérprete local utilizado para preparar el entorno es Python 3.14.4.

### Clonar el repositorio

```bash
git clone https://github.com/JuanPabloArriagada/BDY0101_001D_G3.git
cd BDY0101_001D_G3
```

Si ya tienes el repositorio, abre una terminal en su carpeta raíz.

### Crear y activar el entorno en Windows PowerShell

Comprueba que `python` corresponde a Python 3.14.x. Crea `.venv` solo si todavía
no existe y actívalo:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si `python` no está disponible o apunta a Microsoft Store, utiliza la ruta del
intérprete instalado para crear el entorno, por ejemplo:

```powershell
& 'C:\ruta\a\Python\python.exe' -m venv .venv
```

Si PowerShell bloquea la activación, puedes instalar las dependencias y
comprobarlas usando directamente el intérprete del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

### Crear y activar el entorno en Linux/macOS

Con Python 3.14 instalado, crea `.venv` solo si todavía no existe y actívalo:

```bash
python3.14 --version
python3.14 -m venv .venv
source .venv/bin/activate
```

### Instalar y verificar las dependencias

Con el entorno activado, los comandos son los mismos en ambos sistemas:

```bash
python --version
python -m pip install -r requirements.txt
python -m pip check
python -c "import fastapi, uvicorn, pymongo, pydantic_settings, streamlit, requests, plotly, pandas, dotenv; print('Importaciones correctas')"
```

`requirements.txt` contiene las nueve dependencias del proyecto con comentarios
sobre su propósito. Sus rangos permiten actualizaciones de corrección dentro de
la misma versión menor; `pip` resuelve e instala las dependencias indirectas.

### Desactivar el entorno virtual

```bash
deactivate
```

El entorno `.venv/` se recrea localmente y está excluido de Git, junto con las
cachés, los archivos `.env` y `.streamlit/secrets.toml`. `.env.example` puede
versionarse como plantilla sin credenciales.

Referencia: [documentación oficial de venv](https://docs.python.org/3.14/library/venv.html).

## Base de datos de la Evaluación 2

El archivo [G3_Arriagada_Gonzales_001D.mongodb.js](scripts/G3_Arriagada_Gonzales_001D.mongodb.js)
conserva íntegramente el script original de la Evaluación 2 como respaldo y
punto de partida para la futura integración con FastAPI.

**Advertencia: el script contiene `db.dropDatabase()` después de seleccionar
`eventify_db`. Al ejecutarlo, elimina todas las colecciones y los datos existentes
de esa base antes de volver a crear las colecciones y cargar los datos de prueba.**

El script inicializa `eventify_db` y crea las colecciones `usuarios`, `eventos`,
`ordenes_compra` y `resenas_evaluaciones`. Cada colección utiliza validaciones
estrictas mediante `$jsonSchema`, con campos obligatorios, tipos BSON y
restricciones de valores. Combina documentos embebidos para recintos y tickets
con referencias entre usuarios, eventos, órdenes y reseñas.

Genera e inserta 50 documentos de prueba por colección (200 en total) e incluye
consultas `find()` para revisar la carga. Sus cuatro consultas de agregación son:

- Compras confirmadas de `usuario1@eventify.cl` para eventos en Santiago, con
  detalle de tickets y gasto total.
- Recaudación, tickets vendidos y porcentaje de venta por evento, con la etiqueta
  `Exitoso` cuando las ventas alcanzan al menos el 70 % del stock inicial.
- Eventos futuros programados en Santiago con tickets disponibles de precio
  inferior a 25000.
- Clientes frecuentes con al menos dos compras confirmadas y su gasto acumulado.

El archivo se incorpora como referencia, sin ejecutarlo ni realizar operaciones
sobre MongoDB.

## Conexión a MongoDB Atlas

La configuración local se guarda en el `.env` de la raíz:

```ini
MONGO_URI=
MONGO_DB_NAME=eventify_db
API_BASE_URL=http://localhost:8000
```

`backend/database.py` lee las variables de MongoDB con `pydantic-settings` y
comparte un único cliente de PyMongo entre los servicios. `API_BASE_URL` indica
la dirección del backend para el frontend.

Cada integrante o la profesora debe completar `MONGO_URI` con su propia URI de
Atlas, que incluye las credenciales. Para las operaciones CRUD, el usuario de
MongoDB necesita permisos `readWrite` sobre `eventify_db` y su IP debe estar
permitida en Atlas. No publiques el `.env`.

`get_database()` devuelve la base, `ping_database()` comprueba la conexión y
`close_connection()` cierra el cliente al terminar la aplicación. Los errores
de configuración y del ping no muestran la cadena de conexión.

Desde la raíz, con `.venv` activado, puedes comprobar el ping con:

```bash
python -c "from backend.database import ping_database, close_connection; print(ping_database()); close_connection()"
```

La verificación real de Atlas y sus cuatro colecciones sigue pendiente por un
rechazo de autenticación (código `8000`). No se modificaron credenciales ni datos.

## Iniciar la API

Con el entorno virtual activado, ejecuta desde la raíz del repositorio:

```bash
uvicorn backend.main:app --reload
```

- API: [http://localhost:8000](http://localhost:8000).
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs).

`backend/main.py` crea la aplicación FastAPI, registra los cinco routers y define
`GET /` para comprobar que la API funciona. El controlador de eventos expone los
dos endpoints de lectura; los demás controladores aún no tienen operaciones propias.

## Consultar eventos

- `GET /api/v1/eventos/`: devuelve todos los eventos, o `[]` si no hay documentos.
- `GET /api/v1/eventos/{id}`: devuelve el evento cuyo `_id` coincida con el
  identificador recibido. Responde `400` si el formato del ID es inválido y `404`
  si el evento no existe.

Ambos endpoints aparecen en Swagger, convierten los ObjectId a texto y solo
realizan consultas de lectura a MongoDB.

## Crear eventos

`POST /api/v1/eventos/` recibe los datos mediante el modelo Pydantic `Evento`.
El servicio convierte el modelo con `model_dump()` e inserta el documento con
`insert_one()`, dejando que se asigne `_id` automáticamente.

Si la inserción es correcta, devuelve HTTP `200`:

```json
{"mensaje": "Evento agregado correctamente"}
```

FastAPI responde `422` si los datos no cumplen con el modelo. Si MongoDB rechaza
el documento por su esquema de validación (código `121`), responde `400`.

## Actualizar eventos

`PUT /api/v1/eventos/{id}` recibe el modelo `Evento` completo. El servicio utiliza
`update_one()` con `$set` para actualizar sus campos, sin modificar `_id`.
Comprueba la existencia mediante `matched_count`, por lo que un evento existente
con datos idénticos también se considera actualizado correctamente.

- `200`: `{"mensaje": "Evento actualizado correctamente"}`.
- `400`: ID inválido o rechazo del esquema de MongoDB (código `121`).
- `404`: evento no encontrado.
- `422`: datos incompletos o tipos incorrectos para el modelo.

## Desactivar eventos (Soft Delete)

`DELETE /api/v1/eventos/{id}` realiza una eliminación lógica: usa `update_one()`
con `$set` para establecer `activo: false`, sin borrar el documento ni cambiar
`estado` u otros datos del evento. Tampoco modifica órdenes, reseñas ni usuarios,
por lo que se conservan el historial y las referencias existentes.

- `200`: `{"mensaje": "Evento desactivado correctamente"}`, incluso si ya estaba
  desactivado. Se comprueba su existencia mediante `matched_count`.
- `400`: `ID de evento no válido.`
- `404`: `Evento no encontrado.`

Los GET actuales siguen mostrando los eventos desactivados, sin filtros nuevos.

## Gestionar usuarios

| Endpoint | Función |
|---|---|
| `GET /api/v1/usuarios/` | Lista todos los usuarios, incluidos los inactivos; devuelve `[]` si no hay documentos. |
| `GET /api/v1/usuarios/{id}` | Consulta un usuario por su ObjectId. |
| `POST /api/v1/usuarios/` | Crea un usuario y devuelve `{"mensaje": "Usuario agregado correctamente"}` con HTTP `200`. |
| `PUT /api/v1/usuarios/{id}` | Actualiza el usuario y devuelve `{"mensaje": "Usuario actualizado correctamente"}` con HTTP `200`. |
| `DELETE /api/v1/usuarios/{id}` | Establece `activo: false` y devuelve `{"mensaje": "Usuario desactivado correctamente"}` con HTTP `200`. |

POST y PUT reciben el modelo `Usuario` completo y utilizan `model_dump()`,
conservando las fechas como fechas BSON. MongoDB asigna `_id` al crear el usuario;
la actualización no lo modifica. PUT y DELETE comprueban `matched_count`, por lo
que los datos idénticos o un usuario ya inactivo también se consideran exitosos.

Un ID inválido devuelve `400`, un usuario inexistente devuelve `404` y los datos
incompletos o con tipos incorrectos devuelven `422`. En POST y PUT, un rechazo del
esquema MongoDB (código `121`) devuelve `400`. Las reglas de nombre, correo y rol
(`cliente` o `administrador`) se mantienen en MongoDB, sin añadir correo único.

El soft delete conserva los demás datos del usuario, sus órdenes y sus reseñas.
Los documentos recuperados se serializan para devolver ObjectId y fechas en JSON.

## Compras por usuario y ciudad

`GET /api/v1/analytics/compras-por-usuario-ciudad` recibe los parámetros de
consulta obligatorios `email` y `ciudad`. Reutiliza la Consulta 1 de la Evaluación 2:
relaciona `ordenes_compra` con `usuarios` y `eventos`, y considera únicamente
órdenes con estado `confirmada` que coincidan con el correo y la ciudad del recinto.

Devuelve una lista con `usuario`, `ciudad`, `compras` y `gasto_total`. Cada compra
incluye `evento`, `tipo_ticket`, `cantidad`, `precio_unitario` y `subtotal`.
El gasto total es la suma de los subtotales de los ítems, como en el pipeline original.

En [Swagger](http://localhost:8000/docs), abre **Analítica**, selecciona este GET
y pulsa **Try it out**. Introduce `usuario1@eventify.cl` en `email` y `Santiago`
en `ciudad`, y pulsa **Execute**. La solicitud equivalente es:

```text
/api/v1/analytics/compras-por-usuario-ciudad?email=usuario1@eventify.cl&ciudad=Santiago
```

Responde HTTP `200` con los resultados o con `[]` si no hay coincidencias.
Si falta alguno de los parámetros, FastAPI responde automáticamente HTTP `422`.

## Reporte de ventas por evento

`GET /api/v1/analytics/reporte-ventas-eventos` no recibe parámetros y reutiliza
la Consulta 2 de la Evaluación 2. Relaciona `eventos` con `ordenes_compra` y
devuelve todos los eventos, incluidos los inactivos y aquellos sin compras.

Cada resultado contiene `evento`, `ciudad`, `stock_inicial`, `total_recaudado`,
`tickets_vendidos`, `porcentaje_venta` y `etiqueta`. El stock inicial suma el de
los tickets del evento; la recaudación y las entradas vendidas consideran
únicamente órdenes confirmadas.

El porcentaje es `(tickets_vendidos / stock_inicial) * 100`, sin redondeos
adicionales. Si el stock inicial es cero, el porcentaje es cero. Desde el 70 %
la etiqueta es `Exitoso`; por debajo es `Por Mejorar`.

En [Swagger](http://localhost:8000/docs), abre **Analítica**, selecciona
`GET /api/v1/analytics/reporte-ventas-eventos` y pulsa **Try it out** y **Execute**.
Responde HTTP `200` con una lista de resultados o con `[]` si no existen eventos.
Los eventos sin compras tienen recaudación y entradas vendidas iguales a cero.
