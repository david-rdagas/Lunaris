from fastapi import FastAPI, Header, HTTPException
from typing import Optional
import datetime
import json
import os
from influxdb_client import InfluxDBClient


app = FastAPI(title="IoT Pipeline API", version="1.0")
VALID_API_KEY = os.environ.get("API_KEY", "0000")

# --- Conexión InfluxDB ---
INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "pic-lab-token-2026")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "esei")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "iot_data")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = influx_client.query_api()


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verifica que el header X-API-Key está presente y es correcto."""
    if x_api_key is None or x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: API key inválida o ausente")


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
    return start, stop


def run_query(flux: str, empty_detail: str) -> list:
    """Ejecuta una query Flux y lanza 404 si no hay resultados."""
    try:
        tables = query_api.query(flux, org=INFLUX_ORG)
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

"""
# =============================================
# GET /devices — lista de dispositivos
# =============================================
@app.get("/devices")
def get_devices(x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "telemetry")
        |> last()
        |> group()
    '''
    tables = query_api.query(query, org=INFLUX_ORG)
    
    devices = {}
    for record in [r for table in tables for r in table.records]:
        did = record.values.get("device_id", "unknown")
        devices[did] = {
            "device_id": did,
            "type": record.values.get("type", ""),
            "last_value": record.get_value(),
            "last_timestamp": str(record.get_time())
        }
    
    return {"devices": list(devices.values())}


# =============================================
# GET /devices/{id}/status — estado actual
# =============================================
@app.get("/devices/{device_id}/status")
def get_device_status(device_id: str, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    
    try:
        with open("device_status.json", "r") as f:
            all_status = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=404, detail="No hay datos de estado disponibles")
    
    if device_id not in all_status:
        raise HTTPException(status_code=404, detail=f"Dispositivo '{device_id}' no encontrado")
    
    return all_status[device_id]


# =============================================
# GET /devices/{id}/telemetry — lecturas históricas (opcional)
# =============================================
@app.get("/devices/{device_id}/telemetry")
def get_telemetry(
    device_id: str,
    from_ts: str = None,
    to_ts: str = None,
    x_api_key: Optional[str] = Header(None)
):
    verify_api_key(x_api_key)
    
    start = f"-1h"
    if from_ts:
        start = from_ts
    
    stop = "now()"
    if to_ts:
        stop = to_ts
    
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {start}, stop: {stop})
        |> filter(fn: (r) => r._measurement == "telemetry")
        |> filter(fn: (r) => r.device_id == "{device_id}")
        |> filter(fn: (r) => r._field == "value")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 100)
    '''
    tables = query_api.query(query, org=INFLUX_ORG)
    
    readings = []
    for record in [r for table in tables for r in table.records]:
        readings.append({
            "device_id": record.values.get("device_id", device_id),
            "type": record.values.get("type", ""),
            "timestamp": str(record.get_time()),
            "value": record.get_value()
        })
    
    if not readings:
        raise HTTPException(status_code=404, detail=f"No hay datos para '{device_id}'")
    
    return {"device_id": device_id, "readings": readings}
"""