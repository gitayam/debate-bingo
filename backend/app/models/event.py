from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.orm import relationship

from .base import Base


class Event(Base):
    """Debate event model for organizing games around specific events."""
    
    __tablename__ = "events"
    
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    
    # Event configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    allow_late_join = Column(Boolean, default=True, nullable=False)
    
    # Event metadata
    event_type = Column(String(50), nullable=False)  # presidential, primary, town_hall, etc
    participants = Column(JSON, nullable=True)  # ["Candidate A", "Candidate B"]
    location = Column(String(200), nullable=True)
    stream_url = Column(String(500), nullable=True)
    
    # Statistics
    participant_count = Column(Integer, default=0, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, nullable=True)
    
    # Custom phrases for this event
    custom_phrases = Column(JSON, nullable=True)  # List of phrase IDs specific to this event
    
    # Timing
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    registration_opens = Column(DateTime, nullable=True)
    registration_closes = Column(DateTime, nullable=True)
    
    # Relationships
    game_sessions = relationship("BingoGameSession", back_populates="event")
    scores = relationship("UserScore", back_populates="event")
    game_rooms = relationship("GameRoom", back_populates="event")
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, name='{self.name}', date='{self.event_date}')>"