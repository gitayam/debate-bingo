import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check backend health
    const backendResponse = await fetch('http://backend:8000/health').catch(() => null);
    const backendHealth = backendResponse?.ok ? 'healthy' : 'unreachable';
    
    // Check WebSocket endpoint
    const wsTest = await fetch('http://backend:8000/ws/TEST', {
      headers: {
        'Upgrade': 'websocket',
        'Connection': 'Upgrade',
      }
    }).catch(() => null);
    const wsAvailable = wsTest?.status === 426 || wsTest?.status === 400; // 426 = Upgrade Required, 400 = Bad Request (but endpoint exists)
    
    return NextResponse.json({
      status: 'ok',
      backend: backendHealth,
      websocket: wsAvailable ? 'available' : 'unavailable',
      timestamp: new Date().toISOString(),
      urls: {
        frontend: 'http://localhost:3745',
        backend: 'http://localhost:8745',
        websocket: 'ws://localhost:8745/ws/{room_code}',
        multiplayer: 'http://localhost:3745/multiplayer'
      },
      testUsers: [
        { email: 'user1@demo.com', password: 'demo123' },
        { email: 'user2@demo.com', password: 'demo123' }
      ]
    });
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}