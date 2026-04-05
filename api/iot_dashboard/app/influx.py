"""
Cliente InfluxDB async.
Adapta las queries Flux a los modelos que necesita el dashboard.
"""
import time
import logging
from typing import Any

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from app.config import settings

log = logging.getLogger(__name__)


class InfluxClient:
    def __init__(self):
        self._client = InfluxDBClientAsync(
            url=settings.INFLUX_URL,
            token=settings.INFLUX_TOKEN,
            org=settings.INFLUX_ORG,
        )

    async def close(self):
        await self._client.close()

    # ── Helpers internos ────────────────────────────────────────────────────

    def _query_api(self):
        return self._client.query_api()

    async def _flux(self, query: str) -> list[Any]:
        """Ejecuta una query Flux y devuelve los registros."""
        try:
            api = self._query_api()
            tables = await api.query(query, org=settings.INFLUX_ORG)
            return [record for table in tables for record in table.records]
        except Exception as exc:
            log.error("InfluxDB query error: %s", exc)
            return []

    # ── API pública ─────────────────────────────────────────────────────────

    async def device_list(self) -> list[str]:
        """Devuelve la lista de device_id únicos en el bucket."""
        query = f"""
        import "influxdata/influxdb/schema"
        schema.tagValues(
            bucket: "{settings.INFLUX_BUCKET}",
            tag: "device_id",
        )
        """
        records = await self._flux(query)
        return [r.get_value() for r in records]

    async def latest_all(self) -> dict[str, dict]:
        """
        Último valor de cada campo de cada dispositivo.
        Devuelve:
        {
            "sensor_01": {"temperature": 23.4, "humidity": 55.1, "ts": 1712345678.0},
            ...
        }
        """
        query = f"""
        from(bucket: "{settings.INFLUX_BUCKET}")
          |> range(start: -10m)
          |> filter(fn: (r) => r._measurement == "iot_sensor")
          |> last()
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
        records = await self._flux(query)
        result: dict[str, dict] = {}
        for r in records:
            device = r.values.get("device_id", "unknown")
            entry = {"ts": r.get_time().timestamp() if r.get_time() else time.time()}
            # Campos numéricos
            for field in ("temperature", "humidity", "pressure", "co2", "voltage", "current"):
                if field in r.values and r.values[field] is not None:
                    entry[field] = float(r.values[field])
            result[device] = entry
        return result

    async def timeseries(self, device_id: str, minutes: int = 30) -> list[dict] | None:
        """
        Serie temporal de los últimos N minutos para un dispositivo.
        Devuelve lista de {"ts": float_epoch, "value": float, "field": str}
        o None si el dispositivo no existe.
        """
        query = f"""
        from(bucket: "{settings.INFLUX_BUCKET}")
          |> range(start: -{minutes}m)
          |> filter(fn: (r) => r._measurement == "iot_sensor")
          |> filter(fn: (r) => r.device_id == "{device_id}")
          |> filter(fn: (r) => r._field == "temperature" or
                               r._field == "humidity"    or
                               r._field == "pressure"    or
                               r._field == "co2")
          |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
        """
        records = await self._flux(query)
        if not records:
            return None

        series = []
        for r in records:
            series.append({
                "ts":    r.get_time().timestamp(),
                "field": r.get_field(),
                "value": float(r.get_value()) if r.get_value() is not None else 0.0,
            })
        series.sort(key=lambda x: x["ts"])
        return series

    async def sliding_window_stats(self, device_id: str, minutes: int = 5) -> dict:
        """
        Estadísticas de ventana deslizante: mean, max, min, stddev.
        Usadas por el motor de alertas.
        """
        query = f"""
        from(bucket: "{settings.INFLUX_BUCKET}")
          |> range(start: -{minutes}m)
          |> filter(fn: (r) => r._measurement == "iot_sensor")
          |> filter(fn: (r) => r.device_id == "{device_id}")
        """
        records = await self._flux(query)
        stats: dict[str, list[float]] = {}
        for r in records:
            field = r.get_field()
            val   = r.get_value()
            if val is None:
                continue
            stats.setdefault(field, []).append(float(val))

        result = {}
        for field, vals in stats.items():
            result[field] = {
                "mean":   sum(vals) / len(vals),
                "max":    max(vals),
                "min":    min(vals),
                "count":  len(vals),
            }
        return result
