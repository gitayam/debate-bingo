export interface BingoPhrase {
  id: number;
  text: string;
  category?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BingoCard {
  id: number;
  phrase_id: number;
  position: number;
  is_checked: boolean;
  checked_at?: string;
  is_free_space: boolean;
  phrase: BingoPhrase;
  created_at: string;
  updated_at: string;
}

export interface BingoGameSession {
  id: number;
  session_id: string;
  player_name?: string;
  grid_size: number;
  is_completed: boolean;
  completed_at?: string;
  cards: BingoCard[];
  created_at: string;
  updated_at: string;
}

export interface CreateGameRequest {
  player_name?: string;
  grid_size: number;
}

export interface UpdateCardRequest {
  is_checked: boolean;
}

export interface CompleteGameRequest {
  winning_combination: number[];
  completion_time?: string;
}

export type GridSize = 3 | 5;

export interface WinningCombination {
  positions: number[];
  type: 'row' | 'column' | 'diagonal';
  index: number;
}