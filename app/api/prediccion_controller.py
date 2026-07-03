from fastapi import APIRouter, HTTPException

from app.schemas.prediccion_schema import (
    PrediccionRequest,
    PrediccionResponse,
    EstadoModeloResponse,
    EntrenamientoResponse,
)
from app.services.prediccion_service import (
    obtener_estado_modelo,
    ejecutar_entrenamiento,
    ejecutar_prediccion,
)

router = APIRouter(
    prefix="/api/prediccion-reservas",
    tags=["Predicción de reservas"]
)


@router.get("/estado", response_model=EstadoModeloResponse)
def estado_modelo():
    return obtener_estado_modelo()


@router.post("/entrenar", response_model=EntrenamientoResponse)
def entrenar():
    try:
        return ejecutar_entrenamiento()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible generar el modelo: {str(error)}"
        )


@router.post("/predecir", response_model=PrediccionResponse)
def predecir(request: PrediccionRequest):
    try:
        return ejecutar_prediccion(request)
    except FileNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Debe generar el modelo antes de consultar predicciones."
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible calcular la predicción: {str(error)}"
        )