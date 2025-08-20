from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .base import Base


class User(Base):
    """User model for authentication and profiles."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Profile fields
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    social_links = Column(JSON, nullable=True)  # {"twitter": "", "github": "", etc}
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # google, github, twitter
    oauth_id = Column(String(255), nullable=True)
    
    # Tracking
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    game_sessions = relationship("BingoGameSession", back_populates="user")
    scores = relationship("UserScore", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserSession(Base):
    """User session model for JWT refresh tokens."""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"


class UserPreference(Base):
    """User preferences and settings."""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # UI Preferences
    theme = Column(String(20), default="system", nullable=False)  # light, dark, system
    language = Column(String(10), default="en", nullable=False)
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    notification_events = Column(JSON, default={
        "new_follower": True,
        "game_completed": True,
        "achievement_earned": True,
        "comment_reply": True,
        "event_reminder": True
    }, nullable=False)
    
    # Privacy Settings
    profile_visibility = Column(String(20), default="public", nullable=False)  # public, friends, private
    show_online_status = Column(Boolean, default=True, nullable=False)
    allow_friend_requests = Column(Boolean, default=True, nullable=False)
    show_game_history = Column(Boolean, default=True, nullable=False)
    
    # Game Preferences
    default_grid_size = Column(Integer, default=5, nullable=False)
    auto_save_games = Column(Boolean, default=True, nullable=False)
    sound_effects = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id}, theme='{self.theme}')>"


class UserScore(Base):
    """User scores and game statistics."""
    
    __tablename__ = "user_scores"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_session_id = Column(Integer, ForeignKey("bingo_game_sessions.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    score = Column(Integer, nullable=False)
    time_elapsed = Column(Integer, nullable=False)  # in seconds
    phrases_checked = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)  # percentage
    combo_multiplier = Column(Float, default=1.0, nullable=False)
    
    # Pattern completions
    rows_completed = Column(Integer, default=0, nullable=False)
    columns_completed = Column(Integer, default=0, nullable=False)
    diagonals_completed = Column(Integer, default=0, nullable=False)
    full_card = Column(Boolean, default=False, nullable=False)
    
    # Rankings
    event_rank = Column(Integer, nullable=True)  # Rank within the event
    global_rank = Column(Integer, nullable=True)  # Global rank at time of completion
    
    # Relationships
    user = relationship("User", back_populates="scores")
    game_session = relationship("BingoGameSession")
    event = relationship("Event", back_populates="scores")
    
    def __repr__(self) -> str:
        return f"<UserScore(id={self.id}, user_id={self.user_id}, score={self.score})>"


class Achievement(Base):
    """Achievement definitions."""
    
    __tablename__ = "achievements"
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(String(500), nullable=True)
    points = Column(Integer, default=10, nullable=False)
    category = Column(String(50), nullable=False)  # speed, accuracy, social, special
    tier = Column(String(20), default="bronze", nullable=False)  # bronze, silver, gold, platinum
    
    # Requirements (JSON field for flexibility)
    requirements = Column(JSON, nullable=False)
    # Example: {"type": "games_played", "value": 10}
    # Or: {"type": "speed_completion", "value": 300, "grid_size": 5}
    
    # Tracking
    total_earned = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, code='{self.code}', name='{self.name}')>"


class UserAchievement(Base):
    """User achievement tracking."""
    
    __tablename__ = "user_achievements"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress = Column(JSON, nullable=True)  # For tracking partial progress
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),
    )
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"