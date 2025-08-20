import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useBingoStore } from '@/stores/bingoStore';
import { bingoApi } from '@/services/api';
import {
  CreateGameRequest,
  UpdateCardRequest,
  CompleteGameRequest,
} from '@/types/bingo';

export const useBingoGame = () => {
  const queryClient = useQueryClient();
  const {
    currentGame,
    setCurrentGame,
    setLoading,
    setError,
    toggleCardPosition,
    completeGame,
    resetGame,
    isPositionChecked,
    getCard,
    checkForWin,
  } = useBingoStore();

  // Query to get phrases
  const {
    data: phrases,
    isLoading: phrasesLoading,
    error: phrasesError,
  } = useQuery({
    queryKey: ['bingo-phrases'],
    queryFn: bingoApi.getPhrases,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Mutation to create a new game
  const createGameMutation = useMutation({
    mutationFn: (data: CreateGameRequest) => bingoApi.createGame(data),
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (game) => {
      setCurrentGame(game);
      queryClient.setQueryData(['bingo-game', game.session_id], game);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create game');
    },
    onSettled: () => {
      setLoading(false);
    },
  });

  // Query to get current game
  const {
    data: gameData,
    isLoading: gameLoading,
    error: gameError,
  } = useQuery({
    queryKey: ['bingo-game', currentGame?.session_id],
    queryFn: () => bingoApi.getGame(currentGame!.session_id),
    enabled: !!currentGame?.session_id,
    refetchInterval: 5000, // Refetch every 5 seconds for real-time updates
  });

  // Mutation to update card position
  const updateCardMutation = useMutation({
    mutationFn: ({
      sessionId,
      position,
      data,
    }: {
      sessionId: string;
      position: number;
      data: UpdateCardRequest;
    }) => bingoApi.updateCardPosition(sessionId, position, data),
    onSuccess: (updatedGame) => {
      setCurrentGame(updatedGame);
      queryClient.setQueryData(['bingo-game', updatedGame.session_id], updatedGame);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update card');
    },
  });

  // Mutation to complete game
  const completeGameMutation = useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string;
      data: CompleteGameRequest;
    }) => bingoApi.completeGame(sessionId, data),
    onSuccess: (completedGame) => {
      setCurrentGame(completedGame);
      queryClient.setQueryData(['bingo-game', completedGame.session_id], completedGame);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to complete game');
    },
  });

  // Helper functions
  const createNewGame = (data: CreateGameRequest) => {
    resetGame();
    createGameMutation.mutate(data);
  };

  const handleCardClick = async (position: number) => {
    if (!currentGame) return;

    const card = getCard(position);
    if (!card || card.is_free_space) return;

    const isCurrentlyChecked = isPositionChecked(position);
    const newCheckedState = !isCurrentlyChecked;

    // Optimistically update the UI
    toggleCardPosition(position);

    // Update the backend
    try {
      await updateCardMutation.mutateAsync({
        sessionId: currentGame.session_id,
        position,
        data: { is_checked: newCheckedState },
      });

      // Check for win condition
      if (newCheckedState) {
        const winningCombination = checkForWin();
        if (winningCombination) {
          completeGame(winningCombination);
          await completeGameMutation.mutateAsync({
            sessionId: currentGame.session_id,
            data: {
              winning_combination: winningCombination.positions,
              completion_time: new Date().toISOString(),
            },
          });
        }
      }
    } catch (error) {
      // Revert optimistic update on error
      toggleCardPosition(position);
    }
  };

  const startNewGame = () => {
    resetGame();
    queryClient.removeQueries({ queryKey: ['bingo-game'] });
  };

  return {
    // Data
    phrases,
    currentGame,
    gameData,

    // Loading states
    isLoading: createGameMutation.isPending || gameLoading,
    phrasesLoading,
    isUpdating: updateCardMutation.isPending,
    isCompleting: completeGameMutation.isPending,

    // Error states
    error: createGameMutation.error || gameError || phrasesError,

    // Actions
    createNewGame,
    handleCardClick,
    startNewGame,
    resetGame,

    // Utility functions
    isPositionChecked,
    getCard,
    checkForWin,

    // Store functions
    ...useBingoStore(),
  };
};