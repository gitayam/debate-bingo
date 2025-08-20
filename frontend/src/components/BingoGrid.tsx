'use client';

import React from 'react';
import { useBingoGame } from '@/hooks/useBingoGame';
import { GridSize } from '@/types/bingo';
import { clsx } from 'clsx';

interface BingoGridProps {
  gridSize: GridSize;
  className?: string;
}

export const BingoGrid: React.FC<BingoGridProps> = ({ gridSize, className }) => {
  const { currentGame, handleCardClick, isPositionChecked, isUpdating } = useBingoGame();

  if (!currentGame) {
    return null;
  }

  const renderCell = (position: number) => {
    const card = currentGame.cards.find((c) => c.position === position);
    if (!card) return null;

    const isChecked = isPositionChecked(position);
    const isFreeSpace = card.is_free_space;

    return (
      <button
        key={position}
        onClick={() => !isFreeSpace && handleCardClick(position)}
        disabled={isFreeSpace || isUpdating}
        className={clsx(
          'bingo-cell transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
          {
            'bingo-cell-free': isFreeSpace,
            'bingo-cell-checked': isChecked && !isFreeSpace,
            'bingo-cell-unchecked': !isChecked && !isFreeSpace,
            'cursor-not-allowed opacity-60': isUpdating,
            'cursor-pointer': !isFreeSpace && !isUpdating,
            'cursor-default': isFreeSpace,
          }
        )}
        title={isFreeSpace ? 'Free Space' : card.phrase.text}
      >
        <span className="text-center leading-tight">
          {isFreeSpace ? '★ FREE ★' : card.phrase.text}
        </span>
      </button>
    );
  };

  return (
    <div className={clsx('w-full max-w-4xl mx-auto', className)}>
      {/* Grid header for 5x5 */}
      {gridSize === 5 && (
        <div className="grid grid-cols-5 gap-2 mb-4 text-center font-bold text-2xl text-primary-600 dark:text-primary-400">
          <div>B</div>
          <div>I</div>
          <div>N</div>
          <div>G</div>
          <div>O</div>
        </div>
      )}

      {/* Bingo grid */}
      <div
        className={clsx(
          'grid gap-2 w-full',
          gridSize === 3 ? 'grid-cols-3' : 'grid-cols-5'
        )}
        style={{
          aspectRatio: '1',
        }}
      >
        {Array.from({ length: gridSize * gridSize }, (_, i) => renderCell(i))}
      </div>
    </div>
  );
};