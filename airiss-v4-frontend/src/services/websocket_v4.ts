/**
 * AIRISS v4.0 WebSocket Service
 * 백엔드와 완벽히 호환되는 WebSocket 서비스
 */

export interface WebSocketMessage {
  type: 'analysis_progress' | 'analysis_completed' | 'analysis_failed' | 'analysis_started' | 'analysis_preparing' | 'connection' | 'pong' | 'alert';
  job_id?: string;
  progress?: number;
  processed?: number;
  total?: number;
  current_uid?: string;
  average_score?: number;
  status?: string;
  message?: string;
  error?: string;
  total_processed?: number;  // for analysis_completed
  data?: any;  // generic data field for backward compatibility
  level?: string;  // for alert messages (info, warning, error, success)
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 3000;
  private messageHandlers: Set<(message: WebSocketMessage) => void> = new Set();
  private isConnecting = false;
  private keepAliveInterval: number | null = null;
  private lastPingTime = 0;
  private connectionTimeoutTimer: number | null = null;

  constructor() {
    // 전역 객체로 노출 (디버깅용)
    (window as any).__airiss_ws_service = this;
  }

  async connect(clientId?: string): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('🔌 WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;

    try {
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8003';
      const wsUrl = baseUrl.replace(/^http/, 'ws');
      const id = clientId || `client-${Date.now()}`;
      const fullUrl = `${wsUrl}/connect?client_id=${id}`;
      
      console.log('🔌 Connecting to WebSocket:', fullUrl);
      
      this.ws = new WebSocket(fullUrl);
      
      // 전역 객체로 노출 (디버깅용)
      (window as any).__airiss_ws = this.ws;
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // 연결 타임아웃 타이머 제거
        if (this.connectionTimeoutTimer) {
          window.clearTimeout(this.connectionTimeoutTimer);
          this.connectionTimeoutTimer = null;
        }
        
        // Keep-alive 메커니즘 시작
        this.startKeepAlive();
        
        // 초기 Ping 메시지 전송
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', message);
          
          // pong 메시지 처리
          if (message.type === 'pong') {
            this.lastPingTime = Date.now();
          }
          
          // 모든 핸들러에게 메시지 전달
          this.messageHandlers.forEach(handler => {
            try {
              handler(message);
            } catch (error) {
              console.error('Handler error:', error);
            }
          });
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.isConnecting = false;
      };
      
      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event);
        this.isConnecting = false;
        this.ws = null;
        
        // Keep-alive 중지
        this.stopKeepAlive();
        
        // 자동 재연결 (1000은 정상 종료)
        if (this.reconnectAttempts < this.maxReconnectAttempts && event.code !== 1000) {
          this.reconnectAttempts++;
          const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000);
          console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => this.connect(clientId), delay);
        }
      };
      
      // 연결 타임아웃 설정 (10초)
      this.connectionTimeoutTimer = window.setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CONNECTING) {
          console.error('⚠️ WebSocket connection timeout');
          this.ws.close();
          this.isConnecting = false;
        }
      }, 10000);
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.isConnecting = false;
      throw error;
    }
  }
  
  private startKeepAlive(): void {
    this.stopKeepAlive();
    
    // 15초마다 ping 전송 (더 자주)
    this.keepAliveInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        const now = Date.now();
        
        // 마지막 ping 응답이 30초 이상 오래된 경우 재연결
        if (this.lastPingTime && now - this.lastPingTime > 30000) {
          console.warn('⚠️ No ping response for 30s, reconnecting...');
          this.ws.close();
          return;
        }
        
        const pingSuccess = this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
        
        if (pingSuccess) {
          console.log('🏓 Ping sent at', new Date().toISOString());
        } else {
          console.error('❌ Failed to send ping, WebSocket might be disconnected');
          this.ws.close();
        }
      }
    }, 15000); // 15초마다
  }
  
  private stopKeepAlive(): void {
    if (this.keepAliveInterval) {
      window.clearInterval(this.keepAliveInterval);
      this.keepAliveInterval = null;
    }
  }

  disconnect(): void {
    this.stopKeepAlive();
    if (this.connectionTimeoutTimer) {
      window.clearTimeout(this.connectionTimeoutTimer);
      this.connectionTimeoutTimer = null;
    }
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }
    this.messageHandlers.clear();
  }

  send(data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      return true;
    }
    console.warn('WebSocket not connected');
    return false;
  }

  addMessageHandler(handler: (message: WebSocketMessage) => void): () => void {
    this.messageHandlers.add(handler);
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get connectionState(): string {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'unknown';
    }
  }

  // 분석 작업 구독
  subscribeToAnalysis(jobId: string): void {
    this.send({
      type: 'subscribe',
      event: 'analysis_update',
      job_id: jobId
    });
  }
}

// 싱글톤 인스턴스
const wsService = new WebSocketService();
export default wsService;