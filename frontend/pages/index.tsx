import { useState, useEffect, useRef } from 'react'

export default function Home() {
  const [connected, setConnected] = useState(false)
  const [roomCode, setRoomCode] = useState('LOBBY')
  const [messages, setMessages] = useState<string[]>([])
  const [bingoSquares, setBingoSquares] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  const defaultSquares = [
    'Fake news', 'My opponent', 'The American people', 'Jobs', 'Healthcare',
    'Economy', 'Climate change', 'Immigration', 'Tax cuts', 'Middle class',
    'Wall Street', 'Main Street', 'FREE', 'Infrastructure', 'Education',
    'National security', 'Freedom', 'Democracy', 'Bipartisan', 'Unity',
    'Working families', 'Small business', 'Innovation', 'Constitution', 'Values'
  ]

  useEffect(() => {
    const squares = [...defaultSquares]
    squares[12] = 'FREE'
    setBingoSquares(squares)
  }, [])

  const connectToRoom = () => {
    if (!roomCode.trim()) {
      setMessages(prev => [...prev, 'Error: Room code cannot be empty'])
      return
    }

    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU2NjA0NDc2LCJ0eXBlIjoiYWNjZXNzIn0.E93DNjY0rOPKpTwKIf1YoSkKT0vJVQofF_ubBcYZpXk'
    const wsUrl = `ws://localhost:8745/ws/${roomCode}?token=${token}`
    
    console.log('[WebSocket] Attempting connection to:', wsUrl)
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('[WebSocket] Connection opened')
      setConnected(true)
      setMessages(prev => [...prev, 'Connected to room ' + roomCode])
      
      setTimeout(() => {
        const createRoomMessage = {
          event: 'create_room',
          data: {
            name: 'Debate Bingo Room',
            max_players: 10,
            is_public: true,
            grid_size: 5
          }
        }
        console.log('[WebSocket] Sending create_room:', createRoomMessage)
        ws.send(JSON.stringify(createRoomMessage))
      }, 100)
    }
    
    ws.onmessage = (event) => {
      console.log('[WebSocket] Message received:', event.data)
      try {
        const data = JSON.parse(event.data)
        console.log(`[WebSocket] ${data.event} event:`, data)
        
        if (data.event === 'connected') {
          setMessages(prev => [...prev, `Connected: ${data.data.message}`])
        } else if (data.event === 'error') {
          setMessages(prev => [...prev, `Error: ${data.data.message || data.data.error}`])
          console.log(`[WebSocket] Unknown event:`, data)
        } else {
          setMessages(prev => [...prev, `Received: ${data.event}`])
        }
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error)
        setMessages(prev => [...prev, 'Received invalid message'])
      }
    }
    
    ws.onclose = () => {
      console.log('[WebSocket] Connection closed')
      setConnected(false)
      setMessages(prev => [...prev, 'Disconnected from room'])
    }
    
    ws.onerror = (error) => {
      console.error('[WebSocket] WebSocket error:', error)
      setMessages(prev => [...prev, 'Connection error'])
    }
    
    wsRef.current = ws
  }

  const markSquare = (index: number) => {
    if (!connected || !wsRef.current) return
    if (index === 12) return
    
    const square = bingoSquares[index]
    if (square.startsWith('✓')) return
    
    try {
      const markSquareMessage = {
        event: 'mark_square',
        data: {
          square_id: index,
          square_text: square
        }
      }
      console.log('[WebSocket] Sending mark_square:', markSquareMessage)
      wsRef.current.send(JSON.stringify(markSquareMessage))
      
      const updatedSquares = [...bingoSquares]
      updatedSquares[index] = `✓ ${square}`
      setBingoSquares(updatedSquares)
    } catch (error) {
      console.error('[WebSocket] Failed to send mark_square message:', error)
      setMessages(prev => [...prev, 'Failed to mark square'])
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-8 text-blue-600">
          Debate Bingo
        </h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value)}
              placeholder="Room Code"
              className="flex-1 px-4 py-2 border rounded-lg"
              disabled={connected}
            />
            <button
              onClick={connectToRoom}
              disabled={connected}
              className={`px-6 py-2 rounded-lg font-semibold ${
                connected 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {connected ? 'Connected' : 'Connect'}
            </button>
          </div>
          
          <div className="text-sm">
            Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Bingo Card</h2>
          <div className="grid grid-cols-5 gap-2">
            {bingoSquares.map((square, index) => (
              <button
                key={index}
                onClick={() => markSquare(index)}
                disabled={!connected || index === 12}
                className={`p-3 text-sm font-medium rounded-lg transition-colors ${
                  index === 12
                    ? 'bg-yellow-400 text-black cursor-default'
                    : square.startsWith('✓')
                    ? 'bg-green-500 text-white'
                    : connected
                    ? 'bg-blue-100 hover:bg-blue-200 text-blue-900'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                {square}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-2">Messages</h3>
          <div className="h-32 overflow-y-auto bg-gray-50 rounded p-3 text-sm">
            {messages.map((msg, index) => (
              <div key={index} className="text-gray-700">
                {msg}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}