# 🎮 Multiplayer Debate Bingo - Testing Guide

## 🚀 Quick Start

### Service URLs
- **Frontend**: http://localhost:3745
- **Backend API**: http://localhost:8745
- **WebSocket**: ws://localhost:8745/ws

### Service Ports
- `3745` - Frontend (Next.js)
- `8745` - Backend API (FastAPI)
- `5445` - PostgreSQL Database
- `6390` - Redis (for WebSocket pub/sub)

## 📋 Prerequisites Check

1. **Verify all services are running:**
```bash
docker-compose ps
```

You should see 4 services running:
- debate-bingo-frontend-1
- debate-bingo-backend-1
- debate-bingo-postgres-1
- debate-bingo-redis-1

2. **If services are not running, start them:**
```bash
docker-compose up -d
```

3. **Check backend health:**
```bash
curl http://localhost:8745/health
```
Should return: `{"status":"healthy"}`

## 🧪 Step-by-Step Testing Guide

### Step 1: Create Test Users

First, create demo users for testing multiplayer features:

```bash
python3 create_demo_user.py
```

This creates two demo users:
- **User 1**: email: `user1@demo.com`, password: `demo123`
- **User 2**: email: `user2@demo.com`, password: `demo123`

### Step 2: Test Solo Play (Baseline)

1. Open http://localhost:3745 in your browser
2. Click "Sign In" in the header
3. Sign in with `user1@demo.com` / `demo123`
4. Start a solo game to verify basic functionality works

### Step 3: Test Multiplayer Features

#### A. Test with Single User (Room Creation)

1. **Navigate to Multiplayer:**
   - After signing in, click "Multiplayer" in the header
   - You'll see the multiplayer lobby

2. **Create a Room:**
   - Click "Create Room"
   - Enter room name: "Test Debate Party"
   - Set max players: 10
   - Leave "Public Room" checked
   - Click "Create Room"

3. **Verify Room Creation:**
   - You should see a room code (6 characters like `ABC123`)
   - Room info should show "Test Debate Party"
   - Player count should show "1/10 players"
   - Click the copy button next to the room code

#### B. Test with Two Users (Full Multiplayer)

**Window 1 - Host (User 1):**
1. Open http://localhost:3745 in Chrome/Firefox
2. Sign in as `user1@demo.com`
3. Go to Multiplayer
4. Create a room called "Presidential Debate"
5. Copy the room code

**Window 2 - Guest (User 2):**
1. Open http://localhost:3745 in an incognito/private window
2. Sign in as `user2@demo.com`
3. Go to Multiplayer
4. Click "Join Room"
5. Enter the room code from Window 1
6. Click "Join Room"

**Expected Results:**
- Both windows should show "2/10 players"
- Window 1 should see activity: "Demo User 2 joined the room"
- Both windows should see the same room code

### Step 4: Test Real-Time Features

#### A. Activity Feed Testing

With both users in the same room:

1. **Start a debate game** (if not already started)
2. **In Window 1 (User 1):**
   - Mark a square on the bingo card
3. **In Window 2 (User 2):**
   - Check the Activity Feed (left panel)
   - Should see: "user1 marked '[phrase]'"

#### B. Scoreboard Testing

1. **Both users mark different squares**
2. **Check the Scoreboard (right panel):**
   - Should show both users
   - Scores should update in real-time
   - User with more marks should be ranked #1

#### C. Connection Status

1. **Test disconnection:**
   - Stop the backend: `docker-compose stop backend`
   - Both windows should show "Connecting to multiplayer server..."
   - Restart backend: `docker-compose start backend`
   - Should auto-reconnect

### Step 5: Mobile Testing

1. **Find your computer's local IP:**
   ```bash
   # On Mac:
   ipconfig getifaddr en0
   # On Windows:
   ipconfig
   ```

2. **On your phone:**
   - Connect to same WiFi network
   - Open browser to `http://[YOUR-IP]:3745`
   - Sign in and join the room
   - Verify mobile layout (tabs instead of panels)

## 🔍 What to Look For

### ✅ Success Indicators
- WebSocket shows "Connected to multiplayer server" (green bar)
- Room code is displayed and copyable
- Activity feed updates in real-time
- Scoreboard shows all players
- Player count updates when users join/leave
- No console errors in browser DevTools

### ⚠️ Common Issues & Solutions

**Issue: "Connecting to multiplayer server..." never resolves**
- Solution: Check backend is running: `docker-compose logs backend`
- Verify WebSocket endpoint: `curl http://localhost:8745/health`

**Issue: Can't create/join rooms**
- Solution: Check you're logged in (user menu visible in header)
- Verify database is running: `docker-compose logs postgres`

**Issue: Activity feed not updating**
- Solution: Open browser console (F12)
- Look for WebSocket errors
- Try refreshing both browser windows

**Issue: "Failed to join room" error**
- Solution: Verify room code is correct (6 characters, uppercase)
- Check room still exists (rooms persist until server restart)

## 🛠️ Advanced Testing

### WebSocket Direct Testing

Test WebSocket connection directly:
```bash
python3 test_websocket.py
```

Expected output:
- ✅ WebSocket connection established!
- ✅ Successfully connected to room!
- ✅ Ping/pong test successful!
- ✅ Room creation successful!

### Database Inspection

Check created rooms in database:
```bash
docker-compose exec postgres psql -U postgres -d debate_bingo_dev -c "SELECT room_code, name, current_players FROM game_rooms;"
```

### Monitor Real-Time Logs

Watch backend logs for WebSocket activity:
```bash
docker-compose logs -f backend
```

## 📊 Testing Checklist

- [ ] Solo play works normally
- [ ] Can sign in with demo users
- [ ] Can create a multiplayer room
- [ ] Room code is generated and copyable
- [ ] Can join room with second user
- [ ] Player count updates correctly
- [ ] Activity feed shows join/leave events
- [ ] Activity feed shows square marks
- [ ] Scoreboard updates in real-time
- [ ] Connection status indicator works
- [ ] Mobile layout displays correctly
- [ ] Can leave and rejoin rooms

## 🎯 Expected User Flow

1. **User signs in** → Sees "Multiplayer" option
2. **Creates/joins room** → Sees room info and code
3. **Other users join** → Activity feed shows joins
4. **Users play bingo** → Marks appear in activity feed
5. **Scores update** → Live scoreboard shows rankings
6. **Someone calls BINGO** → Critical alert in activity feed
7. **Users can dispute** → Voting system activates (Phase 3)

## 🐛 Troubleshooting Commands

```bash
# Restart all services
docker-compose restart

# View all logs
docker-compose logs

# Reset database (warning: deletes all data)
docker-compose down -v
docker-compose up -d

# Check WebSocket connections
docker-compose exec backend netstat -an | grep 8000

# Verify Redis is working
docker-compose exec redis redis-cli ping
```

## 🎉 Success Criteria

You've successfully tested the multiplayer features if:
1. Two users can join the same room
2. Both see each other's player count
3. Activity feed updates for both users
4. Scoreboard shows both players
5. No errors in browser console
6. Connection remains stable

---

**Next Steps:** Once basic multiplayer is working, the next phase would integrate square marking from the actual bingo game to trigger real-time updates!