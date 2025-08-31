from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.bingo_service import BingoService
from app.api.privacy_auth import get_current_user, get_optional_user  # Privacy-focused auth
from app.middleware.security import api_rate_limit
from app.schemas.bingo import (
    BingoPhraseResponse,
    BingoGameSessionCreate,
    BingoGameSessionResponse,
    BingoCardUpdate,
    BingoGameComplete,
)

router = APIRouter()


@router.get("/phrases", response_model=List[BingoPhraseResponse])
@api_rate_limit()
def get_bingo_phrases(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get all active bingo phrases. Authentication optional for analytics."""
    service = BingoService(db)
    phrases = service.get_all_phrases()
    
    # Log usage for analytics (user_id if authenticated)
    import logging
    logger = logging.getLogger("analytics")
    logger.info(
        "Phrases requested", 
        extra={"user_id": current_user.get("id") if current_user else None}
    )
    
    return [BingoPhraseResponse.from_orm(phrase) for phrase in phrases]


@router.post("/game", response_model=BingoGameSessionResponse, status_code=status.HTTP_201_CREATED)
@api_rate_limit()
def create_game_session(
    request: Request,
    session_data: BingoGameSessionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)  # Optional auth for solo play
):
    """Create a new bingo game session.
    
    Solo play: No authentication required, just provide a player_name
    Multiplayer: Authentication required (will be enforced in room creation)
    """
    service = BingoService(db)
    try:
        # Add user_id if authenticated (for stats tracking)
        if current_user:
            session_data.user_id = current_user.get("id")
        return service.create_game_session(session_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/game/{session_id}", response_model=BingoGameSessionResponse)
def get_game_session(session_id: str, db: Session = Depends(get_db)):
    """Get a game session by session ID."""
    service = BingoService(db)
    game_session = service.get_game_session(session_id)
    
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )
    
    return game_session


@router.patch("/game/{session_id}/position/{position}", response_model=BingoGameSessionResponse)
def update_card_position(
    session_id: str,
    position: int,
    update_data: BingoCardUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific card position in a game session."""
    if position < 0 or position > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position must be between 0 and 24"
        )
    
    service = BingoService(db)
    game_session = service.update_card_position(session_id, position, update_data)
    
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session or card position not found"
        )
    
    return game_session


@router.post("/game/{session_id}/complete", response_model=BingoGameSessionResponse)
def complete_game(
    session_id: str,
    completion_data: BingoGameComplete,
    db: Session = Depends(get_db)
):
    """Mark a game as completed."""
    service = BingoService(db)
    game_session = service.complete_game(session_id, completion_data)
    
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )
    
    return game_session