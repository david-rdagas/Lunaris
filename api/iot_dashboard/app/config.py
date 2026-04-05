"""
Configuración central — cargada desde variables de entorno o .env
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Autenticación ────────────────────────────────────────────────────────
    API_KEY: str = "iot-dev-key-changeme"

    # ── InfluxDB ─────────────────────────────────────────────────────────────
    INFLUX_URL:    str = "http://localhost:8086"
    INFLUX_TOKEN:  str = "mi-token-influx"
    INFLUX_ORG:    str = "mi-org"
    INFLUX_BUCKET: str = "iot"

    # ── WebSocket / broadcast ─────────────────────────────────────────────────
    BROADCAST_INTERVAL: float = 2.0   # segundos entre actualizaciones

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]

    # ── Alertas — ventana deslizante ─────────────────────────────────────────
    ALERT_WINDOW_MINUTES: int   = 5    # ventana de evaluación
    ALERT_TEMP_HIGH:      float = 80.0 # °C
    ALERT_TEMP_LOW:       float = -10.0
    ALERT_HUM_HIGH:       float = 90.0
    ALERT_PRES_LOW:       float = 950.0
    ALERT_PRES_HIGH:      float = 1050.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
