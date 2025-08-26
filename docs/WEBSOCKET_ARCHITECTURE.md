# WebSocket Architecture for Real-Time Debate Bingo

## Overview
Real-time bidirectional communication architecture using Socket.io, Redis Pub/Sub, and FastAPI for scalable multiplayer gameplay.

## Architecture Diagram
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client 1  │     │   Client 2  │     │   Client N  │
│  Browser/App│     │  Browser/App│     │  Browser/App│
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                          │
                    WebSocket (WSS)
                          │
                    ┌─────▼─────┐
                    │  NGINX LB  │ (Sticky Sessions)
                    └─────┬─────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │  WS Node │      │  WS Node │      │  WS Node │
   │  Server  │      │  Server  │      │  Server  │
   └────┬────┘      └────┬────┘      └────┬────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ┌─────▼─────┐
                    │   Redis   │ (Pub/Sub)
                    │  Cluster  │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  FastAPI  │
                    │  Backend  │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │PostgreSQL │
                    └───────────┘
```

## WebSocket Events Specification

### Connection Events
```typescript
// Client → Server
interface ConnectionEvents {
  'connect': {
    token: string;
    roomCode?: string;
  };
  
  'disconnect': {
    reason: string;
  };
  
  'ping': {
    timestamp: number;
  };
}

// Server → Client
interface ConnectionResponses {
  'connected': {
    userId: number;
    sessionId: string;
  };
  
  'pong': {
    timestamp: number;
    latency: number;
  };
  
  'error': {
    code: string;
    message: string;
  };
}
```

### Room Events
```typescript
// Client → Server
interface RoomEvents {
  'room:create': {
    eventId: number;
    name: string;
    isPublic: boolean;
    maxPlayers: number;
  };
  
  'room:join': {
    roomCode: string;
    password?: string;
  };
  
  'room:leave': {};
  
  'room:ready': {
    ready: boolean;
  };
}

// Server → Client
interface RoomBroadcasts {
  'room:created': {
    roomId: number;
    roomCode: string;
  };
  
  'room:joined': {
    room: Room;
    participants: Participant[];
    yourCard: BingoCard;
  };
  
  'room:userJoined': {
    user: Participant;
    totalPlayers: number;
  };
  
  'room:userLeft': {
    userId: number;
    totalPlayers: number;
  };
  
  'room:started': {
    startTime: string;
    endTime?: string;
  };
}
```

### Game Events
```typescript
// Client → Server
interface GameEvents {
  'square:mark': {
    squareId: number;
    phraseId: number;
    position: number;
  };
  
  'square:unmark': {
    squareId: number;
  };
  
  'bingo:call': {
    pattern: 'row' | 'column' | 'diagonal' | 'full';
    squares: number[];
  };
  
  'dispute:create': {
    targetUserId: number;
    targetSquareId?: number;
    type: 'square' | 'bingo';
    reason: string;
  };
  
  'dispute:vote': {
    disputeId: number;
    vote: boolean; // true = uphold, false = reject
  };
}

// Server → Client  
interface GameBroadcasts {
  'square:marked': {
    userId: number;
    username: string;
    squareId: number;
    phrase: string;
    timestamp: string;
  };
  
  'square:unmarked': {
    userId: number;
    squareId: number;
  };
  
  'bingo:called': {
    userId: number;
    username: string;
    pattern: string;
    verificationId: string;
  };
  
  'bingo:verified': {
    winnerId: number;
    winner: string;
    pattern: string;
    finalRankings: Ranking[];
  };
  
  'dispute:initiated': {
    dispute: Dispute;
    timeRemaining: number;
  };
  
  'dispute:update': {
    disputeId: number;
    votesFor: number;
    votesAgainst: number;
    timeRemaining: number;
  };
  
  'dispute:resolved': {
    disputeId: number;
    result: 'upheld' | 'rejected';
    impact: DisputeImpact;
  };
}
```

### Activity Feed Events
```typescript
// Server → Client Only
interface ActivityEvents {
  'activity:new': {
    id: string;
    type: ActivityType;
    user: {
      id: number;
      username: string;
      avatar?: string;
    };
    content: string;
    timestamp: string;
    priority: 'low' | 'medium' | 'high';
  };
  
  'activity:reaction': {
    activityId: string;
    userId: number;
    reaction: string; // emoji
  };
  
  'activity:removed': {
    activityId: string;
  };
}

type ActivityType = 
  | 'square_marked'
  | 'pattern_complete'
  | 'bingo_called'
  | 'dispute_initiated'
  | 'user_joined'
  | 'achievement_earned'
  | 'milestone_reached';
```

### Scoreboard Events
```typescript
// Server → Client Only
interface ScoreboardEvents {
  'scoreboard:update': {
    rankings: Array<{
      position: number;
      userId: number;
      username: string;
      score: number;
      squaresMarked: number;
      squaresToBingo: number;
      patterns: {
        rows: number[];
        columns: number[];
        diagonals: number[];
      };
      trend: 'up' | 'down' | 'same';
    }>;
    yourPosition: number;
  };
  
  'scoreboard:animation': {
    userId: number;
    animation: 'climb' | 'fall' | 'crown';
  };
}
```

## Implementation Details

### 1. WebSocket Server (Python)
```python
# backend/app/websocket/server.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from redis.asyncio import Redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_rooms: Dict[int, str] = {}
        self.websocket_users: Dict[WebSocket, int] = {}
        
    async def connect(self, websocket: WebSocket, room_code: str, user_id: int):
        await websocket.accept()
        
        # Add to room
        if room_code not in self.active_connections:
            self.active_connections[room_code] = set()
        self.active_connections[room_code].add(websocket)
        
        # Track user
        self.user_rooms[user_id] = room_code
        self.websocket_users[websocket] = user_id
        
        # Notify room
        await self.broadcast_to_room(room_code, {
            "event": "room:userJoined",
            "data": {"userId": user_id}
        }, exclude=websocket)
    
    async def disconnect(self, websocket: WebSocket):
        user_id = self.websocket_users.get(websocket)
        room_code = self.user_rooms.get(user_id)
        
        if room_code and room_code in self.active_connections:
            self.active_connections[room_code].discard(websocket)
            
            # Clean up empty rooms
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
        
        # Clean up user tracking
        if user_id:
            del self.user_rooms[user_id]
            del self.websocket_users[websocket]
    
    async def broadcast_to_room(self, room_code: str, message: dict, exclude: WebSocket = None):
        if room_code in self.active_connections:
            connections = self.active_connections[room_code]
            for connection in connections:
                if connection != exclude:
                    await connection.send_json(message)
    
    async def send_to_user(self, user_id: int, message: dict):
        room_code = self.user_rooms.get(user_id)
        if room_code:
            for ws in self.active_connections.get(room_code, []):
                if self.websocket_users.get(ws) == user_id:
                    await ws.send_json(message)
                    break

manager = ConnectionManager()

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    # Authenticate user from token
    token = await websocket.receive_text()
    user = await authenticate_websocket(token)
    
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(websocket, room_code, user.id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            event = data.get("event")
            payload = data.get("data")
            
            # Handle events
            if event == "square:mark":
                await handle_square_mark(room_code, user.id, payload)
            elif event == "bingo:call":
                await handle_bingo_call(room_code, user.id, payload)
            elif event == "dispute:create":
                await handle_dispute_create(room_code, user.id, payload)
            # ... more event handlers
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

### 2. Redis Pub/Sub Integration
```python
# backend/app/websocket/redis_pubsub.py
import asyncio
from redis.asyncio import Redis
import json

class RedisPubSubManager:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        
    async def publish(self, channel: str, message: dict):
        """Publish message to Redis channel"""
        await self.redis.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str):
        """Subscribe to Redis channel"""
        await self.pubsub.subscribe(channel)
        
    async def listen(self):
        """Listen for messages"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                yield json.loads(message['data'])
    
    async def broadcast_to_room(self, room_code: str, event: str, data: dict):
        """Broadcast event to all nodes via Redis"""
        message = {
            'room_code': room_code,
            'event': event,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.publish(f'room:{room_code}', message)

# Usage in WebSocket handler
redis_manager = RedisPubSubManager(settings.REDIS_URL)

async def redis_listener(room_code: str):
    """Listen to Redis and forward to WebSocket clients"""
    await redis_manager.subscribe(f'room:{room_code}')
    async for message in redis_manager.listen():
        await manager.broadcast_to_room(room_code, message)
```

### 3. Frontend WebSocket Client
```typescript
// frontend/src/lib/websocket.ts
import { io, Socket } from 'socket.io-client';

class WebSocketManager {
  private socket: Socket | null = null;
  private roomCode: string | null = null;
  private listeners: Map<string, Set<Function>> = new Map();
  
  connect(roomCode: string, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.roomCode = roomCode;
      
      this.socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
        path: `/ws/${roomCode}`,
        auth: { token },
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });
      
      this.socket.on('connect', () => {
        console.log('WebSocket connected');
        resolve();
      });
      
      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        reject(error);
      });
      
      this.setupEventListeners();
    });
  }
  
  private setupEventListeners() {
    if (!this.socket) return;
    
    // Game events
    this.socket.on('square:marked', (data) => {
      this.emit('square:marked', data);
    });
    
    this.socket.on('bingo:called', (data) => {
      this.emit('bingo:called', data);
    });
    
    this.socket.on('dispute:initiated', (data) => {
      this.emit('dispute:initiated', data);
    });
    
    // Activity events
    this.socket.on('activity:new', (data) => {
      this.emit('activity:new', data);
    });
    
    // Scoreboard events
    this.socket.on('scoreboard:update', (data) => {
      this.emit('scoreboard:update', data);
    });
  }
  
  on(event: string, handler: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }
  
  off(event: string, handler: Function) {
    this.listeners.get(event)?.delete(handler);
  }
  
  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(handler => handler(data));
  }
  
  send(event: string, data: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }
  
  markSquare(squareId: number, phraseId: number, position: number) {
    this.send('square:mark', { squareId, phraseId, position });
  }
  
  callBingo(pattern: string, squares: number[]) {
    this.send('bingo:call', { pattern, squares });
  }
  
  createDispute(targetUserId: number, type: string, reason: string) {
    this.send('dispute:create', { targetUserId, type, reason });
  }
  
  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
    this.roomCode = null;
    this.listeners.clear();
  }
}

export const wsManager = new WebSocketManager();
```

### 4. React Hook for WebSocket
```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useCallback, useState } from 'react';
import { wsManager } from '@/lib/websocket';
import { useAuthStore } from '@/stores/authStore';

export function useWebSocket(roomCode: string) {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { accessToken } = useAuthStore();
  
  useEffect(() => {
    if (!accessToken || !roomCode) return;
    
    wsManager.connect(roomCode, accessToken)
      .then(() => setConnected(true))
      .catch((err) => setError(err.message));
    
    return () => {
      wsManager.disconnect();
      setConnected(false);
    };
  }, [roomCode, accessToken]);
  
  const on = useCallback((event: string, handler: Function) => {
    wsManager.on(event, handler);
    return () => wsManager.off(event, handler);
  }, []);
  
  const emit = useCallback((event: string, data: any) => {
    wsManager.send(event, data);
  }, []);
  
  return {
    connected,
    error,
    on,
    emit,
    markSquare: wsManager.markSquare.bind(wsManager),
    callBingo: wsManager.callBingo.bind(wsManager),
    createDispute: wsManager.createDispute.bind(wsManager),
  };
}
```

## Performance Optimizations

### 1. Message Batching
```typescript
// Batch multiple updates into single message
const batch = new MessageBatch(100); // 100ms window
batch.add('square:marked', data1);
batch.add('square:marked', data2);
batch.send(); // Sends as single message
```

### 2. Debouncing & Throttling
```typescript
// Throttle scoreboard updates
const throttledScoreboard = throttle(updateScoreboard, 500);

// Debounce activity feed
const debouncedActivity = debounce(addActivity, 200);
```

### 3. Connection Pooling
```python
# Reuse Redis connections
redis_pool = ConnectionPool(max_connections=50)
```

### 4. Binary Protocol (Optional)
```typescript
// Use MessagePack for smaller payload
import { encode, decode } from '@msgpack/msgpack';
socket.send(encode(data));
```

## Monitoring & Analytics

### Key Metrics to Track
- WebSocket connection count
- Message throughput (msg/sec)
- Average latency
- Room occupancy
- Disconnect rate
- Error rate

### Implementation
```python
# Prometheus metrics
websocket_connections = Gauge('ws_connections', 'Active WebSocket connections')
websocket_messages = Counter('ws_messages', 'WebSocket messages sent')
websocket_latency = Histogram('ws_latency', 'WebSocket message latency')
```

## Security Considerations

### Authentication
- JWT validation on connection
- Token refresh mechanism
- Session management

### Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_user_id)

@limiter.limit("100/minute")
async def handle_square_mark():
    pass
```

### Input Validation
```python
from pydantic import BaseModel, validator

class SquareMarkEvent(BaseModel):
    square_id: int
    phrase_id: int
    
    @validator('square_id')
    def valid_square(cls, v):
        if v < 0 or v > 24:
            raise ValueError('Invalid square position')
        return v
```

### Anti-Spam
```python
# Track message frequency
user_message_times = defaultdict(deque)

def check_spam(user_id: int) -> bool:
    times = user_message_times[user_id]
    now = time.time()
    
    # Remove old timestamps
    while times and times[0] < now - 60:
        times.popleft()
    
    # Check rate
    if len(times) > 30:  # Max 30 messages per minute
        return True
    
    times.append(now)
    return False
```

## Deployment Considerations

### Load Balancing
- Use sticky sessions for WebSocket connections
- Session affinity based on user ID
- Health checks for WebSocket nodes

### Scaling Strategy
1. Horizontal scaling of WebSocket nodes
2. Redis Cluster for pub/sub
3. PostgreSQL read replicas
4. CDN for static assets

### Monitoring Setup
- Grafana dashboards
- Prometheus metrics
- Error tracking (Sentry)
- Performance monitoring (New Relic)