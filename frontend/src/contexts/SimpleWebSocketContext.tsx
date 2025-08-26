'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';

interface WebSocketContextType {
  socket: WebSocket | null;
  isConnected: boolean;
  roomCode: string | null;
  roomData: any | null;
  activityFeed: any[];
  scoreboard: any[];
  joinRoom: (roomCode: string) => Promise<void>;
  createRoom: (roomConfig: any) => Promise<string>;
  markSquare: (position: number, phraseId: number) => void;
  callBingo: (pattern: string) => void;
  createDispute: (targetUserId: number, type: string, reason?: string) => void;
  voteOnDispute: (disputeId: number, vote: boolean) => void;
  leaveRoom: () => void;
  debugInfo: string;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const socketRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [roomCode, setRoomCode] = useState<string | null>(null);
  const [roomData, setRoomData] = useState<any | null>(null);
  const [activityFeed, setActivityFeed] = useState<any[]>([]);
  const [scoreboard, setScoreboard] = useState<any[]>([]);
  const [debugInfo, setDebugInfo] = useState<string>('Initializing...');
  
  const { accessToken: token } = useAuthStore();

  // Initialize WebSocket connection
  useEffect(() => {
    if (!token) {
      setDebugInfo('No auth token available');
      console.log('[WebSocket] No token, skipping connection');
      return;
    }

    const connectWebSocket = () => {
      try {
        // Use the raw WebSocket endpoint
        const wsUrl = `ws://localhost:8745/ws/LOBBY?token=${encodeURIComponent(token)}`;
        console.log('[WebSocket] Attempting connection to:', wsUrl);
        setDebugInfo(`Connecting to ${wsUrl}...`);

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('[WebSocket] Connection opened');
          setIsConnected(true);
          setDebugInfo('Connected to WebSocket');
          socketRef.current = ws;
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('[WebSocket] Message received:', data);
            setDebugInfo(`Last message: ${data.event || 'unknown'}`);

            // Handle different event types
            switch (data.event) {
              case 'connected':
                console.log('[WebSocket] Connected event:', data);
                if (data.data?.room_code) {
                  setRoomCode(data.data.room_code);
                }
                break;

              case 'room_created':
                console.log('[WebSocket] Room created:', data);
                if (data.data?.success) {
                  setRoomCode(data.data.room_code);
                  setRoomData(data.data);
                }
                break;

              case 'activity_new':
                console.log('[WebSocket] New activity:', data);
                setActivityFeed(prev => [data.data, ...prev].slice(0, 50));
                break;

              case 'scoreboard_update':
                console.log('[WebSocket] Scoreboard update:', data);
                if (data.data?.rankings) {
                  setScoreboard(data.data.rankings);
                }
                break;

              default:
                console.log('[WebSocket] Unknown event:', data);
            }
          } catch (error) {
            console.error('[WebSocket] Error parsing message:', error);
            setDebugInfo(`Error: ${error}`);
          }
        };

        ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          setDebugInfo(`WebSocket error: ${error}`);
          setIsConnected(false);
        };

        ws.onclose = (event) => {
          console.log('[WebSocket] Connection closed:', event.code, event.reason);
          setDebugInfo(`Disconnected: ${event.reason || 'Connection lost'}`);
          setIsConnected(false);
          socketRef.current = null;

          // Attempt to reconnect after 3 seconds
          if (event.code !== 1000) { // 1000 = normal closure
            setTimeout(() => {
              console.log('[WebSocket] Attempting to reconnect...');
              connectWebSocket();
            }, 3000);
          }
        };

      } catch (error) {
        console.error('[WebSocket] Connection error:', error);
        setDebugInfo(`Connection error: ${error}`);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        console.log('[WebSocket] Closing connection...');
        socketRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [token]);

  // Send a message to the WebSocket
  const sendMessage = useCallback((event: string, data: any = {}) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ event, data });
      console.log('[WebSocket] Sending:', message);
      socketRef.current.send(message);
    } else {
      console.warn('[WebSocket] Cannot send message, not connected');
      setDebugInfo('Cannot send - not connected');
    }
  }, []);

  // Join a room
  const joinRoom = useCallback(async (newRoomCode: string) => {
    console.log('[WebSocket] Joining room:', newRoomCode);
    setDebugInfo(`Joining room ${newRoomCode}...`);
    
    // For now, we'll reconnect to the WebSocket with the room code
    if (socketRef.current) {
      socketRef.current.close(1000, 'Switching rooms');
    }

    const wsUrl = `ws://localhost:8745/ws/${newRoomCode}?token=${encodeURIComponent(token || '')}`;
    const ws = new WebSocket(wsUrl);
    
    return new Promise<void>((resolve, reject) => {
      ws.onopen = () => {
        console.log('[WebSocket] Connected to room:', newRoomCode);
        setRoomCode(newRoomCode);
        socketRef.current = ws;
        setIsConnected(true);
        sendMessage('join_room', {});
        resolve();
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Failed to join room:', error);
        reject(error);
      };
    });
  }, [token, sendMessage]);

  // Create a room
  const createRoom = useCallback(async (config: any): Promise<string> => {
    console.log('[WebSocket] Creating room:', config);
    setDebugInfo('Creating room...');
    
    return new Promise((resolve, reject) => {
      sendMessage('create_room', config);
      
      // Listen for response
      const timeout = setTimeout(() => {
        reject(new Error('Room creation timed out'));
      }, 10000);

      const handleMessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'room_created') {
            clearTimeout(timeout);
            if (data.data?.success) {
              resolve(data.data.room_code);
            } else {
              reject(new Error(data.data?.error || 'Failed to create room'));
            }
            socketRef.current?.removeEventListener('message', handleMessage);
          }
        } catch (error) {
          console.error('[WebSocket] Error handling room creation:', error);
        }
      };

      if (socketRef.current) {
        socketRef.current.addEventListener('message', handleMessage);
      } else {
        clearTimeout(timeout);
        reject(new Error('WebSocket not connected'));
      }
    });
  }, [sendMessage]);

  // Mark a square
  const markSquare = useCallback((position: number, phraseId: number) => {
    sendMessage('square_mark', { position, phrase_id: phraseId });
  }, [sendMessage]);

  // Call BINGO
  const callBingo = useCallback((pattern: string) => {
    sendMessage('bingo_call', { pattern });
  }, [sendMessage]);

  // Create a dispute
  const createDispute = useCallback((targetUserId: number, type: string, reason?: string) => {
    sendMessage('dispute_create', { target_user_id: targetUserId, type, reason });
  }, [sendMessage]);

  // Vote on a dispute
  const voteOnDispute = useCallback((disputeId: number, vote: boolean) => {
    sendMessage('dispute_vote', { dispute_id: disputeId, vote });
  }, [sendMessage]);

  // Leave the current room
  const leaveRoom = useCallback(() => {
    console.log('[WebSocket] Leaving room');
    setDebugInfo('Leaving room...');
    if (socketRef.current) {
      socketRef.current.close(1000, 'Leaving room');
    }
    setRoomCode(null);
    setRoomData(null);
    setActivityFeed([]);
    setScoreboard([]);
  }, []);

  const value: WebSocketContextType = {
    socket: socketRef.current,
    isConnected,
    roomCode,
    roomData,
    activityFeed,
    scoreboard,
    joinRoom,
    createRoom,
    markSquare,
    callBingo,
    createDispute,
    voteOnDispute,
    leaveRoom,
    debugInfo,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};