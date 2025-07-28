import { EventEmitter } from 'events';

/**
 * AIRISS v4.0 WebSocket Integration Service
 * Provides real-time communication for analysis progress and notifications
 */

export interface WebSocketConfig {
  url?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export interface AnalysisProgress {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  current_uid?: string;
  message?: string;
  error?: string;
  timestamp?: string;
  average_score?: number;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  error?: string;
  timestamp?: string;
  job_id?: string;
  message?: string;
  progress?: number;
  processed?: number;
  total?: number;
  current_uid?: string;
  average_score?: number;
}

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isIntentionallyClosed = false;
  private clientId: string;
  private subscriptions: Set<string> = new Set();

  constructor(config?: WebSocketConfig) {
    super();
    this.config = {
      url: process.env.REACT_APP_WS_URL || 'ws://localhost:8003/ws',
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...config
    };
    this.clientId = `client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Connect to WebSocket server
   */
  connect(channels: string[] = ['analysis', 'alerts']): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.isIntentionallyClosed = false;
      const wsUrl = `${this.config.url}/${this.clientId}?channels=${channels.join(',')}`;
      
      console.log('🔌 Connecting to WebSocket:', wsUrl);

      try {
        this.ws = new WebSocket(wsUrl);
        this.setupEventHandlers();

        const connectionTimeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
          this.ws?.close();
        }, 10000);

        this.ws.onopen = () => {
          clearTimeout(connectionTimeout);
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.emit('connected');
          this.startHeartbeat();
          
          // Subscribe to channels
          channels.forEach(channel => {
            this.subscriptions.add(channel);
          });

          resolve();
        };

        this.ws.onerror = (error) => {
          clearTimeout(connectionTimeout);
          console.error('❌ WebSocket connection error:', error);
          reject(error);
        };
      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Setup WebSocket event handlers
   */
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('📨 WebSocket message:', message);
        
        // Handle different message types
        switch (message.type) {
          case 'analysis_progress':
            this.emit('progress', message);
            break;
          case 'analysis_completed':
            this.emit('completed', message);
            break;
          case 'analysis_failed':
            this.emit('failed', message);
            break;
          case 'analysis_started':
            this.emit('started', message);
            break;
          case 'pong':
            // Heartbeat response
            break;
          case 'connection_established':
            this.emit('ready', message);
            break;
          default:
            this.emit('message', message);
        }
      } catch (error) {
        console.error('❌ Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected:', event.code, event.reason);
      this.stopHeartbeat();
      this.emit('disconnected', { code: event.code, reason: event.reason });
      
      if (!this.isIntentionallyClosed && this.reconnectAttempts < this.config.maxReconnectAttempts!) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      this.emit('error', error);
    };
  }

  /**
   * Send message through WebSocket
   */
  send(message: any): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not connected');
      return false;
    }

    try {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      this.ws.send(payload);
      return true;
    } catch (error) {
      console.error('❌ Failed to send message:', error);
      return false;
    }
  }

  /**
   * Subscribe to analysis job updates
   */
  subscribeToJob(jobId: string): boolean {
    return this.send({
      type: 'subscribe',
      job_id: jobId,
      channels: ['analysis']
    });
  }

  /**
   * Unsubscribe from analysis job updates
   */
  unsubscribeFromJob(jobId: string): boolean {
    return this.send({
      type: 'unsubscribe',
      job_id: jobId
    });
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    this.isIntentionallyClosed = true;
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.emit('disconnected', { intentional: true });
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.config.reconnectInterval! * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect(Array.from(this.subscriptions)).catch(error => {
        console.error('❌ Reconnection failed:', error);
      });
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }
    }, this.config.heartbeatInterval!);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getConnectionState(): string {
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

  /**
   * Force reconnect
   */
  forceReconnect(): void {
    this.disconnect();
    setTimeout(() => {
      this.connect(Array.from(this.subscriptions)).catch(error => {
        console.error('❌ Force reconnect failed:', error);
      });
    }, 100);
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export getWebSocketService function for compatibility
export const getWebSocketService = () => websocketService;

// Export for window debugging
if (typeof window !== 'undefined') {
  (window as any).__airiss_ws_service = websocketService;
}

export default websocketService;