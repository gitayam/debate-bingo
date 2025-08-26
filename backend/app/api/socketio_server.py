"""Socket.IO server implementation for multiplayer features."""
import socketio
from fastapi import APIRouter, HTTPException
from typing import Optional
import json
import logging

from app.websocket.connection_manager import manager
from app.websocket.events import (
    handle_create_room,
    handle_join_room,
    handle_square_mark,
    handle_bingo_call,
    handle_dispute
)
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3745', 'http://127.0.0.1:3745'],
    logger=False,
    engineio_logger=False
)

# Create Socket.IO app
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='/socket.io/'
)

# Store user sessions
user_sessions = {}

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection."""
    try:
        # Get token from auth or query params
        token = None
        if auth and 'token' in auth:
            token = auth['token']
        elif 'token' in environ.get('asgi', {}).get('query_string', b'').decode():
            # Parse query string for token
            import urllib.parse
            query = urllib.parse.parse_qs(environ.get('asgi', {}).get('query_string', b'').decode())
            if 'token' in query:
                token = query['token'][0]
        
        if not token:
            logger.error(f"Connection rejected - no token provided for {sid}")
            return False
        
        # Verify token
        try:
            payload = AuthService.verify_token(token)
            user_id = int(payload.get("sub"))
            username = payload.get("username", f"user_{user_id}")
        except Exception as e:
            logger.error(f"Invalid token for {sid}: {e}")
            return False
        
        # Store user session
        user_sessions[sid] = {
            'user_id': user_id,
            'username': username,
            'room_code': None
        }
        
        logger.info(f"User {username} (ID: {user_id}) connected with session {sid}")
        
        # Send connection confirmation
        await sio.emit('connected', {
            'data': {
                'user_id': user_id,
                'message': 'Connected to multiplayer server'
            }
        }, to=sid)
        
        return True
        
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    if sid in user_sessions:
        user_info = user_sessions[sid]
        logger.info(f"User {user_info['username']} disconnected")
        
        # Leave room if in one
        if user_info['room_code']:
            await sio.leave_room(sid, user_info['room_code'])
            # Broadcast user left
            await sio.emit('activity_new', {
                'data': {
                    'type': 'user_left',
                    'user': {
                        'id': user_info['user_id'],
                        'username': user_info['username']
                    },
                    'message': f"{user_info['username']} left the room",
                    'timestamp': 'now'
                }
            }, room=user_info['room_code'], skip_sid=sid)
        
        del user_sessions[sid]

@sio.event
async def create_room(sid, data):
    """Handle room creation."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    result = await handle_create_room(user_info['user_id'], data.get('data', {}))
    
    if result['success']:
        room_code = result['room_code']
        user_sessions[sid]['room_code'] = room_code
        await sio.enter_room(sid, room_code)
        
    await sio.emit('room_created', {'data': result}, to=sid)

@sio.event
async def join_room(sid, data):
    """Handle joining a room."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    room_code = data.get('room_code')
    
    if not room_code:
        await sio.emit('error', {
            'data': {'message': 'Room code required'}
        }, to=sid)
        return
    
    result = await handle_join_room(user_info['user_id'], room_code)
    
    if result['success']:
        user_sessions[sid]['room_code'] = room_code
        await sio.enter_room(sid, room_code)
        
        # Notify room members
        await sio.emit('activity_new', {
            'data': {
                'type': 'user_joined',
                'user': {
                    'id': user_info['user_id'],
                    'username': user_info['username']
                },
                'message': f"{user_info['username']} joined the room",
                'timestamp': 'now'
            }
        }, room=room_code)
    
    await sio.emit('room_joined', {'data': result}, to=sid)

@sio.event
async def leave_room(sid, data):
    """Handle leaving a room."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    room_code = user_info['room_code']
    
    if room_code:
        await sio.leave_room(sid, room_code)
        user_sessions[sid]['room_code'] = None
        
        # Notify room members
        await sio.emit('activity_new', {
            'data': {
                'type': 'user_left',
                'user': {
                    'id': user_info['user_id'],
                    'username': user_info['username']
                },
                'message': f"{user_info['username']} left the room",
                'timestamp': 'now'
            }
        }, room=room_code, skip_sid=sid)

@sio.event
async def square_mark(sid, data):
    """Handle marking a square."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    room_code = user_info['room_code']
    
    if not room_code:
        return
    
    await handle_square_mark(
        user_info['user_id'],
        room_code,
        data.get('data', {})
    )

@sio.event
async def bingo_call(sid, data):
    """Handle BINGO call."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    room_code = user_info['room_code']
    
    if not room_code:
        return
    
    await handle_bingo_call(
        user_info['user_id'],
        room_code,
        data.get('data', {})
    )

@sio.event
async def dispute_create(sid, data):
    """Handle dispute creation."""
    if sid not in user_sessions:
        return
    
    user_info = user_sessions[sid]
    room_code = user_info['room_code']
    
    if not room_code:
        return
    
    await handle_dispute(
        user_info['user_id'],
        room_code,
        data.get('data', {})
    )

@sio.event
async def ping(sid, data):
    """Handle ping for connection keepalive."""
    await sio.emit('pong', {
        'data': {'timestamp': data.get('data', {}).get('timestamp')}
    }, to=sid)

# Export the app
__all__ = ['socket_app', 'sio']