#!/usr/bin/env python3
"""
Simple WebSocket test to verify the fixes.
"""
import asyncio
import websockets
import json

async def test_websocket():
    url = "ws://localhost:8745/ws/LOBBY"
    
    print(f"🔌 Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for initial message
            initial_msg = await websocket.recv()
            initial_data = json.loads(initial_msg)
            print(f"📥 Initial message: {initial_data}")
            
            # Send create_room event
            create_room_msg = {
                "event": "create_room",
                "data": {
                    "name": "Test Room",
                    "max_players": 10,
                    "is_public": True,
                    "grid_size": 5
                }
            }
            
            print(f"📤 Sending: {create_room_msg}")
            await websocket.send(json.dumps(create_room_msg))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            print(f"📥 Response: {response_data}")
            
            # Send invalid message to test error handling
            invalid_msg = {"invalid": "message"}
            print(f"📤 Sending invalid message: {invalid_msg}")
            await websocket.send(json.dumps(invalid_msg))
            
            # Wait for error response
            error_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            error_data = json.loads(error_response)
            print(f"📥 Error response: {error_data}")
            
            print("✅ Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())