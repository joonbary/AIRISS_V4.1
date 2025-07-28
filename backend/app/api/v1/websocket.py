"""
WebSocket API
실시간 통신을 위한 WebSocket 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 연결 관리"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, user_id: str = None):
        """새 연결 추가"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(client_id)
        
        logger.info(f"WebSocket connected: {client_id} (user: {user_id})")
    
    def disconnect(self, client_id: str):
        """연결 제거"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from user connections
        for user_id, connections in self.user_connections.items():
            if client_id in connections:
                connections.remove(client_id)
                if not connections:
                    del self.user_connections[user_id]
                break
        
        logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
    
    async def send_user_message(self, message: dict, user_id: str):
        """특정 사용자의 모든 연결에 메시지 전송"""
        if user_id in self.user_connections:
            for client_id in self.user_connections[user_id]:
                await self.send_personal_message(message, client_id)
    
    async def broadcast(self, message: dict):
        """모든 연결에 메시지 브로드캐스트"""
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except:
                logger.warning(f"Failed to send message to {client_id}")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, client_id: str, user_id: str = None):
    """WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, client_id, user_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to AIRISS WebSocket"
        }, client_id)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, client_id)
            
            elif data.get("type") == "subscribe":
                # Subscribe to specific events
                event_type = data.get("event")
                logger.info(f"Client {client_id} subscribed to {event_type}")
            
            elif data.get("type") == "analysis_update":
                # Forward analysis updates
                if user_id:
                    await manager.send_user_message({
                        "type": "analysis_update",
                        "data": data.get("data")
                    }, user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


@router.get("/connections")
async def get_active_connections():
    """현재 활성 연결 목록"""
    return {
        "total_connections": len(manager.active_connections),
        "connections": list(manager.active_connections.keys()),
        "users_connected": list(manager.user_connections.keys())
    }