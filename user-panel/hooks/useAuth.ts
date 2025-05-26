// /home/ubuntu/user-panel/hooks/useAuth.ts
// Autor: Szymon Fuchs
// Data: 16.08.2021 (aktualizacja 06.08.2021 dla Fazy 1)
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const PUBLIC_PATHS = ['/login', '/register', '/password-reset', '/password-reset/confirm/[token]'];

export const useAuth = (redirectTo = "/login") => {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('saleorAuthToken');
    const currentPath = router.pathname;
    
    // Map dynamic route to its base for PUBLIC_PATHS check
    const isPublicPath = PUBLIC_PATHS.some(publicPath => {
        if (publicPath.includes('[token]')) {
            return currentPath.startsWith(publicPath.split('[token]')[0]);
        }
        return publicPath === currentPath;
    });

    if (!token && !isPublicPath) {
      if (typeof window !== 'undefined') {
         router.push(redirectTo);
      }
    } else if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, [router, redirectTo]);

  return { isAuthenticated, loading };
};
