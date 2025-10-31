/**
 * WebSocket Hook
 * VELOX Trading Platform
 */
import { useEffect, useCallback } from 'react';
import { wsClient } from '../services/websocket';
import { authService } from '../services/auth';

export const useWebSocket = () => {
  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      wsClient.connect(token);
    }

    return () => {
      wsClient.disconnect();
    };
  }, []);

  const subscribe = useCallback((streams: string[], filters?: any) => {
    wsClient.subscribe(streams, filters);
  }, []);

  const unsubscribe = useCallback((streams: string[]) => {
    wsClient.unsubscribe(streams);
  }, []);

  const on = useCallback((messageType: string, handler: (data: any) => void) => {
    wsClient.on(messageType, handler);
  }, []);

  const off = useCallback((messageType: string) => {
    wsClient.off(messageType);
  }, []);

  return { subscribe, unsubscribe, on, off };
};
