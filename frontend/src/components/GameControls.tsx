'use client';

import React from 'react';
import { useBingoGame } from '@/hooks/useBingoGame';
import { RotateCcw, Home } from 'lucide-react';
import { clsx } from 'clsx';

interface GameControlsProps {
  onNewGame?: () => void;
}

export const GameControls: React.FC<GameControlsProps> = ({ onNewGame }) => {
  const { currentGame, startNewGame, resetGame, isLoading } = useBingoGame();

  const handleNewGame = () => {
    startNewGame();
    onNewGame?.();
  };

  const handleResetCard = () => {
    if (confirm('Are you sure you want to reset this card? All progress will be lost.')) {
      resetGame();
    }
  };

  if (!currentGame) return null;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="card p-4">
        <div className="flex flex-wrap items-center justify-center gap-3">
          {/* Reset Current Card */}
          <button
            onClick={handleResetCard}
            disabled={isLoading}
            className={clsx(
              'btn-secondary flex items-center space-x-2 text-sm',
              isLoading && 'opacity-50 cursor-not-allowed'
            )}
            title="Reset current card"
          >
            <RotateCcw size={16} />
            <span>Reset Card</span>
          </button>

          {/* New Game */}
          <button
            onClick={handleNewGame}
            disabled={isLoading}
            className={clsx(
              'btn-primary flex items-center space-x-2 text-sm',
              isLoading && 'opacity-50 cursor-not-allowed'
            )}
            title="Start a new game"
          >
            <Home size={16} />
            <span>New Game</span>
          </button>
        </div>

        {/* Game Instructions */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              How to Play
            </h4>
            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
              Click on phrases when they happen during the debate. Get a complete row, column, 
              or diagonal to win BINGO! The center space is always free in a 5×5 grid.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};