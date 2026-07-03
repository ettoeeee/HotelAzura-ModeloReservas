from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "data" / "dataset_us73_prediccion_mensual.csv"
MODEL_PATH = BASE_DIR / "models" / "modelo_reservas.joblib"
METADATA_PATH = BASE_DIR / "models" / "metadata_modelo.json"

COLUMNAS_REQUERIDAS = ["anio", "mes", "total_reservas_mes"]

MESES_NOMBRE = {
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