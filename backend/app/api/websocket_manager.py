from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Send error: {e}")

    async def broadcast(self, message: dict):
        disconnected = []
        for conn in self.active_connections:
            try:
                await conn.send_text(json.dumps(message))
            except Exception:
                disconnected.append(conn)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def send_scam_alert(alert_data: dict):
    """Send real-time scam alert to all connected clients."""
    await manager.broadcast({
        "type": "SCAM_ALERT",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    })


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time scam alerts."""
    await manager.connect(websocket)
    try:
        await manager.send_personal({
            "type": "CONNECTED",
            "message": "Connected to ScamShield real-time alerts",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get('type') == 'PING':
                    await manager.send_personal({
                        "type": "PONG",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
