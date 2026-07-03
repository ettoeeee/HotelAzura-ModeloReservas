from typing import List, Optional
from pydantic import BaseModel, Field


class PrediccionRequest(BaseModel):
    tipoConsulta: str = Field(
        ...,
        description="mensual, trimestral, semestral o anual"
    )
    anio: int = Field(..., ge=2000, le=2100)
    mes: Optional[int] = Field(None, ge=1, le=12)
    trimestre: Optional[int] = Field(None, ge=1, le=4)
    semestre: Optional[int] = Field(None, ge=1, le=2)


class PrediccionMesResponse(BaseModel):
    anio: int
    mes: int
    nombreMes: str
    reservasEstimadas: int


class DemandaResponse(BaseModel):
    mes: str
    reservasEstimadas: int


class PrediccionResponse(BaseModel):
    tipoConsulta: str
    periodo: str
    totalEstimado: int
    comportamientoEsperado: str
    margenErrorEstimado: Optional[int]
    mayorDemanda: Optional[DemandaResponse]
    menorDemanda: Optional[DemandaResponse]
    predicciones: List[PrediccionMesResponse]


class EstadoModeloResponse(BaseModel):
    modeloDisponible: bool
    historialUtilizado: Optional[str]
    ultimaActualizacion: Optional[str]
    margenErrorEstimado: Optional[int]
    mensaje: str


class EntrenamientoResponse(BaseModel):
    mensaje: str
    modeloDisponible: bool
    historialUtilizado: str
    ultimaActualizacion: str
    margenErrorEstimado: int