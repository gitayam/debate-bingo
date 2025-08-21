'use client';

import React, { useState } from 'react';
import { useAuthStore } from '@/stores/authStore';

export const TestAuth: React.FC = () => {
  const [showTestAuth, setShowTestAuth] = useState(true);
  const { setTokens, setUser } = useAuthStore();

  const handleTestLogin = (userId: number, username: string) => {
    // Generate a test token (this would normally come from the login API)
    const testToken = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIke userId}","username":"${username}","exp":${Math.floor(Date.now() / 1000) + 3600},"type":"access"}.test-signature`;
    
    // Use the real token from our demo user generation (30-day expiry, correct secret key)
    const realToken = userId === 2 
      ? 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidXNlcm5hbWUiOiJ1c2VyMSIsImV4cCI6MTc1ODM2ODI0NSwidHlwZSI6ImFjY2VzcyJ9.1QgvJXzvOBWGq7bEqJODSqz3wEMTDgkXcqneV5-ZXks'
      : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwidXNlcm5hbWUiOiJ1c2VyMiIsImV4cCI6MTc1ODM2ODI0NSwidHlwZSI6ImFjY2VzcyJ9.B7nFh8iWZCt1JYXcg3NO-WYarv5bDwg3N_NaeF5WvnM';
    
    setTokens(realToken, realToken); // Use same token for both access and refresh for testing
    setUser({
      id: userId,
      email: `user${userId === 2 ? '1' : '2'}@demo.com`,
      username: username,
      display_name: `Demo User ${userId === 2 ? 'One' : 'Two'}`,
      avatar_url: undefined,
      bio: undefined,
      is_verified: true,
      created_at: new Date().toISOString(),
    });
    
    setShowTestAuth(false);
    console.log(`[TestAuth] Logged in as ${username} with token:`, realToken.substring(0, 50) + '...');
  };

  if (!showTestAuth) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-yellow-100 border-b-2 border-yellow-300 p-3">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-yellow-800">🧪 Test Authentication (Development Only)</h3>
            <p className="text-sm text-yellow-700">Quick login for testing WebSocket features</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleTestLogin(2, 'user1')}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
            >
              Login as User 1
            </button>
            <button
              onClick={() => handleTestLogin(3, 'user2')}
              className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
            >
              Login as User 2
            </button>
            <button
              onClick={() => setShowTestAuth(false)}
              className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
            >
              Hide
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};