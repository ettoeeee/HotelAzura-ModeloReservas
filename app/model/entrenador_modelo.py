import json
from datetime import datetime

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.core.config import DATASET_PATH, MODEL_PATH, METADATA_PATH, MESES_NOMBRE
from app.model.procesador_datos import (
    cargar_dataset,
    agregar_variables_modelo,
    obtener_historial_utilizado,
)


def entrenar_modelo():
    df = cargar_dataset(DATASET_PATH)

    anio_base = int(df["anio"].min())
    df_modelo = agregar_variables_modelo(df, anio_base)

    X = df_modelo[["indice_tiempo", "mes"]]
    y = df_modelo["total_reservas_mes"]

    modelo = crear_pipeline_modelo()

    margen_error = calcular_margen_error(df_modelo)

    modelo.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, MODEL_PATH)

    metadata = crear_metadata(df, anio_base, margen_error)
    guardar_metadata(metadata)

    return metadata


def crear_pipeline_modelo():
    preprocesador = ColumnTransformer(
        transformers=[
            ("tiempo", StandardScaler(), ["indice_tiempo"]),
            ("mes", OneHotEncoder(handle_unknown="ignore"), ["mes"]),
        ]
    )

    modelo = Pipeline(
        steps=[
            ("preprocesador", preprocesador),
            ("regresion", Ridge(alpha=1.0)),
        ]
    )

    return modelo


def calcular_margen_error(df_modelo):
    # Si hay pocos datos, no se puede evaluar bien.
    # En este caso hay 101, entonces sí podemos usar los últimos 12 meses como prueba.
    if len(df_modelo) < 24:
        return 0

    train = df_modelo.iloc[:-12]
    test = df_modelo.iloc[-12:]

    X_train = train[["indice_tiempo", "mes"]]
    y_train = train["total_reservas_mes"]

    X_test = test[["indice_tiempo", "mes"]]
    y_test = test["total_reservas_mes"]

    modelo_validacion = crear_pipeline_modelo()
    modelo_validacion.fit(X_train, y_train)

    predicciones = modelo_validacion.predict(X_test)
    mae = mean_absolute_error(y_test, predicciones)

    return int(round(mae))


def crear_metadata(df, anio_base, margen_error):
    historial = obtener_historial_utilizado(df)

    mes_inicio_nombre = MESES_NOMBRE[historial["mes_inicio"]]
    mes_fin_nombre = MESES_NOMBRE[historial["mes_fin"]]

    historial_utilizado = (
        f"{mes_inicio_nombre} {historial['anio_inicio']} - "
        f"{mes_fin_nombre} {historial['anio_fin']}"
    )

    q33 = float(np.percentile(df["total_reservas_mes"], 33))
    q66 = float(np.percentile(df["total_reservas_mes"], 66))

    metadata = {
        "modelo_disponible": True,
        "anio_base": int(anio_base),
        "historial_utilizado": historial_utilizado,
        "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "margen_error_estimado": int(margen_error),
        "total_meses_historicos": int(len(df)),
        "umbral_bajo": q33,
        "umbral_alto": q66,
    }

    return metadata


def guardar_metadata(metadata):
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(METADATA_PATH, "w", encoding="utf-8") as archivo:
        json.dump(metadata, archivo, ensure_ascii=False, indent=4)