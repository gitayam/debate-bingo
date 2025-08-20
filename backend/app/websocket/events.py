"""WebSocket event handlers for game interactions."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import random
import string

from app.models.room import GameRoom, RoomParticipant, SquareMark, RoomActivity, Dispute
from app.models.user import User
from app.core.database import SessionLocal
from .connection_manager import manager


def generate_room_code() -> str:
    """Generate a unique 6-character room code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def handle_create_room(user_id: int, data: dict) -> dict:
    """Handle room creation."""
    db = SessionLocal()
    try:
        # Create room
        room = GameRoom(
            room_code=generate_room_code(),
            name=data.get("name", "Debate Watch Party"),
            max_players=data.get("max_players", 50),
            is_public=data.get("is_public", True),
            created_by=user_id,
            event_id=data.get("event_id"),
            grid_size=data.get("grid_size", 5)
        )
        db.add(room)
        db.commit()
        
        # Add creator as first participant
        participant = RoomParticipant(
            room_id=room.id,
            user_id=user_id,
            card_seed=str(random.random())
        )
        db.add(participant)
        
        # Update room player count
        room.current_players = 1
        room.total_players = 1
        
        db.commit()
        
        return {
            "success": True,
            "room_id": room.id,
            "room_code": room.room_code,
            "message": f"Room '{room.name}' created!"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


async def handle_join_room(user_id: int, room_code: str) -> dict:
    """Handle joining a room."""
    db = SessionLocal()
    try:
        # Find room
        room = db.query(GameRoom).filter_by(
            room_code=room_code,
            is_active=True
        ).first()
        
        if not room:
            return {
                "success": False,
                "error": "Room not found or inactive"
            }
        
        # Check if already in room
        existing = db.query(RoomParticipant).filter_by(
            room_id=room.id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if existing:
            return {
                "success": True,
                "room_id": room.id,
                "message": "Already in room"
            }
        
        # Check room capacity
        if room.current_players >= room.max_players:
            return {
                "success": False,
                "error": "Room is full"
            }
        
        # Add participant
        participant = RoomParticipant(
            room_id=room.id,
            user_id=user_id,
            card_seed=str(random.random())
        )
        db.add(participant)
        
        # Update room stats
        room.current_players += 1
        room.total_players += 1
        
        # Create activity
        user = db.query(User).filter_by(id=user_id).first()
        activity = RoomActivity(
            room_id=room.id,
            user_id=user_id,
            activity_type="user_joined",
            activity_data={
                "username": user.username,
                "display_name": user.display_name
            },
            message=f"{user.display_name or user.username} joined the room",
            priority="normal",
            icon="user-plus",
            color="green"
        )
        db.add(activity)
        
        db.commit()
        
        # Broadcast to room
        await manager.broadcast_to_room(
            room_code,
            {
                "event": "activity_new",
                "data": {
                    "type": "user_joined",
                    "user": {
                        "id": user_id,
                        "username": user.username,
                        "display_name": user.display_name
                    },
                    "message": f"{user.display_name or user.username} joined",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "room_id": room.id,
            "room_name": room.name,
            "grid_size": room.grid_size,
            "current_players": room.current_players
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


async def handle_square_mark(user_id: int, room_code: str, data: dict):
    """Handle marking a square."""
    db = SessionLocal()
    try:
        # Get room and participant
        room = db.query(GameRoom).filter_by(room_code=room_code).first()
        if not room:
            return
        
        participant = db.query(RoomParticipant).filter_by(
            room_id=room.id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not participant:
            return
        
        position = data.get("position")
        phrase_id = data.get("phrase_id")
        
        # Check if already marked
        existing = db.query(SquareMark).filter_by(
            room_id=room.id,
            participant_id=participant.id,
            position=position,
            unmarked_at=None
        ).first()
        
        if existing:
            return
        
        # Count how many have marked this phrase (for speed bonus)
        mark_count = db.query(SquareMark).filter_by(
            room_id=room.id,
            phrase_id=phrase_id,
            unmarked_at=None
        ).count()
        
        # Calculate bonus points
        bonus_points = 0
        if mark_count == 0:
            bonus_points = 5  # First to mark
        elif mark_count == 1:
            bonus_points = 3  # Second to mark
        elif mark_count == 2:
            bonus_points = 1  # Third to mark
        
        # Create mark
        mark = SquareMark(
            room_id=room.id,
            participant_id=participant.id,
            position=position,
            phrase_id=phrase_id,
            mark_order=mark_count + 1,
            bonus_points=bonus_points
        )
        db.add(mark)
        
        # Update participant score
        participant.score = (participant.score or 0) + 10 + bonus_points
        
        # Create activity
        user = db.query(User).filter_by(id=user_id).first()
        phrase = db.query(BingoPhrase).filter_by(id=phrase_id).first()
        
        activity = RoomActivity(
            room_id=room.id,
            user_id=user_id,
            activity_type="square_marked",
            activity_data={
                "position": position,
                "phrase": phrase.text,
                "bonus": bonus_points
            },
            message=f"{user.display_name or user.username} marked '{phrase.text}'",
            priority="normal" if bonus_points == 0 else "high",
            icon="check-square",
            color="blue" if bonus_points == 0 else "yellow"
        )
        db.add(activity)
        
        db.commit()
        
        # Broadcast to room
        await manager.broadcast_to_room(
            room_code,
            {
                "event": "square_marked",
                "data": {
                    "user_id": user_id,
                    "username": user.username,
                    "position": position,
                    "phrase": phrase.text,
                    "bonus_points": bonus_points,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Update scoreboard
        await update_scoreboard(room_code)
        
    except Exception as e:
        db.rollback()
        print(f"Square mark error: {e}")
    finally:
        db.close()


async def handle_bingo_call(user_id: int, room_code: str, data: dict):
    """Handle a BINGO call."""
    db = SessionLocal()
    try:
        room = db.query(GameRoom).filter_by(room_code=room_code).first()
        if not room:
            return
        
        user = db.query(User).filter_by(id=user_id).first()
        pattern = data.get("pattern", "line")  # line, diagonal, full
        
        # Create activity
        activity = RoomActivity(
            room_id=room.id,
            user_id=user_id,
            activity_type="bingo_called",
            activity_data={
                "pattern": pattern
            },
            message=f"{user.display_name or user.username} called BINGO!",
            priority="critical",
            icon="trophy",
            color="red"
        )
        db.add(activity)
        db.commit()
        
        # Broadcast to room
        await manager.broadcast_to_room(
            room_code,
            {
                "event": "bingo_called",
                "data": {
                    "user_id": user_id,
                    "username": user.username,
                    "pattern": pattern,
                    "verification_window": 30,  # 30 seconds to dispute
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        print(f"Bingo call error: {e}")
    finally:
        db.close()


async def handle_dispute(user_id: int, room_code: str, data: dict):
    """Handle a dispute."""
    db = SessionLocal()
    try:
        room = db.query(GameRoom).filter_by(room_code=room_code).first()
        if not room:
            return
        
        # Create dispute
        dispute = Dispute(
            room_id=room.id,
            disputed_by=user_id,
            target_user_id=data.get("target_user_id"),
            dispute_type=data.get("type", "square_mark"),
            reason=data.get("reason"),
            expires_at=datetime.utcnow() + timedelta(seconds=30)
        )
        
        if data.get("square_mark_id"):
            dispute.square_mark_id = data.get("square_mark_id")
        
        db.add(dispute)
        db.commit()
        
        # Broadcast dispute
        user = db.query(User).filter_by(id=user_id).first()
        target = db.query(User).filter_by(id=data.get("target_user_id")).first()
        
        await manager.broadcast_to_room(
            room_code,
            {
                "event": "dispute_initiated",
                "data": {
                    "dispute_id": dispute.id,
                    "disputer": user.username,
                    "target": target.username,
                    "type": dispute.dispute_type,
                    "reason": dispute.reason,
                    "expires_in": 30,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        print(f"Dispute error: {e}")
    finally:
        db.close()


async def update_scoreboard(room_code: str):
    """Update and broadcast scoreboard."""
    db = SessionLocal()
    try:
        room = db.query(GameRoom).filter_by(room_code=room_code).first()
        if not room:
            return
        
        # Get participants with scores
        participants = db.query(RoomParticipant).filter_by(
            room_id=room.id,
            is_active=True
        ).order_by(RoomParticipant.score.desc()).all()
        
        rankings = []
        for i, participant in enumerate(participants):
            user = db.query(User).filter_by(id=participant.user_id).first()
            
            # Count marked squares
            marked_count = db.query(SquareMark).filter_by(
                room_id=room.id,
                participant_id=participant.id,
                unmarked_at=None
            ).count()
            
            # Calculate squares to bingo (simplified)
            total_squares = room.grid_size * room.grid_size
            squares_to_bingo = total_squares - marked_count
            
            rankings.append({
                "position": i + 1,
                "user_id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "score": participant.score or 0,
                "squares_marked": marked_count,
                "squares_to_bingo": squares_to_bingo
            })
        
        # Broadcast scoreboard update
        await manager.broadcast_to_room(
            room_code,
            {
                "event": "scoreboard_update",
                "data": {
                    "rankings": rankings[:10],  # Top 10
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        print(f"Scoreboard update error: {e}")
    finally:
        db.close()


# Import after to avoid circular dependency
from app.models.bingo import BingoPhrase