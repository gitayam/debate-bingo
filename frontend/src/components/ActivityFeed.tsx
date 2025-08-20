'use client';

import React from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { 
  CheckSquare, 
  Trophy, 
  AlertTriangle, 
  UserPlus, 
  UserMinus,
  MessageSquare,
  Zap,
  Clock
} from 'lucide-react';

export const ActivityFeed: React.FC = () => {
  const { activityFeed, roomCode } = useWebSocket();

  if (!roomCode) {
    return null;
  }

  const getActivityIcon = (type: string, icon?: string) => {
    switch (icon || type) {
      case 'check-square':
      case 'square_marked':
        return <CheckSquare className="w-4 h-4" />;
      case 'trophy':
      case 'bingo_called':
        return <Trophy className="w-4 h-4" />;
      case 'alert-triangle':
      case 'dispute_initiated':
        return <AlertTriangle className="w-4 h-4" />;
      case 'user-plus':
      case 'user_joined':
        return <UserPlus className="w-4 h-4" />;
      case 'user-minus':
      case 'user_left':
        return <UserMinus className="w-4 h-4" />;
      case 'message':
        return <MessageSquare className="w-4 h-4" />;
      default:
        return <Zap className="w-4 h-4" />;
    }
  };

  const getActivityColor = (priority?: string, color?: string) => {
    if (color) {
      switch (color) {
        case 'blue': return 'text-blue-600 bg-blue-50 border-blue-200';
        case 'green': return 'text-green-600 bg-green-50 border-green-200';
        case 'yellow': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        case 'red': return 'text-red-600 bg-red-50 border-red-200';
        case 'orange': return 'text-orange-600 bg-orange-50 border-orange-200';
        default: return 'text-gray-600 bg-gray-50 border-gray-200';
      }
    }

    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'normal': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'low': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
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

  return (
    <div className="bg-white rounded-lg shadow-md h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Activity Feed</h3>
        <p className="text-xs text-gray-500">Live updates from all players</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {activityFeed.length === 0 ? (
          <div className="text-center py-8">
            <Zap className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No activity yet</p>
            <p className="text-xs text-gray-400 mt-1">Activities will appear here in real-time</p>
          </div>
        ) : (
          activityFeed.map((activity) => {
            const colorClass = getActivityColor(activity.priority, activity.color);
            
            return (
              <div
                key={activity.id}
                className={`flex items-start gap-3 p-3 rounded-lg border transition-all hover:shadow-sm ${colorClass}`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getActivityIcon(activity.type, activity.icon)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 break-words">
                    {activity.message}
                  </p>
                  {activity.data?.bonus_points && activity.data.bonus_points > 0 && (
                    <p className="text-xs text-yellow-600 mt-1">
                      +{activity.data.bonus_points} speed bonus!
                    </p>
                  )}
                  {activity.data?.reason && (
                    <p className="text-xs text-gray-600 mt-1 italic">
                      "{activity.data.reason}"
                    </p>
                  )}
                  <div className="flex items-center gap-1 mt-1">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>
                </div>
                {activity.priority === 'critical' && (
                  <div className="flex-shrink-0">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      BINGO!
                    </span>
                  </div>
                )}
                {activity.type === 'dispute_initiated' && activity.data?.expires_in && (
                  <div className="flex-shrink-0">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                      Vote Now
                    </span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {activityFeed.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-500 text-center">
            Showing last {activityFeed.length} activities
          </p>
        </div>
      )}
    </div>
  );
};