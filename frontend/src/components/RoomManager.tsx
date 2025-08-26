'use client';

import React, { useState } from 'react';
import { useWebSocket } from '@/contexts/SimpleWebSocketContext';
import { Users, Plus, LogIn, Copy, Check, Globe, Lock, Share2, Link, QrCode, MessageCircle } from 'lucide-react';

export const RoomManager: React.FC = () => {
  const { 
    isConnected, 
    roomCode, 
    roomData, 
    joinRoom, 
    createRoom, 
    leaveRoom 
  } = useWebSocket();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [roomName, setRoomName] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(50);
  const [isPublic, setIsPublic] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copiedType, setCopiedType] = useState<'code' | 'link' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCreateRoom = async () => {
    if (!roomName.trim()) {
      setError('Please enter a room name');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const newRoomCode = await createRoom({
        name: roomName,
        maxPlayers,
        isPublic,
        gridSize: 5,
      });

      console.log('Room created with code:', newRoomCode);
      setShowCreateModal(false);
      setRoomName('');
      
      // Auto-join the created room
      await joinRoom(newRoomCode);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create room');
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!joinCode.trim()) {
      setError('Please enter a room code');
      return;
    }

    setIsJoining(true);
    setError(null);

    try {
      await joinRoom(joinCode.toUpperCase());
      setShowJoinModal(false);
      setJoinCode('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join room');
    } finally {
      setIsJoining(false);
    }
  };

  const handleCopyRoomCode = () => {
    if (roomCode) {
      navigator.clipboard.writeText(roomCode);
      setCopied(true);
      setCopiedType('code');
      setTimeout(() => {
        setCopied(false);
        setCopiedType(null);
      }, 2000);
    }
  };

  const getRoomUrl = () => {
    if (typeof window !== 'undefined' && roomCode) {
      return `${window.location.origin}/multiplayer/join/${roomCode}`;
    }
    return '';
  };

  const handleCopyLink = () => {
    const url = getRoomUrl();
    if (url) {
      navigator.clipboard.writeText(url);
      setCopied(true);
      setCopiedType('link');
      setTimeout(() => {
        setCopied(false);
        setCopiedType(null);
      }, 2000);
    }
  };

  const handleShareSocial = (platform: 'twitter' | 'whatsapp' | 'telegram') => {
    const url = getRoomUrl();
    const text = `Join my Debate Bingo room! Room code: ${roomCode}`;
    
    let shareUrl = '';
    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
        break;
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${encodeURIComponent(`${text}\n${url}`)}`;
        break;
      case 'telegram':
        shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
        break;
    }
    
    if (shareUrl) {
      window.open(shareUrl, '_blank');
    }
  };

  // If not connected to WebSocket
  if (!isConnected) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">Connecting to multiplayer server...</p>
      </div>
    );
  }

  // If in a room
  if (roomCode && roomData) {
    return (
      <>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{roomData.name}</h3>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Users className="w-4 h-4" />
                  <span>{roomData.currentPlayers}/{roomData.maxPlayers} players</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  {roomData.isActive ? (
                    <Globe className="w-4 h-4 text-green-500" />
                  ) : (
                    <Lock className="w-4 h-4 text-gray-400" />
                  )}
                  <span>{roomData.isActive ? 'Active' : 'Inactive'}</span>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowShareModal(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button
                onClick={leaveRoom}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 border border-red-300 rounded-md hover:bg-red-50 transition-colors"
              >
                Leave Room
              </button>
            </div>
          </div>

          <div className="bg-gray-50 rounded-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Room Code</p>
                <code className="text-2xl font-mono font-bold text-blue-600 tracking-wider">
                  {roomCode}
                </code>
              </div>
              <button
                onClick={handleCopyRoomCode}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded-md transition-colors"
                title="Copy room code"
              >
                {copied && copiedType === 'code' ? (
                  <Check className="w-5 h-5 text-green-600" />
                ) : (
                  <Copy className="w-5 h-5" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Share this code with others to let them join your room
            </p>
          </div>
        </div>

        {/* Share Modal */}
        {showShareModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Share Room</h3>
              
              <div className="space-y-4">
                {/* Room Code */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Room Code</p>
                  <div className="flex items-center justify-between">
                    <code className="text-xl font-mono font-bold text-blue-600">{roomCode}</code>
                    <button
                      onClick={handleCopyRoomCode}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                    >
                      {copied && copiedType === 'code' ? 'Copied!' : 'Copy Code'}
                    </button>
                  </div>
                </div>

                {/* Direct Link */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Direct Link</p>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={getRoomUrl()}
                      readOnly
                      className="flex-1 px-2 py-1 text-sm bg-white border border-gray-300 rounded-md font-mono text-xs"
                    />
                    <button
                      onClick={handleCopyLink}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                    >
                      {copied && copiedType === 'link' ? 'Copied!' : 'Copy Link'}
                    </button>
                  </div>
                </div>

                {/* Social Sharing */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Share on Social Media</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleShareSocial('twitter')}
                      className="flex-1 px-3 py-2 bg-blue-400 text-white rounded-md hover:bg-blue-500 transition-colors text-sm"
                    >
                      Twitter
                    </button>
                    <button
                      onClick={() => handleShareSocial('whatsapp')}
                      className="flex-1 px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm"
                    >
                      WhatsApp
                    </button>
                    <button
                      onClick={() => handleShareSocial('telegram')}
                      className="flex-1 px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm"
                    >
                      Telegram
                    </button>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowShareModal(false)}
                className="w-full mt-6 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </>
    );
  }

  // Room selection screen
  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Multiplayer Rooms</h2>
        <p className="text-gray-600 mb-6">
          Create a new room or join an existing one to play with others in real-time!
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Create Room
          </button>
          <button
            onClick={() => setShowJoinModal(true)}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 transition-colors"
          >
            <LogIn className="w-5 h-5" />
            Join Room
          </button>
        </div>
      </div>

      {/* Create Room Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Room</h3>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="room-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Room Name
                </label>
                <input
                  id="room-name"
                  type="text"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  placeholder="e.g., Presidential Debate Watch"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={100}
                />
              </div>

              <div>
                <label htmlFor="max-players" className="block text-sm font-medium text-gray-700 mb-1">
                  Max Players
                </label>
                <input
                  id="max-players"
                  type="number"
                  value={maxPlayers}
                  onChange={(e) => setMaxPlayers(Math.max(2, Math.min(100, parseInt(e.target.value) || 2)))}
                  min="2"
                  max="100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Public Room (visible to everyone)
                  </span>
                </label>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateRoom}
                disabled={isCreating}
                className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
              >
                {isCreating ? 'Creating...' : 'Create Room'}
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setError(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Join Room Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Join Room</h3>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="room-code" className="block text-sm font-medium text-gray-700 mb-1">
                  Room Code
                </label>
                <input
                  id="room-code"
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="e.g., ABC123"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-lg tracking-wider uppercase"
                  maxLength={6}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter the 6-character code shared by the room host
                </p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleJoinRoom}
                disabled={isJoining}
                className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors"
              >
                {isJoining ? 'Joining...' : 'Join Room'}
              </button>
              <button
                onClick={() => {
                  setShowJoinModal(false);
                  setError(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};