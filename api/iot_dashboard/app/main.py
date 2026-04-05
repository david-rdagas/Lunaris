"""
IoT Dashboard — FastAPI Backend
================================
Expone:
  - REST  /api/v1/metrics          → últimos valores de cada dispositivo
  - REST  /api/v1/metrics/{device} → serie temporal de un dispositivo
  - REST  /api/v1/alerts           → alertas activas (ventana deslizante)
  - WS    /ws/live                 → push en tiempo real a clientes
  - REST  /grafana/*               → endpoints compatibles SimpleJSON/Infinity
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_api_key
from app.influx import InfluxClient
from app.ws_manager import ConnectionManager
from app.alerts import AlertEngine
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

influx = InfluxClient()
manager = ConnectionManager()
alert_engine = AlertEngine()


# ── Lifespan: arranque y parada ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_loop())
    log.info("IoT Dashboard arrancado")
    yield
    task.cancel()
    await influx.close()
    log.info("IoT Dashboard parado")


app = FastAPI(
    title="IoT Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Loop de broadcast WebSocket ──────────────────────────────────────────────

async def broadcast_loop():
    """Cada BROADCAST_INTERVAL segundos lee InfluxDB y empuja a todos los WS."""
    while True:
        try:
            snapshot = await influx.latest_all()
            alerts   = alert_engine.evaluate(snapshot)
            payload  = {
                "ts":      datetime.now(timezone.utc).isoformat(),
                "devices": snapshot,
                "alerts":  alerts,
            }
            await manager.broadcast(json.dumps(payload))
        except Exception as exc:
            log.exception("Error en broadcast_loop: %s", exc)
        await asyncio.sleep(settings.BROADCAST_INTERVAL)


# ── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket, api_key: str = Query(...)):
    """
    Conexión WebSocket autenticada por api_key en query string.
    ws://host/ws/live?api_key=<KEY>
    """
    if api_key != settings.API_KEY:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket)
    try:
        while True:
            # Mantener viva la conexión; el cliente puede enviar pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ── REST — métricas ──────────────────────────────────────────────────────────

@app.get("/api/v1/metrics", dependencies=[Depends(verify_api_key)])
async def get_metrics():
    """Último valor de cada dispositivo."""
    return await influx.latest_all()


@app.get("/api/v1/metrics/{device_id}", dependencies=[Depends(verify_api_key)])
async def get_device_series(
    device_id: str,
    minutes: int = Query(default=30, ge=1, le=1440),
):
    """Serie temporal de los últimos N minutos para un dispositivo."""
    data = await influx.timeseries(device_id, minutes=minutes)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Dispositivo '{device_id}' no encontrado")
    return {"device_id": device_id, "minutes": minutes, "series": data}


@app.get("/api/v1/alerts", dependencies=[Depends(verify_api_key)])
async def get_alerts():
    """Alertas activas generadas por la ventana deslizante."""
    snapshot = await influx.latest_all()
    return alert_engine.evaluate(snapshot)


# ── Grafana SimpleJSON / Infinity ────────────────────────────────────────────

@app.get("/grafana/")
async def grafana_health():
    """Health check requerido por SimpleJSON datasource."""
    return {"status": "ok"}


@app.post("/grafana/search", dependencies=[Depends(verify_api_key)])
async def grafana_search():
    """Lista de targets disponibles para Grafana."""
    devices = await influx.device_list()
    return devices + ["alerts"]


@app.post("/grafana/query", dependencies=[Depends(verify_api_key)])
async def grafana_query(body: dict):
    """
    Responde en formato SimpleJSON timeseries/table.
    Grafana envía el rango y los targets seleccionados.
    """
    from_ms = int(body["range"]["from"][:-1].replace("T", " ").split(".")[0].replace("-", "").replace(":", "").replace(" ", "")) if "range" in body else None
    results = []

    for target_obj in body.get("targets", []):
        target = target_obj.get("target", "")

        if target == "alerts":
            snapshot = await influx.latest_all()
            alerts = alert_engine.evaluate(snapshot)
            rows = [[a["device"], a["type"], a["value"], a["threshold"], a["ts"]] for a in alerts]
            results.append({
                "type": "table",
                "columns": [
                    {"text": "Device",    "type": "string"},
                    {"text": "Tipo",      "type": "string"},
                    {"text": "Valor",     "type": "number"},
                    {"text": "Umbral",    "type": "number"},
                    {"text": "Timestamp", "type": "time"},
                ],
                "rows": rows,
            })
        else:
            minutes = 30
            if "range" in body:
                try:
                    t0 = datetime.fromisoformat(body["range"]["from"].replace("Z", "+00:00"))
                    t1 = datetime.fromisoformat(body["range"]["to"].replace("Z", "+00:00"))
                    minutes = max(1, int((t1 - t0).total_seconds() / 60))
                except Exception:
                    pass

            series = await influx.timeseries(target, minutes=minutes)
            if series:
                datapoints = [[p["value"], int(p["ts"] * 1000)] for p in series]
                results.append({"target": target, "datapoints": datapoints})

    return results


@app.post("/grafana/annotations", dependencies=[Depends(verify_api_key)])
async def grafana_annotations(body: dict):
    """Devuelve alertas como anotaciones en Grafana."""
    snapshot = await influx.latest_all()
    alerts   = alert_engine.evaluate(snapshot)
    return [
        {
            "annotation": body.get("annotation", {}),
            "time":       int(datetime.fromisoformat(a["ts"].replace("Z", "+00:00")).timestamp() * 1000),
            "title":      f"ALERTA {a['type']}",
            "text":       f"{a['device']}: {a['value']:.2f} (umbral {a['threshold']:.2f})",
            "tags":       [a["device"], a["type"]],
        }
        for a in alerts
    ]
