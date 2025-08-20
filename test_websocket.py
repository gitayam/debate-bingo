#!/usr/bin/env python3
"""
Simple WebSocket test script to verify multiplayer room functionality.
"""
import asyncio
import websockets
import json
import sys
from urllib.parse import urlencode

# Test configuration
BASE_URL = "ws://localhost:8745"
ROOM_CODE = "TEST01"

# Demo authentication token (generated from create_demo_user.py)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidXNlcm5hbWUiOiJ1c2VyMSIsImV4cCI6MTc1NTcxNDk4MSwidHlwZSI6ImFjY2VzcyJ9.HpqubyRR15Si4eQCGQPvQe7t-4gOdecG_SqBORbaC5o"

async def test_websocket_connection():
    """Test basic WebSocket connection and room functionality."""
    
    # Build WebSocket URL with authentication
    query_params = urlencode({"token": TEST_TOKEN})
    websocket_url = f"{BASE_URL}/ws/{ROOM_CODE}?{query_params}"
    
    print(f"Connecting to: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Listen for initial connection message
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                initial_data = json.loads(initial_message)
                print(f"📨 Initial message: {initial_data}")
                
                if initial_data.get("event") == "connected":
                    print("✅ Successfully connected to room!")
                else:
                    print(f"⚠️  Unexpected initial message: {initial_data}")
                    
            except asyncio.TimeoutError:
                print("⚠️  No initial message received within 5 seconds")
            
            # Test ping/pong
            print("\n🏓 Testing ping/pong...")
            ping_message = {
                "event": "ping",
                "data": {"timestamp": "2025-08-20T14:00:00Z"}
            }
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong response
            try:
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong_response)
                print(f"📨 Pong response: {pong_data}")
                
                if pong_data.get("event") == "pong":
                    print("✅ Ping/pong test successful!")
                else:
                    print(f"❌ Expected pong, got: {pong_data}")
                    
            except asyncio.TimeoutError:
                print("❌ Ping/pong test failed - no response")
            
            # Test room creation
            print("\n🏠 Testing room creation...")
            create_room_message = {
                "event": "create_room",
                "data": {
                    "name": "Test Debate Room",
                    "max_players": 10,
                    "is_public": True,
                    "grid_size": 5
                }
            }
            await websocket.send(json.dumps(create_room_message))
            
            # Wait for room creation response
            try:
                room_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                room_data = json.loads(room_response)
                print(f"📨 Room creation response: {room_data}")
                
                if room_data.get("event") == "room_created":
                    if room_data.get("data", {}).get("success"):
                        print("✅ Room creation successful!")
                        room_code = room_data["data"].get("room_code")
                        print(f"   Room code: {room_code}")
                    else:
                        print(f"❌ Room creation failed: {room_data['data'].get('error')}")
                else:
                    print(f"❌ Unexpected room creation response: {room_data}")
                    
            except asyncio.TimeoutError:
                print("❌ Room creation test failed - no response")
            
            print("\n✅ WebSocket test completed!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend server running?")
        print("   Try: docker-compose up backend")
        
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with status: {e.status_code}")
        if e.status_code == 401:
            print("   This is expected - authentication is not implemented yet")
        elif e.status_code == 404:
            print("   WebSocket endpoint not found - check the URL")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🧪 Testing WebSocket Multiplayer Infrastructure")
    print("=" * 50)
    
    try:
        asyncio.run(test_websocket_connection())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)