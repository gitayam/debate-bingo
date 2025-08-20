import random
import uuid
from datetime import datetime
from typing import List, Optional, Set
from sqlalchemy.orm import Session

from app.models.bingo import BingoCard, BingoPhrase, BingoGameSession
from app.schemas.bingo import (
    BingoGameSessionCreate,
    BingoGameSessionResponse,
    BingoCardUpdate,
    BingoGameComplete,
)


class BingoService:
    """Service for managing bingo games."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_phrases(self) -> List[BingoPhrase]:
        """Get all active bingo phrases."""
        return self.db.query(BingoPhrase).filter(BingoPhrase.is_active == True).all()
    
    def create_game_session(self, session_data: BingoGameSessionCreate) -> BingoGameSessionResponse:
        """Create a new bingo game session with a generated card."""
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create game session
        game_session = BingoGameSession(
            session_id=session_id,
            player_name=session_data.player_name,
            grid_size=session_data.grid_size,
        )
        self.db.add(game_session)
        self.db.flush()  # Get the ID without committing
        
        # Generate bingo card
        self._generate_bingo_card(game_session.id, session_data.grid_size)
        
        self.db.commit()
        self.db.refresh(game_session)
        
        return BingoGameSessionResponse.from_orm(game_session)
    
    def get_game_session(self, session_id: str) -> Optional[BingoGameSessionResponse]:
        """Get a game session by session ID."""
        game_session = self.db.query(BingoGameSession).filter(
            BingoGameSession.session_id == session_id
        ).first()
        
        if not game_session:
            return None
            
        return BingoGameSessionResponse.from_orm(game_session)
    
    def update_card_position(
        self, session_id: str, position: int, update_data: BingoCardUpdate
    ) -> Optional[BingoGameSessionResponse]:
        """Update a specific card position in a game session."""
        game_session = self.db.query(BingoGameSession).filter(
            BingoGameSession.session_id == session_id
        ).first()
        
        if not game_session:
            return None
        
        # Find the card at the specified position
        card = self.db.query(BingoCard).filter(
            BingoCard.game_session_id == game_session.id,
            BingoCard.position == position
        ).first()
        
        if not card:
            return None
        
        # Update the card
        card.is_checked = update_data.is_checked
        if update_data.is_checked:
            card.checked_at = datetime.utcnow()
        else:
            card.checked_at = None
        
        # Check for bingo
        if update_data.is_checked and not game_session.is_completed:
            if self._check_for_bingo(game_session.id, game_session.grid_size):
                game_session.is_completed = True
                game_session.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(game_session)
        
        return BingoGameSessionResponse.from_orm(game_session)
    
    def complete_game(self, session_id: str, completion_data: BingoGameComplete) -> Optional[BingoGameSessionResponse]:
        """Mark a game as completed."""
        game_session = self.db.query(BingoGameSession).filter(
            BingoGameSession.session_id == session_id
        ).first()
        
        if not game_session:
            return None
        
        game_session.is_completed = True
        game_session.completed_at = completion_data.completion_time
        
        self.db.commit()
        self.db.refresh(game_session)
        
        return BingoGameSessionResponse.from_orm(game_session)
    
    def _generate_bingo_card(self, game_session_id: int, grid_size: int) -> None:
        """Generate a bingo card for the game session."""
        # Get all available phrases
        phrases = self.get_all_phrases()
        
        if len(phrases) < (grid_size * grid_size - 1):  # -1 for free space
            raise ValueError("Not enough phrases to generate a bingo card")
        
        # Calculate total positions and free space position
        total_positions = grid_size * grid_size
        free_space_position = total_positions // 2  # Center position
        
        # Select random phrases (excluding free space)
        selected_phrases = random.sample(phrases, total_positions - 1)
        
        # Create cards for each position
        phrase_index = 0
        for position in range(total_positions):
            if position == free_space_position:
                # Create free space
                card = BingoCard(
                    game_session_id=game_session_id,
                    phrase_id=selected_phrases[0].id,  # Use any phrase ID (won't be displayed)
                    position=position,
                    is_free_space=True,
                    is_checked=True,  # Free space is always checked
                    checked_at=datetime.utcnow()
                )
            else:
                # Create regular card
                card = BingoCard(
                    game_session_id=game_session_id,
                    phrase_id=selected_phrases[phrase_index].id,
                    position=position,
                    is_free_space=False
                )
                phrase_index += 1
            
            self.db.add(card)
    
    def _check_for_bingo(self, game_session_id: int, grid_size: int) -> bool:
        """Check if the current card state has a bingo."""
        # Get all checked positions
        checked_cards = self.db.query(BingoCard).filter(
            BingoCard.game_session_id == game_session_id,
            BingoCard.is_checked == True
        ).all()
        
        checked_positions: Set[int] = {card.position for card in checked_cards}
        
        # Define winning combinations based on grid size
        winning_combinations = self._get_winning_combinations(grid_size)
        
        # Check if any winning combination is satisfied
        for combination in winning_combinations:
            if combination.issubset(checked_positions):
                return True
        
        return False
    
    def _get_winning_combinations(self, grid_size: int) -> List[Set[int]]:
        """Get all possible winning combinations for the grid size."""
        combinations = []
        
        if grid_size == 3:
            # Rows
            combinations.extend([{0, 1, 2}, {3, 4, 5}, {6, 7, 8}])
            # Columns
            combinations.extend([{0, 3, 6}, {1, 4, 7}, {2, 5, 8}])
            # Diagonals
            combinations.extend([{0, 4, 8}, {2, 4, 6}])
        else:  # grid_size == 5
            # Rows
            combinations.extend([
                {0, 1, 2, 3, 4}, {5, 6, 7, 8, 9}, {10, 11, 12, 13, 14},
                {15, 16, 17, 18, 19}, {20, 21, 22, 23, 24}
            ])
            # Columns
            combinations.extend([
                {0, 5, 10, 15, 20}, {1, 6, 11, 16, 21}, {2, 7, 12, 17, 22},
                {3, 8, 13, 18, 23}, {4, 9, 14, 19, 24}
            ])
            # Diagonals
            combinations.extend([{0, 6, 12, 18, 24}, {4, 8, 12, 16, 20}])
        
        return combinations