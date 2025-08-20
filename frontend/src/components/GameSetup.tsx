'use client';

import React, { useState } from 'react';
import { useBingoGame } from '@/hooks/useBingoGame';
import { GridSize } from '@/types/bingo';
import { clsx } from 'clsx';

interface GameSetupProps {
  onGameStart?: () => void;
}

export const GameSetup: React.FC<GameSetupProps> = ({ onGameStart }) => {
  const { createNewGame, isLoading, playerName, setPlayerName, gridSize, setGridSize } = useBingoGame();
  const [localPlayerName, setLocalPlayerName] = useState(playerName);
  const [localGridSize, setLocalGridSize] = useState<GridSize>(gridSize);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    setPlayerName(localPlayerName);
    setGridSize(localGridSize);
    
    createNewGame({
      player_name: localPlayerName || undefined,
      grid_size: localGridSize,
    });
    
    onGameStart?.();
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="card p-6">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">
          Start New Game
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Player Name */}
          <div>
            <label 
              htmlFor="playerName" 
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Player Name (Optional)
            </label>
            <input
              id="playerName"
              type="text"
              value={localPlayerName}
              onChange={(e) => setLocalPlayerName(e.target.value)}
              placeholder="Enter your name..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
              disabled={isLoading}
            />
          </div>

          {/* Grid Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Grid Size
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setLocalGridSize(3)}
                className={clsx(
                  'p-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                  localGridSize === 3
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:border-primary-300 dark:hover:border-primary-600'
                )}
                disabled={isLoading}
              >
                <div className="text-center">
                  <div className="text-lg font-semibold">3×3</div>
                  <div className="text-xs opacity-75">Quick Game</div>
                </div>
              </button>
              
              <button
                type="button"
                onClick={() => setLocalGridSize(5)}
                className={clsx(
                  'p-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                  localGridSize === 5
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:border-primary-300 dark:hover:border-primary-600'
                )}
                disabled={isLoading}
              >
                <div className="text-center">
                  <div className="text-lg font-semibold">5×5</div>
                  <div className="text-xs opacity-75">Classic</div>
                </div>
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={clsx(
              'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              isLoading
                ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                : 'btn-primary hover:scale-105 active:scale-95'
            )}
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Creating Game...</span>
              </div>
            ) : (
              'Start Game'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};