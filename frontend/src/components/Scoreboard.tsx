'use client';

import React from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { Trophy, Medal, Award, Target, User, TrendingUp } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export const Scoreboard: React.FC = () => {
  const { scoreboard, roomCode } = useWebSocket();
  const { user } = useAuthStore();

  if (!roomCode) {
    return null;
  }

  const getPositionIcon = (position: number) => {
    switch (position) {
      case 1:
        return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 2:
        return <Medal className="w-5 h-5 text-gray-400" />;
      case 3:
        return <Award className="w-5 h-5 text-orange-600" />;
      default:
        return <span className="w-5 h-5 flex items-center justify-center text-sm font-bold text-gray-500">{position}</span>;
    }
  };

  const getPositionStyle = (position: number) => {
    switch (position) {
      case 1:
        return 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-300';
      case 2:
        return 'bg-gradient-to-r from-gray-50 to-gray-100 border-gray-300';
      case 3:
        return 'bg-gradient-to-r from-orange-50 to-orange-100 border-orange-300';
      default:
        return 'bg-white hover:bg-gray-50 border-gray-200';
    }
  };

  const getProgressPercentage = (marked: number, total: number = 25) => {
    return Math.min(100, (marked / total) * 100);
  };

  return (
    <div className="bg-white rounded-lg shadow-md h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Live Scoreboard</h3>
            <p className="text-xs text-gray-500">Top {Math.min(10, scoreboard.length)} players</p>
          </div>
          <TrendingUp className="w-5 h-5 text-blue-600" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {scoreboard.length === 0 ? (
          <div className="text-center py-8">
            <Trophy className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No scores yet</p>
            <p className="text-xs text-gray-400 mt-1">Start marking squares to appear here!</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {scoreboard.map((entry) => {
              const isCurrentUser = user?.id === entry.userId;
              const progress = getProgressPercentage(entry.squaresMarked);
              
              return (
                <div
                  key={entry.userId}
                  className={`p-4 transition-all ${getPositionStyle(entry.position)} ${
                    isCurrentUser ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Position */}
                    <div className="flex-shrink-0">
                      {getPositionIcon(entry.position)}
                    </div>

                    {/* Player Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-gray-900 truncate">
                          {entry.displayName || entry.username}
                          {isCurrentUser && (
                            <span className="ml-2 text-xs font-normal text-blue-600">(You)</span>
                          )}
                        </h4>
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                          <span>{entry.squaresMarked} squares marked</span>
                          <span>{entry.squaresToBingo} to BINGO</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ease-out ${
                              entry.position === 1
                                ? 'bg-gradient-to-r from-yellow-400 to-yellow-500'
                                : entry.position === 2
                                ? 'bg-gradient-to-r from-gray-400 to-gray-500'
                                : entry.position === 3
                                ? 'bg-gradient-to-r from-orange-400 to-orange-500'
                                : 'bg-gradient-to-r from-blue-400 to-blue-500'
                            }`}
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Score */}
                    <div className="flex-shrink-0 text-right">
                      <div className="text-lg font-bold text-gray-900">
                        {entry.score}
                      </div>
                      <div className="text-xs text-gray-500">points</div>
                    </div>
                  </div>

                  {/* Achievement Badges (for top 3) */}
                  {entry.position <= 3 && (
                    <div className="mt-3 flex items-center gap-2">
                      {entry.position === 1 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          👑 Leader
                        </span>
                      )}
                      {entry.squaresMarked >= 10 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          🔥 On Fire
                        </span>
                      )}
                      {entry.squaresToBingo <= 3 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          🎯 Almost There
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {scoreboard.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              <span>{scoreboard.length} players competing</span>
            </div>
            <div className="flex items-center gap-1">
              <Target className="w-3 h-3" />
              <span>First to BINGO wins!</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};