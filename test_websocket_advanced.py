#!/usr/bin/env python3
"""
Advanced WebSocket test with multiple users and room interactions.
"""
import asyncio
import websockets
import json
from urllib.parse import urlencode

# Test configuration  
BASE_URL = "ws://localhost:8745"

# Demo authentication tokens (user1 and user2)
USER1_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidXNlcm5hbWUiOiJ1c2VyMSIsImV4cCI6MTc1NTcxNDk4MSwidHlwZSI6ImFjY2VzcyJ9.HpqubyRR15Si4eQCGQPvQe7t-4gOdecG_SqBORbaC5o"
USER2_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwidXNlcm5hbWUiOiJ1c2VyMiIsImV4cCI6MTc1NTcxNDk4MSwidHlwZSI6ImFjY2VzcyJ9.UlfTbfL817SsU3-NmufZ5GcUidQVGs7dBjtXoNGXhe8"

async def test_user_connection(user_name: str, token: str, room_code: str, test_actions: list):
    """Test a single user's WebSocket connection and actions."""
    
    query_params = urlencode({"token": token})
    websocket_url = f"{BASE_URL}/ws/{room_code}?{query_params}"
    
    print(f"🔌 {user_name} connecting to room {room_code}...")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            # Wait for connection confirmation
            initial_message = await websocket.recv()
            initial_data = json.loads(initial_message)
            print(f"✅ {user_name} connected: {initial_data['data']['message']}")
            
            # Perform test actions
            for action in test_actions:
                await websocket.send(json.dumps(action))
                print(f"📤 {user_name} sent: {action['event']}")
                
                # Listen for responses and broadcasts
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    response_data = json.loads(response)
                    print(f"📥 {user_name} received: {response_data['event']}")
                    
                    if response_data.get('data', {}).get('success') == False:
                        print(f"   ⚠️ Action failed: {response_data['data'].get('error')}")
                    
                except asyncio.TimeoutError:
                    print(f"   ⏰ {user_name} - no response received")
                
                # Small delay between actions
                await asyncio.sleep(0.5)
            
            # Keep connection open for a bit to receive broadcasts
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"📻 {user_name} broadcast: {data['event']}")
            except asyncio.TimeoutError:
                print(f"🔚 {user_name} - no more broadcasts")
                
    except Exception as e:
        print(f"❌ {user_name} error: {e}")

async def test_multiplayer_scenario():
    """Test multiplayer room interactions."""
    
    # Test scenario: User1 creates room, User2 joins, both interact
    room_code = "MULTI1"
    
    # Define user actions
    user1_actions = [
        {
            "event": "create_room",
            "data": {
                "name": "Multiplayer Test Room",
                "max_players": 10,
                "is_public": True,
                "grid_size": 5
            }
        }
    ]
    
    user2_actions = [
        {
            "event": "join_room",
            "data": {}
        }
    ]
    
    # Run both users concurrently
    await asyncio.gather(
        test_user_connection("User1", USER1_TOKEN, room_code, user1_actions),
        test_user_connection("User2", USER2_TOKEN, room_code, user2_actions)
    )

if __name__ == "__main__":
    print("🎮 Testing Advanced WebSocket Multiplayer Scenarios")
    print("=" * 60)
    
    try:
        asyncio.run(test_multiplayer_scenario())
        print("\n✅ Advanced WebSocket tests completed!")
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")