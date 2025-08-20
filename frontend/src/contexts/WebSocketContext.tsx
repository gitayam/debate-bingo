'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '@/stores/authStore';

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  roomCode: string | null;
  roomData: RoomData | null;
  activityFeed: ActivityItem[];
  scoreboard: ScoreboardEntry[];
  joinRoom: (roomCode: string) => Promise<void>;
  createRoom: (roomConfig: CreateRoomConfig) => Promise<string>;
  markSquare: (position: number, phraseId: number) => void;
  callBingo: (pattern: string) => void;
  createDispute: (targetUserId: number, type: string, reason?: string) => void;
  voteOnDispute: (disputeId: number, vote: boolean) => void;
  leaveRoom: () => void;
}

interface RoomData {
  roomId: number;
  roomCode: string;
  name: string;
  currentPlayers: number;
  maxPlayers: number;
  gridSize: number;
  isActive: boolean;
}

interface ActivityItem {
  id: string;
  type: string;
  userId: number;
  username: string;
  message: string;
  timestamp: string;
  data?: any;
  priority?: 'low' | 'normal' | 'high' | 'critical';
  icon?: string;
  color?: string;
}

interface ScoreboardEntry {
  position: number;
  userId: number;
  username: string;
  displayName: string;
  score: number;
  squaresMarked: number;
  squaresToBingo: number;
}

interface CreateRoomConfig {
  name: string;
  maxPlayers?: number;
  isPublic?: boolean;
  gridSize?: number;
  eventId?: number;
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
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [roomCode, setRoomCode] = useState<string | null>(null);
  const [roomData, setRoomData] = useState<RoomData | null>(null);
  const [activityFeed, setActivityFeed] = useState<ActivityItem[]>([]);
  const [scoreboard, setScoreboard] = useState<ScoreboardEntry[]>([]);
  
  const { token } = useAuthStore();

  // Initialize socket connection
  useEffect(() => {
    if (!token) return;

    const initSocket = () => {
      // Only create a new socket if we don't have one
      if (socketRef.current) return;

      const socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8745', {
        path: '/ws',
        transports: ['websocket'],
        auth: {
          token
        },
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      // Connection event handlers
      socket.on('connect', () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      });

      socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      });

      socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        setIsConnected(false);
      });

      // Game event handlers
      socket.on('connected', (data) => {
        console.log('Connected to room:', data);
        if (data.data) {
          setRoomCode(data.data.room_code);
        }
      });

      socket.on('room_created', (data) => {
        console.log('Room created:', data);
        if (data.data && data.data.success) {
          setRoomCode(data.data.room_code);
          setRoomData({
            roomId: data.data.room_id,
            roomCode: data.data.room_code,
            name: data.data.room_name || 'Debate Room',
            currentPlayers: 1,
            maxPlayers: data.data.max_players || 50,
            gridSize: data.data.grid_size || 5,
            isActive: true,
          });
        }
      });

      socket.on('room_joined', (data) => {
        console.log('Room joined:', data);
        if (data.data && data.data.success) {
          setRoomData({
            roomId: data.data.room_id,
            roomCode: roomCode || '',
            name: data.data.room_name,
            currentPlayers: data.data.current_players,
            maxPlayers: 50,
            gridSize: data.data.grid_size,
            isActive: true,
          });
        }
      });

      socket.on('activity_new', (data) => {
        console.log('New activity:', data);
        const activity: ActivityItem = {
          id: `activity-${Date.now()}-${Math.random()}`,
          type: data.data.type,
          userId: data.data.user?.id || 0,
          username: data.data.user?.username || 'Unknown',
          message: data.data.message,
          timestamp: data.data.timestamp,
          data: data.data,
          priority: data.data.priority,
          icon: data.data.icon,
          color: data.data.color,
        };
        setActivityFeed(prev => [activity, ...prev].slice(0, 50)); // Keep last 50 activities
      });

      socket.on('scoreboard_update', (data) => {
        console.log('Scoreboard update:', data);
        if (data.data && data.data.rankings) {
          setScoreboard(data.data.rankings);
        }
      });

      socket.on('square_marked', (data) => {
        console.log('Square marked:', data);
        // Add to activity feed
        const activity: ActivityItem = {
          id: `mark-${Date.now()}`,
          type: 'square_marked',
          userId: data.data.user_id,
          username: data.data.username,
          message: `${data.data.username} marked "${data.data.phrase}"`,
          timestamp: data.data.timestamp,
          data: data.data,
          priority: data.data.bonus_points > 0 ? 'high' : 'normal',
          icon: 'check-square',
          color: data.data.bonus_points > 0 ? 'yellow' : 'blue',
        };
        setActivityFeed(prev => [activity, ...prev].slice(0, 50));
      });

      socket.on('bingo_called', (data) => {
        console.log('BINGO called:', data);
        const activity: ActivityItem = {
          id: `bingo-${Date.now()}`,
          type: 'bingo_called',
          userId: data.data.user_id,
          username: data.data.username,
          message: `🎉 ${data.data.username} called BINGO!`,
          timestamp: data.data.timestamp,
          data: data.data,
          priority: 'critical',
          icon: 'trophy',
          color: 'red',
        };
        setActivityFeed(prev => [activity, ...prev].slice(0, 50));
      });

      socket.on('dispute_initiated', (data) => {
        console.log('Dispute initiated:', data);
        const activity: ActivityItem = {
          id: `dispute-${Date.now()}`,
          type: 'dispute_initiated',
          userId: 0,
          username: data.data.disputer,
          message: `⚠️ ${data.data.disputer} disputed ${data.data.target}'s ${data.data.type}`,
          timestamp: data.data.timestamp,
          data: data.data,
          priority: 'high',
          icon: 'alert-triangle',
          color: 'orange',
        };
        setActivityFeed(prev => [activity, ...prev].slice(0, 50));
      });

      socket.on('error', (data) => {
        console.error('WebSocket error:', data);
      });

      socketRef.current = socket;
    };

    initSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [token]);

  // Join a room
  const joinRoom = useCallback(async (newRoomCode: string) => {
    if (!socketRef.current) {
      throw new Error('WebSocket not connected');
    }

    return new Promise<void>((resolve, reject) => {
      // First connect to the room's WebSocket namespace
      const roomSocket = io(`${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8745'}/ws/${newRoomCode}`, {
        auth: { token },
        query: { token }
      });

      roomSocket.on('connect', () => {
        console.log(`Connected to room ${newRoomCode}`);
        setRoomCode(newRoomCode);
        
        // Send join room event
        roomSocket.emit('join_room', { data: {} });
        
        // Replace the main socket with room socket
        if (socketRef.current) {
          socketRef.current.disconnect();
        }
        socketRef.current = roomSocket;
        
        resolve();
      });

      roomSocket.on('connect_error', (error) => {
        console.error(`Failed to join room ${newRoomCode}:`, error);
        reject(error);
      });
    });
  }, [token]);

  // Create a room
  const createRoom = useCallback(async (config: CreateRoomConfig): Promise<string> => {
    if (!socketRef.current) {
      throw new Error('WebSocket not connected');
    }

    return new Promise((resolve, reject) => {
      socketRef.current!.emit('create_room', {
        data: {
          name: config.name,
          max_players: config.maxPlayers || 50,
          is_public: config.isPublic !== false,
          grid_size: config.gridSize || 5,
          event_id: config.eventId,
        }
      });

      // Listen for response
      const handleRoomCreated = (data: any) => {
        if (data.data && data.data.success) {
          resolve(data.data.room_code);
        } else {
          reject(new Error(data.data?.error || 'Failed to create room'));
        }
        socketRef.current?.off('room_created', handleRoomCreated);
      };

      socketRef.current.on('room_created', handleRoomCreated);

      // Timeout after 10 seconds
      setTimeout(() => {
        socketRef.current?.off('room_created', handleRoomCreated);
        reject(new Error('Room creation timed out'));
      }, 10000);
    });
  }, []);

  // Mark a square
  const markSquare = useCallback((position: number, phraseId: number) => {
    if (!socketRef.current) return;
    
    socketRef.current.emit('square_mark', {
      data: {
        position,
        phrase_id: phraseId,
      }
    });
  }, []);

  // Call BINGO
  const callBingo = useCallback((pattern: string) => {
    if (!socketRef.current) return;
    
    socketRef.current.emit('bingo_call', {
      data: {
        pattern,
      }
    });
  }, []);

  // Create a dispute
  const createDispute = useCallback((targetUserId: number, type: string, reason?: string) => {
    if (!socketRef.current) return;
    
    socketRef.current.emit('dispute_create', {
      data: {
        target_user_id: targetUserId,
        type,
        reason,
      }
    });
  }, []);

  // Vote on a dispute
  const voteOnDispute = useCallback((disputeId: number, vote: boolean) => {
    if (!socketRef.current) return;
    
    socketRef.current.emit('dispute_vote', {
      data: {
        dispute_id: disputeId,
        vote,
      }
    });
  }, []);

  // Leave the current room
  const leaveRoom = useCallback(() => {
    if (socketRef.current && roomCode) {
      socketRef.current.emit('leave_room', {});
      setRoomCode(null);
      setRoomData(null);
      setActivityFeed([]);
      setScoreboard([]);
    }
  }, [roomCode]);

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
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};