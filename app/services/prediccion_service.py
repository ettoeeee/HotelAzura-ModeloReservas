import json

from app.core.config import METADATA_PATH
from app.model.entrenador_modelo import entrenar_modelo
from app.model.predictor_modelo import predecir_meses


def obtener_estado_modelo():
    if not METADATA_PATH.exists():
        return {
            "modeloDisponible": False,
            "historialUtilizado": None,
            "ultimaActualizacion": None,
            "margenErrorEstimado": None,
            "mensaje": "Modelo no generado."
        }

    with open(METADATA_PATH, "r", encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    return {
        "modeloDisponible": bool(metadata.get("modelo_disponible", False)),
        "historialUtilizado": metadata.get("historial_utilizado"),
        "ultimaActualizacion": metadata.get("ultima_actualizacion"),
        "margenErrorEstimado": metadata.get("margen_error_estimado"),
        "mensaje": "Modelo disponible."
    }


def ejecutar_entrenamiento():
    metadata = entrenar_modelo()

    return {
        "mensaje": "Modelo generado correctamente.",
        "modeloDisponible": True,
        "historialUtilizado": metadata["historial_utilizado"],
        "ultimaActualizacion": metadata["ultima_actualizacion"],
        "margenErrorEstimado": metadata["margen_error_estimado"]
    }


def ejecutar_prediccion(request):
    tipo = request.tipoConsulta.lower().strip()

    meses = obtener_meses_por_tipo(
        tipo=tipo,
        anio=request.anio,
        mes=request.mes,
        trimestre=request.trimestre,
        semestre=request.semestre
    )

    predicciones, metadata = predecir_meses(meses)

    total_estimado = sum(item["reservasEstimadas"] for item in predicciones)

    mayor = max(predicciones, key=lambda x: x["reservasEstimadas"])
    menor = min(predicciones, key=lambda x: x["reservasEstimadas"])

    comportamiento = generar_comportamiento(
        tipo=tipo,
        predicciones=predicciones,
        metadata=metadata
    )

    periodo = generar_periodo_texto(tipo, request.anio, request.mes, request.trimestre, request.semestre)

    return {
        "tipoConsulta": tipo,
        "periodo": periodo,
        "totalEstimado": total_estimado,
        "comportamientoEsperado": comportamiento,
        "margenErrorEstimado": metadata.get("margen_error_estimado"),
        "mayorDemanda": {
            "mes": mayor["nombreMes"],
            "reservasEstimadas": mayor["reservasEstimadas"]
        },
        "menorDemanda": {
            "mes": menor["nombreMes"],
            "reservasEstimadas": menor["reservasEstimadas"]
        },
        "predicciones": predicciones
    }


def obtener_meses_por_tipo(tipo, anio, mes=None, trimestre=None, semestre=None):
    if tipo == "mensual":
        if mes is None:
            raise ValueError("Para una consulta mensual debe indicar el mes.")
        return [{"anio": anio, "mes": mes}]

    if tipo == "trimestral":
        if trimestre is None:
            raise ValueError("Para una consulta trimestral debe indicar el trimestre.")

        trimestres = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12],
        }

        return [{"anio": anio, "mes": m} for m in trimestres[trimestre]]

    if tipo == "semestral":
        if semestre is None:
            raise ValueError("Para una consulta semestral debe indicar el semestre.")

        semestres = {
            1: [1, 2, 3, 4, 5, 6],
            2: [7, 8, 9, 10, 11, 12],
        }

        return [{"anio": anio, "mes": m} for m in semestres[semestre]]

    if tipo == "anual":
        return [{"anio": anio, "mes": m} for m in range(1, 13)]

    raise ValueError("El tipo de consulta debe ser mensual, trimestral, semestral o anual.")


def generar_periodo_texto(tipo, anio, mes=None, trimestre=None, semestre=None):
    meses_nombre = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    if tipo == "mensual":
        return f"{meses_nombre[mes]} {anio}"

    if tipo == "trimestral":
        nombres = {
            1: "I Trimestre - Enero a Marzo",
            2: "II Trimestre - Abril a Junio",
            3: "III Trimestre - Julio a Septiembre",
            4: "IV Trimestre - Octubre a Diciembre",
        }
        return f"{nombres[trimestre]} {anio}"

    if tipo == "semestral":
        nombres = {
            1: "I Semestre - Enero a Junio",
            2: "II Semestre - Julio a Diciembre",
        }
        return f"{nombres[semestre]} {anio}"

    if tipo == "anual":
        return f"Año {anio}"

    return str(anio)


def generar_comportamiento(tipo, predicciones, metadata):
    if len(predicciones) == 1:
        valor = predicciones[0]["reservasEstimadas"]
        mes = predicciones[0]["nombreMes"]

        umbral_bajo = metadata.get("umbral_bajo", 0)
        umbral_alto = metadata.get("umbral_alto", 0)

        if valor >= umbral_alto:
            nivel = "alta"
        elif valor <= umbral_bajo:
            nivel = "baja"
        else:
            nivel = "media"

        return (
            f"Se espera una demanda {nivel} para {mes}, "
            f"de acuerdo con el patrón histórico de reservas del hotel."
        )

    valores = [item["reservasEstimadas"] for item in predicciones]
    diferencias = [valores[i + 1] - valores[i] for i in range(len(valores) - 1)]

    primer_mes = predicciones[0]
    ultimo_mes = predicciones[-1]

    if all(d >= 0 for d in diferencias):
        texto_tendencia = "Se espera un comportamiento creciente durante el periodo."
    elif all(d <= 0 for d in diferencias):
        texto_tendencia = "Se espera un comportamiento decreciente durante el periodo."
    else:
        texto_tendencia = "Se espera un comportamiento variable durante el periodo."

    descripcion_movimiento = generar_descripcion_movimiento(predicciones, diferencias)

    return (
        f"{texto_tendencia} "
        f"El periodo inicia en {primer_mes['nombreMes']} con "
        f"{primer_mes['reservasEstimadas']} reservas estimadas y finaliza en "
        f"{ultimo_mes['nombreMes']} con {ultimo_mes['reservasEstimadas']} reservas estimadas. "
        f"{descripcion_movimiento}"
    )


def generar_descripcion_movimiento(predicciones, diferencias):
    aumentos = sum(1 for d in diferencias if d > 0)
    disminuciones = sum(1 for d in diferencias if d < 0)
    sin_cambios = sum(1 for d in diferencias if d == 0)

    if aumentos > 0 and disminuciones == 0:
        return "La demanda muestra aumentos progresivos entre los meses analizados."

    if disminuciones > 0 and aumentos == 0:
        return "La demanda muestra disminuciones progresivas entre los meses analizados."

    if aumentos > disminuciones:
        return "Aunque existen variaciones entre meses, predominan los aumentos dentro del periodo."

    if disminuciones > aumentos:
        return "Aunque existen variaciones entre meses, predominan las disminuciones dentro del periodo."

    if sin_cambios == len(diferencias):
        return "La demanda se mantiene estable durante todo el periodo."

    return "La demanda presenta subidas y bajadas sin una dirección completamente uniforme."