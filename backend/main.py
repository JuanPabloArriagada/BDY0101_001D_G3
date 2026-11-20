from fastapi import FastAPI
from backend.controllers import (
    usuarios_controller,
    eventos_controller,
    analytics_controller,
    kpis_controller,
)


app = FastAPI(title="API Eventify Global", version="1.0")

app.include_router(usuarios_controller.router)
app.include_router(eventos_controller.router)
app.include_router(analytics_controller.router)
app.include_router(kpis_controller.router)


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "API Eventify Global funcionando correctamente"}
