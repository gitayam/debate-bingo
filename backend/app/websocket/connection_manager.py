"""WebSocket connection manager for real-time features."""
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

from app.services.auth_service import AuthService
from app.core.database import SessionLocal


class ConnectionManager:
    """Manages WebSocket connections and room subscriptions."""
    
    def __init__(self):
        # room_code -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # user_id -> room_code
        self.user_rooms: Dict[int, str] = {}
        # WebSocket -> user_id
        self.connection_users: Dict[WebSocket, int] = {}
        # room_code -> set of user_ids
        self.room_users: Dict[str, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str, user_id: int) -> bool:
        """Connect a user to a room."""
        try:
            await websocket.accept()
            
            # Add to room connections
            if room_code not in self.active_connections:
                self.active_connections[room_code] = set()
                self.room_users[room_code] = set()
            
            self.active_connections[room_code].add(websocket)
            self.room_users[room_code].add(user_id)
            
            # Track user-room mapping
            self.user_rooms[user_id] = room_code
            self.connection_users[websocket] = user_id
            
            # Notify room of new user
            await self.broadcast_to_room(
                room_code,
                {
                    "event": "user_joined",
                    "data": {
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "total_users": len(self.room_users[room_code])
                    }
                },
                exclude=websocket
            )
            
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a user from their room."""
        user_id = self.connection_users.get(websocket)
        
        if not user_id:
            return
        
        room_code = self.user_rooms.get(user_id)
        
        if room_code and room_code in self.active_connections:
            # Remove from room
            self.active_connections[room_code].discard(websocket)
            self.room_users[room_code].discard(user_id)
            
            # Clean up empty rooms
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
                del self.room_users[room_code]
            else:
                # Notify remaining users
                await self.broadcast_to_room(
                    room_code,
                    {
                        "event": "user_left",
                        "data": {
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "total_users": len(self.room_users[room_code])
                        }
                    }
                )
        
        # Clean up user tracking
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        if websocket in self.connection_users:
            del self.connection_users[websocket]
    
    async def broadcast_to_room(
        self,
        room_code: str,
        message: dict,
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast message to all users in a room."""
        if room_code not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[room_code]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except:
                    # Track disconnected connections
                    disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to a specific user."""
        room_code = self.user_rooms.get(user_id)
        
        if not room_code or room_code not in self.active_connections:
            return
        
        for connection in self.active_connections[room_code]:
            if self.connection_users.get(connection) == user_id:
                try:
                    await connection.send_json(message)
                except:
                    await self.disconnect(connection)
                break
    
    def get_room_users(self, room_code: str) -> Set[int]:
        """Get all user IDs in a room."""
        return self.room_users.get(room_code, set())
    
    def get_user_room(self, user_id: int) -> Optional[str]:
        """Get the room code for a user."""
        return self.user_rooms.get(user_id)
    
    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user is connected."""
        return user_id in self.user_rooms


# Global connection manager instance
manager = ConnectionManager()