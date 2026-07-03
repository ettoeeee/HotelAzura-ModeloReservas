import pandas as pd
from app.core.config import COLUMNAS_REQUERIDAS


def cargar_dataset(ruta_dataset):
    df = pd.read_csv(ruta_dataset)

    validar_columnas(df)
    validar_datos(df)

    df = df.sort_values(["anio", "mes"]).reset_index(drop=True)

    return df


def validar_columnas(df):
    columnas = list(df.columns)

    for columna in COLUMNAS_REQUERIDAS:
        if columna not in columnas:
            raise ValueError(f"El dataset no contiene la columna requerida: {columna}")


def validar_datos(df):
    if df.empty:
        raise ValueError("El dataset está vacío.")

    if df["anio"].isnull().any():
        raise ValueError("Existen valores vacíos en la columna anio.")

    if df["mes"].isnull().any():
        raise ValueError("Existen valores vacíos en la columna mes.")

    if df["total_reservas_mes"].isnull().any():
        raise ValueError("Existen valores vacíos en la columna total_reservas_mes.")

    if not df["mes"].between(1, 12).all():
        raise ValueError("La columna mes debe tener valores entre 1 y 12.")

    if (df["total_reservas_mes"] < 0).any():
        raise ValueError("La cantidad de reservas no puede ser negativa.")

    duplicados = df.duplicated(subset=["anio", "mes"]).any()
    if duplicados:
        raise ValueError("El dataset contiene registros duplicados para un mismo año y mes.")


def agregar_variables_modelo(df, anio_base):
    df = df.copy()

    df["indice_tiempo"] = ((df["anio"] - anio_base) * 12) + (df["mes"] - 1)

    return df


def obtener_historial_utilizado(df):
    primer_registro = df.iloc[0]
    ultimo_registro = df.iloc[-1]

    return {
        "anio_inicio": int(primer_registro["anio"]),
        "mes_inicio": int(primer_registro["mes"]),
        "anio_fin": int(ultimo_registro["anio"]),
        "mes_fin": int(ultimo_registro["mes"]),
    }