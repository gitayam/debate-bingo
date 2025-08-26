'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Clock, 
  Users, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle,
  CheckCircle,
  Shield,
  MessageSquare,
  Gavel
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useWebSocket } from '@/contexts/SimpleWebSocketContext';

interface EventDetails {
  id: string;
  type: string;
  phrase?: string;
  message: string;
  timestamp: string;
  userId?: string;
  username?: string;
  playersMarked?: number;
  disputes?: Dispute[];
  supports?: Support[];
  votes?: { up: number; down: number; userVote?: 'up' | 'down' | null };
  isSubstantiated?: boolean;
  substantiatedBy?: string;
  substantiatedAt?: string;
}

interface Dispute {
  id: string;
  userId: string;
  username: string;
  reason: string;
  timestamp: string;
}

interface Support {
  id: string;
  userId: string;
  username: string;
  reason: string;
  timestamp: string;
}

interface EventDetailsModalProps {
  event: EventDetails;
  isOpen: boolean;
  onClose: () => void;
}

export const EventDetailsModal: React.FC<EventDetailsModalProps> = ({ 
  event, 
  isOpen, 
  onClose 
}) => {
  const { user } = useAuthStore();
  const { socket, roomCode } = useWebSocket();
  const [activeTab, setActiveTab] = useState<'details' | 'challenge' | 'support'>('details');
  const [challengeReason, setChallengeReason] = useState('');
  const [supportReason, setSupportReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localVotes, setLocalVotes] = useState(event.votes || { up: 0, down: 0 });
  const [userVote, setUserVote] = useState<'up' | 'down' | null>(event.votes?.userVote || null);
  
  // Check if user is admin (you may need to adjust this based on your auth implementation)
  const isAdmin = user?.role === 'admin' || user?.isAdmin;

  useEffect(() => {
    if (isOpen) {
      // Request full event details when modal opens
      if (socket && roomCode) {
        socket.send(JSON.stringify({
          type: 'get_event_details',
          eventId: event.id,
          roomCode
        }));
      }
    }
  }, [isOpen, event.id, socket, roomCode]);

  // Listen for event updates
  useEffect(() => {
    if (!socket || !isOpen) return;

    const handleMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'event_details_update' && data.eventId === event.id) {
          // Update local state with new data
          if (data.votes) {
            setLocalVotes(data.votes);
            setUserVote(data.votes.userVote || null);
          }
        }
      } catch (error) {
        console.error('Error handling event update:', error);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, event.id, isOpen]);

  const handleVote = (voteType: 'up' | 'down') => {
    if (!socket || !roomCode) return;

    const newVote = userVote === voteType ? null : voteType;
    
    // Optimistic update
    setUserVote(newVote);
    setLocalVotes(prev => ({
      up: prev.up + (voteType === 'up' ? (newVote ? 1 : -1) : (userVote === 'up' ? -1 : 0)),
      down: prev.down + (voteType === 'down' ? (newVote ? 1 : -1) : (userVote === 'down' ? -1 : 0))
    }));

    socket.send(JSON.stringify({
      type: 'vote_event',
      eventId: event.id,
      voteType: newVote,
      roomCode
    }));
  };

  const handleChallenge = async () => {
    if (!challengeReason.trim() || !socket || !roomCode) return;

    setIsSubmitting(true);
    try {
      socket.send(JSON.stringify({
        type: 'challenge_event',
        eventId: event.id,
        reason: challengeReason.trim(),
        userId: user?.id,
        username: user?.username || 'Anonymous',
        roomCode
      }));
      
      setChallengeReason('');
      setActiveTab('details');
    } catch (error) {
      console.error('Error submitting challenge:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSupport = async () => {
    if (!supportReason.trim() || !socket || !roomCode) return;

    setIsSubmitting(true);
    try {
      socket.send(JSON.stringify({
        type: 'support_event',
        eventId: event.id,
        reason: supportReason.trim(),
        userId: user?.id,
        username: user?.username || 'Anonymous',
        roomCode
      }));
      
      setSupportReason('');
      setActiveTab('details');
    } catch (error) {
      console.error('Error submitting support:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubstantiate = () => {
    if (!socket || !roomCode || !isAdmin) return;

    socket.send(JSON.stringify({
      type: 'substantiate_event',
      eventId: event.id,
      adminId: user?.id,
      adminName: user?.username || 'Admin',
      roomCode
    }));
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Event Details</h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-200 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Substantiation Banner */}
        {event.isSubstantiated && (
          <div className="px-6 py-3 bg-green-50 border-b border-green-200">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-green-800">
                Substantiated by {event.substantiatedBy}
              </span>
              {event.substantiatedAt && (
                <span className="text-xs text-green-600 ml-auto">
                  {formatTimestamp(event.substantiatedAt)}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Event Info */}
        <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {event.phrase || event.message}
          </h3>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{formatTimestamp(event.timestamp)}</span>
            </div>
            {event.playersMarked !== undefined && (
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                <span>{event.playersMarked} players marked this</span>
              </div>
            )}
          </div>
        </div>

        {/* Voting Section */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => handleVote('up')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors ${
                  userVote === 'up'
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
                <span className="font-medium">{localVotes.up}</span>
              </button>
              <button
                onClick={() => handleVote('down')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors ${
                  userVote === 'down'
                    ? 'bg-red-100 text-red-700 border border-red-300'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <ThumbsDown className="w-4 h-4" />
                <span className="font-medium">{localVotes.down}</span>
              </button>
            </div>
            
            {isAdmin && !event.isSubstantiated && (
              <button
                onClick={handleSubstantiate}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              >
                <Gavel className="w-4 h-4" />
                Mark as Substantiated
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('details')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'details'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Discussion ({(event.disputes?.length || 0) + (event.supports?.length || 0)})
            </div>
          </button>
          <button
            onClick={() => setActiveTab('challenge')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'challenge'
                ? 'text-orange-600 border-b-2 border-orange-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Challenge
            </div>
          </button>
          <button
            onClick={() => setActiveTab('support')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'support'
                ? 'text-green-600 border-b-2 border-green-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Shield className="w-4 h-4" />
              Support
            </div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="px-6 py-4 max-h-[300px] overflow-y-auto">
          {activeTab === 'details' && (
            <div className="space-y-4">
              {/* Challenges */}
              {event.disputes && event.disputes.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Challenges</h4>
                  <div className="space-y-2">
                    {event.disputes.map((dispute) => (
                      <div key={dispute.id} className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{dispute.username}</p>
                            <p className="text-sm text-gray-700 mt-1">{dispute.reason}</p>
                          </div>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(dispute.timestamp)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Supports */}
              {event.supports && event.supports.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Support</h4>
                  <div className="space-y-2">
                    {event.supports.map((support) => (
                      <div key={support.id} className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{support.username}</p>
                            <p className="text-sm text-gray-700 mt-1">{support.reason}</p>
                          </div>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(support.timestamp)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(!event.disputes || event.disputes.length === 0) && 
               (!event.supports || event.supports.length === 0) && (
                <p className="text-center text-gray-500 py-8">
                  No discussions yet. Be the first to challenge or support this event!
                </p>
              )}
            </div>
          )}

          {activeTab === 'challenge' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Provide evidence or reasoning why this event didn't actually happen:
              </p>
              <textarea
                value={challengeReason}
                onChange={(e) => setChallengeReason(e.target.value)}
                placeholder="Explain why you think this didn't happen..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                rows={4}
                maxLength={500}
              />
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {challengeReason.length}/500 characters
                </span>
                <button
                  onClick={handleChallenge}
                  disabled={!challengeReason.trim() || isSubmitting}
                  className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Challenge'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'support' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Provide evidence or reasoning why this event did happen:
              </p>
              <textarea
                value={supportReason}
                onChange={(e) => setSupportReason(e.target.value)}
                placeholder="Explain why you think this did happen..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                rows={4}
                maxLength={500}
              />
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {supportReason.length}/500 characters
                </span>
                <button
                  onClick={handleSupport}
                  disabled={!supportReason.trim() || isSubmitting}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Support'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};