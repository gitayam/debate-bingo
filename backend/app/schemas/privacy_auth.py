"""Privacy-focused authentication schemas for hash-based accounts."""
from typing import Optional
from pydantic import BaseModel, Field, validator


class AccountCreate(BaseModel):
    """Request to create a new anonymous account."""
    # No fields required - accounts are generated anonymously
    pass


class AccountLogin(BaseModel):
    """Login with account hash only (no password)."""
    account_hash: str = Field(
        ..., 
        min_length=16,
        max_length=16,
        description="16-character hex account hash"
    )
    
    @validator('account_hash')
    def validate_account_hash(cls, v):
        """Validate account hash format."""
        if len(v) != 16:
            raise ValueError('Account hash must be exactly 16 characters')
        
        # Must be valid hex
        try:
            int(v, 16)
        except ValueError:
            raise ValueError('Account hash must be valid hexadecimal')
        
        return v.lower()  # Normalize to lowercase


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class AccountResponse(BaseModel):
    """User account information (privacy-safe)."""
    id: int
    account_hash: str
    username: str
    is_anonymous: bool = True
    created_at: str
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user: AccountResponse


class TokenRefresh(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Valid refresh token")


class AccountDeactivate(BaseModel):
    """Account deactivation request (for privacy)."""
    account_hash: str = Field(..., description="Account hash to deactivate")
    confirm: bool = Field(..., description="Confirmation flag")
    
    @validator('confirm')
    def must_confirm(cls, v):
        """Require explicit confirmation."""
        if not v:
            raise ValueError('Must confirm account deactivation')
        return v


class AccountInfo(BaseModel):
    """Public account information."""
    username: str
    created_at: str
    is_anonymous: bool = True
    # No sensitive information exposed


class UsageStats(BaseModel):
    """Privacy-safe usage statistics."""
    games_played: int
    total_time_played: int  # seconds
    achievements_earned: int
    # No personally identifiable information