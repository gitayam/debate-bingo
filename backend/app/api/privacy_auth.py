"""Privacy-focused authentication endpoints using hash-based accounts."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.privacy_auth import (
    AccountCreate, AccountLogin, TokenResponse, AccountResponse,
    AuthResponse, TokenRefresh, AccountDeactivate, AccountInfo, UsageStats
)
from app.services.privacy_auth_service import PrivacyAuthService
from app.models.user import User
from app.middleware.security import auth_rate_limit, api_rate_limit

router = APIRouter()
security = HTTPBearer(auto_error=False)  # Optional auth
security_logger = logging.getLogger("security")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = PrivacyAuthService()
    user = auth_service.get_current_user(db, credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    auth_service = PrivacyAuthService()
    return auth_service.get_current_user(db, credentials.credentials)


@router.post("/account/create", response_model=AuthResponse)
@api_rate_limit()
def create_account(
    request: Request,
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """Create a new anonymous account with hash-based identifier.
    
    No personal information required - generates secure random account hash.
    """
    security_logger.info(
        "Anonymous account creation requested",
        extra={"client_ip": request.client.host if request.client else "unknown"}
    )
    
    auth_service = PrivacyAuthService()
    
    try:
        # Create anonymous account
        user, account_hash = auth_service.create_anonymous_account(db)
        
        # Generate tokens
        tokens = auth_service.login_with_hash(db, account_hash)
        
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create account tokens"
            )
        
        security_logger.info(
            "Anonymous account created successfully",
            extra={
                "user_id": user.id,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        return AuthResponse(**tokens)
        
    except Exception as e:
        security_logger.error(
            "Account creation failed",
            extra={
                "error": str(e),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/account/login", response_model=AuthResponse)
@auth_rate_limit()  # 5 attempts per minute
def login_with_hash(
    credentials: AccountLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login using account hash only (no password required).
    
    Provides privacy-focused authentication similar to Mullvad VPN.
    """
    security_logger.info(
        "Hash-based login attempt",
        extra={
            "account_hash": credentials.account_hash[:4] + "****",  # Partially obscured
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    auth_service = PrivacyAuthService()
    tokens = auth_service.login_with_hash(db, credentials.account_hash)
    
    if not tokens:
        security_logger.warning(
            "Login failed - invalid account hash",
            extra={
                "account_hash": credentials.account_hash[:4] + "****",
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account hash",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    security_logger.info(
        "Login successful",
        extra={
            "user_id": tokens["user"]["id"],
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return AuthResponse(**tokens)


@router.post("/token/refresh", response_model=TokenResponse)
@api_rate_limit()
def refresh_token(
    refresh_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    auth_service = PrivacyAuthService()
    
    new_access_token = auth_service.refresh_access_token(db, refresh_data.refresh_token)
    
    if not new_access_token:
        security_logger.warning(
            "Token refresh failed",
            extra={"client_ip": request.client.host if request.client else "unknown"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_data.refresh_token,  # Keep same refresh token
        token_type="bearer"
    )


@router.get("/account/me", response_model=AccountInfo)
def get_account_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current account information (privacy-safe)."""
    return AccountInfo(
        username=current_user.username,
        created_at=current_user.created_at.isoformat(),
        is_anonymous=current_user.is_anonymous
    )


@router.get("/account/stats", response_model=UsageStats)
def get_usage_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get privacy-safe usage statistics."""
    # Calculate stats without exposing personal data
    games_played = len(current_user.game_sessions) if current_user.game_sessions else 0
    achievements_earned = len(current_user.achievements) if current_user.achievements else 0
    
    # Calculate total time played
    total_time = 0
    if current_user.scores:
        total_time = sum(score.time_elapsed for score in current_user.scores)
    
    return UsageStats(
        games_played=games_played,
        total_time_played=total_time,
        achievements_earned=achievements_earned
    )


@router.post("/account/deactivate")
@auth_rate_limit()
def deactivate_account(
    deactivate_data: AccountDeactivate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate account for privacy compliance.
    
    This is a soft delete that preserves game history but removes personal access.
    """
    if current_user.account_hash != deactivate_data.account_hash:
        security_logger.warning(
            "Account deactivation failed - hash mismatch",
            extra={
                "user_id": current_user.id,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account hash mismatch"
        )
    
    auth_service = PrivacyAuthService()
    success = auth_service.deactivate_account(db, current_user.account_hash)
    
    if success:
        security_logger.info(
            "Account deactivated",
            extra={
                "user_id": current_user.id,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        return {"message": "Account deactivated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )


@router.get("/health")
def privacy_auth_health():
    """Health check for privacy auth system."""
    return {
        "status": "healthy",
        "auth_type": "privacy_hash_based",
        "features": [
            "anonymous_accounts",
            "no_email_required", 
            "no_password_required",
            "mullvad_style_hashes",
            "privacy_compliant"
        ]
    }