'use client';

import React, { useState } from 'react';
import { GameSetup } from '@/components/GameSetup';
import { BingoGrid } from '@/components/BingoGrid';
import { GameStatus } from '@/components/GameStatus';
import { GameControls } from '@/components/GameControls';
import { useBingoGame } from '@/hooks/useBingoGame';

export default function HomePage() {
  const { currentGame, gridSize, error } = useBingoGame();
  const [showSetup, setShowSetup] = useState(!currentGame);

  const handleGameStart = () => {
    setShowSetup(false);
  };

  const handleNewGame = () => {
    setShowSetup(true);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Error Display */}
      {error && (
        <div className="card p-4 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <div className="text-red-700 dark:text-red-300 text-center">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">
              {typeof error === 'string' ? error : 'Something went wrong. Please try again.'}
            </p>
          </div>
        </div>
      )}

      {/* Game Setup or Game Play */}
      {showSetup || !currentGame ? (
        <div className="animate-fade-in">
          <GameSetup onGameStart={handleGameStart} />
        </div>
      ) : (
        <div className="space-y-6 animate-fade-in">
          {/* Game Status */}
          <GameStatus />

          {/* Bingo Grid */}
          <div className="flex justify-center">
            <BingoGrid gridSize={gridSize} />
          </div>

          {/* Game Controls */}
          <GameControls onNewGame={handleNewGame} />
        </div>
      )}

      {/* Loading State */}
      {!showSetup && !currentGame && !error && (
        <div className="text-center py-12">
          <div className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <div className="w-6 h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span>Loading game...</span>
          </div>
        </div>
      )}
    </div>
  );
}