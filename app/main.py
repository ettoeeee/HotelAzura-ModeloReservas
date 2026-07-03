from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.prediccion_controller import router as prediccion_router

app = FastAPI(
    title="Hotel Azura - Modelo Predictivo de Reservas",
    description="API para entrenar y consultar predicciones de reservas hoteleras.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Luego podés limitarlo al dominio del frontend admin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediccion_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API del modelo predictivo de reservas de Hotel Azura funcionando correctamente."
    }