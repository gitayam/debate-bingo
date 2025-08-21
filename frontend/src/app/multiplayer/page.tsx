'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { RoomManager } from '@/components/RoomManager';
import { ActivityFeed } from '@/components/ActivityFeed';
import { Scoreboard } from '@/components/Scoreboard';
import { BingoGrid } from '@/components/BingoGrid';
import { GameStatus } from '@/components/GameStatus';
import { TestAuth } from '@/components/TestAuth';
import { LiveComments } from '@/components/LiveComments';
import { useBingoGame } from '@/hooks/useBingoGame';
import { useWebSocket } from '@/contexts/SimpleWebSocketContext';
import { Wifi, WifiOff } from 'lucide-react';

export default function MultiplayerPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { currentGame, gridSize } = useBingoGame();
  const { isConnected, roomCode, debugInfo, joinRoom } = useWebSocket();
  const [layout, setLayout] = useState<'desktop' | 'mobile'>('desktop');
  const [showDebug, setShowDebug] = useState(true); // Show debug in dev
  const [activeTab, setActiveTab] = useState<'game' | 'activity' | 'scoreboard'>('game');

  // Check authentication and pending room join
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    // Check if there's a pending room to join (from URL join)
    const pendingRoomCode = sessionStorage.getItem('pendingRoomCode');
    if (pendingRoomCode && isConnected && !roomCode) {
      sessionStorage.removeItem('pendingRoomCode');
      joinRoom(pendingRoomCode.toUpperCase()).catch(console.error);
    }
  }, [isAuthenticated, isConnected, roomCode, router]);

  // Detect screen size for responsive layout
  useEffect(() => {
    const checkLayout = () => {
      setLayout(window.innerWidth >= 1024 ? 'desktop' : 'mobile');
    };
    
    checkLayout();
    window.addEventListener('resize', checkLayout);
    return () => window.removeEventListener('resize', checkLayout);
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please log in to access multiplayer features.</p>
      </div>
    );
  }

  return (
    <div className="max-w-full">
      {/* Test Authentication */}
      <TestAuth />

      {/* Debug Panel (Development Only) */}
      {showDebug && (
        <div className="mb-4 p-4 bg-gray-100 border border-gray-300 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-bold text-sm">WebSocket Debug Info</h3>
            <button 
              onClick={() => setShowDebug(false)}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Hide
            </button>
          </div>
          <div className="text-xs font-mono space-y-1">
            <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>
            <div>Room: {roomCode || 'None'}</div>
            <div>Debug: {debugInfo || 'No debug info'}</div>
            <div>Token: {useAuthStore.getState().accessToken ? '✓ Available' : '✗ Missing'}</div>
          </div>
        </div>
      )}

      {/* Connection Status Bar */}
      <div className={`mb-4 px-4 py-2 rounded-lg flex items-center justify-between ${
        isConnected 
          ? 'bg-green-50 border border-green-200' 
          : 'bg-red-50 border border-red-200'
      }`}>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-700">Connected to multiplayer server</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-red-600" />
              <span className="text-sm text-red-700">Connecting to multiplayer server...</span>
            </>
          )}
        </div>
        {roomCode && (
          <span className="text-sm font-mono font-bold text-blue-600">
            Room: {roomCode}
          </span>
        )}
      </div>

      {/* Room Manager - Shows when not in a room */}
      {!roomCode && (
        <div className="mb-6">
          <RoomManager />
        </div>
      )}

      {/* Main Game Layout - Shows when in a room */}
      {roomCode && currentGame && (
        <>
          {/* Desktop Layout */}
          {layout === 'desktop' && (
            <div className="grid grid-cols-12 gap-4">
              {/* Left Panel - Unified Activity Feed */}
              <div className="col-span-3">
                <ActivityFeed includeTimeline />
              </div>

              {/* Center Panel - Game */}
              <div className="col-span-6 space-y-4">
                {/* Room Info with Share Button */}
                <RoomManager />
                
                {/* Game Info (without timeline) */}
                <GameStatus hideTimeline />
                
                {/* Bingo Grid - Primary Focus */}
                <div className="flex justify-center">
                  <BingoGrid gridSize={gridSize} />
                </div>
              </div>

              {/* Right Panel - Scores & Comments */}
              <div className="col-span-3 space-y-4">
                {/* Compact Scoreboard */}
                <Scoreboard compact />
                
                {/* Live Comments */}
                <LiveComments />
              </div>
            </div>
          )}

          {/* Mobile Layout */}
          {layout === 'mobile' && (
            <div className="space-y-4">
              {/* Room Info */}
              <RoomManager />
              
              {/* Tab Navigation */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="flex border-b border-gray-200">
                  <button
                    className={`flex-1 px-4 py-3 text-sm font-medium ${
                      activeTab === 'game' 
                        ? 'text-blue-600 border-b-2 border-blue-600' 
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    onClick={() => setActiveTab('game')}
                  >
                    Game
                  </button>
                  <button
                    className={`flex-1 px-4 py-3 text-sm font-medium ${
                      activeTab === 'activity' 
                        ? 'text-blue-600 border-b-2 border-blue-600' 
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    onClick={() => setActiveTab('activity')}
                  >
                    Activity
                  </button>
                  <button
                    className={`flex-1 px-4 py-3 text-sm font-medium ${
                      activeTab === 'scoreboard' 
                        ? 'text-blue-600 border-b-2 border-blue-600' 
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    onClick={() => setActiveTab('scoreboard')}
                  >
                    Scoreboard
                  </button>
                </div>

                {/* Tab Content */}
                <div className="p-4">
                  {/* Game Tab */}
                  {activeTab === 'game' && (
                    <div className="space-y-4">
                      <GameStatus />
                      <div className="flex justify-center">
                        <BingoGrid gridSize={gridSize} />
                      </div>
                    </div>
                  )}
                  
                  {/* Activity Tab */}
                  {activeTab === 'activity' && <ActivityFeed />}
                  
                  {/* Scoreboard Tab */}
                  {activeTab === 'scoreboard' && <Scoreboard />}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Loading State when in room but no game */}
      {roomCode && !currentGame && (
        <div className="text-center py-12">
          <div className="inline-flex items-center space-x-2 text-gray-600">
            <div className="w-6 h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span>Loading game...</span>
          </div>
        </div>
      )}

      {/* Instructions when not in a room */}
      {!roomCode && isConnected && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Welcome to Multiplayer Debate Bingo! 🎮
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <span>Create a room to host your own debate watch party</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <span>Join an existing room using a 6-character room code</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <span>See other players' moves in real-time</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <span>Compete for the top spot on the live scoreboard</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <span>Challenge suspicious bingo calls with the dispute system</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}