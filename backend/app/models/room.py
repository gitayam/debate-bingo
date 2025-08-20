"""Game room models for multiplayer functionality."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from .base import Base


class GameRoom(Base):
    """Game room for multiplayer sessions."""
    
    __tablename__ = "game_rooms"
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    room_code = Column(String(6), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    max_players = Column(Integer, default=50, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Game settings
    grid_size = Column(Integer, default=5, nullable=False)
    game_mode = Column(String(50), default="classic", nullable=False)  # classic, speed, tournament
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Statistics
    current_players = Column(Integer, default=0, nullable=False)
    total_players = Column(Integer, default=0, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="game_rooms")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("RoomParticipant", back_populates="room", cascade="all, delete-orphan")
    activities = relationship("RoomActivity", back_populates="room", cascade="all, delete-orphan")
    square_marks = relationship("SquareMark", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<GameRoom(id={self.id}, code='{self.room_code}', name='{self.name}')>"


class RoomParticipant(Base):
    """Participants in a game room."""
    
    __tablename__ = "room_participants"
    
    room_id = Column(Integer, ForeignKey("game_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session info
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_ready = Column(Boolean, default=False, nullable=False)
    
    # Game data
    card_seed = Column(String(100), nullable=True)  # For unique card generation
    bingo_card = Column(JSON, nullable=True)  # Store the actual card layout
    score = Column(Integer, default=0, nullable=False)
    final_position = Column(Integer, nullable=True)
    
    # Connection info
    connection_id = Column(String(100), nullable=True)  # WebSocket connection ID
    last_ping = Column(DateTime, nullable=True)
    
    # Relationships
    room = relationship("GameRoom", back_populates="participants")
    user = relationship("User")
    marks = relationship("SquareMark", back_populates="participant")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('room_id', 'user_id', name='_room_user_uc'),
    )
    
    def __repr__(self) -> str:
        return f"<RoomParticipant(room_id={self.room_id}, user_id={self.user_id})>"


class SquareMark(Base):
    """Track when users mark squares in real-time."""
    
    __tablename__ = "square_marks"
    
    room_id = Column(Integer, ForeignKey("game_rooms.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("room_participants.id"), nullable=False)
    
    # Square info
    position = Column(Integer, nullable=False)  # 0-24 for 5x5, 0-8 for 3x3
    phrase_id = Column(Integer, ForeignKey("bingo_phrases.id"), nullable=False)
    
    # Timing
    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    unmarked_at = Column(DateTime, nullable=True)
    
    # Validation
    is_disputed = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    
    # Speed bonus
    mark_order = Column(Integer, nullable=True)  # 1st, 2nd, 3rd to mark this phrase
    bonus_points = Column(Integer, default=0, nullable=False)
    
    # Relationships
    room = relationship("GameRoom", back_populates="square_marks")
    participant = relationship("RoomParticipant", back_populates="marks")
    phrase = relationship("BingoPhrase")
    dispute = relationship("Dispute", back_populates="square_mark")
    
    def __repr__(self) -> str:
        return f"<SquareMark(room_id={self.room_id}, position={self.position})>"


class RoomActivity(Base):
    """Activity feed for game rooms."""
    
    __tablename__ = "room_activities"
    
    room_id = Column(Integer, ForeignKey("game_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # square_marked, bingo_called, user_joined, etc.
    activity_data = Column(JSON, nullable=False)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, critical
    
    # Display
    message = Column(Text, nullable=True)  # Pre-formatted message for display
    icon = Column(String(50), nullable=True)  # Icon identifier
    color = Column(String(20), nullable=True)  # Color scheme
    
    # Relationships
    room = relationship("GameRoom", back_populates="activities")
    user = relationship("User")
    reactions = relationship("ActivityReaction", back_populates="activity", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<RoomActivity(id={self.id}, type='{self.activity_type}')>"


class ActivityReaction(Base):
    """Reactions to activity feed items."""
    
    __tablename__ = "activity_reactions"
    
    activity_id = Column(Integer, ForeignKey("room_activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reaction = Column(String(20), nullable=False)  # emoji or reaction type
    
    # Relationships
    activity = relationship("RoomActivity", back_populates="reactions")
    user = relationship("User")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('activity_id', 'user_id', name='_activity_user_uc'),
    )
    
    def __repr__(self) -> str:
        return f"<ActivityReaction(activity_id={self.activity_id}, reaction='{self.reaction}')>"


class Dispute(Base):
    """Disputes for square marks and bingo calls."""
    
    __tablename__ = "disputes"
    
    room_id = Column(Integer, ForeignKey("game_rooms.id"), nullable=False)
    square_mark_id = Column(Integer, ForeignKey("square_marks.id"), nullable=True)
    disputed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dispute details
    dispute_type = Column(String(50), nullable=False)  # square_mark, bingo_call
    reason = Column(Text, nullable=True)
    
    # Timing
    expires_at = Column(DateTime, nullable=False)  # 30 seconds from creation
    resolved_at = Column(DateTime, nullable=True)
    
    # Resolution
    resolution = Column(String(50), nullable=True)  # upheld, rejected, expired
    votes_for = Column(Integer, default=0, nullable=False)
    votes_against = Column(Integer, default=0, nullable=False)
    
    # Relationships
    room = relationship("GameRoom")
    square_mark = relationship("SquareMark", back_populates="dispute")
    disputer = relationship("User", foreign_keys=[disputed_by])
    target_user = relationship("User", foreign_keys=[target_user_id])
    votes = relationship("DisputeVote", back_populates="dispute", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Dispute(id={self.id}, type='{self.dispute_type}')>"


class DisputeVote(Base):
    """Votes on disputes."""
    
    __tablename__ = "dispute_votes"
    
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote = Column(Boolean, nullable=False)  # True = uphold, False = reject
    voted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    dispute = relationship("Dispute", back_populates="votes")
    user = relationship("User")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('dispute_id', 'user_id', name='_dispute_user_uc'),
    )
    
    def __repr__(self) -> str:
        return f"<DisputeVote(dispute_id={self.dispute_id}, vote={self.vote})>"