'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { AuthModal } from './AuthModal';
import { UserMenu } from './UserMenu';
import { LogIn, Home, Users } from 'lucide-react';

export function Header() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { isAuthenticated } = useAuthStore();
  const pathname = usePathname();
  
  return (
    <>
      <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-orange-600 bg-clip-text text-transparent font-display">
                  Debate Bingo
                </h1>
              </Link>
              
              {/* Navigation Links */}
              <nav className="hidden md:flex items-center gap-4">
                <Link
                  href="/"
                  className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    pathname === '/' 
                      ? 'bg-gray-100 text-gray-900' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Home className="w-4 h-4" />
                  Solo Play
                </Link>
                {isAuthenticated && (
                  <Link
                    href="/multiplayer"
                    className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      pathname === '/multiplayer' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Users className="w-4 h-4" />
                    Multiplayer
                  </Link>
                )}
              </nav>
            </div>
            
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <UserMenu />
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </header>
      
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}