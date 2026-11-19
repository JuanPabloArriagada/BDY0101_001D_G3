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

Una verificación anterior recibió un rechazo de autenticación (código `8000`).
El 19-11-2026 se comprobó correctamente el ping y la lectura de la Consulta 3
desde la API y Streamlit. No se modificaron credenciales ni datos.

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

## Eventos futuros con filtros

`GET /api/v1/analytics/eventos-futuros` reutiliza la Consulta 3 de la Evaluación 2
sobre `eventos`. Recibe dos parámetros opcionales: `ciudad`, predeterminado en
`Santiago`, y `precio_maximo`, predeterminado en `25000`.

Selecciona eventos posteriores a la fecha UTC actual, con estado `programado`
y en la ciudad indicada, sin filtrar por `activo`. Devuelve cada tipo de ticket
por separado si tiene stock disponible mayor que cero y su precio es
estrictamente menor que el límite; un precio igual al límite queda excluido.

Cada resultado contiene `evento`, `fecha_evento`, `ciudad`, `tipo_ticket`,
`precio` y `stock_disponible`. Responde HTTP `200` con los resultados o con `[]`
si no hay coincidencias.

En [Swagger](http://localhost:8000/docs), abre **Analítica**, selecciona este GET
y pulsa **Try it out** y **Execute** para probar los valores predeterminados.
Puedes cambiar ambos parámetros, por ejemplo:

```text
/api/v1/analytics/eventos-futuros?ciudad=Concepción&precio_maximo=30000
```

## Clientes frecuentes

`GET /api/v1/analytics/clientes-frecuentes` no recibe parámetros y reutiliza
la Consulta 4 de la Evaluación 2. Relaciona `usuarios` con `ordenes_compra`
para identificar usuarios con rol `cliente` que tengan al menos dos órdenes
confirmadas, incluidos los clientes inactivos.

Devuelve `nombre`, `email`, `cantidad_compras`, `total_gastado` y `tipo_cliente`.
La cantidad cuenta órdenes confirmadas y el gasto suma el campo `total` de esas
órdenes. La clasificación conserva `Frecuente` y `Ocasional`; el filtro final
devuelve únicamente clientes de tipo `Frecuente`.

En [Swagger](http://localhost:8000/docs), abre **Analítica**, selecciona
`GET /api/v1/analytics/clientes-frecuentes` y pulsa **Try it out** y **Execute**.
Responde HTTP `200` con los resultados o con `[]` si ningún cliente cumple
el criterio.

## Indicadores de negocio (KPIs)

`GET /api/v1/kpis` no recibe parámetros y devuelve tres indicadores calculados
en MongoDB para el futuro dashboard.

| Indicador | Cálculo | Utilidad |
|---|---|---|
| `recaudacion_total` | Suma de `total` de las órdenes confirmadas en `ordenes_compra`. | Mide el volumen de ventas confirmado. |
| `gasto_promedio_orden` | Promedio de `total` de esas órdenes confirmadas. | Permite conocer el importe promedio gastado por orden. |
| `calificacion_promedio` | Promedio de `puntuacion` de todas las reseñas de `resenas_evaluaciones`, en la escala de 1 a 5. | Permite observar la satisfacción de los asistentes. |

Una sola agregación calcula la recaudación y el gasto promedio. Otra calcula la
calificación promedio. Los promedios se redondean a dos decimales y los valores
se devuelven como números, sin símbolos monetarios ni unidades.

Si no hay órdenes confirmadas, los dos indicadores de compras son cero. Si no
hay reseñas, la calificación promedio es cero. La respuesta es HTTP `200`.

Ejemplo ilustrativo de respuesta, con valores ficticios:

```json
{
  "recaudacion_total": 1500000,
  "gasto_promedio_orden": 50000,
  "calificacion_promedio": 4.2
}
```

En [Swagger](http://localhost:8000/docs), abre **KPIs**, selecciona
`GET /api/v1/kpis` y pulsa **Try it out** y **Execute** para consultar los valores.

## Iniciar Streamlit y comprobar la conexión

Con `.venv` activado en ambas terminales, ejecuta desde la raíz del repositorio:

**Terminal 1 — FastAPI:**

```powershell
uvicorn backend.main:app --reload
```

**Terminal 2 — Streamlit:**

```powershell
streamlit run frontend/app.py
```

Abre [http://localhost:8501](http://localhost:8501) y pulsa **Comprobar conexión**.
El frontend consulta únicamente `GET /` y muestra la confirmación y el mensaje
devuelto por FastAPI.

`API_BASE_URL` indica la dirección del backend. Se carga desde el `.env` de la
raíz y utiliza `http://localhost:8000` como valor predeterminado si no está
definida. Streamlit se comunica por HTTP, sin acceder directamente a MongoDB.

Si FastAPI no está disponible, tarda más de cinco segundos o devuelve un error,
la pantalla muestra un aviso y sigue funcionando. Después de iniciar o revisar
la API, puedes volver a pulsar el botón. Esta pantalla inicial todavía no
incluye visualizaciones ni formularios administrativos.

## Navegación del dashboard

El menú lateral **Navegación** permite cambiar entre cuatro secciones dentro de
la misma aplicación. **Inicio** es la opción predeterminada.

- **Inicio:** conserva la presentación del proyecto y el botón **Comprobar conexión**.
- **Dashboard:** muestra los tres indicadores de negocio obtenidos desde FastAPI.
- **Analítica:** incluye las visualizaciones de las cuatro consultas originales de la Evaluación 2.
- **Administración:** panel para listar, crear, editar y desactivar usuarios y eventos.

Administración utiliza los CRUD existentes de FastAPI. Dashboard consulta sus KPIs al
mostrarse; los reportes de Analítica se consultan solo al pulsar su botón o
enviar su formulario. **Comprobar conexión**, en Inicio, consulta `GET /`.

Con `.venv` activado, inicia la aplicación desde la raíz con:

```powershell
streamlit run frontend/app.py
```

Para comprobar la conexión, mantén FastAPI ejecutándose en otra terminal con
el comando indicado en la sección anterior.

## Tarjetas de KPIs en Dashboard

La sección **Dashboard** muestra tres tarjetas en columnas. Cada ejecución de
esta sección realiza una única consulta HTTP a `GET /api/v1/kpis` mediante
`consultar_api()` y utiliza los valores actuales devueltos por FastAPI.

- **Recaudación total:** suma del total de las órdenes confirmadas.
- **Gasto promedio por orden:** importe promedio de esas órdenes confirmadas.
- **Calificación promedio:** puntuación promedio general de las reseñas.

Los importes se muestran como pesos chilenos, sin decimales y con puntos como
separadores de miles. La calificación utiliza dos decimales, coma decimal y
escala `/ 5`. El frontend solo aplica formato visual; los cálculos siguen en
MongoDB y FastAPI.

Los ceros recibidos correctamente se muestran normalmente. Si la consulta
falla, aparece el mensaje del cliente HTTP y no se muestran tarjetas con
valores de ejemplo. Inicio conserva su comprobación de conexión; Analítica
incluye sus reportes y Administración permite gestionar usuarios y eventos.

Con `.venv` activado en ambas terminales y desde la raíz del proyecto:

```powershell
# Terminal 1
uvicorn backend.main:app --reload
```

```powershell
# Terminal 2
streamlit run frontend/app.py
```

Abre [http://localhost:8501](http://localhost:8501) y selecciona **Dashboard**
en el menú lateral para ver los tres indicadores.

## Consulta 1 en Analítica: compras por usuario y ciudad

En **Analítica**, el formulario **Compras por usuario y ciudad** consulta
`GET /api/v1/analytics/compras-por-usuario-ciudad` mediante los parámetros
`email` y `ciudad`. Muestra las compras confirmadas de ese usuario en eventos
de la ciudad indicada.

Los campos son editables y comienzan con `usuario1@eventify.cl` y `Santiago`,
como en la Evaluación 2. La solicitud se realiza únicamente al pulsar
**Consultar compras**. Se eliminan los espacios iniciales y finales; si falta
algún filtro, aparece una advertencia y no se consulta la API.

Cuando hay resultados, se muestra el usuario, la ciudad y la métrica **Gasto
total**, tomada directamente de `gasto_total` de FastAPI y presentada como
pesos chilenos, sin decimales y con puntos como separadores de miles.

La tabla conserva todas las compras, incluidas las repetidas, con las columnas
**Evento**, **Tipo de entrada**, **Cantidad**, **Precio unitario** y **Subtotal**.
Una copia permite formatear los importes sin modificar los datos numéricos.

El gráfico de barras **Gasto por evento** suma los subtotales por nombre de
evento únicamente para representarlos visualmente. No recalcula ni sustituye
la métrica `gasto_total` y utiliza la misma respuesta HTTP que la tabla.

Si no hay coincidencias, aparece un mensaje informativo. Si la consulta falla,
se conserva el error del cliente HTTP y no se muestran resultados inventados.
Las cuatro consultas originales están disponibles en Analítica.

Con FastAPI y Streamlit iniciados en terminales separadas, según las
instrucciones anteriores, abre [http://localhost:8501](http://localhost:8501),
selecciona **Analítica**, completa los filtros y pulsa **Consultar compras**
para ver la métrica, la tabla y el gráfico.

## Consulta 2 en Analítica: ventas y ocupación por evento

Después de Consulta 1, la sección **Ventas y ocupación por evento** consulta
`GET /api/v1/analytics/reporte-ventas-eventos` únicamente al pulsar
**Consultar ventas por evento**, sin parámetros. La misma respuesta se utiliza
para la tabla y ambos gráficos.

La tabla conserva todos los registros y muestra **Evento**, **Ciudad**,
**Stock inicial**, **Total recaudado**, **Tickets vendidos**, **Porcentaje
vendido** y **Clasificación**. Los importes se presentan como pesos chilenos
y los porcentajes con dos decimales y coma decimal. Solo una copia de
presentación recibe este formato; los gráficos mantienen los valores numéricos.

- **Top 10 eventos por recaudación:** barras horizontales con `total_recaudado`.
- **Top 10 eventos por porcentaje vendido:** barras horizontales con `porcentaje_venta`.

Cada gráfico ordena de mayor a menor y muestra hasta diez registros para
facilitar su lectura; la tabla permanece completa. Los nombres incluyen la
ciudad y, si todavía coinciden, su posición original únicamente en los gráficos.
No se fusionan eventos ni se eliminan duplicados.

El porcentaje representa entradas vendidas respecto del stock inicial,
no asistencia real. Se conserva incluso si supera el 100 %. La clasificación
se muestra como la entrega FastAPI: **Exitoso** desde el 70 % y **Por Mejorar**
por debajo. Estos cálculos se realizan en MongoDB; Streamlit no los recalcula.
Se conservan los eventos sin ventas y con stock inicial cero.

Si la respuesta es `[]`, aparece un aviso de ausencia de eventos. Si falla la
solicitud, se conserva el error del cliente HTTP y no se muestran datos de
ejemplo. Las cuatro consultas originales están disponibles en Analítica.

Con FastAPI y Streamlit iniciados en terminales separadas según las
instrucciones anteriores, abre [http://localhost:8501](http://localhost:8501),
selecciona **Analítica** y pulsa **Consultar ventas por evento** para ver la
tabla completa y los dos gráficos.

**Verificación anterior (19-11-2026):** el ping de solo lectura a Atlas,
limitado a ocho segundos, devolvió `ServerSelectionTimeoutError`. En esa prueba
se verificaron la tabla, ambos gráficos y la navegación con respuestas HTTP
simuladas. Posteriormente, durante la verificación de Consulta 3, Consulta 2
funcionó con datos reales en la API y el navegador, sin modificar documentos.

## Consulta 3 en Analítica: eventos futuros con disponibilidad

Después de Consulta 2, el formulario **Eventos futuros con disponibilidad**
consulta `GET /api/v1/analytics/eventos-futuros` mediante `ciudad` y
`precio_maximo`. Sus valores iniciales son `Santiago` y `25000` CLP.

La solicitud se realiza únicamente al pulsar **Buscar eventos disponibles**.
La ciudad se recorta con `.strip()` y debe estar informada; el precio máximo
debe ser positivo. El backend busca entradas con precio estrictamente menor
que ese máximo, además de aplicar sus filtros de fecha futura, estado y stock.
Streamlit no repite estos filtros ni filtra por actividad.

Cada fila de la tabla representa un tipo de entrada y conserva **Evento**,
**Fecha del evento**, **Ciudad**, **Tipo de entrada**, **Precio** y **Stock
disponible**. Los precios se presentan como pesos chilenos sin decimales.
En las fechas solo se sustituye la primera `T` por un espacio para facilitar
la lectura: se conservan segundos, fracciones y la información de zona horaria
recibida, sin conversiones. El formato se aplica a una copia de presentación.

El gráfico horizontal **Stock disponible por evento y tipo de entrada** muestra
una barra por registro, utilizando directamente `stock_disponible`. No agrupa,
elimina duplicados ni limita la cantidad de resultados. Las etiquetas incluyen
evento y tipo de entrada; cuando se repiten se añade la fecha y, si es necesario,
la posición original únicamente para distinguir las barras.

Si la respuesta es `[]`, aparece un aviso de ausencia de coincidencias. Si falla
la solicitud, se conserva el error del cliente HTTP sin inventar resultados.
Las cuatro consultas originales están disponibles en Analítica.

Con FastAPI y Streamlit iniciados en terminales separadas según las instrucciones
anteriores, abre [http://localhost:8501](http://localhost:8501), selecciona
**Analítica**, introduce los filtros y pulsa **Buscar eventos disponibles**.

**Verificación real (19-11-2026):** con `Santiago` y `25000`, Atlas devolvió
seis registros. La tabla mostró las seis filas y el gráfico seis barras, con
precio de $15.000 y stock de 40 en cada registro, coincidiendo con la respuesta
de FastAPI. También se comprobaron las Consultas 1 y 2 y las tres tarjetas de
KPIs. Las operaciones fueron exclusivamente de lectura.

## Consulta 4 en Analítica: clientes frecuentes

Después de Consulta 3, **Clientes frecuentes** consulta
`GET /api/v1/analytics/clientes-frecuentes` únicamente al pulsar
**Consultar clientes frecuentes**, sin parámetros. La misma respuesta se
utiliza para la tabla y ambos gráficos.

Un cliente frecuente tiene al menos dos órdenes de compra confirmadas.
MongoDB cuenta esas órdenes mediante `$size` y suma su campo `total` para
obtener el gasto; la cantidad de compras no representa entradas individuales.
Streamlit no repite estos cálculos ni excluye clientes inactivos.

La tabla conserva todos los registros recibidos y muestra **Nombre**,
**Correo electrónico**, **Cantidad de compras**, **Total gastado** y **Tipo
de cliente**. Una copia permite presentar el gasto como pesos chilenos, sin
decimales y con puntos como separadores de miles, manteniendo los valores
numéricos originales para los gráficos. La clasificación se muestra exactamente
como la entrega FastAPI, sin recalcularla.

- **Top 10 clientes por gasto total:** barras horizontales con `total_gastado`.
- **Top 10 clientes por cantidad de compras:** barras horizontales con `cantidad_compras`.

Cada gráfico ordena su indicador de mayor a menor, con el valor más alto arriba,
y muestra hasta diez clientes para facilitar la lectura. La tabla permanece
completa. Las etiquetas incluyen nombre y correo; si se repiten, se añade su
posición original. Se reutilizan en ambos gráficos sin fusionar registros.

Si la respuesta es `[]`, aparece un mensaje de ausencia de clientes con al menos
dos órdenes confirmadas. Si falla la solicitud, se conserva el error del cliente
HTTP y no se muestran tablas ni gráficos con datos inventados.

Con FastAPI y Streamlit iniciados en terminales separadas según las instrucciones
anteriores, abre [http://localhost:8501](http://localhost:8501), selecciona
**Analítica** y pulsa **Consultar clientes frecuentes** para ver la tabla y
los dos gráficos. Las cuatro visualizaciones originales están disponibles.

**Verificación real (19-11-2026):** FastAPI devolvió cinco clientes, cada uno
con dos órdenes confirmadas, $150.000 gastados y clasificación `Frecuente`.
La tabla conservó las cinco filas y cada gráfico mostró cinco barras con los
mismos valores de la API. También se comprobaron las Consultas 1, 2 y 3 y los
tres KPIs en Streamlit. Todas las operaciones fueron de lectura, sin modificar
documentos, credenciales ni configuración.

## Panel administrativo CRUD

En **Administración**, selecciona **Usuarios** o **Eventos** y una operación:
**Listar**, **Crear**, **Editar** o **Desactivar**. Solo se muestra la operación
elegida. El panel se comunica por HTTP con FastAPI, sin conectarse a MongoDB.

| Operación | Método | Usuarios | Eventos |
|---|---|---|---|
| Listar | GET | `/api/v1/usuarios/` | `/api/v1/eventos/` |
| Consultar para editar o desactivar | GET | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |
| Crear | POST | `/api/v1/usuarios/` | `/api/v1/eventos/` |
| Editar | PUT | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |
| Desactivar | DELETE | `/api/v1/usuarios/{id}` | `/api/v1/eventos/{id}` |

**Listar** muestra los IDs y los registros activos e inactivos. Pulsa
**Actualizar listado** para obtener los datos actuales. En edición y
desactivación, el selector muestra etiquetas legibles pero utiliza `_id`;
después consulta el documento seleccionado para precargar sus datos.

Los formularios de usuarios incluyen nombre, correo, rol (`cliente` o
`administrador`), activo, fecha de nacimiento y fecha de registro. Las fechas
nuevas se envían en ISO 8601 a medianoche. Al editar una fecha se conserva su
hora y zona originales; si no cambia, se conserva la cadena original completa.

Los formularios de eventos incluyen información general, fecha y hora, estado,
activo, recinto y entradas. El recinto es un objeto con nombre, ciudad,
dirección y capacidad. Las entradas son una lista de objetos con tipo, precio,
stock inicial y stock disponible. El editor permite añadir filas al crear;
al editar mantiene filas fijas para conservar General, VIP y los demás tipos.
Se pueden modificar sus precios y stocks. Se indica la zona horaria de la fecha;
las fechas nuevas se interpretan en UTC y las existentes no se convierten de
zona silenciosamente. Los valores sin cambios conservan su precisión original.

POST y PUT envían todos los campos del modelo, sin `_id` en el cuerpo. Solo se
envían al confirmar el formulario. Se validan los campos obligatorios, el correo,
las fechas, la capacidad positiva, al menos una entrada y los precios y stocks
no negativos; los stocks deben ser enteros. MongoDB conserva sus validadores.

**Desactivar** requiere marcar la confirmación y enviar el formulario del ID
seleccionado. DELETE establece `activo: false` y conserva el documento y su
historial. Un registro ya inactivo se informa sin enviar otro DELETE.

`consultar_api()` conserva las lecturas existentes. `enviar_api()` centraliza
POST, PUT y DELETE, con timeout de cinco segundos y sin reintentos automáticos.
Muestra errores 400, 404, 422 y 500, fallos de conexión, timeout y respuestas
inválidas. Los errores de lectura mantienen el mensaje genérico del cliente GET.
Una respuesta fallida no muestra éxito. Ante un error de red o de confirmación,
consulta el listado antes de repetir: la operación podría haberse aplicado.

El último mensaje confirmado permanece visible al cambiar a **Listar** y
actualizar la tabla. No se utiliza caché ni una recarga automática para ocultarlo.

Para usar el panel, inicia desde la raíz, con `.venv` activado en dos terminales:

```powershell
# Terminal 1
uvicorn backend.main:app --reload
```

```powershell
# Terminal 2
streamlit run frontend/app.py
```

Abre [http://localhost:8501](http://localhost:8501) y selecciona **Administración**.
Listar y seleccionar registros realiza lecturas. Confirmar creación, edición o
desactivación modifica la base configurada: revisa el registro y los datos antes
de enviar. Las pruebas de escritura de esta tarea deben utilizar solicitudes
simuladas o interceptadas; la integración con Atlas se limita a GET. No ejecutes
el script original de MongoDB, porque contiene `db.dropDatabase()`.

**Verificación (19-11-2026):** los GET reales devolvieron 50 usuarios y 50 eventos,
incluidos 20 eventos inactivos. Las tablas y la precarga coincidieron con FastAPI.
POST, PUT y DELETE se probaron con solicitudes interceptadas, incluyendo fechas
con offsets y fracciones, varias entradas, confirmación por ID y errores HTTP y
de red. Se comprobaron las cuatro consultas analíticas y los tres KPIs. La
navegación real utilizó exclusivamente GET y no se ejecutaron escrituras en Atlas.
