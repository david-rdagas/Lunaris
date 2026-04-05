"""
Gestor de conexiones WebSocket activas.
Thread-safe para asyncio; no necesita locks porque el event loop es single-thread.
"""
import logging
from fastapi import WebSocket

log = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._active.append(ws)
        log.info("WS conectado. Total activos: %d", len(self._active))

    def disconnect(self, ws: WebSocket):
        self._active.discard(ws) if hasattr(self._active, "discard") else None
        try:
            self._active.remove(ws)
        except ValueError:
            pass
        log.info("WS desconectado. Total activos: %d", len(self._active))

    async def broadcast(self, message: str):
        """Envía el mensaje a todos los clientes conectados. Desconecta los caídos."""
        dead: list[WebSocket] = []
        for ws in list(self._active):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
