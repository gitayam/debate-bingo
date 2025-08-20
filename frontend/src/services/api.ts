import axios from 'axios';
import {
  BingoPhrase,
  BingoGameSession,
  CreateGameRequest,
  UpdateCardRequest,
  CompleteGameRequest,
} from '@/types/bingo';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8745';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const bingoApi = {
  // Get all phrases
  getPhrases: async (): Promise<BingoPhrase[]> => {
    const response = await api.get('/bingo/phrases');
    return response.data;
  },

  // Create a new game session
  createGame: async (data: CreateGameRequest): Promise<BingoGameSession> => {
    const response = await api.post('/bingo/game', data);
    return response.data;
  },

  // Get game session by ID
  getGame: async (sessionId: string): Promise<BingoGameSession> => {
    const response = await api.get(`/bingo/game/${sessionId}`);
    return response.data;
  },

  // Update card position
  updateCardPosition: async (
    sessionId: string,
    position: number,
    data: UpdateCardRequest
  ): Promise<BingoGameSession> => {
    const response = await api.patch(
      `/bingo/game/${sessionId}/position/${position}`,
      data
    );
    return response.data;
  },

  // Complete game
  completeGame: async (
    sessionId: string,
    data: CompleteGameRequest
  ): Promise<BingoGameSession> => {
    const response = await api.post(`/bingo/game/${sessionId}/complete`, data);
    return response.data;
  },
};

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);