'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useWebSocket } from '@/contexts/SimpleWebSocketContext';
import { useAuthStore } from '@/stores/authStore';

interface JoinRoomPageProps {
  params: {
    roomCode: string;
  };
}

export default function JoinRoomPage({ params }: JoinRoomPageProps) {
  const router = useRouter();
  const { isConnected, joinRoom } = useWebSocket();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    const handleJoin = async () => {
      // Check if user is authenticated
      if (!isAuthenticated) {
        // Store the room code in session storage to join after login
        sessionStorage.setItem('pendingRoomCode', params.roomCode);
        router.push('/'); // Redirect to login
        return;
      }

      // Wait for WebSocket connection
      if (!isConnected) {
        // Wait a bit for connection
        const timeout = setTimeout(() => {
          handleJoin(); // Retry
        }, 1000);
        return () => clearTimeout(timeout);
      }

      // Join the room
      try {
        await joinRoom(params.roomCode.toUpperCase());
        router.push('/multiplayer');
      } catch (error) {
        console.error('Failed to join room:', error);
        // Show error and redirect
        router.push('/multiplayer');
      }
    };

    handleJoin();
  }, [params.roomCode, isAuthenticated, isConnected, joinRoom, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full">
        <div className="text-center">
          <div className="mb-4">
            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Joining Room
          </h2>
          <p className="text-gray-600 mb-4">
            Room Code: <span className="font-mono font-bold text-blue-600">{params.roomCode.toUpperCase()}</span>
          </p>
          <p className="text-sm text-gray-500">
            {!isAuthenticated 
              ? 'Redirecting to login...' 
              : !isConnected 
              ? 'Connecting to server...'
              : 'Joining room...'}
          </p>
        </div>
      </div>
    </div>
  );
}