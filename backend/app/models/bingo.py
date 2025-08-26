from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship

from .base import Base


class BingoPhrase(Base):
    """Bingo phrase model."""
    
    __tablename__ = "bingo_phrases"
    
    text = Column(Text, nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<BingoPhrase(id={self.id}, text='{self.text[:30]}...')>"


class BingoGameSession(Base):
    """Bingo game session model."""
    
    __tablename__ = "bingo_game_sessions"
    
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    player_name = Column(String(100), nullable=True)
    grid_size = Column(Integer, nullable=False, default=5)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # User relationship (optional for backward compatibility)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Event relationship (optional)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    # Relationships
    cards = relationship("BingoCard", back_populates="game_session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="game_sessions")
    event = relationship("Event", back_populates="game_sessions")
    
    def __repr__(self) -> str:
        return f"<BingoGameSession(id={self.id}, session_id='{self.session_id}')>"


class BingoCard(Base):
    """Bingo card model."""
    
    __tablename__ = "bingo_cards"
    
    game_session_id = Column(Integer, ForeignKey("bingo_game_sessions.id"), nullable=False)
    phrase_id = Column(Integer, ForeignKey("bingo_phrases.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 0-24 for 5x5 grid, 0-8 for 3x3
    is_checked = Column(Boolean, default=False, nullable=False)
    checked_at = Column(DateTime, nullable=True)
    is_free_space = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    game_session = relationship("BingoGameSession", back_populates="cards")
    phrase = relationship("BingoPhrase")
    
    def __repr__(self) -> str:
        return f"<BingoCard(id={self.id}, position={self.position}, checked={self.is_checked})>"