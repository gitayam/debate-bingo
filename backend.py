#!/usr/bin/env python3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(title="Debate Bingo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3745", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.rooms: Dict[str, dict] = {}
        
    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)
        
    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            self.active_connections[room_code].remove(websocket)
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
                
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str, room_code: str, exclude_websocket: Optional[WebSocket] = None):
        if room_code in self.active_connections:
            for connection in self.active_connections[room_code]:
                if connection != exclude_websocket:
                    await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Debate Bingo Backend API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, token: Optional[str] = None):
    await manager.connect(websocket, room_code)
    
    initial_message = {
        "event": "connected",
        "data": {
            "user_id": 1,
            "room_code": room_code,
            "message": "Connected to room",
            "timestamp": datetime.now().isoformat()
        }
    }
    await manager.send_personal_message(json.dumps(initial_message), websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                response = {
                    "event": "error",
                    "data": {
                        "success": False,
                        "error": "Invalid JSON format"
                    }
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                continue
            
            event = message.get("event")
            event_data = message.get("data", {})
            
            if event is None or not isinstance(event, str):
                response = {
                    "event": "error", 
                    "data": {
                        "success": False,
                        "error": "Missing or invalid 'event' field in message"
                    }
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                continue
            
            if event == "create_room":
                manager.rooms[room_code] = {
                    "name": event_data.get("name", "Unnamed Room"),
                    "max_players": event_data.get("max_players", 10),
                    "is_public": event_data.get("is_public", True),
                    "grid_size": event_data.get("grid_size", 5),
                    "created_at": datetime.now().isoformat(),
                    "players": []
                }
                
                response = {
                    "event": "room_created",
                    "data": {
                        "success": True,
                        "room": manager.rooms[room_code]
                    }
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                
                broadcast_msg = {
                    "event": "room_update",
                    "data": {
                        "room_code": room_code,
                        "room": manager.rooms[room_code]
                    }
                }
                await manager.broadcast(json.dumps(broadcast_msg), room_code, websocket)
                
            elif event == "join_room":
                if room_code in manager.rooms:
                    response = {
                        "event": "room_joined",
                        "data": {
                            "success": True,
                            "room": manager.rooms[room_code]
                        }
                    }
                else:
                    response = {
                        "event": "room_joined",
                        "data": {
                            "success": False,
                            "error": "Room does not exist"
                        }
                    }
                await manager.send_personal_message(json.dumps(response), websocket)
                
                if room_code in manager.rooms:
                    broadcast_msg = {
                        "event": "player_joined",
                        "data": {
                            "room_code": room_code,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    await manager.broadcast(json.dumps(broadcast_msg), room_code, websocket)
                    
            elif event == "mark_square":
                broadcast_msg = {
                    "event": "square_marked",
                    "data": {
                        "square_id": event_data.get("square_id"),
                        "room_code": room_code,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await manager.broadcast(json.dumps(broadcast_msg), room_code)
                
            else:
                response = {
                    "event": "error",
                    "data": {
                        "success": False,
                        "error": f"Unknown event: {event}",
                        "message": f"Unknown event: {event}"
                    }
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)
        if room_code in manager.active_connections:
            broadcast_msg = {
                "event": "player_disconnected",
                "data": {
                    "room_code": room_code,
                    "timestamp": datetime.now().isoformat()
                }
            }
            await manager.broadcast(json.dumps(broadcast_msg), room_code)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8745)