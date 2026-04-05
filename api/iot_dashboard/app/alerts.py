"""
Motor de alertas con ventana deslizante.
Evalúa el snapshot actual contra umbrales configurados.
Puede extenderse para evaluar derivadas (rate of change) o anomalías estadísticas.
"""
from datetime import datetime, timezone
from app.config import settings


class AlertEngine:
    """
    Genera alertas a partir del snapshot de últimos valores.
    Las reglas están organizadas por campo y tipo de umbral.
    """

    RULES: list[dict] = []  # se construye en __init__ desde settings

    def __init__(self):
        cfg = settings
        self.RULES = [
            # ── Temperatura ──────────────────────────────────────────────────
            {
                "field":     "temperature",
                "type":      "HIGH_TEMP",
                "threshold": cfg.ALERT_TEMP_HIGH,
                "op":        "gt",
                "severity":  "critical",
                "message":   "Temperatura alta",
            },
            {
                "field":     "temperature",
                "type":      "LOW_TEMP",
                "threshold": cfg.ALERT_TEMP_LOW,
                "op":        "lt",
                "severity":  "warning",
                "message":   "Temperatura baja",
            },
            # ── Humedad ──────────────────────────────────────────────────────
            {
                "field":     "humidity",
                "type":      "HIGH_HUM",
                "threshold": cfg.ALERT_HUM_HIGH,
                "op":        "gt",
                "severity":  "warning",
                "message":   "Humedad excesiva",
            },
            # ── Presión ──────────────────────────────────────────────────────
            {
                "field":     "pressure",
                "type":      "LOW_PRES",
                "threshold": cfg.ALERT_PRES_LOW,
                "op":        "lt",
                "severity":  "warning",
                "message":   "Presión atmosférica baja",
            },
            {
                "field":     "pressure",
                "type":      "HIGH_PRES",
                "threshold": cfg.ALERT_PRES_HIGH,
                "op":        "gt",
                "severity":  "warning",
                "message":   "Presión atmosférica alta",
            },
        ]

    def evaluate(self, snapshot: dict[str, dict]) -> list[dict]:
        """
        Evalúa todas las reglas contra el snapshot actual.
        snapshot: { device_id: { field: value, ... }, ... }
        Devuelve lista de alertas activas.
        """
        alerts: list[dict] = []
        now = datetime.now(timezone.utc).isoformat()

        for device_id, fields in snapshot.items():
            for rule in self.RULES:
                field = rule["field"]
                if field not in fields:
                    continue
                value     = fields[field]
                threshold = rule["threshold"]
                triggered = (
                    value > threshold if rule["op"] == "gt" else value < threshold
                )
                if triggered:
                    alerts.append({
                        "device":    device_id,
                        "type":      rule["type"],
                        "severity":  rule["severity"],
                        "message":   rule["message"],
                        "field":     field,
                        "value":     round(value, 3),
                        "threshold": threshold,
                        "ts":        now,
                    })

        return alerts

    def evaluate_with_derivative(
        self,
        current: dict[str, dict],
        previous: dict[str, dict],
        interval_s: float,
    ) -> list[dict]:
        """
        Extensión: detecta cambios rápidos (rate of change).
        Úsala si almacenas el snapshot anterior en el broadcast_loop.
        """
        alerts = self.evaluate(current)
        if not previous or interval_s <= 0:
            return alerts

        RATE_RULES = [
            {"field": "temperature", "max_rate": 5.0,  "type": "RAPID_TEMP_CHANGE"},
            {"field": "pressure",    "max_rate": 10.0, "type": "RAPID_PRES_CHANGE"},
        ]
        now = datetime.now(timezone.utc).isoformat()

        for device_id, fields in current.items():
            prev = previous.get(device_id, {})
            for rule in RATE_RULES:
                f = rule["field"]
                if f not in fields or f not in prev:
                    continue
                rate = abs(fields[f] - prev[f]) / interval_s  # unidad/s
                if rate > rule["max_rate"]:
                    alerts.append({
                        "device":    device_id,
                        "type":      rule["type"],
                        "severity":  "warning",
                        "message":   f"Cambio rápido en {f}: {rate:.2f}/s",
                        "field":     f,
                        "value":     round(rate, 3),
                        "threshold": rule["max_rate"],
                        "ts":        now,
                    })
        return alerts
