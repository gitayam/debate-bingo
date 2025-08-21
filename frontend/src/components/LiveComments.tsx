'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '@/contexts/SimpleWebSocketContext';
import { useAuthStore } from '@/stores/authStore';
import { MessageCircle, Send, Clock } from 'lucide-react';

interface Comment {
  id: string;
  userId: string;
  username: string;
  displayName?: string;
  message: string;
  timestamp: string;
}

export const LiveComments: React.FC = () => {
  const { roomCode, isConnected, socket } = useWebSocket();
  const { user } = useAuthStore();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isSending, setIsSending] = useState(false);
  const commentsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new comments arrive
  const scrollToBottom = () => {
    commentsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [comments]);

  // Listen for incoming comments via WebSocket
  useEffect(() => {
    if (!socket || !isConnected) return;

    const handleComment = (data: any) => {
      if (data.type === 'comment' || data.type === 'new_comment') {
        const comment: Comment = {
          id: data.id || `${Date.now()}-${Math.random()}`,
          userId: data.userId,
          username: data.username,
          displayName: data.displayName,
          message: data.message,
          timestamp: data.timestamp || new Date().toISOString()
        };
        setComments(prev => [...prev, comment].slice(-50)); // Keep last 50 comments
      }
    };

    const handleCommentsUpdate = (data: any) => {
      if (data.type === 'comments_update' && Array.isArray(data.comments)) {
        setComments(data.comments.slice(-50));
      }
    };

    socket.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        handleComment(data);
        handleCommentsUpdate(data);
      } catch (error) {
        console.error('Error parsing comment message:', error);
      }
    });

    // Request initial comments when joining room
    if (roomCode) {
      socket.send(JSON.stringify({
        type: 'get_comments',
        roomCode
      }));
    }

    return () => {
      // Cleanup listeners if needed
    };
  }, [socket, isConnected, roomCode]);

  const handleSendComment = () => {
    if (!newComment.trim() || !socket || !isConnected || !roomCode || isSending) {
      return;
    }

    setIsSending(true);

    try {
      const commentData = {
        type: 'send_comment',
        roomCode,
        message: newComment.trim(),
        userId: user?.id,
        username: user?.username || 'Anonymous',
        displayName: user?.displayName,
        timestamp: new Date().toISOString()
      };

      socket.send(JSON.stringify(commentData));

      // Optimistically add the comment locally
      const optimisticComment: Comment = {
        id: `${Date.now()}-${Math.random()}`,
        userId: user?.id || '',
        username: user?.username || 'Anonymous',
        displayName: user?.displayName,
        message: newComment.trim(),
        timestamp: new Date().toISOString()
      };
      
      setComments(prev => [...prev, optimisticComment].slice(-50));
      setNewComment('');
    } catch (error) {
      console.error('Error sending comment:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendComment();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) {
      return 'just now';
    } else if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!roomCode) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md flex flex-col h-[400px]">
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Live Chat</h3>
          <MessageCircle className="w-4 h-4 text-blue-600" />
        </div>
      </div>

      {/* Comments List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {comments.length === 0 ? (
          <div className="text-center py-8">
            <MessageCircle className="w-6 h-6 text-gray-300 mx-auto mb-2" />
            <p className="text-xs text-gray-500">No comments yet</p>
            <p className="text-xs text-gray-400 mt-1">Be the first to comment!</p>
          </div>
        ) : (
          <>
            {comments.map((comment) => {
              const isCurrentUser = user?.id === comment.userId;
              return (
                <div
                  key={comment.id}
                  className={`flex gap-2 ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[80%] ${isCurrentUser ? 'order-2' : ''}`}>
                    <div className={`rounded-lg px-3 py-2 ${
                      isCurrentUser 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      {!isCurrentUser && (
                        <p className={`text-xs font-medium mb-1 ${
                          isCurrentUser ? 'text-blue-100' : 'text-gray-600'
                        }`}>
                          {comment.displayName || comment.username}
                        </p>
                      )}
                      <p className="text-sm break-words">{comment.message}</p>
                    </div>
                    <div className="flex items-center gap-1 mt-1 px-1">
                      <Clock className="w-2.5 h-2.5 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(comment.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={commentsEndRef} />
          </>
        )}
      </div>

      {/* Comment Input */}
      <div className="border-t border-gray-200 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={200}
            disabled={!isConnected || isSending}
          />
          <button
            onClick={handleSendComment}
            disabled={!newComment.trim() || !isConnected || isSending}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="mt-1 text-xs text-gray-500 text-right">
          {newComment.length}/200
        </div>
      </div>
    </div>
  );
};