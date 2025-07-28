import { EventEmitter } from 'events';

export interface AnalysisProgress {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  currentEmployee?: string;
  message?: string;
  error?: string;
}

export interface AnalysisResult {
  uid: string;
  overall_score: number;
  grade: string;
  dimension_scores: Record<string, number>;
}

export interface WebSocketMessage {
  type:
    | 'progress'
    | 'result'
    | 'complete'
    | 'error'
    | 'alert'
    | 'notification'
    | 'connection_established'
    | 'pong'
    | 'ready';
  data?: any;
  error?: string;
  message?: string;
  timestamp?: string;
}

class RobustWebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 3000; // 3초부터 시작
  private maxReconnectInterval: number = 30000; // 최대 30초
  private reconnectDecay: number = 1.5; // 재연결 간격 증가 비율
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectTimer?: NodeJS.Timeout;
  private pingTimer?: NodeJS.Timeout;
  private url: string;
  private clientId: string;
  private isConnecting: boolean = false;
  private shouldReconnect: boolean = true;
  private channels: string[] = [];

  constructor() {
    super();
    
    // 환경별 WebSocket URL 설정
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const wsPort = process.env.REACT_APP_WS_PORT || '8003';
    
    // 개발/운영 환경 자동 감지
    if (host === 'localhost' || host === '127.0.0.1') {
      this.url = `ws://localhost:${wsPort}/ws`;
    } else {
      this.url = `${protocol}//${host}:${wsPort}/ws`;
    }
    
    // 환경변수 우선 사용
    this.url = process.env.REACT_APP_WS_URL || this.url;
    
    this.clientId = this.generateClientId();
    
    console.log('🔧 WebSocket Service 초기화');
    console.log('📍 Base URL:', this.url);
    console.log('👤 Client ID:', this.clientId);
  }

  private generateClientId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    const userAgent = navigator.userAgent.slice(0, 10).replace(/[^a-zA-Z0-9]/g, '');
    return `airiss-${userAgent}-${timestamp}-${random}`;
  }

  connect(channels: string[] = ['analysis', 'alerts']): void {
    if (this.isConnecting) {
      console.log('🔄 이미 연결 시도 중...');
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ 이미 연결됨');
      return;
    }

    this.isConnecting = true;
    this.channels = channels;
    this.shouldReconnect = true;
    
    const channelsParam = channels.join(',');
    const wsUrl = `${this.url}/${this.clientId}?channels=${channelsParam}`;
    
    console.log(`🔌 WebSocket 연결 시도: ${wsUrl}`);
    console.log(`📡 채널: ${channels.join(', ')}`);
    console.log(`🔄 재연결 시도: ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupWebSocketEvents();
    } catch (error) {
      console.error('❌ WebSocket 생성 실패:', error);
      this.isConnecting = false;
      this.emit('error', error);
      this.scheduleReconnect();
    }
  }

  private setupWebSocketEvents(): void {
    if (!this.ws) return;

    // 연결 성공
    this.ws.onopen = () => {
      console.log('✅ WebSocket 연결 성공!');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.reconnectInterval = 3000; // 재연결 간격 초기화
      
      this.emit('connected');
      this.clearReconnectTimer();
      this.startPingInterval();
      
      // 연결 확인 메시지 전송
      this.send({
        type: 'ping',
        message: 'Connection established'
      });
    };

    // 메시지 수신
    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('📨 WebSocket 메시지 수신:', data.type, data);
        this.handleMessage(data);
      } catch (error) {
        console.error('❌ 메시지 파싱 오류:', error);
        console.log('📄 원본 데이터:', event.data);
      }
    };

    // 연결 오류
    this.ws.onerror = (error) => {
      console.error('❌ WebSocket 오류:', error);
      
      // 상세한 오류 정보 수집
      const errorInfo = {
        readyState: this.ws?.readyState,
        url: this.ws?.url,
        protocol: this.ws?.protocol,
        timestamp: new Date().toISOString(),
        reconnectAttempts: this.reconnectAttempts
      };
      
      console.error('🔍 오류 상세 정보:', errorInfo);
      
      this.isConnecting = false;
      this.emit('error', {
        message: 'WebSocket 연결 오류',
        details: errorInfo,
        originalError: error
      });
      
      // 네트워크 오류일 가능성이 높으므로 재연결 시도
      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    };

    // 연결 종료
    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket 연결 종료:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });
      
      this.isConnecting = false;
      this.stopPingInterval();
      
      this.emit('disconnected', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });
      
      // 정상 종료(1000)가 아닌 경우 재연결
      if (this.shouldReconnect && event.code !== 1000) {
        console.log('🔄 비정상 종료 감지 - 재연결 시도');
        this.scheduleReconnect();
      }
    };
  }

  private handleMessage(data: WebSocketMessage): void {
    switch (data.type) {
      case 'progress':
        this.emit('progress', data.data as AnalysisProgress);
        break;
      case 'result':
        this.emit('result', data.data as AnalysisResult);
        break;
      case 'complete':
        console.log('🎉 분석 완료:', data.data);
        this.emit('complete', data.data);
        break;
      case 'error':
        console.error('📨 서버 오류:', data.error || data.message);
        this.emit('serverError', data.error || data.message);
        break;
      case 'alert':
        this.emit('alert', data.data);
        break;
      case 'notification':
        this.emit('notification', data.data);
        break;
      case 'connection_established':
      case 'ready':
        console.log('🎯 연결 준비 완료:', data);
        this.emit('ready', data);
        break;
      case 'pong':
        console.log('🏓 Pong 수신 - 연결 유지됨');
        break;
      default:
        console.warn('⚠️ 알 수 없는 메시지 타입:', data.type);
        this.emit('message', data);
        break;
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ 최대 재연결 시도 횟수 초과');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.clearReconnectTimer();
    
    // 지수 백오프: 재연결 간격을 점진적으로 증가
    const currentInterval = Math.min(
      this.reconnectInterval * Math.pow(this.reconnectDecay, this.reconnectAttempts),
      this.maxReconnectInterval
    );
    
    console.log(`🔄 ${currentInterval}ms 후 재연결 시도 (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
    
    this.reconnectTimer = setTimeout(() => {
      if (this.shouldReconnect) {
        this.reconnectAttempts++;
        console.log(`🔄 재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.connect(this.channels);
      }
    }, currentInterval);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    
    // 30초마다 ping 전송하여 연결 유지
    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      } else {
        console.warn('⚠️ Ping 중단 - WebSocket 연결 없음');
        this.stopPingInterval();
      }
    }, 30000);
  }

  private stopPingInterval(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = undefined;
    }
  }

  disconnect(): void {
    console.log('🔌 WebSocket 연결 해제');
    this.shouldReconnect = false;
    this.clearReconnectTimer();
    this.stopPingInterval();
    
    if (this.ws) {
      // 정상 종료 코드로 연결 해제
      this.ws.close(1000, 'Normal closure by client');
      this.ws = null;
    }
    
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  send(data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const message = {
          ...data,
          timestamp: new Date().toISOString(),
          client_id: this.clientId
        };
        
        this.ws.send(JSON.stringify(message));
        console.log('📤 메시지 전송:', message.type || 'unknown');
        return true;
      } catch (error) {
        console.error('❌ 메시지 전송 실패:', error);
        this.emit('error', error);
        return false;
      }
    } else {
      const state = this.ws?.readyState;
      console.error(`❌ WebSocket 연결되지 않음 (상태: ${state})`);
      
      // 연결이 끊어진 경우 재연결 시도
      if (this.shouldReconnect && !this.isConnecting) {
        console.log('🔄 메시지 전송 실패로 인한 재연결 시도');
        this.connect(this.channels);
      }
      
      return false;
    }
  }

  // 분석 시작 알림
  notifyAnalysisStart(jobId: string): void {
    this.send({
      type: 'analysis_start',
      jobId,
      message: 'Analysis started'
    });
  }

  // 채널 구독
  subscribeToChannel(channel: string): void {
    this.send({
      type: 'subscribe',
      channel
    });
  }

  // 연결 상태 확인
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // 연결 상태 문자열
  getConnectionStatus(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }

  // 재연결 수동 시도
  forceReconnect(): void {
    console.log('🔄 강제 재연결 시도');
    this.disconnect();
    setTimeout(() => {
      this.connect(this.channels);
    }, 1000);
  }

  // 상태 정보 반환
  getStatus() {
    return {
      clientId: this.clientId,
      url: this.url,
      isConnected: this.isConnected(),
      connectionStatus: this.getConnectionStatus(),
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      shouldReconnect: this.shouldReconnect,
      channels: this.channels,
      isConnecting: this.isConnecting
    };
  }

  // 연결 테스트
  async testConnection(): Promise<boolean> {
    return new Promise((resolve) => {
      if (this.isConnected()) {
        resolve(true);
        return;
      }

      const testHandler = () => {
        this.removeListener('connected', testHandler);
        this.removeListener('error', errorHandler);
        resolve(true);
      };

      const errorHandler = () => {
        this.removeListener('connected', testHandler);
        this.removeListener('error', errorHandler);
        resolve(false);
      };

      this.once('connected', testHandler);
      this.once('error', errorHandler);

      this.connect(this.channels);

      // 10초 타임아웃
      setTimeout(() => {
        this.removeListener('connected', testHandler);
        this.removeListener('error', errorHandler);
        resolve(false);
      }, 10000);
    });
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
const robustWebSocketService = new RobustWebSocketService();

// 전역 디버깅을 위해 window에 등록
if (typeof window !== 'undefined') {
  (window as any).__airiss_ws = robustWebSocketService;
  (window as any).webSocketService = robustWebSocketService;
}

export default robustWebSocketService;
