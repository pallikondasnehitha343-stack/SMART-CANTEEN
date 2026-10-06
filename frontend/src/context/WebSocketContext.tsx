'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';

type MessageCallback = (data: any) => void;

interface WebSocketContextType {
  isConnected: boolean;
  subscribe: (channel: string, callback: MessageCallback) => () => void;
  send: (channel: string, message: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const socketsRef = useRef<Map<string, WebSocket>>(new Map());
  const callbacksRef = useRef<Map<string, Set<MessageCallback>>>(new Map());

  const getWsUrl = (channel: string) => {
    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    return `${baseUrl}/${channel}`;
  };

  const subscribe = useCallback((channel: string, callback: MessageCallback) => {
    if (!callbacksRef.current.has(channel)) {
      callbacksRef.current.set(channel, new Set());
    }
    callbacksRef.current.get(channel)!.add(callback);

    // Open connection for channel if not already open
    if (!socketsRef.current.has(channel)) {
      try {
        const ws = new WebSocket(getWsUrl(channel));
        
        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const listeners = callbacksRef.current.get(channel);
            if (listeners) {
              listeners.forEach((cb) => cb(data));
            }
          } catch (e) {
            console.error('WebSocket parse error:', e);
          }
        };

        ws.onclose = () => {
          socketsRef.current.delete(channel);
          if (socketsRef.current.size === 0) {
            setIsConnected(false);
          }
        };

        ws.onerror = () => {
          // Graceful fallback for mock dev
          setIsConnected(false);
        };

        socketsRef.current.set(channel, ws);
      } catch (e) {
        console.warn('Could not establish WebSocket connection:', e);
      }
    }

    // Return cleanup unsubscribe function
    return () => {
      const listeners = callbacksRef.current.get(channel);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          callbacksRef.current.delete(channel);
          const ws = socketsRef.current.get(channel);
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
          socketsRef.current.delete(channel);
        }
      }
    };
  }, []);

  const send = useCallback((channel: string, message: any) => {
    const ws = socketsRef.current.get(channel);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(typeof message === 'string' ? message : JSON.stringify(message));
    }
  }, []);

  return (
    <WebSocketContext.Provider value={{ isConnected, subscribe, send }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}
