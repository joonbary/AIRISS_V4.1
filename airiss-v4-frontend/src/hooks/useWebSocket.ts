import { useState, useEffect, useCallback, useRef } from 'react';
import wsService, { WebSocketMessage } from '../services/websocket_v4';

interface ProgressData {
  progress: number;
  processed: number;
  total: number;
  current_uid?: string;
  average_score?: number;
  estimated_remaining?: number;
  processing_speed?: number;
  status?: string;  // Add status field
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  connectionStatus: string;
  progress: { [jobId: string]: ProgressData };
  lastMessage: WebSocketMessage | null;
  error: Error | null;
  connect: (channels?: string[]) => Promise<void>;
  disconnect: () => void;
  sendMessage: (data: any) => void;
  subscribeToJob: (jobId: string) => () => void;
  getJobProgress: (jobId: string) => ProgressData | null;
  clearError: () => void;
}

interface UseWebSocketOptions {
  baseUrl?: string;
  autoConnect?: boolean;
  channels?: string[];
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8003',
    autoConnect = false,
    channels = ['analysis', 'alerts']
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [progress, setProgress] = useState<{ [jobId: string]: ProgressData }>({});
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const unsubscribeRef = useRef<(() => void) | null>(null);
  const mountedRef = useRef(true);

  // WebSocket message handler
  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (!mountedRef.current) return;
    
    setLastMessage(message);

    // Update progress for specific job
    if (message.job_id && message.type === 'analysis_progress') {
      setProgress(prev => {
        const newProgress = { ...prev };
        const jobProgress = newProgress[message.job_id!] || {
          progress: 0,
          processed: 0,
          total: 0
        };

        // Calculate processing speed and estimated time
        const now = Date.now();
        const timeKey = `${message.job_id}_time`;
        const lastTime = (window as any)[timeKey] || now;
        const timeDiff = (now - lastTime) / 1000; // seconds
        
        if (message.processed && message.total) {
          const processedDiff = (message.processed || 0) - jobProgress.processed;
          const processingSpeed = timeDiff > 0 ? processedDiff / timeDiff : 0;
          const remaining = (message.total || 0) - (message.processed || 0);
          const estimatedRemaining = processingSpeed > 0 ? remaining / processingSpeed : 0;

          newProgress[message.job_id!] = {
            progress: message.progress || 0,
            processed: message.processed || 0,
            total: message.total || 0,
            current_uid: message.current_uid,
            average_score: message.average_score,
            processing_speed: processingSpeed,
            estimated_remaining: estimatedRemaining
          };

          (window as any)[timeKey] = now;
        }

        return newProgress;
      });
    }

    // Clear progress when analysis completes
    if (message.job_id && (message.type === 'analysis_completed' || message.type === 'analysis_failed')) {
      setProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[message.job_id!];
        return newProgress;
      });
    }
  }, []);

  // Update connection state
  const updateConnectionState = useCallback(() => {
    if (mountedRef.current) {
      setIsConnected(wsService.isConnected);
      setConnectionStatus(wsService.connectionState);
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(async (connectChannels?: string[]) => {
    try {
      setError(null);
      
      await wsService.connect();
      
      // Subscribe to all messages
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      
      unsubscribeRef.current = wsService.addMessageHandler(handleMessage);
      
      updateConnectionState();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      setError(error as Error);
    }
  }, [handleMessage, updateConnectionState]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
      unsubscribeRef.current = null;
    }
    
    wsService.disconnect();
    updateConnectionState();
  }, [updateConnectionState]);

  // Auto-connect on mount
  useEffect(() => {
    mountedRef.current = true;
    
    if (autoConnect) {
      connect();
    }

    // Monitor connection state changes
    const interval = setInterval(updateConnectionState, 1000);

    // Cleanup on unmount
    return () => {
      mountedRef.current = false;
      clearInterval(interval);
      disconnect();
    };
  }, [autoConnect, connect, disconnect, updateConnectionState]);

  // Subscribe to specific job
  const subscribeToJob = useCallback((jobId: string) => {
    wsService.subscribeToAnalysis(jobId);
    
    // Return a no-op unsubscribe function for API compatibility
    return () => {};
  }, []);

  // Send message
  const sendMessage = useCallback((message: any) => {
    return wsService.send(message);
  }, []);

  // Get job progress
  const getJobProgress = useCallback((jobId: string) => {
    return progress[jobId] || null;
  }, [progress]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isConnected,
    connectionStatus,
    progress,
    lastMessage,
    error,
    connect,
    disconnect,
    sendMessage,
    subscribeToJob,
    getJobProgress,
    clearError
  };
};

export default useWebSocket;