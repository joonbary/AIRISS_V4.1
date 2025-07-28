# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set, Optional
import json
import asyncio
from datetime import datetime

router = APIRouter()

# WebSocket client manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.client_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "job_id": job_id,
            "message": f"Connected to job {job_id}",
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_client(self, websocket: WebSocket, client_id: str, channels: list = None):
        await websocket.accept()
        self.client_connections[client_id] = websocket
        
        await websocket.send_json({
            "type": "connection_established",
            "client_id": client_id,
            "channels": channels or ["analysis", "alerts"],
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    def disconnect_client(self, client_id: str):
        if client_id in self.client_connections:
            del self.client_connections[client_id]
    
    async def send_progress(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[job_id]:
                try:
                    await websocket.send_json(data)
                except:
                    disconnected.add(websocket)
            
            for websocket in disconnected:
                self.disconnect(websocket, job_id)
    
    async def broadcast_to_job(self, job_id: str, message: dict):
        await self.send_progress(job_id, message)
    
    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.client_connections:
            try:
                await self.client_connections[client_id].send_json(message)
            except:
                self.disconnect_client(client_id)
    
    async def broadcast_to_all_clients(self, message: dict):
        disconnected = []
        for client_id, websocket in self.client_connections.items():
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect_client(client_id)

manager = ConnectionManager()

# 기존 엔드포인트 (하위 호환성)
@router.websocket("/ws/analysis/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    
    try:
        await websocket.send_json({
            "type": "status",
            "job_id": job_id,
            "message": "Waiting for analysis updates...",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        print(f"Client disconnected from job {job_id}")

# 새로운 클라이언트 기반 엔드포인트 (프론트엔드 호환)
@router.websocket("/ws/{client_id}")
async def websocket_client_endpoint(
    websocket: WebSocket, 
    client_id: str,
    channels: Optional[str] = Query(default="analysis,alerts")
):
    """프론트엔드 호환 WebSocket 엔드포인트"""
    channel_list = [ch.strip() for ch in channels.split(',') if ch.strip()]
    
    await manager.connect_client(websocket, client_id, channel_list)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # ping/pong 처리
            if data == "ping":
                await websocket.send_text("pong")
            else:
                # JSON 메시지 처리
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        })
                except json.JSONDecodeError:
                    # 텍스트 메시지로 처리
                    pass
                    
    except WebSocketDisconnect:
        manager.disconnect_client(client_id)
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect_client(client_id)
