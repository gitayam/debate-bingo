'use client';

import React from 'react';
import { useBingoGame } from '@/hooks/useBingoGame';
import { Trophy, Clock, User } from 'lucide-react';
import { clsx } from 'clsx';

export const GameStatus: React.FC = () => {
  const { currentGame, isGameCompleted, winningCombination, timeline } = useBingoGame();

  if (!currentGame) return null;

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString();
  };

  const getGameDuration = () => {
    if (!currentGame.completed_at) return null;
    
    const start = new Date(currentGame.created_at);
    const end = new Date(currentGame.completed_at);
    const durationMs = end.getTime() - start.getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Game Info */}
      <div className="card p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            {currentGame.player_name && (
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <User size={16} />
                <span className="text-sm font-medium">{currentGame.player_name}</span>
              </div>
            )}
            
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <span className="text-sm">Grid: {currentGame.grid_size}×{currentGame.grid_size}</span>
            </div>
            
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <Clock size={16} />
              <span className="text-sm">
                Started: {formatTime(currentGame.created_at)}
              </span>
            </div>
          </div>

          {isGameCompleted && (
            <div className="flex items-center space-x-2 text-primary-600 dark:text-primary-400">
              <Trophy size={20} />
              <span className="font-semibold">BINGO!</span>
              {getGameDuration() && (
                <span className="text-sm">({getGameDuration()})</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bingo Celebration */}
      {isGameCompleted && (
        <div className="card p-6 bg-gradient-to-r from-primary-50 to-orange-50 dark:from-primary-900/20 dark:to-orange-900/20 border-primary-200 dark:border-primary-800">
          <div className="text-center space-y-4">
            <div className="text-4xl font-bold text-primary-600 dark:text-primary-400 animate-pulse-glow">
              🎉 BINGO! 🎉
            </div>
            
            {winningCombination && (
              <div className="text-lg text-gray-700 dark:text-gray-300">
                You got a{' '}
                <span className="font-semibold capitalize text-primary-600 dark:text-primary-400">
                  {winningCombination.type}
                </span>
                !
              </div>
            )}
            
            {getGameDuration() && (
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Completed in {getGameDuration()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Timeline */}
      {timeline.length > 0 && (
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
            Timeline
          </h3>
          
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {timeline.map((entry, index) => (
              <div
                key={index}
                className={clsx(
                  'flex items-start space-x-3 p-2 rounded-lg text-sm transition-all duration-200',
                  index === timeline.length - 1
                    ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800'
                    : 'bg-gray-50 dark:bg-gray-800'
                )}
              >
                <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap mt-0.5">
                  {formatTime(entry.timestamp)}
                </span>
                <span className="text-gray-700 dark:text-gray-300 flex-1">
                  {entry.phrase}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};