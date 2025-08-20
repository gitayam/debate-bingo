import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  BingoGameSession,
  BingoCard,
  GridSize,
  WinningCombination,
} from '@/types/bingo';

interface BingoState {
  // Game state
  currentGame: BingoGameSession | null;
  isLoading: boolean;
  error: string | null;
  
  // Game configuration
  playerName: string;
  gridSize: GridSize;
  
  // Game progress
  checkedPositions: Set<number>;
  timeline: Array<{ position: number; phrase: string; timestamp: string }>;
  winningCombination: WinningCombination | null;
  isGameCompleted: boolean;
  
  // Actions
  setCurrentGame: (game: BingoGameSession | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPlayerName: (name: string) => void;
  setGridSize: (size: GridSize) => void;
  
  // Game actions
  toggleCardPosition: (position: number) => void;
  completeGame: (combination: WinningCombination) => void;
  resetGame: () => void;
  
  // Utility functions
  getCard: (position: number) => BingoCard | undefined;
  isPositionChecked: (position: number) => boolean;
  getWinningCombinations: () => WinningCombination[];
  checkForWin: () => WinningCombination | null;
}

const getWinningCombinationsForGrid = (gridSize: GridSize): WinningCombination[] => {
  const combinations: WinningCombination[] = [];
  
  if (gridSize === 3) {
    // Rows
    combinations.push(
      { positions: [0, 1, 2], type: 'row', index: 0 },
      { positions: [3, 4, 5], type: 'row', index: 1 },
      { positions: [6, 7, 8], type: 'row', index: 2 }
    );
    // Columns
    combinations.push(
      { positions: [0, 3, 6], type: 'column', index: 0 },
      { positions: [1, 4, 7], type: 'column', index: 1 },
      { positions: [2, 5, 8], type: 'column', index: 2 }
    );
    // Diagonals
    combinations.push(
      { positions: [0, 4, 8], type: 'diagonal', index: 0 },
      { positions: [2, 4, 6], type: 'diagonal', index: 1 }
    );
  } else {
    // 5x5 grid
    // Rows
    for (let i = 0; i < 5; i++) {
      combinations.push({
        positions: [i * 5, i * 5 + 1, i * 5 + 2, i * 5 + 3, i * 5 + 4],
        type: 'row',
        index: i,
      });
    }
    // Columns
    for (let i = 0; i < 5; i++) {
      combinations.push({
        positions: [i, i + 5, i + 10, i + 15, i + 20],
        type: 'column',
        index: i,
      });
    }
    // Diagonals
    combinations.push(
      { positions: [0, 6, 12, 18, 24], type: 'diagonal', index: 0 },
      { positions: [4, 8, 12, 16, 20], type: 'diagonal', index: 1 }
    );
  }
  
  return combinations;
};

export const useBingoStore = create<BingoState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentGame: null,
      isLoading: false,
      error: null,
      playerName: '',
      gridSize: 5,
      checkedPositions: new Set(),
      timeline: [],
      winningCombination: null,
      isGameCompleted: false,
      
      // Basic setters
      setCurrentGame: (game) => {
        set({ currentGame: game });
        if (game) {
          const checkedPositions = new Set(
            game.cards
              .filter((card) => card.is_checked)
              .map((card) => card.position)
          );
          set({ checkedPositions });
        }
      },
      
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      setPlayerName: (name) => set({ playerName: name }),
      setGridSize: (size) => set({ gridSize: size }),
      
      // Game actions
      toggleCardPosition: (position) => {
        const { currentGame, checkedPositions } = get();
        if (!currentGame) return;
        
        const card = currentGame.cards.find((c) => c.position === position);
        if (!card || card.is_free_space) return;
        
        const newCheckedPositions = new Set(checkedPositions);
        const isCurrentlyChecked = checkedPositions.has(position);
        
        if (isCurrentlyChecked) {
          newCheckedPositions.delete(position);
        } else {
          newCheckedPositions.add(position);
          
          // Add to timeline
          const newTimelineEntry = {
            position,
            phrase: card.phrase.text,
            timestamp: new Date().toISOString(),
          };
          
          set((state) => ({
            timeline: [...state.timeline, newTimelineEntry],
          }));
        }
        
        set({ checkedPositions: newCheckedPositions });
        
        // Check for win
        const winningCombination = get().checkForWin();
        if (winningCombination && !get().isGameCompleted) {
          get().completeGame(winningCombination);
        }
      },
      
      completeGame: (combination) => {
        set({
          winningCombination: combination,
          isGameCompleted: true,
        });
      },
      
      resetGame: () => {
        set({
          currentGame: null,
          checkedPositions: new Set(),
          timeline: [],
          winningCombination: null,
          isGameCompleted: false,
          error: null,
        });
      },
      
      // Utility functions
      getCard: (position) => {
        const { currentGame } = get();
        return currentGame?.cards.find((card) => card.position === position);
      },
      
      isPositionChecked: (position) => {
        const { checkedPositions } = get();
        return checkedPositions.has(position);
      },
      
      getWinningCombinations: () => {
        const { gridSize } = get();
        return getWinningCombinationsForGrid(gridSize);
      },
      
      checkForWin: () => {
        const { checkedPositions, gridSize } = get();
        const combinations = getWinningCombinationsForGrid(gridSize);
        
        for (const combination of combinations) {
          const isWinning = combination.positions.every((pos) =>
            checkedPositions.has(pos)
          );
          if (isWinning) {
            return combination;
          }
        }
        
        return null;
      },
    }),
    {
      name: 'bingo-game-storage',
      partialize: (state) => ({
        playerName: state.playerName,
        gridSize: state.gridSize,
        currentGame: state.currentGame,
        checkedPositions: Array.from(state.checkedPositions),
        timeline: state.timeline,
        winningCombination: state.winningCombination,
        isGameCompleted: state.isGameCompleted,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray(state.checkedPositions)) {
          state.checkedPositions = new Set(state.checkedPositions);
        }
      },
    }
  )
);