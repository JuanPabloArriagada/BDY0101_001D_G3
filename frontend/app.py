import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_BASE_URL = (os.getenv("API_BASE_URL") or "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Eventify Global", layout="wide")


def consultar_api(endpoint: str, params: dict = None):
    try:
        respuesta = requests.get(
            f"{API_BASE_URL}/{endpoint.lstrip('/')}", params=params, timeout=5
        )
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        st.error("La API no devolvió una respuesta JSON válida.")
    except requests.exceptions.HTTPError:
        st.error("La API respondió con un error HTTP.")
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con FastAPI o se agotó el tiempo de espera.")
    return None


seccion = st.sidebar.radio(
    "Navegación", ["Inicio", "Dashboard", "Analítica", "Administración"]
)

if seccion == "Inicio":
    st.title("Eventify Global")
    st.caption("Dashboard de gestión y análisis de eventos.")
    st.subheader("Conexión con FastAPI")

    if st.button("Comprobar conexión"):
        datos = consultar_api("/")
        if datos is not None:
            st.success("Conexión con FastAPI establecida.")
            st.write(datos["mensaje"])
elif seccion == "Dashboard":
    st.title("Dashboard")
    st.caption("Indicadores de negocio de Eventify Global")
    datos = consultar_api("/api/v1/kpis")
    if datos is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Recaudación total", f"${datos['recaudacion_total']:,.0f}".replace(",", ".")
        )
        col2.metric(
            "Gasto promedio por orden", f"${datos['gasto_promedio_orden']:,.0f}".replace(",", ".")
        )
        col3.metric(
            "Calificación promedio", f"{datos['calificacion_promedio']:.2f} / 5".replace(".", ",")
        )
elif seccion == "Analítica":
    st.title("Analítica")
    st.caption("Reportes disponibles en el backend de Eventify Global.")
    st.subheader("Compras por usuario y ciudad")
    st.caption("Compras confirmadas de un usuario en eventos de la ciudad indicada.")

    with st.form("consulta_compras"):
        correo = st.text_input("Correo electrónico", value="usuario1@eventify.cl")
        ciudad = st.text_input("Ciudad", value="Santiago")
        consultar = st.form_submit_button("Consultar compras")

    if consultar:
        correo = correo.strip()
        ciudad = ciudad.strip()
        if not correo or not ciudad:
            st.warning("Ingresa el correo electrónico y la ciudad.")
        else:
            datos = consultar_api(
                "/api/v1/analytics/compras-por-usuario-ciudad",
                params={"email": correo, "ciudad": ciudad},
            )
            if datos is not None:
                if not datos:
                    st.info("No se encontraron compras confirmadas para este usuario en la ciudad indicada.")
                else:
                    resultado = datos[0]
                    st.write("Usuario:", resultado["usuario"])
                    st.write("Ciudad:", resultado["ciudad"])
                    st.metric("Gasto total", f"${resultado['gasto_total']:,.0f}".replace(",", "."))

                    compras = pd.DataFrame(resultado["compras"])
                    tabla = compras.copy()
                    for columna in ("precio_unitario", "subtotal"):
                        tabla[columna] = tabla[columna].map("${:,.0f}".format).str.replace(",", ".", regex=False)
                    tabla = tabla.rename(columns={
                        "evento": "Evento",
                        "tipo_ticket": "Tipo de entrada",
                        "cantidad": "Cantidad",
                        "precio_unitario": "Precio unitario",
                        "subtotal": "Subtotal",
                    })
                    st.dataframe(tabla, hide_index=True)

                    gasto_evento = compras.groupby("evento", as_index=False)["subtotal"].sum()
                    figura = px.bar(
                        gasto_evento,
                        x="evento",
                        y="subtotal",
                        title="Gasto por evento",
                        labels={"evento": "Evento", "subtotal": "Gasto (CLP)"},
                    )
                    st.plotly_chart(figura)

    st.divider()
    st.subheader("Ventas y ocupación por evento")
    st.caption("Reporte de recaudación y porcentaje de entradas vendidas por evento.")
    st.caption("El porcentaje compara entradas vendidas con el stock inicial; no representa asistencia real.")

    if st.button("Consultar ventas por evento"):
        datos_ventas = consultar_api("/api/v1/analytics/reporte-ventas-eventos")
        if datos_ventas is not None:
            if not datos_ventas:
                st.info("No se encontraron eventos para generar el reporte de ventas.")
            else:
                ventas = pd.DataFrame(datos_ventas)
                tabla_ventas = ventas.copy()
                tabla_ventas["total_recaudado"] = tabla_ventas["total_recaudado"].map("${:,.0f}".format).str.replace(",", ".", regex=False)
                tabla_ventas["porcentaje_venta"] = tabla_ventas["porcentaje_venta"].map("{:.2f} %".format).str.replace(".", ",", regex=False)
                tabla_ventas = tabla_ventas.rename(columns={
                    "evento": "Evento",
                    "ciudad": "Ciudad",
                    "stock_inicial": "Stock inicial",
                    "total_recaudado": "Total recaudado",
                    "tickets_vendidos": "Tickets vendidos",
                    "porcentaje_venta": "Porcentaje vendido",
                    "etiqueta": "Clasificación",
                })
                st.dataframe(tabla_ventas, hide_index=True)

                graficos_ventas = ventas.copy()
                graficos_ventas["evento_visual"] = graficos_ventas["evento"] + " — " + graficos_ventas["ciudad"]
                repetidos = graficos_ventas["evento_visual"].duplicated(keep=False)
                graficos_ventas.loc[repetidos, "evento_visual"] += " [" + (graficos_ventas.index[repetidos] + 1).astype(str) + "]"

                for campo, titulo, eje in (
                    ("total_recaudado", "Top 10 eventos por recaudación", "Recaudación (CLP)"),
                    ("porcentaje_venta", "Top 10 eventos por porcentaje vendido", "Porcentaje vendido (%)"),
                ):
                    top_eventos = graficos_ventas.sort_values(campo, ascending=False).head(10)
                    figura_ventas = px.bar(
                        top_eventos,
                        x=campo,
                        y="evento_visual",
                        orientation="h",
                        title=titulo,
                        labels={campo: eje, "evento_visual": "Evento y ciudad"},
                    )
                    figura_ventas.update_yaxes(autorange="reversed")
                    st.plotly_chart(figura_ventas)

    st.divider()
    st.subheader("Eventos futuros con disponibilidad")
    st.caption("Entradas disponibles de eventos futuros, filtradas por ciudad y precio máximo.")

    with st.form("consulta_eventos_futuros"):
        ciudad_futura = st.text_input("Ciudad", value="Santiago")
        precio_maximo = st.number_input("Precio máximo (CLP)", min_value=1, value=25000, step=1000)
        st.caption("Se buscan entradas con precio estrictamente menor al máximo ingresado.")
        buscar_disponibles = st.form_submit_button("Buscar eventos disponibles")

    if buscar_disponibles:
        ciudad_futura = ciudad_futura.strip()
        if not ciudad_futura or precio_maximo <= 0:
            st.warning("Ingresa una ciudad y un precio máximo mayor que cero.")
        else:
            datos_disponibles = consultar_api(
                "/api/v1/analytics/eventos-futuros",
                params={"ciudad": ciudad_futura, "precio_maximo": precio_maximo},
            )
            if datos_disponibles is not None:
                if not datos_disponibles:
                    st.info("No se encontraron eventos futuros con entradas disponibles para los filtros seleccionados.")
                else:
                    disponibilidad = pd.DataFrame(datos_disponibles)
                    tabla_disponibilidad = disponibilidad.copy()
                    fechas_visibles = disponibilidad["fecha_evento"].str.replace("T", " ", n=1, regex=False)
                    tabla_disponibilidad["fecha_evento"] = fechas_visibles
                    tabla_disponibilidad["precio"] = tabla_disponibilidad["precio"].map("${:,.0f}".format).str.replace(",", ".", regex=False)
                    tabla_disponibilidad = tabla_disponibilidad.rename(columns={
                        "evento": "Evento",
                        "fecha_evento": "Fecha del evento",
                        "ciudad": "Ciudad",
                        "tipo_ticket": "Tipo de entrada",
                        "precio": "Precio",
                        "stock_disponible": "Stock disponible",
                    })
                    st.dataframe(tabla_disponibilidad, hide_index=True)

                    grafico_disponibilidad = disponibilidad.copy()
                    grafico_disponibilidad["entrada_visual"] = disponibilidad["evento"] + " — " + disponibilidad["tipo_ticket"]
                    repetidas = grafico_disponibilidad["entrada_visual"].duplicated(keep=False)
                    grafico_disponibilidad.loc[repetidas, "entrada_visual"] += " — " + fechas_visibles.loc[repetidas]
                    if grafico_disponibilidad["entrada_visual"].duplicated().any():
                        grafico_disponibilidad["entrada_visual"] += " [" + (grafico_disponibilidad.index + 1).astype(str) + "]"
                    figura_disponibilidad = px.bar(
                        grafico_disponibilidad,
                        x="stock_disponible",
                        y="entrada_visual",
                        orientation="h",
                        title="Stock disponible por evento y tipo de entrada",
                        labels={"stock_disponible": "Stock disponible", "entrada_visual": "Evento y tipo de entrada"},
                    )
                    figura_disponibilidad.update_yaxes(autorange="reversed")
                    st.plotly_chart(figura_disponibilidad)

    st.info("Solo queda pendiente la visualización de clientes frecuentes (Consulta 4).")
else:
    st.title("Administración")
    st.caption("Gestión de usuarios y eventos de Eventify Global.")
    st.info("Aquí se podrán administrar usuarios y eventos en las siguientes tareas.")
