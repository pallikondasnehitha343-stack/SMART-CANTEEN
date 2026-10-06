import json
from typing import Dict, Set, Any
from fastapi import WebSocket

class ConnectionManager:
    """
    Multi-channel WebSocket Connection Manager for real-time canteen orchestration.
    Channels:
    - 'order:{order_id}'  -> Student live tracking & QR token delivery
    - 'queue:updates'      -> Live queue positions & dynamic ETAs
    - 'kitchen:kds'        -> Live Kitchen Display System Kanban
    - 'admin:metrics'      -> Live peak status & operational throughput
    """
    def __init__(self):
        # Map of channel_name -> Set[WebSocket]
        self.active_channels: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_channels:
            self.active_channels[channel] = set()
        self.active_channels[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_channels and websocket in self.active_channels[channel]:
            self.active_channels[channel].remove(websocket)
            if not self.active_channels[channel]:
                del self.active_channels[channel]

    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast JSON message to all active listeners on the specified channel"""
        if channel in self.active_channels:
            disconnected_sockets = set()
            for connection in self.active_channels[channel]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected_sockets.add(connection)
            for dead_sock in disconnected_sockets:
                self.active_channels[channel].remove(dead_sock)

    async def broadcast_order_update(self, order_id: int, data: Dict[str, Any]):
        """Broadcast update to order tracking page and kitchen display"""
        await self.broadcast(f"order:{order_id}", data)
        await self.broadcast("kitchen:kds", {"event": "ORDER_UPDATED", "order": data})
        await self.broadcast("queue:updates", {"event": "QUEUE_SYNC", "order_id": order_id})

    async def broadcast_queue_update(self, summary_data: Dict[str, Any]):
        """Broadcast live queue shifts"""
        await self.broadcast("queue:updates", {"event": "QUEUE_SUMMARY", "data": summary_data})
        await self.broadcast("kitchen:kds", {"event": "QUEUE_SYNC", "data": summary_data})

ws_manager = ConnectionManager()
