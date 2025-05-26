// /home/ubuntu/user-panel/components/layout/Layout.tsx
// Autor: Szymon Fuchs
// Data: 17.08.2021
import React from 'react';
import NavigationMenu from './NavigationMenu';
import { useAuth } from '../../hooks/useAuth';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen"><p>Ładowanie...</p></div>;
  }

  if (!isAuthenticated) {
    if (typeof window !== 'undefined' && window.location.pathname !== '/login' && window.location.pathname !== '/register' && !window.location.pathname.startsWith('/password-reset')) {
         window.location.href = '/login';
    }
    return null;
  }

  return (
    <div className="flex">
      <NavigationMenu />
      <main className="flex-1 p-4 sm:p-8 bg-gray-100 min-h-screen">
        {children}
      </main>
    </div>
  );
};

export default Layout;
