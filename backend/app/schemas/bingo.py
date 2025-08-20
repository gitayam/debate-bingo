from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class BingoPhraseBase(BaseModel):
    """Base bingo phrase schema."""
    text: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class BingoPhraseResponse(BingoPhraseBase):
    """Bingo phrase response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BingoCardBase(BaseModel):
    """Base bingo card schema."""
    position: int = Field(..., ge=0, le=24)
    is_free_space: bool = False


class BingoCardCreate(BingoCardBase):
    """Bingo card creation schema."""
    phrase_id: int


class BingoCardUpdate(BaseModel):
    """Bingo card update schema."""
    is_checked: bool


class BingoCardResponse(BingoCardBase):
    """Bingo card response schema."""
    id: int
    phrase_id: int
    is_checked: bool
    checked_at: Optional[datetime] = None
    phrase: BingoPhraseResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BingoGameSessionBase(BaseModel):
    """Base bingo game session schema."""
    player_name: Optional[str] = Field(None, max_length=100)
    grid_size: int = Field(5, ge=3, le=5)


class BingoGameSessionCreate(BingoGameSessionBase):
    """Bingo game session creation schema."""
    pass


class BingoGameSessionResponse(BingoGameSessionBase):
    """Bingo game session response schema."""
    id: int
    session_id: str
    is_completed: bool
    completed_at: Optional[datetime] = None
    cards: List[BingoCardResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BingoGameComplete(BaseModel):
    """Bingo game completion schema."""
    winning_combination: List[int] = Field(..., description="List of positions that form the winning line")
    completion_time: datetime = Field(default_factory=datetime.utcnow)