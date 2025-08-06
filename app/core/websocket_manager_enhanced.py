"""
강화된 WebSocket 매니저 - 실시간 상태 동기화 보장
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)

class WebSocketChannel(str, Enum):
    """WebSocket 채널 정의"""
    WORKFLOW = "workflow"
    ANALYSIS = "analysis"
    ALERTS = "alerts"
    SYSTEM = "system"
    USER = "user"

class WebSocketMessageType(str, Enum):
    """메시지 타입 정의"""
    STATUS_UPDATE = "status_update"
    PROGRESS_UPDATE = "progress_update"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"
    DOWNLOAD_READY = "download_ready"
    TASK_UPDATE = "task_update"

class ConnectionManager:
    """WebSocket 연결 관리"""
    
    def __init__(self):
        # 채널별 연결 관리
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            channel.value: {} for channel in WebSocketChannel
        }
        # 사용자별 연결 매핑
        self.user_connections: Dict[str, Set[str]] = {}
        # 메시지 큐 (연결이 끊긴 경우 재전송용)
        self.message_queue: Dict[str, list] = {}
        # 하트비트 관리
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, 
                     user_id: Optional[str] = None, channels: list = None):
        """WebSocket 연결"""
        await websocket.accept()
        
        # 기본 채널 설정
        if not channels:
            channels = [WebSocketChannel.WORKFLOW, WebSocketChannel.ALERTS]
            
        # 채널별 연결 추가
        for channel in channels:
            channel_name = channel.value if isinstance(channel, WebSocketChannel) else channel
            self.active_connections[channel_name][client_id] = websocket
            
        # 사용자 연결 매핑
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(client_id)
            
        # 하트비트 시작
        self.heartbeat_tasks[client_id] = asyncio.create_task(
            self._heartbeat(websocket, client_id)
        )
        
        # 대기 중인 메시지 전송
        if client_id in self.message_queue:
            for message in self.message_queue[client_id]:
                await self.send_personal_message(message, websocket)
            del self.message_queue[client_id]
            
        logger.info(f"WebSocket connected: {client_id} (user: {user_id})")
        
        # 연결 확인 메시지
        await self.send_personal_message({
            "type": WebSocketMessageType.INFO,
            "message": "Connected to AIRISS WebSocket",
            "timestamp": datetime.utcnow().isoformat(),
            "channels": channels
        }, websocket)
        
    async def disconnect(self, client_id: str):
        """WebSocket 연결 해제"""
        # 하트비트 태스크 취소
        if client_id in self.heartbeat_tasks:
            self.heartbeat_tasks[client_id].cancel()
            del self.heartbeat_tasks[client_id]
            
        # 모든 채널에서 제거
        for channel in self.active_connections.values():
            if client_id in channel:
                del channel[client_id]
                
        # 사용자 연결 매핑 제거
        for user_id, connections in self.user_connections.items():
            if client_id in connections:
                connections.remove(client_id)
                if not connections:
                    del self.user_connections[user_id]
                break
                
        logger.info(f"WebSocket disconnected: {client_id}")
        
    async def _heartbeat(self, websocket: WebSocket, client_id: str):
        """하트비트 전송 (연결 상태 확인)"""
        try:
            while True:
                await asyncio.sleep(30)  # 30초마다
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
        except WebSocketDisconnect:
            await self.disconnect(client_id)
        except Exception as e:
            logger.error(f"Heartbeat error for {client_id}: {e}")
            await self.disconnect(client_id)
            
    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """개인 메시지 전송"""
        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            else:
                await websocket.send_text(str(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            
    async def send_to_client(self, message: Any, client_id: str):
        """특정 클라이언트에 메시지 전송"""
        sent = False
        
        for channel in self.active_connections.values():
            if client_id in channel:
                websocket = channel[client_id]
                await self.send_personal_message(message, websocket)
                sent = True
                break
                
        if not sent:
            # 연결이 없으면 큐에 저장
            if client_id not in self.message_queue:
                self.message_queue[client_id] = []
            self.message_queue[client_id].append(message)
            logger.info(f"Message queued for offline client: {client_id}")
            
    async def send_to_user(self, message: Any, user_id: str):
        """특정 사용자의 모든 연결에 메시지 전송"""
        if user_id in self.user_connections:
            for client_id in self.user_connections[user_id]:
                await self.send_to_client(message, client_id)
                
    async def broadcast_to_channel(self, message: Any, channel: WebSocketChannel):
        """특정 채널의 모든 연결에 브로드캐스트"""
        channel_name = channel.value if isinstance(channel, WebSocketChannel) else channel
        
        if channel_name in self.active_connections:
            disconnected_clients = []
            
            for client_id, websocket in self.active_connections[channel_name].items():
                try:
                    await self.send_personal_message(message, websocket)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {client_id}: {e}")
                    disconnected_clients.append(client_id)
                    
            # 연결이 끊긴 클라이언트 제거
            for client_id in disconnected_clients:
                await self.disconnect(client_id)
                
    async def broadcast_to_all(self, message: Any):
        """모든 연결에 브로드캐스트"""
        for channel in WebSocketChannel:
            await self.broadcast_to_channel(message, channel)

class EnhancedWebSocketManager:
    """강화된 WebSocket 매니저"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self._status_cache: Dict[str, Any] = {}  # 상태 캐시
        
    async def handle_connection(self, websocket: WebSocket, client_id: str, 
                               user_id: Optional[str] = None):
        """WebSocket 연결 처리"""
        try:
            # 연결 수락
            await self.connection_manager.connect(websocket, client_id, user_id)
            
            # 메시지 수신 루프
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self._handle_message(message, client_id, user_id)
                
        except WebSocketDisconnect:
            await self.connection_manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
            await self.connection_manager.disconnect(client_id)
            
    async def _handle_message(self, message: Dict, client_id: str, 
                             user_id: Optional[str]):
        """클라이언트 메시지 처리"""
        msg_type = message.get('type')
        
        if msg_type == 'subscribe':
            # 채널 구독
            channels = message.get('channels', [])
            logger.info(f"Client {client_id} subscribing to: {channels}")
            
        elif msg_type == 'get_status':
            # 상태 요청
            job_id = message.get('job_id')
            if job_id and job_id in self._status_cache:
                await self.connection_manager.send_to_client(
                    self._status_cache[job_id], client_id
                )
                
        elif msg_type == 'ping':
            # Ping 응답
            await self.connection_manager.send_to_client({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            }, client_id)
            
    async def notify_workflow_status(self, job_id: str, status: str, 
                                   progress: float, details: Dict = None):
        """워크플로우 상태 알림"""
        message = {
            'type': WebSocketMessageType.STATUS_UPDATE,
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        # 캐시 업데이트
        self._status_cache[job_id] = message
        
        # 워크플로우 채널에 브로드캐스트
        await self.connection_manager.broadcast_to_channel(
            message, WebSocketChannel.WORKFLOW
        )
        
        logger.info(f"Workflow status update: {job_id} -> {status} ({progress}%)")
        
    async def notify_task_update(self, job_id: str, task_id: str, 
                               task_name: str, status: str):
        """개별 태스크 업데이트 알림"""
        message = {
            'type': WebSocketMessageType.TASK_UPDATE,
            'job_id': job_id,
            'task_id': task_id,
            'task_name': task_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.connection_manager.broadcast_to_channel(
            message, WebSocketChannel.WORKFLOW
        )
        
    async def notify_download_ready(self, job_id: str, download_url: str, 
                                  user_id: str):
        """다운로드 준비 완료 알림"""
        message = {
            'type': WebSocketMessageType.DOWNLOAD_READY,
            'job_id': job_id,
            'download_url': download_url,
            'timestamp': datetime.utcnow().isoformat(),
            'message': '분석이 완료되었습니다. 결과를 다운로드할 수 있습니다.'
        }
        
        # 해당 사용자에게만 전송
        await self.connection_manager.send_to_user(message, user_id)
        
        # 알림 채널에도 브로드캐스트
        await self.connection_manager.broadcast_to_channel(
            message, WebSocketChannel.ALERTS
        )
        
        logger.info(f"Download ready notification sent: {job_id} -> {user_id}")
        
    async def notify_error(self, job_id: str, error_message: str, 
                         user_id: Optional[str] = None, technical_details: Dict = None):
        """오류 알림"""
        message = {
            'type': WebSocketMessageType.ERROR,
            'job_id': job_id,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat(),
            'technical_details': technical_details
        }
        
        if user_id:
            # 특정 사용자에게 전송
            await self.connection_manager.send_to_user(message, user_id)
        else:
            # 알림 채널에 브로드캐스트
            await self.connection_manager.broadcast_to_channel(
                message, WebSocketChannel.ALERTS
            )
            
        logger.error(f"Error notification: {job_id} - {error_message}")
        
    async def notify_system_event(self, event_type: str, message: str, 
                                details: Dict = None):
        """시스템 이벤트 알림"""
        event_message = {
            'type': WebSocketMessageType.INFO,
            'event_type': event_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        # 시스템 채널에 브로드캐스트
        await self.connection_manager.broadcast_to_channel(
            event_message, WebSocketChannel.SYSTEM
        )
        
    def get_connection_stats(self) -> Dict:
        """연결 통계 조회"""
        total_connections = sum(
            len(channel) for channel in self.connection_manager.active_connections.values()
        )
        
        channel_stats = {
            channel: len(connections)
            for channel, connections in self.connection_manager.active_connections.items()
        }
        
        return {
            'total_connections': total_connections,
            'active_users': len(self.connection_manager.user_connections),
            'channels': channel_stats,
            'queued_messages': sum(
                len(messages) for messages in self.connection_manager.message_queue.values()
            )
        }

# 전역 WebSocket 매니저 인스턴스
_websocket_manager = None

def get_websocket_manager() -> EnhancedWebSocketManager:
    """싱글톤 WebSocket 매니저 반환"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = EnhancedWebSocketManager()
    return _websocket_manager