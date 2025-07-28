"""
WebSocket API
실시간 통신을 위한 WebSocket 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging

# 중앙 WebSocket Manager 사용
from app.core.websocket_manager import manager, ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 연결 엔드포인트"""
    # 채널 리스트 설정 (기본적으로 분석 채널 구독)
    channels = ["analysis", "alerts"]
    
    await manager.connect(websocket, client_id, channels)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to AIRISS WebSocket",
            "channels": channels
        }, client_id)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type", "")
            
            if message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, client_id)
            
            elif message_type == "subscribe":
                # Subscribe to specific channels
                new_channels = data.get("channels", [])
                for channel in new_channels:
                    if channel in manager.channel_subscribers and client_id not in manager.channel_subscribers[channel]:
                        manager.channel_subscribers[channel].append(client_id)
                
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "channels": new_channels
                }, client_id)
            
            elif message_type == "analysis_update":
                # Forward analysis updates to analysis channel
                await manager.send_analysis_progress(
                    data.get("job_id", ""),
                    data.get("data", {})
                )
            
            else:
                # Echo back for unknown message types
                await manager.send_personal_message({
                    "type": "echo",
                    "original": data
                }, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


@router.websocket("/ws")
async def websocket_endpoint_alt(websocket: WebSocket):
    """Alternative WebSocket endpoint for compatibility"""
    import uuid
    client_id = str(uuid.uuid4())
    await websocket_endpoint(websocket, client_id)


@router.get("/connections")
async def get_active_connections():
    """현재 활성 연결 목록"""
    return manager.get_connection_info()