# IoT Dashboard — FastAPI + Grafana

Stack: **FastAPI** → **InfluxDB** → **Grafana** (Infinity / SimpleJSON datasource)

```
InfluxDB  ←──(Flux queries)──  FastAPI  ──(REST/WS)──→  Grafana
                                   │
                                   └──(WebSocket push)──→  clientes web opcionales
```

---

## Estructura

```
iot_dashboard/
├── app/
│   ├── main.py        # FastAPI: rutas REST, WS, Grafana SimpleJSON
│   ├── auth.py        # Autenticación API key (header o query param)
│   ├── config.py      # Settings desde .env (pydantic-settings)
│   ├── influx.py      # Cliente InfluxDB async (Flux queries)
│   ├── ws_manager.py  # Gestor de conexiones WebSocket
│   └── alerts.py      # Motor de alertas con ventana deslizante
├── grafana_provisioning/
│   ├── datasources/iot.yml           # Auto-provisiona Infinity + SimpleJSON
│   └── dashboards/
│       ├── dashboard.yml             # Config del proveedor
│       └── iot_realtime.json         # Dashboard pre-construido
├── .env.example       # Variables de entorno (copiar a .env)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Arranque rápido

```bash
# 1. Copia y edita las variables de entorno
cp .env.example .env
# Edita .env: INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET, API_KEY

# 2. Arranca todo
docker compose up -d

# Grafana → http://localhost:3000  (admin / admin)
# API     → http://localhost:8000/docs
```

---

## Autenticación

### REST / Grafana
Cualquier request necesita la API key. Se acepta en:

```
# Header (recomendado)
X-API-Key: iot-dev-key-changeme

# Query param
GET /api/v1/metrics?api_key=iot-dev-key-changeme
```

### WebSocket
La API key va en el query string de la conexión:

```js
const ws = new WebSocket("ws://localhost:8000/ws/live?api_key=iot-dev-key-changeme");
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## Endpoints

| Método | Ruta                          | Descripción                            |
|--------|-------------------------------|----------------------------------------|
| GET    | `/api/v1/metrics`             | Último valor de todos los dispositivos |
| GET    | `/api/v1/metrics/{device_id}` | Serie temporal (`?minutes=30`)         |
| GET    | `/api/v1/alerts`              | Alertas activas ahora                  |
| WS     | `/ws/live`                    | Push en tiempo real (2 s)              |
| GET    | `/grafana/`                   | Health check Grafana                   |
| POST   | `/grafana/search`             | Lista de targets                       |
| POST   | `/grafana/query`              | Datos timeseries / tabla               |
| POST   | `/grafana/annotations`        | Alertas como anotaciones               |
| GET    | `/docs`                       | Swagger UI                             |

---

## Integrar en tu proyecto Python existente

Si ya tienes un proyecto FastAPI, monta la app como sub-aplicación:

```python
# tu_proyecto/main.py
from fastapi import FastAPI
from app.main import app as dashboard_app  # importa la app del dashboard

main_app = FastAPI()
main_app.mount("/dashboard", dashboard_app)
```

O incluye solo el router (requiere refactorizar `main.py` en routers):

```python
from app.routers import metrics, grafana, ws
main_app.include_router(metrics.router, prefix="/dashboard/api/v1")
main_app.include_router(grafana.router, prefix="/dashboard/grafana")
```

---

## Ajustar umbrales de alerta

Edita `.env`:

```env
ALERT_TEMP_HIGH=75.0    # °C — alerta si supera
ALERT_TEMP_LOW=-5.0     # °C — alerta si baja de
ALERT_HUM_HIGH=85.0     # % humedad relativa
ALERT_PRES_LOW=960.0    # hPa
ALERT_PRES_HIGH=1040.0  # hPa
ALERT_WINDOW_MINUTES=5  # ventana de evaluación
```

Para alertas por **rate of change** (cambio rápido), usa `alert_engine.evaluate_with_derivative()` en `main.py` y guarda el snapshot anterior entre broadcasts.

---

## Configurar Grafana manualmente (sin Docker)

1. Instala el plugin **Infinity** o **SimpleJSON**:
   ```bash
   grafana-cli plugins install yesoreyeram-infinity-datasource
   # o: grafana-cli plugins install grafana-simple-json-datasource
   ```
2. Crea un datasource apuntando a `http://<tu-host>:8000/grafana`
3. Añade el header `X-API-Key` con tu clave
4. Importa `grafana_provisioning/dashboards/iot_realtime.json`

---

## Variables de entorno completas

| Variable               | Default                    | Descripción                        |
|------------------------|----------------------------|------------------------------------|
| `API_KEY`              | `iot-dev-key-changeme`     | Clave de autenticación             |
| `INFLUX_URL`           | `http://localhost:8086`    | URL de InfluxDB                    |
| `INFLUX_TOKEN`         | —                          | Token de acceso InfluxDB           |
| `INFLUX_ORG`           | `mi-org`                   | Organización InfluxDB              |
| `INFLUX_BUCKET`        | `iot`                      | Bucket donde están los datos       |
| `BROADCAST_INTERVAL`   | `2.0`                      | Segundos entre pushes WS           |
| `CORS_ORIGINS`         | `["*"]`                    | Orígenes permitidos CORS           |
| `ALERT_WINDOW_MINUTES` | `5`                        | Ventana deslizante (min)           |
| `ALERT_TEMP_HIGH`      | `80.0`                     | Umbral temperatura alta (°C)       |
| `ALERT_TEMP_LOW`       | `-10.0`                    | Umbral temperatura baja (°C)       |
| `ALERT_HUM_HIGH`       | `90.0`                     | Umbral humedad alta (%)            |
| `ALERT_PRES_LOW`       | `950.0`                    | Umbral presión baja (hPa)          |
| `ALERT_PRES_HIGH`      | `1050.0`                   | Umbral presión alta (hPa)          |
