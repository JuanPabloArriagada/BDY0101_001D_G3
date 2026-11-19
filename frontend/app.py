import os
from pathlib import Path

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
    st.write(
        "- Compras por usuario y ciudad.\n"
        "- Reporte de ventas por evento.\n"
        "- Eventos futuros con filtros.\n"
        "- Clientes frecuentes."
    )
    st.info("Las visualizaciones de estos reportes se implementarán posteriormente.")
else:
    st.title("Administración")
    st.caption("Gestión de usuarios y eventos de Eventify Global.")
    st.info("Aquí se podrán administrar usuarios y eventos en las siguientes tareas.")
