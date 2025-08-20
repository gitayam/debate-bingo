from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.bingo_service import BingoService
from app.schemas.bingo import (
    BingoPhraseResponse,
    BingoGameSessionCreate,
    BingoGameSessionResponse,
    BingoCardUpdate,
    BingoGameComplete,
)

router = APIRouter()


@router.get("/phrases", response_model=List[BingoPhraseResponse])
def get_bingo_phrases(db: Session = Depends(get_db)):
    """Get all active bingo phrases."""
    service = BingoService(db)
    phrases = service.get_all_phrases()
    return [BingoPhraseResponse.from_orm(phrase) for phrase in phrases]


@router.post("/game", response_model=BingoGameSessionResponse, status_code=status.HTTP_201_CREATED)
def create_game_session(
    session_data: BingoGameSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new bingo game session."""
    service = BingoService(db)
    try:
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