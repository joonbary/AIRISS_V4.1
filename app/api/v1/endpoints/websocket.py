"""
WebSocket API
실시간 통신을 위한 WebSocket 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging
import asyncio

# 중앙 WebSocket Manager 사용
from app.core.websocket_manager import manager, ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 연결 엔드포인트"""
    # 채널 리스트 설정 (기본적으로 분석 채널 구독)
    channels = ["analysis", "alerts"]
    
    try:
        await manager.connect(websocket, client_id, channels)
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to AIRISS WebSocket",
            "channels": channels
        }, client_id)
        
        # Listen for messages with timeout
        while True:
            try:
                # WebSocket 메시지를 기다리되, 타임아웃 설정
                # receive_json()이 블로킹되는 것을 방지하기 위해 receive_text() 사용
                websocket_data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # 60초 타임아웃 (Railway 환경 고려)
                )
                
                # JSON 파싱
                try:
                    data = json.loads(websocket_data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {client_id}: {websocket_data}")
                    continue
                
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
                    
            except asyncio.TimeoutError:
                # 타임아웃 발생 시 ping 체크
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    # ping 실패 시 연결 종료
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in websocket loop for {client_id}: {e}")
                break
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected (WebSocketDisconnect)")
    except asyncio.CancelledError:
        logger.info(f"Client {client_id} connection cancelled")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        # 연결 종료 시 처리
        manager.disconnect(client_id)
        try:
            await websocket.close()
        except:
            pass


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