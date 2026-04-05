from fastapi import FastAPI, Header, HTTPException, Query
from typing import Optional
from datetime import datetime
import json
import os
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IoT Pipeline API", version="1.0")
VALID_API_KEY = os.getenv("API_KEY")

# --- Conexión InfluxDB ---
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = influx_client.query_api()


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verifica que el header X-API-Key está presente y es correcto."""
    if x_api_key is None or x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: API key inválida o ausente")
    else:
        print("Api key validada!")


def validate_range(from_ts: Optional[str], to_ts: Optional[str]) -> tuple[str, str]:
    """
    Valida y normaliza el rango temporal.
    Acepta formato ISO 8601: 2026-03-01T00:00:00Z
    Devuelve (start, stop) listos para usar en Flux.
    """
    start = from_ts if from_ts else "-1h"   # default: última hora
    stop  = to_ts   if to_ts   else "now()"

    if from_ts:
        try:
            datetime.fromisoformat(from_ts.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="from_ts inválido. Usa formato ISO 8601: 2026-03-01T00:00:00Z"
            )
    if to_ts:
        try:
            datetime.fromisoformat(to_ts.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="to_ts inválido. Usa formato ISO 8601: 2026-03-01T12:00:00Z"
            )
    print("Rango valido!")
    return start, stop


def run_query(flux: str, empty_detail: str) -> list:
    """Ejecuta una query Flux y lanza 404 si no hay resultados."""
    try:
        tables = query_api.query(flux, org=INFLUX_ORG)
        print("Query ejecutada!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando InfluxDB: {e}")

    records = [r for table in tables for r in table.records]
    if not records:
        raise HTTPException(status_code=404, detail=empty_detail)
    return records


# ── Endpoint 1: Temperatura ───────────────────────────────────────────────────
@app.get(
    "/telemetry/temperature",
    summary="Lecturas de temperatura",
    description="Devuelve las lecturas del termómetro `s-termometer-01` en el rango indicado.",
    tags=["Telemetría"]
)
def get_temperature(
    from_ts,
    to_ts,
    x_api_key: Optional[str] = Header(None)
):
    verify_api_key(x_api_key)
    start, stop = validate_range(from_ts, to_ts)

    flux = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {start}, stop: {stop})
        |> filter(fn: (r) => r._measurement == "s-termometer-01")
        |> filter(fn: (r) => r._field == "value")
        |> sort(columns: ["_time"], desc: true)
    '''
    records = run_query(flux, "No hay lecturas de temperatura en ese rango")

    return {
        "sensor": "s-termometer-01",
        "from": from_ts or "última hora",
        "to":   to_ts   or "ahora",
        "count": len(records),
        "readings": [
            {
                "timestamp": str(r.get_time()),
                "value":     r.get_value(),
                "unit":      r.values.get("unit", ""),
            }
            for r in records
        ]
    }


@app.get(
    "/sensors/status",
    summary="Estado de los sensores",
    description=(
        "Devuelve los mensajes de status de los sensores en el rango indicado. "
        "Filtra por sensor concreto con el parámetro `sensor_id`."
    ),
    tags=["Estado"]
)
def get_status(
    from_ts:   Optional[str] = Query(None, description="Inicio del rango. ISO 8601"),
    to_ts:     Optional[str] = Query(None, description="Fin del rango.   ISO 8601"),
    sensor_id: Optional[str] = Query(None, description="Ej: s-termometer-01, s-imu-01"),
    x_api_key: Optional[str] = Header(None)
):
    verify_api_key(x_api_key)
    start, stop = validate_range(from_ts, to_ts)

    sensor_filter = f'|> filter(fn: (r) => r._measurement == "{sensor_id}")' if sensor_id else ""

    flux = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {start}, stop: {stop})
        {sensor_filter}
        |> filter(fn: (r) => r._field == "status")
        |> sort(columns: ["_time"], desc: true)
    '''
    records = run_query(flux, "No hay datos de status en ese rango")

    return {
        "from":  from_ts   or "última hora",
        "to":    to_ts     or "ahora",
        "sensor_id": sensor_id or "todos",
        "count": len(records),
        "events": [
            {
                "timestamp": str(r.get_time()),
                "sensor":    r.values.get("_measurement"),
                "status":    r.get_value(),
            }
            for r in records
        ]
    }


@app.get(
    "/telemetry/max",
    summary="Valor máximo de un sensor",
    description=(
        "Devuelve el valor más alto registrado por un sensor en el rango indicado. "
        "Usa `sensor_id` para especificar el sensor: `s-termometer-01`, `s-barometer-01`, etc."
    ),
    tags=["Telemetría"]
)
def get_max_value(
    sensor_id: str            = Query(..., description="ID del sensor: s-termometer-01, s-barometer-01"),
    from_ts:   Optional[str]  = Query(None, description="Inicio del rango. ISO 8601: 2026-03-01T00:00:00Z"),
    to_ts:     Optional[str]  = Query(None, description="Fin del rango.   ISO 8601: 2026-03-01T12:00:00Z"),
    x_api_key: Optional[str]  = Header(None)
):
    verify_api_key(x_api_key)
    start, stop = validate_range(from_ts, to_ts)

    flux = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {start}, stop: {stop})
        |> filter(fn: (r) => r._measurement == "{sensor_id}")
        |> filter(fn: (r) => r._field == "value")
        |> max()
    '''
    records = run_query(flux, f"No hay datos para '{sensor_id}' en ese rango")

    r = records[0]
    return {
        "sensor":     sensor_id,
        "from":       from_ts or "última hora",
        "to":         to_ts   or "ahora",
        "max_value":  r.get_value(),
        "timestamp":  str(r.get_time()),
        "unit":       r.values.get("unit", ""),
    }