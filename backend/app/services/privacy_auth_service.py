"""Privacy-focused authentication service using hash-based account numbers."""
import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User


class PrivacyAuthService:
    """Privacy-focused authentication using anonymous hash-based accounts."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @staticmethod
    def generate_account_hash() -> str:
        """Generate a unique account hash (similar to Mullvad account numbers).
        
        Format: 16-character hex string (64-bit entropy)
        Example: 4a8c9f2d1e7b3c6a
        """
        # Generate 64-bit random value
        random_bytes = secrets.token_bytes(8)
        
        # Convert to hex string (16 characters)
        account_hash = random_bytes.hex()
        
        return account_hash
    
    @staticmethod
    def is_valid_account_hash(account_hash: str) -> bool:
        """Validate account hash format."""
        if not account_hash:
            return False
        
        # Must be exactly 16 hex characters
        if len(account_hash) != 16:
            return False
        
        try:
            # Must be valid hex
            int(account_hash, 16)
            return True
        except ValueError:
            return False
    
    def create_anonymous_account(self, db: Session) -> tuple[User, str]:
        """Create a new anonymous account with hash-based identifier.
        
        Returns:
            tuple: (User object, account_hash)
        """
        # Generate unique account hash
        account_hash = self.generate_account_hash()
        
        # Ensure uniqueness (very unlikely collision, but be safe)
        while db.query(User).filter(User.account_hash == account_hash).first():
            account_hash = self.generate_account_hash()
        
        # Create anonymous user
        user = User(
            account_hash=account_hash,
            username=f"user_{account_hash[:8]}",  # Display name: user_4a8c9f2d
            email=None,  # No email required for privacy
            password_hash=None,  # No password required
            is_active=True,
            is_anonymous=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user, account_hash
    
    def authenticate_by_hash(self, db: Session, account_hash: str) -> Optional[User]:
        """Authenticate user by account hash only."""
        if not self.is_valid_account_hash(account_hash):
            return None
        
        user = db.query(User).filter(
            User.account_hash == account_hash,
            User.is_active == True
        ).first()
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # Extract account hash from token
        account_hash = payload.get("sub")
        if not account_hash:
            return None
        
        # Get user by account hash
        user = self.authenticate_by_hash(db, account_hash)
        return user
    
    def login_with_hash(self, db: Session, account_hash: str) -> Optional[dict]:
        """Login using only account hash (no password required).
        
        Returns:
            dict: Contains access_token, refresh_token, user info
        """
        user = self.authenticate_by_hash(db, account_hash)
        if not user:
            return None
        
        # Create tokens
        access_token = self.create_access_token(data={"sub": account_hash})
        refresh_token = self.create_refresh_token(data={"sub": account_hash})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "account_hash": user.account_hash,
                "username": user.username,
                "is_anonymous": user.is_anonymous
            }
        }
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        account_hash = payload.get("sub")
        if not account_hash:
            return None
        
        # Verify user still exists and is active
        user = self.authenticate_by_hash(db, account_hash)
        if not user:
            return None
        
        # Create new access token
        access_token = self.create_access_token(data={"sub": account_hash})
        return access_token
    
    def deactivate_account(self, db: Session, account_hash: str) -> bool:
        """Deactivate an account (soft delete for privacy)."""
        user = self.authenticate_by_hash(db, account_hash)
        if not user:
            return False
        
        user.is_active = False
        user.deactivated_at = datetime.utcnow()
        db.commit()
        
        return True