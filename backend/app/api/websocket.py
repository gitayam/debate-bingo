"""WebSocket API endpoints for real-time features."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json

from app.websocket.connection_manager import manager
from app.websocket.events import (
    handle_create_room,
    handle_join_room,
    handle_square_mark,
    handle_bingo_call,
    handle_dispute
)
from app.services.auth_service import AuthService
from app.core.database import SessionLocal

router = APIRouter()


async def get_current_user_ws(token: str) -> Optional[dict]:
    """Authenticate WebSocket connection."""
    try:
        payload = AuthService.verify_token(token)
        return {"id": int(payload.get("sub"))}
    except:
        return None


@router.websocket("/ws/{room_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time game interactions."""
    
    # Authenticate user
    user = await get_current_user_ws(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    user_id = user["id"]
    
    # Connect to room
    connected = await manager.connect(websocket, room_code, user_id)
    if not connected:
        await websocket.close(code=4002, reason="Connection failed")
        return
    
    # Send initial connection success
    await websocket.send_json({
        "event": "connected",
        "data": {
            "user_id": user_id,
            "room_code": room_code,
            "message": "Connected to room"
        }
    })
    
    try:
        # Handle incoming messages
        while True:
            # Receive message
            data = await websocket.receive_json()
            event_type = data.get("event")
            event_data = data.get("data", {})
            
            # Route events to handlers
            if event_type == "create_room":
                result = await handle_create_room(user_id, event_data)
                await websocket.send_json({
                    "event": "room_created",
                    "data": result
                })
                
            elif event_type == "join_room":
                result = await handle_join_room(user_id, room_code)
                await websocket.send_json({
                    "event": "room_joined",
                    "data": result
                })
                
            elif event_type == "square_mark":
                await handle_square_mark(user_id, room_code, event_data)
                
            elif event_type == "square_unmark":
                # TODO: Implement unmarking
                pass
                
            elif event_type == "bingo_call":
                await handle_bingo_call(user_id, room_code, event_data)
                
            elif event_type == "dispute_create":
                await handle_dispute(user_id, room_code, event_data)
                
            elif event_type == "dispute_vote":
                # TODO: Implement dispute voting
                pass
                
            elif event_type == "ping":
                # Heartbeat
                await websocket.send_json({
                    "event": "pong",
                    "data": {"timestamp": event_data.get("timestamp")}
                })
                
            else:
                # Unknown event
                await websocket.send_json({
                    "event": "error",
                    "data": {
                        "message": f"Unknown event: {event_type}"
                    }
                })
                
    except WebSocketDisconnect:
        # Handle disconnection
        await manager.disconnect(websocket)
        
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
        await websocket.close(code=4003, reason="Server error")